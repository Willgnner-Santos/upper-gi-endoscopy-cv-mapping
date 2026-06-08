"""
Gera duas figuras metodologicas para o artigo ENIAC/BRACIS:
  1. methodology_workflow.png  -- fluxo geral da revisao sistematica (3 fases)
  2. study_selection_flow.png  -- funil PRISMA de selecao dos estudos

Saida em: E:/Doutorado-V2/Revisao-Literatura-refinada-V3/consolidado/
"""

from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle
import matplotlib.patches as mpatches

OUT_DIR = Path(r"E:/Doutorado-V2/Revisão-Literatura-refinada-V3/consolidado")
OUT_DIR.mkdir(parents=True, exist_ok=True)

# Paleta sobria e moderna
NAVY    = "#0b2545"
BLUE    = "#13315c"
TEAL    = "#3a86b5"
SKY     = "#cfe3f3"
LIGHT   = "#eef4fa"
GREY_BG = "#f7f7f7"
GREY_BX = "#e9ecef"
TEXT    = "#0a0a0a"


def box(ax, x, y, w, h, text, *,
        fc=SKY, ec=BLUE, fontsize=10, fontweight="normal",
        text_color=TEXT, lw=1.4, rounding=0.06):
    patch = FancyBboxPatch(
        (x, y), w, h,
        boxstyle=f"round,pad=0.02,rounding_size={rounding}",
        linewidth=lw, edgecolor=ec, facecolor=fc,
    )
    ax.add_patch(patch)
    ax.text(
        x + w / 2, y + h / 2, text,
        ha="center", va="center",
        fontsize=fontsize, fontweight=fontweight, color=text_color,
        linespacing=1.35,
    )
    return (x, y, w, h)


def arrow(ax, p_from, p_to, *, color=NAVY, lw=1.6, mutation=18):
    a = FancyArrowPatch(
        p_from, p_to,
        arrowstyle="-|>", mutation_scale=mutation,
        linewidth=lw, color=color,
        shrinkA=2, shrinkB=2,
    )
    ax.add_patch(a)


def line(ax, p_from, p_to, *, color=NAVY, lw=1.6):
    a = FancyArrowPatch(
        p_from, p_to,
        arrowstyle="-", mutation_scale=10,
        linewidth=lw, color=color,
        shrinkA=0, shrinkB=0,
    )
    ax.add_patch(a)


# =============================================================================
# FIGURA 1 -- methodology workflow (3 fases x N etapas, layout vertical limpo)
# =============================================================================
def make_workflow():
    fig, ax = plt.subplots(figsize=(11, 6.5), dpi=300)
    ax.set_xlim(0, 22)
    ax.set_ylim(0, 12)
    ax.set_axis_off()
    ax.set_facecolor("white")

    # Tres "raias" verticais (uma por fase)
    phases = [
        {"name": "PLANNING",   "x": 1.0,  "color": NAVY,
         "steps": ["Goal & Scope\nDefinition",
                   "Research\nQuestions (GQM)",
                   "Search String\nConstruction"]},
        {"name": "CONDUCTING", "x": 8.4,  "color": TEAL,
         "steps": ["Database\nSearch (6 sources)",
                   "Screening &\nDeduplication",
                   "Eligibility &\nManual Triage",
                   "Data\nExtraction"]},
        {"name": "REPORTING",  "x": 15.8, "color": NAVY,
         "steps": ["Analysis &\nThematic Synthesis",
                   "Gap\nIdentification",
                   "Final Report &\nResearch Tracks"]},
    ]

    swim_w = 5.6
    swim_top = 11.2
    swim_bot = 0.6

    # fundo de cada raia
    for ph in phases:
        rect = FancyBboxPatch(
            (ph["x"] - 0.2, swim_bot - 0.05), swim_w + 0.4,
            swim_top - swim_bot + 0.1,
            boxstyle="round,pad=0.0,rounding_size=0.2",
            linewidth=0, facecolor=GREY_BG,
        )
        ax.add_patch(rect)
        # cabeçalho da fase
        ax.add_patch(FancyBboxPatch(
            (ph["x"], swim_top - 0.95), swim_w, 0.85,
            boxstyle="round,pad=0.02,rounding_size=0.10",
            linewidth=0, facecolor=ph["color"],
        ))
        ax.text(ph["x"] + swim_w / 2, swim_top - 0.52,
                ph["name"], ha="center", va="center",
                fontsize=13, fontweight="bold", color="white")

    # caixas de etapas em cada raia
    step_centers = {ph["name"]: [] for ph in phases}
    for ph in phases:
        n = len(ph["steps"])
        # area util: do fim do header ate o fundo da raia
        top = swim_top - 1.15
        bot = swim_bot + 0.3
        usable = top - bot
        h_box = 1.35
        if n > 1:
            spacing = (usable - n * h_box) / (n - 1)
        else:
            spacing = 0
        cur_top = top
        for step in ph["steps"]:
            y = cur_top - h_box
            box(ax, ph["x"] + 0.4, y, swim_w - 0.8, h_box, step,
                fc="white", ec=ph["color"], fontsize=10,
                fontweight="bold", lw=1.6)
            step_centers[ph["name"]].append(
                (ph["x"] + swim_w / 2, y, y + h_box / 2, y + h_box)
            )
            cur_top = y - spacing

    # setas verticais dentro da raia
    for ph in phases:
        centers = step_centers[ph["name"]]
        for i in range(len(centers) - 1):
            cx, ybot, _, _ = centers[i]
            cx2, _, _, ytop = centers[i + 1]
            arrow(ax, (cx, ybot), (cx2, ytop),
                  color=ph["color"], lw=1.8, mutation=18)

    # setas horizontais entre fases (do meio da raia A ao meio da raia B)
    for i in range(len(phases) - 1):
        a, b = phases[i], phases[i + 1]
        y_mid = (swim_top + swim_bot) / 2 - 0.5
        x_a = a["x"] + swim_w + 0.2
        x_b = b["x"] - 0.2
        arrow(ax, (x_a, y_mid), (x_b, y_mid),
              color=NAVY, lw=2.0, mutation=22)

    # rodape: refinamento iterativo (texto sob as raias, nao seta cruzada)
    ax.text(11, 0.15,
            "Steps within and across phases follow iterative refinement loops "
            "(PRISMA 2020).",
            ha="center", va="center",
            fontsize=9, fontstyle="italic", color="#444")

    plt.tight_layout()
    out = OUT_DIR / "methodology_workflow.png"
    plt.savefig(out, dpi=300, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"saved: {out}")


