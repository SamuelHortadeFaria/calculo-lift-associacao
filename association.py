from itertools import combinations

def pair_binary_stats(df, col_a, col_b, total_n):
    # Pre-processing: Clean 'X' vs empty/NaN
    s_a = df[col_a].fillna('').apply(lambda x: str(x).strip().upper() == 'X')
    s_b = df[col_b].fillna('').apply(lambda x: str(x).strip().upper() == 'X')

    # 1. Counts
    count_a = s_a.sum()
    count_b = s_b.sum()
    count_both = (s_a & s_b).sum()

    # 2. Probabilities (Using the provided total_n)
    p_a = count_a / total_n
    p_b = count_b / total_n
    p_both = count_both / total_n

    # 3. Metrics
    support = p_both
    conf_a_to_b = count_both / count_a if count_a > 0 else 0
    conf_b_to_a = count_both / count_b if count_b > 0 else 0
    lift = p_both / (p_a * p_b) if (p_a * p_b) > 0 else 1.0

    return {
        "Rule": f"{col_a} <-> {col_b}",
        "Count_A": int(count_a),
        "Count_B": int(count_b),
        "Count_Both": int(count_both),
        "Support": round(support, 4),
        "Confidence_A_to_B": round(conf_a_to_b, 4),
        "Confidence_B_to_A": round(conf_b_to_a, 4),
        "Lift": round(lift, 4)
    }


# -----------------------------------

def calculate_cross_rules(df, columns, total_n):
    """
    Generates all cross pairings between the provided list of columns and return results
    """
    results = []

    for col_a, col_b in combinations(columns, 2):
        stats = pair_binary_stats(df, col_a, col_b, total_n)
        results.append(stats)

    return results

# -----------------------------------

def bulk_pair_binary_stats(df, premise_cols, consequence_cols, total_n):
    """
    Generates pairings between provided premise and consequence cols and return results
    """
    all_results = []

    for cons in consequence_cols:
        cons_results = []

        for prem in premise_cols:
            stats = pair_binary_stats(df, prem, cons, total_n)
            cons_results.append(stats)

        all_results.append(cons_results)

    return all_results


def bulk_pair_binary_stats_to_txt(results, filename):
    with open(filename, 'w') as f:
        f.write("PREMISE VS CONSEQUENCE ASSOCIATION RULE MINING RESULTS\n")
        for cons_results in results:
            f.write("=========================\n")
            f.write("=========================\n")
            f.write("=========================\n")
            for stats in cons_results:
                f.write("-----------------------\n")
                for key, value in stats.items():
                    f.write(f"{key}: {value}\n")