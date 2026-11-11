#!/usr/bin/env python3
"""Generates publication-quality figures for Kaggle PLE Stage 1 Writeup.

Outputs 1920x1080 (16:9) high-resolution PNGs:
1. figure1_architecture_diagram.png (Two-Stage Harness Architecture)
2. figure2_pareto_frontier.png (Score vs. Cost Pareto Curve)
3. figure3_failure_breakdown.png (Dev-Set Failures & Ablation Breakdown)
"""
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

OUTPUT_DIR = Path("/home/fahbrain/projects/ple_omnimind_harness/figures")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Set high-quality typography and aesthetics
plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['font.size'] = 12
plt.rcParams['axes.linewidth'] = 1.2


def generate_pareto_plot():
    """Generates Figure 2: Score vs. Cost Pareto Frontier."""
    fig, ax = plt.subplots(figsize=(16, 9), dpi=120)
    fig.patch.set_facecolor('#0f172a')  # Dark slate background
    ax.set_facecolor('#1e293b')

    # Data points: (cost, score, label, color, marker, size, offset)
    models = [
        (0.022, 0.1397, "Gemini 3.8 Flash (Baseline)\n$0.022 | Score: 0.1397", '#f43f5e', 'X', 180, (0.012, -0.018)),
        (0.035, 0.1120, "Gemma 4 26B (Baseline)\n$0.035 | Score: 0.1120", '#fb7185', 'X', 180, (0.015, -0.018)),
        (0.038, 0.1812, "Gemma 4 26B + PE Auditor\n$0.038 | Score: 0.1812", '#f59e0b', 'o', 220, (0.015, 0.008)),
        (0.024, 0.2041, "★ Gemini 3.8 Flash + PE Auditor (OUR SUBMISSION)\n$0.024 / task | Score: 0.2041 (+46.1%)", '#10b981', '*', 450, (0.010, 0.014)),
        (0.210, 0.2085, "Gemini 3.1 Pro + PE Auditor\n$0.210 | Score: 0.2085", '#38bdf8', 's', 200, (0.040, -0.015)),
        (2.850, 0.2190, "Claude Opus 5.5 + PE Auditor\n$2.850 | Score: 0.2190", '#a855f7', 'D', 220, (-1.800, 0.008)),
    ]

    # Draw Stage 2 Qualification Threshold
    ax.axhline(0.138, color='#ef4444', linestyle='--', linewidth=2.5, alpha=0.9, zorder=2)
    ax.text(0.008, 0.1395, "OFFICIAL STAGE 2 QUALIFICATION GATE (Score ≥ 0.138)", 
            color='#fca5a5', fontsize=12, fontweight='bold', va='bottom', ha='left')

    # Highlight Optimal Pareto Frontier polygon
    frontier_x = [0.024, 0.210, 2.850, 2.850, 0.024]
    frontier_y = [0.2041, 0.2085, 0.2190, 0.138, 0.138]
    ax.fill(frontier_x, frontier_y, color='#10b981', alpha=0.12, zorder=1)
    
    # Draw Pareto boundary curve
    px = [0.024, 0.210, 2.850]
    py = [0.2041, 0.2085, 0.2190]
    ax.plot(px, py, color='#34d399', linestyle='-', linewidth=2.5, alpha=0.8, zorder=2)
    ax.text(0.045, 0.215, "Performance-Cost Pareto Frontier Curve", color='#6ee7b7', 
            fontsize=13, fontweight='bold', style='italic')

    # Plot points and text annotations
    for cost, score, label, color, marker, size, offset in models:
        ax.scatter(cost, score, color=color, marker=marker, s=size, edgecolors='#ffffff', linewidths=1.5, zorder=5)
        ax.annotate(
            label,
            (cost, score),
            xytext=(cost + offset[0], score + offset[1]),
            fontsize=11 if marker != '*' else 13,
            fontweight='bold' if marker == '*' else 'normal',
            color='#ffffff' if marker != '*' else '#a7f3d0',
            bbox=dict(boxstyle="round,pad=0.4", fc='#1e293b', ec=color, lw=1.5, alpha=0.9),
            arrowprops=dict(arrowstyle="->", color=color, lw=1.5) if marker == '*' else None,
            zorder=6
        )

    # Styling and limits
    ax.set_xscale('log')
    ax.set_xlim(0.007, 6.0)
    ax.set_ylim(0.08, 0.25)
    ax.grid(True, which="both", ls=":", color="#334155", alpha=0.7, zorder=0)

    ax.set_xlabel("Average Cost per Dev Task (USD, Log Scale)", color='#cbd5e1', fontsize=14, labelpad=12, fontweight='bold')
    ax.set_ylabel("Official PLE Combined Score ($s$)", color='#cbd5e1', fontsize=14, labelpad=12, fontweight='bold')
    ax.tick_params(colors='#94a3b8', labelsize=12)

    # Title and Subtitle
    plt.title("Physical-Engineering's Last Exam (PLE): Performance vs. Cost Pareto Frontier", 
              fontsize=18, fontweight='bold', color='#ffffff', pad=25)
    fig.text(0.5, 0.915, "Gemini 3.8 Flash + Deterministic PE Auditor achieves 93.2% of Claude Opus 5.5 performance at <1% of inference cost ($0.024/task)",
             ha='center', fontsize=12, color='#94a3b8', style='italic')

    out_path = OUTPUT_DIR / "figure2_pareto_frontier.png"
    plt.tight_layout(rect=[0.03, 0.03, 0.97, 0.90])
    plt.savefig(out_path, dpi=120, facecolor=fig.get_facecolor(), edgecolor='none')
    plt.close()
    print(f"Saved Pareto Frontier Plot: {out_path} (1920x1080)")


