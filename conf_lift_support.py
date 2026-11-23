import math

from conf_lift_table import floor_round

# --- Stage 3 (variant): format for CSV keeping support -----------------------
#
# Same tuple tables produced by ``build_consequence_table`` / ``build_cross_table``
# and annotated by ``append_averages`` in ``conf_lift_table``; the only difference
# from ``format_conf_lift`` is that the support component is kept in the output.


def format_conf_lift_support(table, decimals=2):
    """
    Render each ``(confidence, lift, support)`` tuple as the
    ``"conf (lift) [support]"`` string, floored to ``decimals`` places. Scalar
    summary cells (the appended averages and DPs) are floored to the same
    precision; empty cells are left untouched. Returns a new frame ready for
    ``to_csv``.
    """
    def fmt(cell):
        if isinstance(cell, tuple):
            conf, lift, support = cell
            return (
                f"{floor_round(conf, decimals):.{decimals}f} "
                f"({floor_round(lift, decimals):.{decimals}f}) "
                f"[{floor_round(support, decimals):.{decimals}f}]"
            )
        if isinstance(cell, (int, float)) and not (isinstance(cell, float) and math.isnan(cell)):
            return f"{floor_round(cell, decimals):.{decimals}f}"
        return cell

    return table.map(fmt)
