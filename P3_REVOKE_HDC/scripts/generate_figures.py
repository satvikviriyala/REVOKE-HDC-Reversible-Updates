"""
Generate Publication-Quality SVG Figures for REVOKE-HDC:
1. Fig. 2: Flip-Count Distribution (F) with Mean, p95, and Maximum indicators.
2. Fig. 3: Bytes per Update vs Flip Count (F), showing 16 + 2F curve,
   the 512-byte snapshot line, and the F = 248 break-even threshold.
"""

import csv
import json
import math
import os
from typing import List


def generate_figures():
    print("=== Generating REVOKE-HDC Figures ===")
    os.makedirs("P3_REVOKE_HDC/results/figures", exist_ok=True)

    # Load summary and raw data
    summary_path = "P3_REVOKE_HDC/results/processed/flip_density_summary.json"
    with open(summary_path) as f:
        summary = json.load(f)

    raw_csv_path = "P3_REVOKE_HDC/results/raw/flip_density_1000.csv"
    f_values = []
    with open(raw_csv_path) as f:
        reader = csv.DictReader(f)
        for row in reader:
            f_values.append(int(row["F"]))

    mean_f = summary["flip_distribution"]["mean_F"]
    p95_f = summary["flip_distribution"]["p95_F"]
    max_f = summary["flip_distribution"]["max_F"]

    # -------------------------------------------------------------
    # Figure 2: Flip-Count Distribution (F) Histogram
    # -------------------------------------------------------------
    bins = [0] * 100  # bins 0..99
    for val in f_values:
        if 0 <= val < 100:
            bins[val] += 1

    max_bin_count = max(bins)

    svg_w, svg_h = 800, 500
    margin_left, margin_right = 70, 40
    margin_top, margin_bottom = 60, 60
    plot_w = svg_w - margin_left - margin_right
    plot_h = svg_h - margin_top - margin_bottom

    # Build SVG 2
    svg2 = []
    svg2.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {svg_w} {svg_h}" width="{svg_w}" height="{svg_h}">')
    svg2.append('<rect width="100%" height="100%" fill="#ffffff"/>')
    svg2.append(f'<text x="{svg_w//2}" y="32" font-family="Arial, sans-serif" font-size="18" font-weight="bold" text-anchor="middle" fill="#1e293b">Figure 2: Measured Flip-Count Distribution (F) over 1,000 Admitted Updates</text>')

    # Gridlines and Y-axis
    y_ticks = 5
    for i in range(y_ticks + 1):
        y_val = int((max_bin_count / y_ticks) * i)
        y_pos = margin_top + plot_h - int((y_val / max_bin_count) * plot_h)
        svg2.append(f'<line x1="{margin_left}" y1="{y_pos}" x2="{margin_left + plot_w}" y2="{y_pos}" stroke="#e2e8f0" stroke-width="1"/>')
        svg2.append(f'<text x="{margin_left - 10}" y="{y_pos + 4}" font-family="Arial, sans-serif" font-size="12" text-anchor="end" fill="#64748b">{y_val}</text>')

    # X-axis ticks (0, 20, 40, 60, 80, 96)
    x_ticks = [0, 20, 40, 60, 80, 96]
    for tick in x_ticks:
        x_pos = margin_left + int((tick / 96.0) * plot_w)
        svg2.append(f'<line x1="{x_pos}" y1="{margin_top}" x2="{x_pos}" y2="{margin_top + plot_h}" stroke="#e2e8f0" stroke-width="1"/>')
        svg2.append(f'<text x="{x_pos}" y="{margin_top + plot_h + 20}" font-family="Arial, sans-serif" font-size="12" text-anchor="middle" fill="#64748b">{tick}</text>')

    # Histogram Bars (group into bin widths of 2)
    bar_width = (plot_w / 48.0) * 0.85
    for b in range(0, 96, 2):
        count = bins[b] + (bins[b+1] if b+1 < 100 else 0)
        bar_h = int((count / max_bin_count) * plot_h)
        x_pos = margin_left + int((b / 96.0) * plot_w)
        y_pos = margin_top + plot_h - bar_h
        svg2.append(f'<rect x="{x_pos}" y="{y_pos}" width="{bar_width:.1f}" height="{bar_h}" fill="#3b82f6" rx="2" opacity="0.85"/>')

    # Vertical Indicator Lines: Mean, p95, Max
    x_mean = margin_left + int((mean_f / 96.0) * plot_w)
    x_p95 = margin_left + int((p95_f / 96.0) * plot_w)
    x_max = margin_left + int((max_f / 96.0) * plot_w)

    # Mean Line (Green)
    svg2.append(f'<line x1="{x_mean}" y1="{margin_top}" x2="{x_mean}" y2="{margin_top + plot_h}" stroke="#10b981" stroke-width="2.5" stroke-dasharray="5,4"/>')
    svg2.append(f'<text x="{x_mean - 6}" y="{margin_top + 25}" font-family="Arial, sans-serif" font-size="12" font-weight="bold" fill="#047857" text-anchor="end">Mean F = {mean_f:.1f}</text>')

    # p95 Line (Amber)
    svg2.append(f'<line x1="{x_p95}" y1="{margin_top}" x2="{x_p95}" y2="{margin_top + plot_h}" stroke="#f59e0b" stroke-width="2.5" stroke-dasharray="5,4"/>')
    svg2.append(f'<text x="{x_p95 + 6}" y="{margin_top + 45}" font-family="Arial, sans-serif" font-size="12" font-weight="bold" fill="#b45309" text-anchor="start">p95 F = {p95_f}</text>')

    # Max Line (Purple)
    svg2.append(f'<line x1="{x_max}" y1="{margin_top}" x2="{x_max}" y2="{margin_top + plot_h}" stroke="#8b5cf6" stroke-width="2.5" stroke-dasharray="5,4"/>')
    svg2.append(f'<text x="{x_max - 6}" y="{margin_top + 65}" font-family="Arial, sans-serif" font-size="12" font-weight="bold" fill="#6d28d9" text-anchor="end">Max F = {max_f}</text>')

    # Axes
    svg2.append(f'<line x1="{margin_left}" y1="{margin_top + plot_h}" x2="{margin_left + plot_w}" y2="{margin_top + plot_h}" stroke="#334155" stroke-width="1.5"/>')
    svg2.append(f'<line x1="{margin_left}" y1="{margin_top}" x2="{margin_left}" y2="{margin_top + plot_h}" stroke="#334155" stroke-width="1.5"/>')

    # Axis Labels
    svg2.append(f'<text x="{margin_left + plot_w//2}" y="{margin_top + plot_h + 46}" font-family="Arial, sans-serif" font-size="13" font-weight="bold" text-anchor="middle" fill="#1e293b">Affected Dimensions per Update (F)</text>')
    svg2.append(f'<text transform="rotate(-90)" x="-{margin_top + plot_h//2}" y="24" font-family="Arial, sans-serif" font-size="13" font-weight="bold" text-anchor="middle" fill="#1e293b">Count of Updates</text>')

    svg2.append('</svg>')

    fig2_path = "P3_REVOKE_HDC/results/figures/fig2_flip_distribution.svg"
    with open(fig2_path, "w") as f:
        f.write("\n".join(svg2))
    print(f"Generated Figure 2: {fig2_path}")

    # -------------------------------------------------------------
    # Figure 3: Bytes per Update vs Flip Count (Break-Even Curve)
    # -------------------------------------------------------------
    svg3 = []
    svg3.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {svg_w} {svg_h}" width="{svg_w}" height="{svg_h}">')
    svg3.append('<rect width="100%" height="100%" fill="#ffffff"/>')
    svg3.append(f'<text x="{svg_w//2}" y="32" font-family="Arial, sans-serif" font-size="18" font-weight="bold" text-anchor="middle" fill="#1e293b">Figure 3: Journal Record Bytes vs Flip Count (F) &amp; Break-Even Boundary</text>')

    # X axis: F from 0 to 280
    # Y axis: Bytes from 0 to 600
    max_x = 280
    max_y = 600

    # Gridlines and Y ticks
    for y_val in range(0, max_y + 1, 100):
        y_pos = margin_top + plot_h - int((y_val / max_y) * plot_h)
        svg3.append(f'<line x1="{margin_left}" y1="{y_pos}" x2="{margin_left + plot_w}" y2="{y_pos}" stroke="#e2e8f0" stroke-width="1"/>')
        svg3.append(f'<text x="{margin_left - 10}" y="{y_pos + 4}" font-family="Arial, sans-serif" font-size="12" text-anchor="end" fill="#64748b">{y_val} B</text>')

    # X ticks
    for x_val in range(0, max_x + 1, 40):
        x_pos = margin_left + int((x_val / max_x) * plot_w)
        svg3.append(f'<line x1="{x_pos}" y1="{margin_top}" x2="{x_pos}" y2="{margin_top + plot_h}" stroke="#e2e8f0" stroke-width="1"/>')
        svg3.append(f'<text x="{x_pos}" y="{margin_top + plot_h + 20}" font-family="Arial, sans-serif" font-size="12" text-anchor="middle" fill="#64748b">{x_val}</text>')

    # Operating Range Shading (F in 0..96)
    x_96 = margin_left + int((96 / max_x) * plot_w)
    svg3.append(f'<rect x="{margin_left}" y="{margin_top}" width="{x_96 - margin_left}" height="{plot_h}" fill="#3b82f6" opacity="0.08"/>')
    svg3.append(f'<text x="{margin_left + (x_96 - margin_left)//2}" y="{margin_top + 30}" font-family="Arial, sans-serif" font-size="12" font-weight="bold" fill="#2563eb" text-anchor="middle">REVOKE-HDC Operating Regime (F ≤ 96)</text>')

    # Full Snapshot Baseline Line (512 Bytes, Red)
    y_snap = margin_top + plot_h - int((512 / max_y) * plot_h)
    svg3.append(f'<line x1="{margin_left}" y1="{y_snap}" x2="{margin_left + plot_w}" y2="{y_snap}" stroke="#ef4444" stroke-width="2.5"/>')
    svg3.append(f'<text x="{margin_left + plot_w - 10}" y="{y_snap - 8}" font-family="Arial, sans-serif" font-size="12" font-weight="bold" fill="#dc2626" text-anchor="end">Arm C Snapshot Baseline (512 Bytes)</text>')

    # Sparse Record Sizing Line: 16 + 2*F (Blue)
    p_start_x = margin_left
    p_start_y = margin_top + plot_h - int((16 / max_y) * plot_h)
    p_end_x = margin_left + int((max_x / max_x) * plot_w)
    p_end_y = margin_top + plot_h - int(((16 + 2 * max_x) / max_y) * plot_h)
    svg3.append(f'<line x1="{p_start_x}" y1="{p_start_y}" x2="{p_end_x}" y2="{p_end_y}" stroke="#2563eb" stroke-width="3"/>')
    svg3.append(f'<text x="{p_start_x + 60}" y="{p_start_y - 25}" font-family="Arial, sans-serif" font-size="12" font-weight="bold" fill="#1d4ed8">Arm D Sparse Journal (16 + 2F Bytes)</text>')

    # Break-even point (F = 248, Bytes = 512)
    x_be = margin_left + int((248 / max_x) * plot_w)
    y_be = margin_top + plot_h - int((512 / max_y) * plot_h)
    svg3.append(f'<circle cx="{x_be}" cy="{y_be}" r="6" fill="#f59e0b" stroke="#b45309" stroke-width="2"/>')
    svg3.append(f'<line x1="{x_be}" y1="{margin_top}" x2="{x_be}" y2="{margin_top + plot_h}" stroke="#f59e0b" stroke-width="1.5" stroke-dasharray="4,4"/>')
    svg3.append(f'<text x="{x_be + 8}" y="{y_be + 22}" font-family="Arial, sans-serif" font-size="12" font-weight="bold" fill="#b45309">Break-Even Point: F = 248 (512 B)</text>')

    # Maximum Operating Point marker (F = 96, Bytes = 208)
    x_fmax = margin_left + int((96 / max_x) * plot_w)
    y_fmax = margin_top + plot_h - int((208 / max_y) * plot_h)
    svg3.append(f'<circle cx="{x_fmax}" cy="{y_fmax}" r="6" fill="#10b981" stroke="#047857" stroke-width="2"/>')
    svg3.append(f'<text x="{x_fmax + 8}" y="{y_fmax - 8}" font-family="Arial, sans-serif" font-size="12" font-weight="bold" fill="#047857">F_max = 96 (208 B: 59.4% Memory Savings!)</text>')

    # Axes
    svg3.append(f'<line x1="{margin_left}" y1="{margin_top + plot_h}" x2="{margin_left + plot_w}" y2="{margin_top + plot_h}" stroke="#334155" stroke-width="1.5"/>')
    svg3.append(f'<line x1="{margin_left}" y1="{margin_top}" x2="{margin_left}" y2="{margin_top + plot_h}" stroke="#334155" stroke-width="1.5"/>')

    # Axis Labels
    svg3.append(f'<text x="{margin_left + plot_w//2}" y="{margin_top + plot_h + 46}" font-family="Arial, sans-serif" font-size="13" font-weight="bold" text-anchor="middle" fill="#1e293b">Flip Count / Affected Dimensions (F)</text>')
    svg3.append(f'<text transform="rotate(-90)" x="-{margin_top + plot_h//2}" y="20" font-family="Arial, sans-serif" font-size="13" font-weight="bold" text-anchor="middle" fill="#1e293b">Memory per Update (Bytes)</text>')

    svg3.append('</svg>')

    fig3_path = "P3_REVOKE_HDC/results/figures/fig3_bytes_vs_f_breakeven.svg"
    with open(fig3_path, "w") as f:
        f.write("\n".join(svg3))
    print(f"Generated Figure 3: {fig3_path}")


if __name__ == "__main__":
    generate_figures()