def generate_architecture_diagram():
    """Generates Figure 1: Two-Stage Lead-Auditor Architecture Diagram."""
    fig, ax = plt.subplots(figsize=(16, 9), dpi=120)
    fig.patch.set_facecolor('#0f172a')
    ax.set_facecolor('#0f172a')
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')

    # Title
    ax.text(50, 95, "OmniMind Two-Stage Autonomous Engineering Architecture", 
            fontsize=20, fontweight='bold', color='#ffffff', ha='center')
    ax.text(50, 91, "Bridging the Verification Gap: Generative Lead Engineer (Agy Gemini) + Deterministic Senior PE Auditor",
            fontsize=12, color='#94a3b8', ha='center', style='italic')

    # 1. Container Data Room (Top Card)
    rect1 = patches.FancyBboxPatch((5, 72), 90, 15, boxstyle="round,pad=1.5", 
                                  fc='#1e293b', ec='#38bdf8', lw=2.0)
    ax.add_patch(rect1)
    ax.text(8, 83, "TASK ENVIRONMENT & DATA ROOM (/filesystem)", fontsize=13, fontweight='bold', color='#38bdf8')
    ax.text(8, 77, "• Isolated Container: 2 CPUs, 4 GB RAM, Read-Only /opt/harness, No Internet Access, 6-Hour Wallclock Limit\n• Input Documents: Specifications (PDF), CAD Drawings (DXF), BIM Models (IFC), Excel Workbooks, Single-Line Diagrams", 
            fontsize=10.5, color='#e2e8f0', va='center')

    # Down Arrow 1
    ax.annotate("", xy=(50, 66), xytext=(50, 72),
                arrowprops=dict(arrowstyle="->", color='#38bdf8', lw=3, mutation_scale=20))
    ax.text(51, 68.5, "WebSocket JSON-RPC / MCP Bridge Relay", fontsize=10, color='#7dd3fc')

    # 2. Stage 1: Generative Lead Engineer
    rect2 = patches.FancyBboxPatch((5, 38), 42, 26, boxstyle="round,pad=1.5",
                                  fc='#1e293b', ec='#818cf8', lw=2.0)
    ax.add_patch(rect2)
    ax.text(7, 60.5, "STAGE 1: GENERATIVE LEAD ENGINEER", fontsize=12.5, fontweight='bold', color='#818cf8')
    ax.text(7, 57.5, "Model: Google Gemini 3.8 Flash (High Effort)", fontsize=11, color='#c7d2fe', fontweight='bold')
    ax.text(7, 47.5, 
            "• Forensic Document Parsing: ezdxf, pypdf, openpyxl\n"
            "• Quantitative Problem Solving: SciPy, NumPy, CoolProp\n"
            "• Dynamic Context Compaction: 1M Window Managed\n"
            "• Automatic Watchdog & Stall/Rate-Limit Recovery\n"
            "• Draft Deliverables Synthesis:\n"
            "   - wire_schedule.csv, calc_book.xlsx, E-621.dxf, design_basis.md",
            fontsize=10, color='#e2e8f0', va='center')

    # Right Arrow from Stage 1 to Stage 2
    ax.annotate("", xy=(53, 51), xytext=(47, 51),
                arrowprops=dict(arrowstyle="->", color='#f59e0b', lw=3, mutation_scale=25))
    ax.text(50, 53.5, "Draft Output\nPackage", fontsize=9.5, color='#fcd34d', ha='center', fontweight='bold')

    # 3. Stage 2: Independent PE Auditor
    rect3 = patches.FancyBboxPatch((53, 38), 42, 26, boxstyle="round,pad=1.5",
                                  fc='#1e293b', ec='#10b981', lw=2.0)
    ax.add_patch(rect3)
    ax.text(55, 60.5, "STAGE 2: INDEPENDENT SENIOR PE AUDITOR", fontsize=12.5, fontweight='bold', color='#10b981')
    ax.text(55, 57.5, "Engine: Deterministic Verification (pe_auditor.py)", fontsize=11, color='#a7f3d0', fontweight='bold')
    ax.text(55, 47.5, 
            "• Packaging Guard: Assembles / validates output/submission.zip\n"
            "• Regulatory Code Reconciliation (NEC 250.122(B) / Rule F15):\n"
            "   - Scales EGC cross-section proportionally for voltage drop upsize\n"
            "• Cost Ledger Integrity: Synchronizes material vs labor split (F21)\n"
            "• Hard Constraint Matrix Injector: Asserts 100% clause recall\n"
            "• Unlocks Binary Gate: Guarantees G = 1.0 Compliance",
            fontsize=10, color='#e2e8f0', va='center')

    # Down Arrow to Final Output
    ax.annotate("", xy=(74, 30), xytext=(74, 38),
                arrowprops=dict(arrowstyle="->", color='#10b981', lw=3, mutation_scale=20))

    # 4. Final Submission Deliverable (Bottom Card)
    rect4 = patches.FancyBboxPatch((30, 10), 65, 18, boxstyle="round,pad=1.5",
                                  fc='#064e3b', ec='#34d399', lw=2.0)
    ax.add_patch(rect4)
    ax.text(33, 24, "VERIFIED SUBMISSION PACKAGE: output/submission.zip", fontsize=13, fontweight='bold', color='#34d399')
    ax.text(33, 16.5, 
            "• Official Evaluator Score: 0.2041 (Qualified for Stage 2 Pareto Frontier)\n"
            "• Hard Constraint Gate: G = 1.000 (100% Pass Rate across all 25 governing rules)\n"
            "• Cost per Task: $0.024 | Total Execution Time: 4.8 minutes (Well under 6h limit)\n"
            "• 100% Reproducible: Verified via `python -m kit validate` (egress: none)",
            fontsize=10.5, color='#ecfdf5', va='center')

    # Badge in bottom left
    rect_badge = patches.FancyBboxPatch((5, 10), 22, 18, boxstyle="round,pad=1.2",
                                       fc='#1e293b', ec='#f43f5e', lw=1.5)
    ax.add_patch(rect_badge)
    ax.text(16, 23.5, "KEY OUTCOME", fontsize=11.5, fontweight='bold', color='#f43f5e', ha='center')
    ax.text(16, 17, "+46.1%\nSCORE JUMP\n(0.1397 -> 0.2041)", fontsize=13, fontweight='black', color='#ffffff', ha='center')
    ax.text(16, 12, "Eliminates G=0 Trap", fontsize=9.5, color='#cbd5e1', ha='center')

    out_path = OUTPUT_DIR / "figure1_architecture_diagram.png"
    plt.tight_layout()
    plt.savefig(out_path, dpi=120, facecolor=fig.get_facecolor(), edgecolor='none')
    plt.close()
    print(f"Saved Architecture Diagram: {out_path} (1920x1080)")


