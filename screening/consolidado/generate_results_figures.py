"""
Gera figuras da secao de Resultados a partir dos numeros consolidados em
relatorio_revisao_literatura.md (V3).

Saida em: E:/Doutorado-V2/Revisao-Literatura-refinada-V3/consolidado/
  - publications_by_year.png
  - studies_by_database.png
  - themes_distribution.png
"""

from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

OUT_DIR = Path(r"E:/Doutorado-V2/Revisão-Literatura-refinada-V3/consolidado")
OUT_DIR.mkdir(parents=True, exist_ok=True)

# Paleta consistente com as figuras de metodologia
NAVY  = "#0b2545"
BLUE  = "#13315c"
TEAL  = "#3a86b5"
SKY   = "#cfe3f3"
LIGHT = "#eef4fa"
GREY  = "#888888"

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "axes.edgecolor": "#333",
    "axes.labelcolor": "#222",
    "axes.titleweight": "bold",
    "axes.spines.top": False,
    "axes.spines.right": False,
})


# =============================================================================
# Figura 1 — Publicacoes por ano (1.621 incluidos)
# =============================================================================
def make_publications_by_year():
    years = ["≤2014", "2015", "2016", "2017", "2018", "2019",
             "2020", "2021", "2022", "2023", "2024", "2025", "2026*"]
    counts = [40, 13, 11, 12, 26, 64, 94, 162, 163, 209, 260, 334, 232]

    fig, ax = plt.subplots(figsize=(9, 4.2), dpi=300)
    bars = ax.bar(years, counts, color=TEAL, edgecolor=BLUE, linewidth=1.0)

    # destaque do ano parcial
    bars[-1].set_color(SKY)
    bars[-1].set_edgecolor(BLUE)
    bars[-1].set_hatch("//")

    for b, c in zip(bars, counts):
        ax.text(b.get_x() + b.get_width() / 2, b.get_height() + 4,
                str(c), ha="center", va="bottom", fontsize=9, color=BLUE)

    ax.set_ylabel("Number of included studies", fontsize=11)
    ax.set_xlabel("Publication year", fontsize=11)
    ax.set_ylim(0, max(counts) + 40)
    ax.tick_params(axis="x", labelsize=10, rotation=0)
    ax.tick_params(axis="y", labelsize=10)
    ax.grid(axis="y", linestyle=":", alpha=0.4)

    ax.text(0.99, 0.95,
            "* 2026: partial coverage (collection up to May 2026)",
            transform=ax.transAxes, ha="right", va="top",
            fontsize=8, fontstyle="italic", color="#444")

    plt.tight_layout()
    out = OUT_DIR / "publications_by_year.png"
    plt.savefig(out, dpi=300, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"saved: {out}")


# =============================================================================
# Figura 2 — Estudos por base (apos triagem, deduplicado)
# =============================================================================
def make_studies_by_database():
    bases = ["Scopus", "Scopus\n(VLM/FMs)", "Springer\nNature Link", "PubMed",
             "ScienceDirect", "Web of\nScience", "IEEE\nXplore"]
    included = [426, 279, 269, 229, 197, 161, 60]
    raw       = [472, 379, 389, 325, 454, 386, 146]

    x = np.arange(len(bases))
    width = 0.38

    fig, ax = plt.subplots(figsize=(10, 4.5), dpi=300)
    b1 = ax.bar(x - width / 2, raw, width,
                label="Raw records", color=SKY, edgecolor=BLUE, linewidth=1.0)
    b2 = ax.bar(x + width / 2, included, width,
                label="Included after screening",
                color=TEAL, edgecolor=BLUE, linewidth=1.0)

    for bars in (b1, b2):
        for b in bars:
            ax.text(b.get_x() + b.get_width() / 2, b.get_height() + 6,
                    str(int(b.get_height())),
                    ha="center", va="bottom", fontsize=8, color=BLUE)

    ax.set_xticks(x)
    ax.set_xticklabels(bases, fontsize=9.5)
    ax.set_ylabel("Number of records", fontsize=11)
    ax.set_ylim(0, max(raw) + 70)
    ax.tick_params(axis="y", labelsize=10)
    ax.grid(axis="y", linestyle=":", alpha=0.4)
    ax.legend(loc="upper right", frameon=False, fontsize=10)

    plt.tight_layout()
    out = OUT_DIR / "studies_by_database.png"
    plt.savefig(out, dpi=300, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"saved: {out}")


