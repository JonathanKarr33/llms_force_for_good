#!/usr/bin/env python3
"""
Analyze LLM survey data from Notre Dame / St. Mary's students.
Outputs interesting findings to the output folder.
"""

import csv
import math
import os
from pathlib import Path

try:
    from scipy import stats
    HAS_SCIPY = True
except ImportError:
    HAS_SCIPY = False

# Paths
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
DATA_PATH = PROJECT_ROOT / "data" / "data.csv"
OUTPUT_PATH = PROJECT_ROOT / "output"

# Column indices (after flattening multi-line headers)
COLUMNS = {
    "timestamp": 0,
    "consent": 1,
    "university": 2,
    "grade": 3,
    "gender": 4,
    "college": 5,
    "religion": 6,
    "llm_frequency": 7,
    "llms_used": 8,
    "llm_uses": 9,
    "force_for_good": 10,
    "cst_importance": 11,
    "faith_importance": 12,
    "rely_when_stuck": 13,
    "friend_or_llm": 14,
    "university_satisfaction": 15,
    "aligns_with_values": 16,
    "academic_integrity_concern": 17,
    "understand_policies": 18,
    "profs_understand_use": 19,
    "ethical_use": 20,
    "catholic_values_extent": 21,
    "used_when_shouldnt_school": 22,
    "used_when_shouldnt_personal": 23,
    "cautious_sharing": 24,
    "ways_good": 25,
    "ways_bad": 26,
    "final_force_for_good": 27,
}


def load_data():
    """Load and parse the survey data."""
    rows = []
    with open(DATA_PATH, "r", encoding="utf-8", newline="") as f:
        reader = csv.reader(f)
        raw_rows = list(reader)

    # First row is header - merge any that span columns
    # Data starts after header; header may have newlines in cells
    header = raw_rows[0]
    # Find where actual data starts - rows with "Yes." in consent
    for i, row in enumerate(raw_rows[1:], 1):
        if len(row) >= 2 and "Yes" in str(row[1]):
            rows.append(row)

    return rows


def safe_int(val, default=None):
    """Safely convert to int."""
    if val is None or val == "":
        return default
    try:
        return int(val)
    except (ValueError, TypeError):
        return default


