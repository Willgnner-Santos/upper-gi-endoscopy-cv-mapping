"""
Gera estatísticas descritivas dos artigos incluídos para alimentar o
relatório V3: distribuição temporal, top venues, temas, técnicas, etc.

Saída: consolidado/_analytics_v3.json
"""
from __future__ import annotations

import csv
import json
import re
import unicodedata
from collections import Counter
from pathlib import Path

CONSOL = Path("E:/Doutorado-V2/Revisão-Literatura-refinada-V3/consolidado")

def _norm(text: str) -> str:
    if not text:
        return ""
    t = text.lower()
    t = unicodedata.normalize("NFKD", t)
    t = "".join(c for c in t if not unicodedata.combining(c))
    t = re.sub(r"\s+", " ", t)
    return t.strip()

def main() -> None:
    rows = list(csv.DictReader((CONSOL / "artigos_incluidos.csv").open(encoding="utf-8")))
    excl = list(csv.DictReader((CONSOL / "artigos_excluidos.csv").open(encoding="utf-8")))
    dups = list(csv.DictReader((CONSOL / "duplicatas_identificadas.csv").open(encoding="utf-8")))
    mr = list(csv.DictReader((CONSOL / "artigos_duvida_revisao_manual.csv").open(encoding="utf-8")))

    # --- Distribuição temporal ---
    years: Counter = Counter()
    for r in rows:
        y = (r.get("year") or "").strip()
        m = re.search(r"(19|20)\d{2}", y)
        if m:
            years[int(m.group(0))] += 1

    # --- Top venues (com normalização de variantes abreviadas) ---
    VENUE_CANON = {
        "gastrointest endosc": "Gastrointestinal Endoscopy",
        "gastrointestinal endoscopy": "Gastrointestinal Endoscopy",
        "surg endosc": "Surgical Endoscopy",
        "surgical endoscopy": "Surgical Endoscopy",
        "world j gastroenterol": "World Journal of Gastroenterology",
        "world journal of gastroenterology": "World Journal of Gastroenterology",
        "dig endosc": "Digestive Endoscopy",
        "digestive endoscopy": "Digestive Endoscopy",
        "dig liver dis": "Digestive and Liver Disease",
        "digestive and liver disease": "Digestive and Liver Disease",
        "endoscopy": "Endoscopy",
        "sci rep": "Scientific Reports",
        "scientific reports": "Scientific Reports",
        "gastric cancer": "Gastric Cancer",
        "comput biol med": "Computers in Biology and Medicine",
        "computers in biology and medicine": "Computers in Biology and Medicine",
        "biomed signal process control": "Biomedical Signal Processing and Control",
        "biomedical signal processing and control": "Biomedical Signal Processing and Control",
        "ieee access": "IEEE Access",
        "ieee j biomed health inform": "IEEE Journal of Biomedical and Health Informatics",
        "ieee transactions on medical imaging": "IEEE Transactions on Medical Imaging",
        "comput methods programs biomed": "Computer Methods and Programs in Biomedicine",
        "med image anal": "Medical Image Analysis",
        "medical image analysis": "Medical Image Analysis",
        "j gastroenterol hepatol": "Journal of Gastroenterology and Hepatology",
        "journal of gastroenterology and hepatology": "Journal of Gastroenterology and Hepatology",
        "diagnostics (basel)": "Diagnostics",
        "diagnostics": "Diagnostics",
        "expert syst appl": "Expert Systems with Applications",
        "expert systems with applications": "Expert Systems with Applications",
    }
    venues: Counter = Counter()
    for r in rows:
        v = (r.get("venue") or "").strip()
        if v:
            v = re.sub(r"\s+", " ", v).strip()
            v_key = _norm(v).rstrip(".")
            v_canon = VENUE_CANON.get(v_key, v)
            venues[v_canon] += 1

    # --- Bases ---
    bases: Counter = Counter()
    for r in rows:
        bases[r["base"]] += 1

    # --- Distribuição por base de origem entre incluídos ---
    base_string: Counter = Counter()
    for r in rows:
        base_string[(r["base"], r["string_id"])] += 1

    # --- Temas / técnicas ---
    THEMES = {
        "câncer gástrico":               ["gastric cancer", "gastric carcinoma", "gastric adenocarc", "stomach cancer"],
        "esôfago / Barrett / SCC":       ["esophag", "oesophag", "barrett", "squamous cell carcinoma", "scc"],
        "pólipo":                        ["polyp"],
        "úlcera":                        ["ulcer"],
        "erosão":                        ["erosion"],
        "metaplasia intestinal":         ["intestinal metaplasia", "metaplasia"],
        "atrofia gástrica":              ["atrophic gastritis", "gastric atrophy"],
        "h. pylori":                     ["helicobacter", "h. pylori", "h pylori"],
        "hemorragia":                    ["bleeding", "hemorrhage", "haemorrhage"],
        "NEOPLASIA / displasia / EGC":   ["neoplasi", "dysplasi", "early gastric cancer"],
        "doença celíaca":                ["celiac", "coeliac"],
        "anatomical landmarks":          ["landmark", "anatomical site", "stomach site"],
        "cápsula endoscópica":           ["capsule endosc", "wireless capsule"],
        "tempo real":                    ["real-time", "real time"],
        "segmentação":                   ["segmentation", "u-net", "unet"],
        "detecção":                      ["detection"],
        "classificação":                 ["classification"],
        "qualidade de imagem":           ["quality assessment", "image quality", "informative frame", "blurry"],
        "dataset/benchmark":             ["dataset", "benchmark", "data descriptor"],
        "Vision Transformer":            ["vision transformer", "vit ", "vit-", "swin"],
        "EfficientNet":                  ["efficientnet"],
        "ResNet":                        ["resnet"],
        "DenseNet":                      ["densenet"],
        "MobileNet":                     ["mobilenet"],
        "YOLO":                          ["yolo"],
        "transfer learning":             ["transfer learning"],
        "self-supervised":               ["self-supervised", "self supervised", "contrastive"],
        "few-shot":                      ["few-shot", "few shot"],
        "multilabel":                    ["multilabel", "multi-label", "multi label"],
        "desbalanceamento":              ["imbalanc", "long-tailed", "long tailed"],
        "explicabilidade":               ["grad-cam", "gradcam", "explainab", " xai"],
        "atenção":                       ["attention"],
        "GAN/aug. sintético":            ["gan ", "generative adversar", "synthetic"],
        "data augmentation":             ["augmentation"],
        "federated":                     ["federated"],
        "domain adaptation":             ["domain adaptation", "domain shift", "cross-domain"],
        "calibração / incerteza":        ["calibration", "uncertainty", "conformal"],
        "foundation model / VLM":        ["foundation model", "biomedclip", "llava", "clip ",
                                          "vision-language model", "vision language model",
                                          "large multimodal model", "lvlm", "mllm",
                                          "gpt-4v", "gpt-4 vision", "gpt-4o", "gemini",
                                          "med-flamingo", "med-gemini", "med-palm",
                                          "endo-fm", "endofm", "medsam", "segment anything",
                                          "medclip", "zero-shot", "vlm"],
        "artefato (saliva/luz/blur)":    ["artefact", "artifact", "saliva", "specular", "glare"],
        "Brasil/LatAm":                  ["brazil", "brazilian", "latin america", "south america"],
    }

    theme_counts: Counter = Counter()
    for r in rows:
        text = _norm(r.get("title", "")) + " " + _norm(r.get("venue", ""))
        for theme, terms in THEMES.items():
            if any(t in text for t in terms):
                theme_counts[theme] += 1

    # --- Brasileiros (heurística): autor afiliado ou texto menciona Brasil ---
    br_articles = []
    for r in rows:
        a = _norm(r.get("authors", ""))
        t = _norm(r.get("title", "")) + " " + _norm(r.get("venue", ""))
        if any(k in (a + " " + t) for k in ["brazil", "brasileir", "ufmg", "ufrj", "unifesp",
                                              "ufma", "usp ", "unicamp", "ufes", "ufpe",
                                              "ufrn", "ufrgs", "ufmt", "ufpa", "ufg",
                                              "uff ", "puc-", "puc rio", "embrapa",
                                              "fiocruz", "uerj", "porto alegre", "sao paulo",
                                              "rio de janeiro", "belo horizonte", "salvador"]):
            br_articles.append(r)

    out = {
        "totais": {
            "incluidos": len(rows),
            "excluidos": len(excl),
            "duplicatas": len(dups),
            "manual_review": len(mr),
        },
        "incluidos_por_ano": dict(sorted(years.items())),
        "top_venues_30": venues.most_common(30),
        "incluidos_por_base": dict(bases),
        "incluidos_por_base_string": {f"{b}/{s}": n for (b, s), n in sorted(base_string.items())},
        "temas": dict(sorted(theme_counts.items(), key=lambda kv: -kv[1])),
        "brasileiros_count": len(br_articles),
        "brasileiros_amostras": [
            {"title": r.get("title", ""), "year": r.get("year", ""), "venue": r.get("venue", ""),
             "authors": r.get("authors", "")[:200], "doi": r.get("doi", ""),
             "base": r["base"], "string_id": r["string_id"]}
            for r in br_articles
        ],
    }
    (CONSOL / "_analytics_v3.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    # Print resumo
    print("Incluídos:", out["totais"]["incluidos"])
    print("\nIncluídos por ano (>= 2018):")
    for y, n in sorted(years.items()):
        if y >= 2015:
            print(f"  {y}: {n}")
    print("\nTop 15 venues:")
    for v, n in venues.most_common(15):
        print(f"  {n:4d}  {v[:80]}")
    print("\nTemas (top 25):")
    for theme, n in sorted(theme_counts.items(), key=lambda kv: -kv[1])[:25]:
        print(f"  {n:4d}  {theme}")
    print(f"\nArtigos com sinal brasileiro: {len(br_articles)}")
    for r in br_articles[:25]:
        print(f"  [{r['year']}] {r.get('title','')[:90]}")

if __name__ == "__main__":
    main()
