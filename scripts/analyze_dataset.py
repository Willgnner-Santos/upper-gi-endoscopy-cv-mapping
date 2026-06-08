"""
Análise descritiva do dataset brasileiro de endoscopia digestiva alta.

Entradas:
  E:/Doutorado/Data/Imgs/                         (arquivos .jpg)
  E:/Doutorado/Data/Planilha sem título - IMAGENS ROTULADAS.csv

Saídas:
  E:/Doutorado/Revisão-Literatura-refinada/consolidado/dataset_stats.json
  E:/Doutorado/Revisão-Literatura-refinada/consolidado/dataset_cooccurrence.csv

Não modifica nada em Data/.
"""
from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path

DATA_DIR = Path("E:/Doutorado/Data")
IMGS_DIR = DATA_DIR / "Imgs"
CSV_PATH = DATA_DIR / "Planilha sem título - IMAGENS ROTULADAS.csv"
OUT_DIR = Path("E:/Doutorado/Revisão-Literatura-refinada/consolidado")
OUT_DIR.mkdir(parents=True, exist_ok=True)

LABEL_COLS = [
    "NORMAL", "ALTERADO", "SALIVA", "LUZ", "ENANTEMA",
    "PÓLIPO", "ÚLCERA", "EROSÃO", "MICRONODULARIDADE",
    "ECTASIA VASCULAR", "NEOPLASIA",
]

def load_rows() -> list[dict]:
    rows = []
    with CSV_PATH.open(encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for r in reader:
            rows.append(r)
    return rows

def to_bin(v: str) -> int | None:
    """Planilha usa 1=Presente, 2=Ausente. Qualquer outro valor = NaN."""
    v = (v or "").strip()
    if v == "1":
        return 1
    if v == "2":
        return 0
    return None

def main() -> None:
    files = sorted([p.name for p in IMGS_DIR.glob("*.jpg")])
    file_set = set(files)
    print(f"Imagens em Data/Imgs: {len(files)}")

    rows = load_rows()
    print(f"Linhas na planilha: {len(rows)}")

    # image_name está em 'Coluna 1'
    labels_by_img: dict[str, list[dict]] = {}
    for r in rows:
        img = (r.get("Coluna 1") or "").strip()
        if not img:
            continue
        labels_by_img.setdefault(img, []).append(r)

    # Filtra apenas imagens que existem no disco
    images_with_labels = sorted(file_set & set(labels_by_img.keys()))
    images_no_label = sorted(file_set - set(labels_by_img.keys()))
    labels_no_image = sorted(set(labels_by_img.keys()) - file_set)

    # Duplicatas na planilha
    duplicated = {k: v for k, v in labels_by_img.items() if len(v) > 1}

    # Monta matriz binária (primeira ocorrência)
    binary_rows = []
    for img in images_with_labels:
        rec = labels_by_img[img][0]
        row = {"image_name": img}
        for col in LABEL_COLS:
            row[col] = to_bin(rec.get(col, ""))
        binary_rows.append(row)

    total = len(binary_rows)
    per_label_presence = {}
    per_label_missing = {}
    for col in LABEL_COLS:
        present = sum(1 for r in binary_rows if r[col] == 1)
        absent = sum(1 for r in binary_rows if r[col] == 0)
        missing = sum(1 for r in binary_rows if r[col] is None)
        ir = (absent / max(present, 1)) if present > 0 else None
        per_label_presence[col] = {
            "present": present,
            "absent": absent,
            "missing": missing,
            "prevalence_pct": round(100 * present / total, 2) if total else 0,
            "imbalance_ratio": round(ir, 2) if ir is not None else None,
        }

    # Número de rótulos positivos simultâneos por imagem (distribuição multilabel)
    n_labels_per_img = Counter()
    n_pathologies_per_img = Counter()  # excluindo NORMAL/ALTERADO/SALIVA/LUZ
    pathology_cols = [c for c in LABEL_COLS if c not in ("NORMAL", "ALTERADO", "SALIVA", "LUZ")]
    for r in binary_rows:
        n_all = sum(1 for c in LABEL_COLS if r[c] == 1)
        n_path = sum(1 for c in pathology_cols if r[c] == 1)
        n_labels_per_img[n_all] += 1
        n_pathologies_per_img[n_path] += 1

    # Co-ocorrência 2x2 entre patologias
    cooc = {}
    for i, a in enumerate(pathology_cols):
        for b in pathology_cols[i + 1:]:
            n = sum(1 for r in binary_rows if r[a] == 1 and r[b] == 1)
            cooc[f"{a} + {b}"] = n

    # Artefato × patologia
    artifacts = ["SALIVA", "LUZ"]
    art_path = {}
    for art in artifacts:
        for path in pathology_cols:
            n = sum(1 for r in binary_rows if r[art] == 1 and r[path] == 1)
            art_path[f"{art} + {path}"] = n

    # Imagens com apenas NORMAL e nada mais
    pure_normal = sum(
        1 for r in binary_rows
        if r["NORMAL"] == 1 and all(r[c] in (0, None) for c in LABEL_COLS if c != "NORMAL")
    )
    pure_altered_no_path = sum(
        1 for r in binary_rows
        if r["ALTERADO"] == 1 and all(r[c] in (0, None) for c in pathology_cols)
    )

    summary = {
        "total_files_in_Imgs": len(files),
        "total_rows_in_csv": len(rows),
        "images_with_labels": len(images_with_labels),
        "images_without_labels": len(images_no_label),
        "labels_without_image": len(labels_no_image),
        "duplicated_in_csv_count": len(duplicated),
        "duplicated_examples": list(duplicated.keys())[:15],
        "per_label": per_label_presence,
        "labels_per_image_distribution": dict(sorted(n_labels_per_img.items())),
        "pathologies_per_image_distribution": dict(sorted(n_pathologies_per_img.items())),
        "pure_normal_images": pure_normal,
        "altered_without_pathology_label": pure_altered_no_path,
        "cooccurrence_pathology_pairs_top10": dict(sorted(cooc.items(), key=lambda x: -x[1])[:10]),
        "artifact_pathology_intersections": art_path,
        "images_no_label_examples": images_no_label[:10],
        "labels_no_image_examples": labels_no_image[:10],
    }

    (OUT_DIR / "dataset_stats.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    with (OUT_DIR / "dataset_cooccurrence.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["label_a", "label_b", "co_occurrence"])
        for k, v in sorted(cooc.items(), key=lambda x: -x[1]):
            a, b = k.split(" + ")
            w.writerow([a, b, v])

    print(json.dumps(summary, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