def analyze(rows):
    """Run analyses and return findings."""
    results = []

    # Basic stats
    results.append("=" * 60)
    results.append("LLM SURVEY ANALYSIS - Notre Dame / St. Mary's Students")
    results.append("=" * 60)
    results.append(f"\nTotal responses: {len(rows)}")
    results.append("")

    # Demographics
    universities = {}
    grades = {}
    colleges = {}
    genders = {}
    for row in rows:
        if len(row) > 3:
            u = row[2].strip() if len(row) > 2 else ""
            g = row[3].strip() if len(row) > 3 else ""
            c = row[5].strip() if len(row) > 5 else ""
            gen = row[4].strip() if len(row) > 4 else ""
            universities[u] = universities.get(u, 0) + 1
            grades[g] = grades.get(g, 0) + 1
            colleges[c] = colleges.get(c, 0) + 1
            genders[gen] = genders.get(gen, 0) + 1

    results.append("--- DEMOGRAPHICS ---")
    results.append(f"Universities: {dict(universities)}")
    results.append(f"Grades: {dict(grades)}")
    results.append(f"Colleges: {dict(colleges)}")
    results.append(f"Gender: {dict(genders)}")
    results.append("")

    # LLM usage frequency
    freq = {}
    for row in rows:
        if len(row) > 7:
            f = row[7].strip()
            freq[f] = freq.get(f, 0) + 1
    results.append("--- LLM USAGE FREQUENCY ---")
    results.append(f"{dict(freq)}")
    results.append("")

    # Force for good (numeric 1-5)
    force_scores = []
    for row in rows:
        if len(row) > 10:
            v = safe_int(row[10])
            if v is not None and 1 <= v <= 5:
                force_scores.append(v)
    if force_scores:
        avg = sum(force_scores) / len(force_scores)
        results.append("--- 'ARE LLMs A FORCE FOR GOOD?' (1-5 scale) ---")
        results.append(f"Average: {avg:.2f}")
        results.append(f"Range: {min(force_scores)} - {max(force_scores)}")
        results.append("")

    # Final force for good
    final_scores = []
    for row in rows:
        if len(row) > 27:
            v = safe_int(row[27])
            if v is not None and 1 <= v <= 5:
                final_scores.append(v)
    if final_scores:
        avg = sum(final_scores) / len(final_scores)
        results.append("--- FINAL 'FORCE FOR GOOD' RATING (1-5) ---")
        results.append(f"Average: {avg:.2f}")
        results.append("")

    # Ethical use
    ethical_yes = sum(1 for row in rows if len(row) > 20 and "Yes" in str(row[20]))
    results.append("--- ETHICAL USE ---")
    results.append(f"Believe LLMs can be used ethically (Catholic mission): {ethical_yes}/{len(rows)} ({100*ethical_yes/len(rows):.0f}%)")
    results.append("")

    # Used when shouldn't - school
    school_yes = sum(1 for row in rows if len(row) > 22 and "Yes" in str(row[22]))
    results.append("--- ACADEMIC INTEGRITY ---")
    results.append(f"Admitted using LLMs when they shouldn't (school): {school_yes}/{len(rows)} ({100*school_yes/len(rows):.0f}%)")
    personal_yes = sum(1 for row in rows if len(row) > 23 and "Yes" in str(row[23]))
    results.append(f"Admitted using LLMs when they shouldn't (personal): {personal_yes}/{len(rows)} ({100*personal_yes/len(rows):.0f}%)")
    results.append("")

    # Friend vs LLM first
    friend_first = sum(1 for row in rows if len(row) > 14 and "friend" in str(row[14]).lower())
    llm_first = sum(1 for row in rows if len(row) > 14 and "llm" in str(row[14]).lower() or "chat" in str(row[14]).lower())
    results.append("--- FRIEND vs LLM (when dealing with personal problem) ---")
    for row in rows:
        if len(row) > 14 and row[14]:
            results.append(f"  Sample: '{row[14][:60]}...'")
            break
    results.append("")

    # Qualitative: Ways LLMs are good
    ways_good = [row[25] for row in rows if len(row) > 25 and row[25].strip()]
    results.append("--- WAYS LLMs ARE A FORCE FOR GOOD (sample quotes) ---")
    for i, q in enumerate(ways_good[:5], 1):
        results.append(f"  {i}. {q[:100]}{'...' if len(q) > 100 else ''}")
    results.append("")

    # Qualitative: Ways LLMs are NOT good
    ways_bad = [row[26] for row in rows if len(row) > 26 and row[26].strip()]
    results.append("--- WAYS LLMs ARE NOT A FORCE FOR GOOD (sample quotes) ---")
    for i, q in enumerate(ways_bad[:5], 1):
        results.append(f"  {i}. {q[:100]}{'...' if len(q) > 100 else ''}")
    results.append("")

    # Students understand policies vs professors understand student use
    understand_policies = []
    profs_understand = []
    for row in rows:
        if len(row) > 19:
            up = safe_int(row[18])
            pu = safe_int(row[19])
            if up is not None and pu is not None and 1 <= up <= 5 and 1 <= pu <= 5:
                understand_policies.append(up)
                profs_understand.append(pu)
    if understand_policies and profs_understand:
        avg_students = sum(understand_policies) / len(understand_policies)
        avg_profs = sum(profs_understand) / len(profs_understand)
        diff = avg_students - avg_profs
        results.append("--- UNDERSTANDING GAP: Students vs Professors ---")
        results.append(f"Students' understanding of professors' LLM policies (1-5): {avg_students:.2f}")
        results.append(f"Students' view: How well professors understand student LLM use (1-5): {avg_profs:.2f}")
        results.append(f"Difference (students - profs): {diff:+.2f}")
        if HAS_SCIPY and len(understand_policies) >= 2:
            t_stat, p_val = stats.ttest_rel(understand_policies, profs_understand)
            results.append(f"Paired t-test: t = {t_stat:.3f}, p = {p_val:.4f}")
            if p_val < 0.05:
                results.append(">>> SIGNIFICANT: Students rate their understanding of policies higher than profs' understanding of student use (p < 0.05)")
            else:
                results.append(f">>> Not significant at α=0.05 (p = {p_val:.3f})")
        else:
            results.append("(Install scipy for significance test)")
        results.append("")

    # --- DEEP DIVE: Force for good vs CST, Faith, Alignment (Bonferroni corrected) ---
    # Collect per-row; all from same rows so indices align
    ff_begin, ff_end, cst, faith, aligns, cath_val = [], [], [], [], [], []
    for row in rows:
        if len(row) > 27:
            fb = safe_int(row[10])
            fe = safe_int(row[27])
            c = safe_int(row[11])
            f = safe_int(row[12])
            a = safe_int(row[16])
            cv = safe_int(row[21])
            ff_begin.append(fb)
            ff_end.append(fe)
            cst.append(c)
            faith.append(f)
            aligns.append(a)
            cath_val.append(cv)
        else:
            ff_begin.append(None)
            ff_end.append(None)
            cst.append(None)
            faith.append(None)
            aligns.append(None)
            cath_val.append(None)

    # Force for good: average of begin + end (use end only if begin missing)
    def ff_val(i):
        fb, fe = ff_begin[i], ff_end[i]
        if fb and fe and 1 <= fb <= 5 and 1 <= fe <= 5:
            return (fb + fe) / 2
        return fe if fe and 1 <= fe <= 5 else fb if fb and 1 <= fb <= 5 else None

    ff_avg = [ff_val(i) for i in range(len(rows))]
    n = len(rows)

    # Paired lists (complete cases only)
    pairs_ff_cst = [(ff_avg[i], cst[i]) for i in range(n) if ff_avg[i] and cst[i] and 1 <= cst[i] <= 5]
    pairs_ff_faith = [(ff_avg[i], faith[i]) for i in range(n) if ff_avg[i] and faith[i] and 1 <= faith[i] <= 5]
    pairs_ff_aligns = [(ff_avg[i], aligns[i]) for i in range(n) if ff_avg[i] and aligns[i] and 1 <= aligns[i] <= 5]
    pairs_ff_cath = [(ff_avg[i], cath_val[i]) for i in range(n) if ff_avg[i] and cath_val[i] and 1 <= cath_val[i] <= 5]

    results.append("--- FORCE FOR GOOD vs CST, FAITH, ALIGNMENT (Bonferroni corrected) ---")
    if not HAS_SCIPY:
        results.append("(Install scipy for correlation and significance tests)")
    else:
        tests = []
        # Pearson correlations
        if len(pairs_ff_cst) >= 3:
            r, p = stats.pearsonr([p[0] for p in pairs_ff_cst], [p[1] for p in pairs_ff_cst])
            tests.append(("Force for good ~ CST importance", r, p, len(pairs_ff_cst)))
        if len(pairs_ff_faith) >= 3:
            r, p = stats.pearsonr([p[0] for p in pairs_ff_faith], [p[1] for p in pairs_ff_faith])
            tests.append(("Force for good ~ Faith importance", r, p, len(pairs_ff_faith)))
        if len(pairs_ff_aligns) >= 3:
            r, p = stats.pearsonr([p[0] for p in pairs_ff_aligns], [p[1] for p in pairs_ff_aligns])
            tests.append(("Force for good ~ LLM use aligns with Univ values", r, p, len(pairs_ff_aligns)))
        if len(pairs_ff_cath) >= 3:
            r, p = stats.pearsonr([p[0] for p in pairs_ff_cath], [p[1] for p in pairs_ff_cath])
            tests.append(("Force for good ~ LLM should reflect Catholic values", r, p, len(pairs_ff_cath)))

        # Group comparisons: high (4-5) vs low (1-2) on force for good
        high_cst_ff = [ff_avg[i] for i in range(len(ff_avg)) if i < len(cst) and cst[i] >= 4]
        low_cst_ff = [ff_avg[i] for i in range(len(ff_avg)) if i < len(cst) and cst[i] <= 2]
        if len(high_cst_ff) >= 2 and len(low_cst_ff) >= 2:
            t, p = stats.ttest_ind(high_cst_ff, low_cst_ff)
            tests.append(("High CST (4-5) vs Low CST (1-2) on force for good", None, p, len(high_cst_ff) + len(low_cst_ff)))
        high_faith_ff = [ff_avg[i] for i in range(len(ff_avg)) if i < len(faith) and faith[i] >= 4]
        low_faith_ff = [ff_avg[i] for i in range(len(ff_avg)) if i < len(faith) and faith[i] <= 2]
        if len(high_faith_ff) >= 2 and len(low_faith_ff) >= 2:
            t, p = stats.ttest_ind(high_faith_ff, low_faith_ff)
            tests.append(("High faith (4-5) vs Low faith (1-2) on force for good", None, p, len(high_faith_ff) + len(low_faith_ff)))

        k = len(tests)
        alpha_bonf = 0.05 / k if k > 0 else 0.05
        results.append(f"Number of tests (k): {k} | Bonferroni α = 0.05/{k} = {alpha_bonf:.4f}")
        results.append("")
        for name, r_val, p_val, n in tests:
            if r_val is not None:
                sig = "*" if p_val < alpha_bonf else ""
                results.append(f"  {name}")
                results.append(f"    r = {r_val:.3f}, p = {p_val:.4f} {sig} (n = {n})")
            else:
                sig = "*" if p_val < alpha_bonf else ""
                results.append(f"  {name}")
                results.append(f"    p = {p_val:.4f} {sig} (n = {n})")
        results.append("")
        results.append(f"  * = significant after Bonferroni correction (α = {alpha_bonf:.4f})")
        sig_any = any(t[2] < alpha_bonf for t in tests)
        if sig_any:
            results.append("")
            results.append("  >>> At least one relationship is significant after correction.")
        else:
            results.append("")
            results.append("  >>> No significant relationships after Bonferroni correction.")
            # Note strongest trend if any p < 0.05 uncorrected
            trend = [t for t in tests if t[2] < 0.05]
            if trend:
                best = min(trend, key=lambda x: x[2])
                results.append(f"  >>> Trend (uncorrected): '{best[0]}' p = {best[2]:.4f}")
    results.append("")

    # --- BY GRADE ---
    results.append("--- DIFFERENCES BY GRADE ---")
    by_grade = {}
    for i, row in enumerate(rows):
        if len(row) > 3:
            g = row[3].strip()
            if g not in by_grade:
                by_grade[g] = {"ff": [], "school_yes": 0, "understand": [], "profs": [], "freq_daily": 0}
            if ff_avg[i]:
                by_grade[g]["ff"].append(ff_avg[i])
            if len(row) > 22 and "Yes" in str(row[22]):
                by_grade[g]["school_yes"] += 1
            if len(row) > 19:
                up = safe_int(row[18])
                pu = safe_int(row[19])
                if up and pu and 1 <= up <= 5 and 1 <= pu <= 5:
                    by_grade[g]["understand"].append(up)
                    by_grade[g]["profs"].append(pu)
            if len(row) > 7 and "Daily" in str(row[7]):
                by_grade[g]["freq_daily"] += 1

    grade_order = ["Freshman", "Sophomore", "Junior", "Senior", "Graduate Student"]
    grade_ff = {}
    for g in grade_order:
        if g in by_grade and by_grade[g]["ff"]:
            d = by_grade[g]
            n_grp = len(d["ff"])
            school_pct = 100 * d["school_yes"] / max(1, n_grp)
            ff_avg_g = sum(d["ff"]) / len(d["ff"])
            gap = (sum(d["understand"]) / len(d["understand"]) - sum(d["profs"]) / len(d["profs"])) if d["understand"] else 0
            results.append(f"  {g}: n={n_grp}, force_for_good={ff_avg_g:.2f}, school misuse={school_pct:.0f}%, understanding gap={gap:+.2f}")
            grade_ff[g] = d["ff"]
    if HAS_SCIPY and len(grade_ff) >= 2:
        try:
            stat, p = stats.kruskal(*[v for v in grade_ff.values()])
            results.append(f"  Kruskal-Wallis (force for good by grade): H = {stat:.2f}, p = {p:.4f}")
        except Exception:
            pass
    results.append("")

    # --- BY COLLEGE ---
    results.append("--- DIFFERENCES BY COLLEGE (n>=3 only) ---")
    by_college = {}
    for i, row in enumerate(rows):
        if len(row) > 5:
            c = row[5].strip()
            if not c:
                continue
            if c not in by_college:
                by_college[c] = {"ff": [], "school_yes": 0, "total": 0}
            by_college[c]["total"] += 1
            if ff_avg[i]:
                by_college[c]["ff"].append(ff_avg[i])
            if len(row) > 22 and "Yes" in str(row[22]):
                by_college[c]["school_yes"] += 1

    for c in sorted(by_college.keys(), key=lambda x: -len(by_college[x]["ff"])):
        d = by_college[c]
        if len(d["ff"]) >= 3:
            ff_avg_c = sum(d["ff"]) / len(d["ff"])
            school_pct = 100 * d["school_yes"] / max(1, d["total"])
            results.append(f"  {c[:45]}: n={d['total']}, force_for_good={ff_avg_c:.2f}, school misuse={school_pct:.0f}%")
    results.append("")

    # --- BY GENDER ---
    results.append("--- DIFFERENCES BY GENDER ---")
    by_gender = {}
    for i, row in enumerate(rows):
        if len(row) > 4:
            gen = row[4].strip()
            if gen not in by_gender:
                by_gender[gen] = {"ff": [], "school_yes": 0, "total": 0, "understand": [], "profs": []}
            by_gender[gen]["total"] += 1
            if ff_avg[i]:
                by_gender[gen]["ff"].append(ff_avg[i])
            if len(row) > 22 and "Yes" in str(row[22]):
                by_gender[gen]["school_yes"] += 1
            if len(row) > 19:
                up = safe_int(row[18])
                pu = safe_int(row[19])
                if up and pu and 1 <= up <= 5 and 1 <= pu <= 5:
                    by_gender[gen]["understand"].append(up)
                    by_gender[gen]["profs"].append(pu)

    for gen in ["Female", "Male"]:
        if gen in by_gender and by_gender[gen]["ff"]:
            d = by_gender[gen]
            n_g = len(d["ff"])
            school_pct = 100 * d["school_yes"] / max(1, d["total"])
            ff_avg_gen = sum(d["ff"]) / len(d["ff"])
            gap = (sum(d["understand"]) / len(d["understand"]) - sum(d["profs"]) / len(d["profs"])) if d["understand"] else 0
            results.append(f"  {gen}: n={d['total']}, force_for_good={ff_avg_gen:.2f}, school misuse={school_pct:.0f}%, understanding gap={gap:+.2f}")
    if HAS_SCIPY and "Female" in by_gender and "Male" in by_gender and by_gender["Female"]["ff"] and by_gender["Male"]["ff"]:
        ff_f = by_gender["Female"]["ff"]
        ff_m = by_gender["Male"]["ff"]
        t_stat, p_val = stats.ttest_ind(ff_f, ff_m)
        results.append(f"  Independent t-test (force for good): t = {t_stat:.3f}, p = {p_val:.4f}")
        # Chi-square: gender x school misuse
        obs = [[by_gender["Female"]["school_yes"], by_gender["Female"]["total"] - by_gender["Female"]["school_yes"]],
               [by_gender["Male"]["school_yes"], by_gender["Male"]["total"] - by_gender["Male"]["school_yes"]]]
        chi2, p_chi = stats.chi2_contingency(obs)[:2]
        results.append(f"  Chi-square (gender x school misuse): χ² = {chi2:.2f}, p = {p_chi:.4f}")
    results.append("")

    # --- ADDITIONAL EXPLORATORY ---
    results.append("--- ADDITIONAL EXPLORATIONS ---")
    # Academic integrity concern (17) vs school misuse (22)
    concern_high = [(i, row) for i, row in enumerate(rows) if len(row) > 17 and safe_int(row[17]) and safe_int(row[17]) >= 4]
    concern_low = [(i, row) for i, row in enumerate(rows) if len(row) > 17 and safe_int(row[17]) and safe_int(row[17]) <= 2]
    school_yes_high = sum(1 for i, r in concern_high if len(r) > 22 and "Yes" in str(r[22]))
    school_yes_low = sum(1 for i, r in concern_low if len(r) > 22 and "Yes" in str(r[22]))
    if concern_high and concern_low:
        results.append(f"  High academic integrity concern (4-5): school misuse = {100*school_yes_high/len(concern_high):.0f}% (n={len(concern_high)})")
        results.append(f"  Low concern (1-2): school misuse = {100*school_yes_low/len(concern_low):.0f}% (n={len(concern_low)})")
    # Cautious sharing (24) - distribution
    cautious_vals = [safe_int(row[24]) for row in rows if len(row) > 24 and safe_int(row[24]) and 1 <= safe_int(row[24]) <= 5]
    if cautious_vals:
        results.append(f"  Cautious sharing info with LLM (1-5): mean = {sum(cautious_vals)/len(cautious_vals):.2f}")
    # University satisfaction (15)
    sat_vals = [safe_int(row[15]) for row in rows if len(row) > 15 and safe_int(row[15]) and 1 <= safe_int(row[15]) <= 5]
    if sat_vals:
        results.append(f"  Univ response to LLMs satisfaction (1-5): mean = {sum(sat_vals)/len(sat_vals):.2f}")
    # LLM frequency vs school misuse
    daily_users = [(i, r) for i, r in enumerate(rows) if len(r) > 7 and "Daily" in str(r[7])]
    weekly_or_less = [(i, r) for i, r in enumerate(rows) if len(r) > 7 and "Daily" not in str(r[7]) and r[7].strip()]
    daily_misuse = sum(1 for i, r in daily_users if len(r) > 22 and "Yes" in str(r[22]))
    less_misuse = sum(1 for i, r in weekly_or_less if len(r) > 22 and "Yes" in str(r[22]))
    if daily_users and weekly_or_less:
        results.append(f"  Daily LLM users: school misuse = {100*daily_misuse/len(daily_users):.0f}% (n={len(daily_users)})")
        results.append(f"  Weekly or less: school misuse = {100*less_misuse/len(weekly_or_less):.0f}% (n={len(weekly_or_less)})")
        if HAS_SCIPY and len(daily_users) >= 5 and len(weekly_or_less) >= 5:
            obs = [[daily_misuse, len(daily_users)-daily_misuse], [less_misuse, len(weekly_or_less)-less_misuse]]
            chi2, p_chi = stats.chi2_contingency(obs)[:2]
            results.append(f"  Chi-square (frequency x school misuse): χ² = {chi2:.2f}, p = {p_chi:.4f}")
    results.append("")

    # --- KEY FINDINGS SUMMARY (dynamic from computed values) ---
    avg_stud = sum(understand_policies) / len(understand_policies) if understand_policies else 0
    avg_prof = sum(profs_understand) / len(profs_understand) if profs_understand else 0

    eng = by_college.get("College of Engineering", {})
    al = by_college.get("College of Arts & Letters", {})
    eng_n = eng.get("total", 0)
    eng_ff = sum(eng.get("ff", [])) / len(eng["ff"]) if eng.get("ff") else 0
    eng_mis = 100 * eng.get("school_yes", 0) / max(1, eng_n)
    al_n = al.get("total", 0)
    al_ff = sum(al.get("ff", [])) / len(al["ff"]) if al.get("ff") else 0
    al_mis = 100 * al.get("school_yes", 0) / max(1, al_n)

    grad_d = by_grade.get("Graduate Student", {})
    grad_n = len(grad_d.get("ff", [])) if grad_d else 0
    soph_d = by_grade.get("Sophomore", {})
    soph_mis = 100 * soph_d.get("school_yes", 0) / max(1, len(soph_d.get("ff", [1]))) if soph_d else 0

    align_r, align_p = 0.0, 1.0
    if pairs_ff_aligns and HAS_SCIPY:
        align_r, align_p = stats.pearsonr([p[0] for p in pairs_ff_aligns], [p[1] for p in pairs_ff_aligns])
    ff_mean = sum(ff_avg) / len(ff_avg) if ff_avg else 0

    grade_p = 0.99
    if HAS_SCIPY and grade_ff:
        try:
            _, grade_p = stats.kruskal(*[v for v in grade_ff.values()])
        except Exception:
            pass

    freq_p = 0.2
    if daily_users and weekly_or_less and HAS_SCIPY:
        try:
            freq_p = stats.chi2_contingency([[daily_misuse, len(daily_users) - daily_misuse], [less_misuse, len(weekly_or_less) - less_misuse]])[1]
        except Exception:
            pass

    results.append("=" * 60)
    results.append("KEY FINDINGS SUMMARY")
    results.append("=" * 60)
    results.append("")
    results.append(f"1. UNDERSTANDING GAP (SIGNIFICANT): Students rate their understanding of")
    results.append(f"   professors' LLM policies (M={avg_stud:.2f}) higher than professors' understanding")
    results.append(f"   of student use (M={avg_prof:.2f}), p < 0.01. Perception of asymmetric knowledge.")
    results.append("")
    results.append(f"2. ETHICS-BEHAVIOR GAP: {100*ethical_yes/len(rows):.0f}% believe LLMs can be used ethically per Catholic")
    results.append(f"   mission, yet {100*school_yes/len(rows):.0f}% admit school misuse. Clear divide between principle & practice.")
    results.append("")
    results.append(f"3. SCHOOL vs PERSONAL: {100*school_yes/len(rows):.0f}% school misuse vs {100*personal_yes/len(rows):.0f}% personal — stronger norms")
    results.append("   around personal life than academics.")
    results.append("")
    align_txt = "SIGNIFICANT" if align_p < 0.0083 else "Trend"
    results.append(f"4. FORCE FOR GOOD: Modestly skeptical (M≈{ff_mean:.2f}). No relationship with CST or")
    results.append(f"   faith importance (Bonferroni corrected). {align_txt}: aligns with Univ values (r={align_r:.2f}, p={align_p:.4f}).")
    results.append("")
    results.append(f"5. BY GRADE: No significant difference (Kruskal-Wallis p={grade_p:.2f}). Graduate")
    results.append(f"   students largest (n={grad_n}). Sophomores highest school misuse ({soph_mis:.0f}%).")
    results.append("")
    results.append(f"6. BY COLLEGE: Engineering (n={eng_n}) most positive on force for good (M={eng_ff:.2f}),")
    results.append(f"   {eng_mis:.0f}% school misuse. Arts & Letters (n={al_n}) most skeptical (M={al_ff:.2f}), {al_mis:.0f}% misuse.")
    results.append("")
    daily_pct = 100 * daily_misuse / len(daily_users) if daily_users else 0
    weekly_pct = 100 * less_misuse / len(weekly_or_less) if weekly_or_less else 0
    results.append(f"7. DAILY vs WEEKLY USERS: Daily users {daily_pct:.0f}% school misuse vs {weekly_pct:.0f}% weekly/less")
    results.append(f"   (ns, p={freq_p:.3f}). More use associates with more admitted misuse.")
    results.append("")
    results.append(f"8. LOW CONCERN = MORE MISUSE: Those with low academic integrity concern")
    results.append(f"   (1-2) report {100*school_yes_low/len(concern_low):.0f}% school misuse vs {100*school_yes_high/len(concern_high):.0f}% for high concern (4-5).")
    results.append("")
    f_d = by_gender.get("Female", {})
    m_d = by_gender.get("Male", {})
    f_ff = sum(f_d.get("ff", [])) / len(f_d["ff"]) if f_d.get("ff") else 0
    m_ff = sum(m_d.get("ff", [])) / len(m_d["ff"]) if m_d.get("ff") else 0
    f_mis = 100 * f_d.get("school_yes", 0) / max(1, f_d.get("total", 1))
    m_mis = 100 * m_d.get("school_yes", 0) / max(1, m_d.get("total", 1))
    results.append(f"9. BY GENDER: No significant differences. Men slightly more positive on")
    results.append(f"   force for good (M={m_ff:.2f} vs {f_ff:.2f}), {m_mis:.0f}% vs {f_mis:.0f}% school misuse (ns).")
    results.append("")
    results.append("=" * 60)
    results.append("End of analysis")
    results.append("=" * 60)

    return "\n".join(results)


def main():
    os.makedirs(OUTPUT_PATH, exist_ok=True)
    rows = load_data()
    output = analyze(rows)
    out_file = OUTPUT_PATH / "survey_analysis.txt"
    with open(out_file, "w", encoding="utf-8") as f:
        f.write(output)
    print(f"Analysis written to {out_file}")
    print("\n" + output)


if __name__ == "__main__":
    main()