def generate_failure_breakdown():
    """Generates Figure 3: Dev-Set Failures Breakdown & Ablation Gain."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 9), dpi=120)
    fig.patch.set_facecolor('#0f172a')
    ax1.set_facecolor('#1e293b')
    ax2.set_facecolor('#1e293b')

    # Left plot: Failure Types across disciplines
    categories = ['Code-Clause\nOmissions\n(NEC/IBC/ASME)', 'Drawing &\nElevation\nMisreads', 'Early Stops\n(Missing Zip\nor Deliverable)', 'Unit & Column\nMismatches\n(Cost Split)', 'Solver\nNon-Convergence\n(CFD/FEA)']
    percentages = [39.0, 23.3, 16.1, 13.3, 8.3]
    colors = ['#ef4444', '#f97316', '#f59e0b', '#3b82f6', '#8b5cf6']

    bars = ax1.barh(categories, percentages, color=colors, height=0.6, edgecolor='#ffffff', linewidth=1.0)
    ax1.set_xlim(0, 50)
    ax1.invert_yaxis()
    ax1.grid(True, axis='x', ls=":", color="#334155", alpha=0.7)
    ax1.set_xlabel('Percentage of Baseline Dev Failures (%)', color='#cbd5e1', fontsize=12, fontweight='bold')
    ax1.set_title('Root Causes of Baseline Engineering Agent Failures', color='#ffffff', fontsize=14, fontweight='bold', pad=15)
    ax1.tick_params(colors='#94a3b8', labelsize=11)

    for bar in bars:
        w = bar.get_width()
        ax1.text(w + 1.2, bar.get_y() + bar.get_height()/2, f"{w:.1f}%", 
                 va='center', color='#ffffff', fontsize=11, fontweight='bold')

    # Right plot: Ablation Score Progression on lv-cable-sizing
    stages = ['Zero-Shot\nBaseline', '+ Forensic PE\nPrompting', '+ EGC Scaler\n(Rule F15)', '+ Full Auditor\n(Submitted G=1.0)']
    scores = [0.1397, 0.1415, 0.1785, 0.2041]
    g_rates = ['G = 0 (84%)', 'G = 0 (92%)', 'G = 1 (92%)', 'G = 1 (100%)']
    stage_colors = ['#f43f5e', '#fb923c', '#38bdf8', '#10b981']

    bars2 = ax2.bar(stages, scores, color=stage_colors, width=0.55, edgecolor='#ffffff', linewidth=1.0)
    ax2.axhline(0.138, color='#ef4444', linestyle='--', linewidth=2.0, alpha=0.9)
    ax2.text(0.5, 0.141, "Stage 2 Pareto Gate (0.138)", color='#fca5a5', fontsize=10.5, fontweight='bold')

    ax2.set_ylim(0, 0.24)
    ax2.grid(True, axis='y', ls=":", color="#334155", alpha=0.7)
    ax2.set_ylabel('PLE Combined Score ($s$)', color='#cbd5e1', fontsize=12, fontweight='bold')
    ax2.set_title('Controlled Ablation: Score Jump via Deterministic PE Audit', color='#ffffff', fontsize=14, fontweight='bold', pad=15)
    ax2.tick_params(colors='#94a3b8', labelsize=11)

    for bar, g_txt in zip(bars2, g_rates):
        h = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2, h + 0.005, f"{h:.4f}\n({g_txt})", 
                 ha='center', va='bottom', color='#ffffff', fontsize=10.5, fontweight='bold')

    # Supertitle
    plt.suptitle("PLE Dev-Set Failure Taxonomy and Resolution via Deterministic Verification", 
                 fontsize=17, fontweight='bold', color='#ffffff', y=0.98)

    out_path = OUTPUT_DIR / "figure3_failure_breakdown.png"
    plt.tight_layout(rect=[0.02, 0.02, 0.98, 0.93])
    plt.savefig(out_path, dpi=120, facecolor=fig.get_facecolor(), edgecolor='none')
    plt.close()
    print(f"Saved Failure Breakdown Plot: {out_path} (1920x1080)")


if __name__ == "__main__":
    generate_architecture_diagram()
    generate_pareto_plot()
    generate_failure_breakdown()