# =============================================================================
# FIGURA 2 -- study selection flow (PRISMA-like, alinhamento limpo)
# =============================================================================
def make_selection_flow():
    fig, ax = plt.subplots(figsize=(11, 8.0), dpi=300)
    ax.set_xlim(0, 22)
    ax.set_ylim(0, 16)
    ax.set_axis_off()
    ax.set_facecolor("white")

    # parametros de layout
    main_x   = 5.0
    main_w   = 9.0
    side_x   = 15.5
    side_w   = 5.5
    box_h    = 1.8
    gap      = 0.55
    label_x  = 0.6
    label_w  = 3.6

    # Definicao das fases (label, indices das caixas que cobre)
    # caixas principais (de cima para baixo)
    main_boxes = [
        # text, has_side, side_text
        ("Records identified through 6 databases\n"
         "IEEE Xplore, Scopus, Web of Science, PubMed,\n"
         "ScienceDirect, Springer Nature Link\n"
         "(n = 2,172)",
         True,
         "Duplicates removed\n(n = 737)"),
        ("Records after deduplication\n(by DOI + normalized title)\n(n = 1,435)",
         True,
         "Abstracts enriched via\nNCBI E-utilities and Crossref\n"
         "(78% coverage)"),
        ("Records screened by title, abstract\nand keywords with heuristic rules\n"
         "(n = 1,435)",
         True,
         "Manual triage (V1 + V3)\n65 borderline cases\n"
         "(14 included, 51 excluded)"),
        ("Records assessed for eligibility\n"
         "(automatic + manual decisions)\n(n = 1,435)",
         True,
         "Records excluded (n = 77)\nout-of-scope, editorial,\n"
         "non-image, false positives"),
        ("Studies included in the\nsystematic review\n(n = 1,358)",
         False, None),
    ]

    # fases que agrupam as caixas: (titulo, idx_inicio, idx_fim_inclusivo)
    phases = [
        ("Identification", 0, 0, NAVY),
        ("Screening",      1, 2, TEAL),
        ("Eligibility",    3, 3, NAVY),
        ("Inclusion",      4, 4, TEAL),
    ]

    # calcular posicoes Y das caixas principais (de cima para baixo)
    n = len(main_boxes)
    top_y = 14.0
    box_positions = []
    for i in range(n):
        y = top_y - i * (box_h + gap)
        box_positions.append(y)

    # caixas principais
    for i, (text, has_side, _) in enumerate(main_boxes):
        y = box_positions[i]
        box(ax, main_x, y, main_w, box_h, text,
            fc=SKY, ec=BLUE, fontsize=10, fontweight="normal", lw=1.8)

    # caixas laterais (alinhadas verticalmente com a caixa principal correspondente)
    for i, (_, has_side, side_text) in enumerate(main_boxes):
        if not has_side:
            continue
        y = box_positions[i]
        box(ax, side_x, y, side_w, box_h, side_text,
            fc=GREY_BX, ec="#888", fontsize=9, fontweight="normal", lw=1.2)

    # setas verticais entre caixas principais
    for i in range(n - 1):
        y1 = box_positions[i]
        y2 = box_positions[i + 1]
        cx = main_x + main_w / 2
        arrow(ax, (cx, y1), (cx, y2 + box_h),
              color=NAVY, lw=1.8, mutation=20)

    # setas horizontais (caixa principal -> lateral)
    for i, (_, has_side, _) in enumerate(main_boxes):
        if not has_side:
            continue
        y = box_positions[i] + box_h / 2
        arrow(ax, (main_x + main_w, y), (side_x, y),
              color=NAVY, lw=1.6, mutation=18)

    # rotulos verticais de fase (a esquerda, abrangendo as caixas que cobrem)
    for ph_name, idx_a, idx_b, color in phases:
        y_top = box_positions[idx_a] + box_h
        y_bot = box_positions[idx_b]
        h = y_top - y_bot
        # caixa do rotulo da fase
        rect = FancyBboxPatch(
            (label_x, y_bot), label_w, h,
            boxstyle="round,pad=0.02,rounding_size=0.10",
            linewidth=0, facecolor=color,
        )
        ax.add_patch(rect)
        ax.text(label_x + label_w / 2, y_bot + h / 2, ph_name,
                ha="center", va="center",
                fontsize=12, fontweight="bold", color="white",
                rotation=0)

    # rodape
    ax.text(11, 0.1,
            "Adapted from PRISMA 2020 [Page et al. 2021]",
            ha="center", va="center",
            fontsize=9, fontstyle="italic", color="#444")

    plt.tight_layout()
    out = OUT_DIR / "study_selection_flow.png"
    plt.savefig(out, dpi=300, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"saved: {out}")


if __name__ == "__main__":
    make_workflow()
    make_selection_flow()
