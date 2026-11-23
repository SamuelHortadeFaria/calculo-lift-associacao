import math

import numpy as np
import pandas as pd


def floor_round(x, decimals=2):
    factor = 10 ** decimals
    return math.floor(x * factor) / factor


# --- Stage 1: build raw frames of (confidence, lift, support) tuples ---------
#
# Cells hold unrounded tuples so downstream stages (averaging, filtering,
# formatting) can work on the real numbers instead of pre-formatted strings.


def build_consequence_table(results, premise_cols, consequence_cols, is_a_to_b=True):
    """
    Premise x consequence frame: rows are premises, columns are consequences.

    ``results`` is the nested list from ``bulk_pair_binary_stats`` indexed as
    ``results[cons_idx][prem_idx]``. Each cell ``loc[prem, cons]`` is the raw,
    unrounded tuple ``(confidence, lift, support)`` for the rule ``prem -> cons``.
    """
    conf_key = "Confidence_A_to_B" if is_a_to_b else "Confidence_B_to_A"
    table = pd.DataFrame(index=premise_cols, columns=consequence_cols, dtype=object)

    for cons_idx, cons in enumerate(consequence_cols):
        for prem_idx, prem in enumerate(premise_cols):
            r = results[cons_idx][prem_idx]
            table.loc[prem, cons] = (r[conf_key], r["Lift"], r["Support"])

    return table


def build_cross_table(results, columns):
    """
    Square frame for the cross association of a single group of columns.

    ``results`` is the flat list from ``calculate_cross_rules``. Each off-diagonal
    cell ``loc[row, col]`` is the raw, unrounded tuple ``(confidence, lift,
    support)`` for the directional rule ``row -> col``; lift and support are
    symmetric, confidence is not. The diagonal is left empty.
    """
    table = pd.DataFrame(index=columns, columns=columns, dtype=object)

    for r in results:
        col_a, col_b = r["Rule"].split(" <-> ")
        lift = r["Lift"]
        support = r["Support"]
        table.loc[col_a, col_b] = (r["Confidence_A_to_B"], lift, support)
        table.loc[col_b, col_a] = (r["Confidence_B_to_A"], lift, support)

    return table


# --- Stage 2: append averages ------------------------------------------------


# Tuple component for each metric, with the label used in the appended summary.
_METRICS = (("Confiança", 0), ("Lift", 1), ("Suporte", 2))


def _component(cells, idx):
    """Pull the ``idx``-th tuple component out of ``cells``, skipping empty cells."""
    return [cell[idx] for cell in cells if isinstance(cell, tuple)]


def _summary(cells):
    """Return ``{Media_<metric>: mean, DP_<metric>: std}`` for one line of cells."""
    out = {}
    for label, idx in _METRICS:
        vals = _component(cells, idx)
        out[f"Media_{label}"] = float(np.mean(vals)) if vals else None
        out[f"DP_{label}"] = float(np.std(vals)) if vals else None
    return out


def append_averages(table, axis=0):
    """
    Append the mean and standard deviation of each value (confidence, lift,
    support) as summary lines: ``Media_Confiança``/``DP_Confiança``,
    ``Media_Lift``/``DP_Lift`` and ``Media_Suporte``/``DP_Suporte``.

    ``axis=0`` appends summary rows (aggregating down each column); ``axis=1``
    appends summary columns (aggregating across each row). Each summary cell is a
    raw scalar, so support stays available for filtering before formatting.
    Returns a new frame; the input is left untouched.
    """
    result = table.copy()

    if axis == 0:
        per_col = {col: _summary(table[col]) for col in table.columns}
        for stat in _summary([]):  # iterate the six labels in order
            result.loc[stat] = pd.Series({col: per_col[col][stat] for col in table.columns})
    elif axis == 1:
        per_row = {idx: _summary(table.loc[idx]) for idx in table.index}
        for stat in _summary([]):
            result[stat] = pd.Series({idx: per_row[idx][stat] for idx in table.index})
    else:
        raise ValueError("axis must be 0 (append rows) or 1 (append columns)")

    return result


# --- Stage 3: format for CSV -------------------------------------------------


def format_conf_lift(table, decimals=2):
    """
    Render each ``(confidence, lift, support)`` tuple as the ``"conf (lift)"``
    string, floored to ``decimals`` places. Scalar summary cells (the appended
    averages and DPs) are floored to the same precision; empty cells are left
    untouched. Returns a new frame ready for ``to_csv``.
    """
    def fmt(cell):
        if isinstance(cell, tuple):
            conf, lift, _support = cell
            return f"{floor_round(conf, decimals):.{decimals}f} ({floor_round(lift, decimals):.{decimals}f})"
        if isinstance(cell, (int, float)) and not (isinstance(cell, float) and math.isnan(cell)):
            return f"{floor_round(cell, decimals):.{decimals}f}"
        return cell

    return table.map(fmt)