# =============================================================================
# Figura 3 — Distribuicao tematica (frequencias do corpus)
# =============================================================================
def make_themes_distribution():
    # tema -> contagem (do _analytics_v3.json atualizado com S6-VLM-FMs)
    themes = [
        ("Gastric cancer",                267),
        ("Detection",                     253),
        ("Esophagus / Barrett / SCC",     239),
        ("Neoplasia / dysplasia / EGC",   157),
        ("Classification",                149),
        ("Segmentation",                  109),
        ("Capsule endoscopy",              84),
        ("Foundation model / VLM",         74),
        ("Polyp",                          64),
        ("Real-time",                      58),
        ("H. pylori",                      47),
        ("Ulcer",                          43),
        ("Attention mechanisms",           35),
        ("Dataset / benchmark",            32),
        ("Intestinal metaplasia",          29),
        ("Bleeding / hemorrhage",          28),
        ("Self-supervised learning",       21),
        ("Gastric atrophy",                20),
        ("Vision Transformer",             11),
        ("Explainability (Grad-CAM, XAI)",  8),
        ("Image artifact (saliva/light)",   9),
        ("Few-shot",                        5),
        ("Imbalance",                       4),
        ("Calibration / uncertainty",       4),
        ("Brazil / LatAm",                  2),
        ("Multilabel",                      2),
        ("Domain adaptation",               2),
    ]

    # ordenar e separar em "tematicas dominantes" vs "alvo da tese"
    target_set = {
        "Self-supervised learning", "Vision Transformer",
        "Explainability (Grad-CAM, XAI)", "Image artifact (saliva/light)",
        "Brazil / LatAm", "Domain adaptation", "Foundation model / VLM",
        "Multilabel", "Imbalance", "Few-shot", "Calibration / uncertainty",
    }

    themes.sort(key=lambda t: t[1], reverse=False)  # asc para barh top->bottom maior
    labels = [t[0] for t in themes]
    counts = [t[1] for t in themes]
    colors = [TEAL if lab not in target_set else "#d97706" for lab in labels]

    fig, ax = plt.subplots(figsize=(9, 9), dpi=300)
    bars = ax.barh(labels, counts, color=colors, edgecolor=BLUE, linewidth=0.8)

    for b, c in zip(bars, counts):
        ax.text(b.get_width() + 3, b.get_y() + b.get_height() / 2,
                str(c), va="center", ha="left", fontsize=8.5, color=BLUE)

    ax.set_xlabel("Number of included studies (n = 1,621)", fontsize=11)
    ax.set_xlim(0, max(counts) + 25)
    ax.tick_params(axis="x", labelsize=9)
    ax.tick_params(axis="y", labelsize=9.5)
    ax.grid(axis="x", linestyle=":", alpha=0.4)

    # legenda (proxy)
    p1 = mpatches.Patch(color=TEAL, label="Dominant topics")
    p2 = mpatches.Patch(color="#d97706", label="Thesis-target topics (gaps)")
    ax.legend(handles=[p1, p2], loc="lower right", frameon=False, fontsize=10)

    plt.tight_layout()
    out = OUT_DIR / "themes_distribution.png"
    plt.savefig(out, dpi=300, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"saved: {out}")


if __name__ == "__main__":
    make_publications_by_year()
    make_studies_by_database()
    make_themes_distribution()
