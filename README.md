# Systematic Mapping: Computer Vision for Upper-GI Endoscopy

Open audit repository for the systematic literature mapping described in the paper.  
All screening artefacts, search strings, decision logs, and analysis scripts are published here to enable independent replication and third-party audit.

---

## What is in this repository

```
.
├── screening/                  # All screening evidence
│   ├── consolidado/            # Consolidated results across all sources
│   │   ├── artigos_incluidos.csv          # 1 621 included records
│   │   ├── artigos_excluidos.csv          # 113 excluded records (with reasons)
│   │   ├── duplicatas_identificadas.csv   # 817 identified duplicates
│   │   ├── artigos_duvida_revisao_manual.csv  # Records sent to manual review (0 pending)
│   │   ├── todos_artigos_refinados_sem_duplicatas.bib  # Full deduplicated BibTeX corpus
│   │   ├── resumo_por_base_string.csv     # Counts by source × search string
│   │   ├── dataset_stats.json             # Dataset characterisation statistics
│   │   ├── dataset_cooccurrence.csv       # Label co-occurrence matrix
│   │   ├── _analytics_v3.json             # Full analytics (venues, years, themes)
│   │   ├── _summary.json                  # Pipeline run summary
│   │   ├── _abstract_cache.json           # Enriched abstracts (NCBI + Crossref)
│   │   ├── generate_methodology_figures.py
│   │   └── generate_results_figures.py
│   ├── IEEE/          S1–S6   screening_log.csv + artigos_refinados.bib per string
│   ├── Pub-Med/       S2,S3,S5
│   ├── ScienceDirect/ S1–S6,S8–S10
│   ├── Scopus/        S1–S5
│   ├── Scopus-VLM-FMs/ S1–S3  (Foundation Models / VLMs supplementary search)
│   ├── Springer-Nature-Link/ S1–S5
│   └── Web-of-Science/ S1–S6
└── scripts/
    ├── refine_literature_v3.py   # Main screening pipeline (V3)
    ├── refine_literature.py      # V1 pipeline (archived for reference)
    ├── analyze_literature_v3.py  # Descriptive statistics
    ├── analyze_dataset.py        # Dataset characterisation
    ├── apply_manual_triage.py    # Applies V1 manual decisions
    ├── manual_triage.csv         # 35 V1 manual decisions (bibtex key)
    └── manual_triage_v3.csv      # 30 V3 manual decisions (DOI key)
```

---

## Search scope

**Topic.** Computer vision and deep learning applied to upper gastrointestinal (upper-GI) endoscopy images — gastroscopy / esophagogastroduodenoscopy (EGD) — with emphasis on multilabel classification, class imbalance, image artefacts (saliva, specular light), and explainability.

**Sources searched (7):** IEEE Xplore · Scopus · Web of Science · PubMed · ScienceDirect · Springer Nature Link · Scopus (VLM/FMs supplementary)

**Date of last execution:** 2026-05-20

---

## Search strings

All Boolean search strings are embedded in the pipeline script [`scripts/refine_literature_v3.py`](scripts/refine_literature_v3.py) (see the `BASES` dictionary, lines ~58–250). The strings below summarise each search strategy; the exact Boolean operators are in the script.

### Core strings (applied across most sources)

| ID | Focus | Example terms |
|----|-------|---------------|
| S1 | Main — AI/DL in upper-GI endoscopy | `("upper gastrointestinal" OR "gastroscopy" OR "esophagogastroduodenoscopy") AND ("deep learning" OR "convolutional neural network" OR "computer vision")` |
| S2 | DL/CNN specific | `("ResNet" OR "DenseNet" OR "EfficientNet" OR "MobileNet") AND ("endoscopy" OR "gastroscopy")` |
| S3 | Gastric lesions | `("gastric lesion" OR "gastric polyp" OR "ulcer" OR "erosion") AND ("deep learning" OR "image classification")` |
| S4 | Gastric polyps | `("gastric polyp") AND ("deep learning" OR "classification")` |
| S5 | Brazil / Latin America | `("Brazil" OR "Latin America") AND ("endoscopy") AND ("deep learning" OR "artificial intelligence")` |
| S6 | Datasets BR/LatAm | `("gastric" OR "endoscopy") AND ("dataset" OR "benchmark") AND ("Brazil" OR "Latin America")` |

### ScienceDirect-specific strings (SD1–SD10)

Adapted for ScienceDirect's full-text Boolean syntax; details in `BASES["ScienceDirect"]` in the script.

### Supplementary: Foundation Models / VLMs in endoscopy (Scopus, 2022–2026)

| ID | Focus |
|----|-------|
| S1 (VLM) | Foundation models / VLMs — conceptual (151 records) |
| S2 (VLM) | Named models: Endo-FM, LLaVA-Med, BioMedCLIP, MedSAM, etc. (68 records) |
| S3 (VLM) | Commercial multimodal: GPT-4V, GPT-4o, Gemini, Claude + endoscopy (160 records) |

All three strings use `PUBYEAR > 2021`.

---

## PRISMA flow summary

| Stage | Records |
|-------|--------:|
| Identified (all sources, pre-dedup) | 2 551 |
| After deduplication (DOI + normalised title) | 1 734 |
| Included | **1 621** |
| Excluded | 113 |
| Duplicates removed | 817 |
| Pending manual review | **0** |
| Records with abstract | 2 057 / 2 551 (81 %) |

### Included records by source

| Source | Included |
|--------|--------:|
| Scopus | 426 |
| Scopus (VLM/FMs) | 279 |
| Springer Nature Link | 269 |
| PubMed | 229 |
| ScienceDirect | 197 |
| Web of Science | 161 |
| IEEE Xplore | 60 |
| **Total** | **1 621** |

---

## Screening pipeline

The automated heuristic (`refine_literature_v3.py`) classifies each record as **included**, **excluded**, or **manual review** based on:

- **Included:** (a) upper-GI endoscopy + computer vision/DL component; **or** (b) upper-GI finding + CV; **or** (c) endoscopy + methodological contribution relevant to the study (multilabel, imbalance, artefacts, explainability); **or** (d) record retrieved by a strong Boolean string with no negative signals in the title.
- **Excluded:** clearly out of scope — pure colonoscopy, other imaging modalities (MRI, fundus, chest X-ray), NLP without image component, unrelated domains.
- **Manual review:** ambiguous titles, editorial aggregates (subject indexes, full-issue PDFs), proceedings without individual abstracts.

Manual decisions override the heuristic (precedence: `manual_v3 → manual_v1 → heuristic`). Each decision is recorded with an individual justification in [`scripts/manual_triage_v3.csv`](scripts/manual_triage_v3.csv) and [`scripts/manual_triage.csv`](scripts/manual_triage.csv).

### Abstract enrichment

Abstracts missing from raw exports were retrieved via:
- **NCBI E-utilities** (`efetch`) for PubMed records (325/325 PMIDs processed, ~3 req/s).
- **Crossref API** (`api.crossref.org/works/{DOI}`, mailto-polite) for DOIs from other sources (~60 % success; Springer book chapters rarely have abstracts in Crossref).

Results are cached in `screening/consolidado/_abstract_cache.json`; re-running the pipeline does not issue new HTTP requests.

### Sensitivity check

Reclassifying the 2 057 records that have abstracts using **title + keywords only** (dropping abstract text) reproduces 97 % of full-pipeline decisions, demonstrating low sensitivity to criterion variation across the abstract-enrichment step.

---

## Reproducibility

### Requirements

```
pip install bibtexparser requests
```

Python ≥ 3.10. No other non-standard dependency.

### Running the pipeline

```bash
# 1. Edit the ROOT paths at the top of the script to point to your local copy
#    (ROOT_ORIG, ROOT_OUT, MANUAL_TRIAGE_OLD, MANUAL_TRIAGE_V3)
python scripts/refine_literature_v3.py

# 2. Generate descriptive statistics
python scripts/analyze_literature_v3.py

# 3. Generate figures
python screening/consolidado/generate_methodology_figures.py
python screening/consolidado/generate_results_figures.py
```

> **Note on paths.** The scripts use absolute Windows paths (`E:/Doutorado-V2/...`) that must be updated to match your local directory layout before running. All logic is path-independent; only the constants at the top of each file need changing.

---

## File descriptions

| File | Description |
|------|-------------|
| `screening/consolidado/artigos_incluidos.csv` | All 1 621 included records with source, string ID, DOI, title, year, venue, decision, and justification |
| `screening/consolidado/artigos_excluidos.csv` | All 113 excluded records with individual exclusion reason |
| `screening/consolidado/duplicatas_identificadas.csv` | All 817 duplicate pairs with match key (DOI or normalised title) |
| `screening/<Source>/S*/screening_log.csv` | Per-string decision log: one row per record with decision and reason |
| `screening/<Source>/S*/artigos_refinados.bib` | BibTeX of records that passed screening for that source × string |
| `screening/consolidado/todos_artigos_refinados_sem_duplicatas.bib` | Full deduplicated included corpus (BibTeX, 1 621 records) |
| `scripts/manual_triage.csv` | 35 V1 manual decisions keyed by BibTeX key |
| `scripts/manual_triage_v3.csv` | 30 V3 manual decisions keyed by DOI |
| `screening/consolidado/_analytics_v3.json` | Machine-readable analytics: included counts by year, venue, source, theme |
| `screening/consolidado/resumo_por_base_string.csv` | Raw / included / excluded / duplicate counts per source × string |

---

## Limitations and mitigations

**Single-screener.** Screening was performed by one researcher. Three mechanisms mitigate this limitation:

1. The automated heuristic reduces subjective decisions to a minimum — the same record always receives the same outcome.
2. Reclassifying records with abstracts using title + keywords only reproduces 97 % of full-pipeline decisions, demonstrating low sensitivity to criterion variation.
3. This repository publishes the source code, complete search strings with exact Boolean operators, PRISMA artefacts, and all decision CSVs, enabling third-party audit and replication.

**Abstract coverage.** 19 % of records lack abstracts (mainly Springer book chapters). The pipeline includes them if the Boolean string already restricts the domain and the title shows no negative signals — consistent with PRISMA guidance that the search string is the primary inclusion filter.

---

## Licence

Data files (CSV, BIB, JSON) are released under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).  
Code files (Python scripts) are released under the [MIT Licence](https://opensource.org/licenses/MIT).
