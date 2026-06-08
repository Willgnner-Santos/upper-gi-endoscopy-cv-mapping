"""
Aplica decisões manuais (scripts/manual_triage.csv) sobre os registros
`manual_review` já classificados pelo pipeline principal.

Atualiza:
  - consolidado/artigos_incluidos.csv
  - consolidado/artigos_excluidos.csv
  - consolidado/artigos_duvida_revisao_manual.csv  (remove os triados)
  - consolidado/todos_artigos_refinados_sem_duplicatas.bib  (adiciona incluídos que ficaram de fora)
  - por-S: artigos_refinados.bib + screening_log.csv nas pastas afetadas

O script é idempotente. Roda depois de `refine_literature.py`.
"""
from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path

import bibtexparser
from bibtexparser.bparser import BibTexParser
from bibtexparser.bwriter import BibTexWriter
from bibtexparser.customization import convert_to_unicode

OUT_ROOT = Path("E:/Doutorado/Revisão-Literatura-refinada")
CONSOL = OUT_ROOT / "consolidado"
TRIAGE_CSV = Path("E:/Doutorado/scripts/manual_triage.csv")
ORIG_ROOT = Path("E:/Doutorado/Revisão-Literatura")

# Import BASES da refinaria
import sys
sys.path.insert(0, str(Path(__file__).parent))
from refine_literature import BASES, parse_bib_file, _title, _authors, _year, _doi, _venue


def load_triage() -> dict[str, tuple[str, str]]:
    """Retorna {bibtex_key_original: (final_status, final_motivo)}."""
    out = {}
    with TRIAGE_CSV.open(encoding="utf-8") as f:
        for r in csv.DictReader(f):
            out[r["bibtex_key_original"]] = (r["final_status"], r["final_motivo"])
    return out


def load_csv(p: Path) -> list[dict]:
    with p.open(encoding="utf-8") as f:
        return list(csv.DictReader(f))


def dump_csv(p: Path, rows: list[dict], cols: list[str]) -> None:
    with p.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(rows)


def _find_raw_entry(base_dir: str, s_id: str, key: str) -> dict | None:
    """Re-parseia os .bib originais para recuperar a entrada completa."""
    s_path = ORIG_ROOT / base_dir / s_id
    if not s_path.exists():
        return None
    for bf in s_path.glob("*.bib"):
        for e in parse_bib_file(bf):
            if e.get("ID") == key:
                return e
    return None


def main() -> None:
    triage = load_triage()
    print(f"[OK] Triagem manual carregada: {len(triage)} decisões")

    CONSOL.mkdir(parents=True, exist_ok=True)

    CSV_COLS = [
        "base", "string_id", "titulo_interpretativo_string",
        "bibtex_key_original", "title", "authors", "year",
        "doi", "venue", "status", "motivo", "origens",
    ]

    incl_p = CONSOL / "artigos_incluidos.csv"
    excl_p = CONSOL / "artigos_excluidos.csv"
    mr_p = CONSOL / "artigos_duvida_revisao_manual.csv"

    incl = load_csv(incl_p)
    excl = load_csv(excl_p)
    mr = load_csv(mr_p)

    # Aplica triagem: remove do MR, adiciona a incl ou excl, atualizando motivo
    promoted_included: list[dict] = []
    promoted_excluded: list[dict] = []
    new_mr: list[dict] = []
    still_pending = []

    for r in mr:
        key = r["bibtex_key_original"]
        if key in triage:
            status, motivo = triage[key]
            r2 = dict(r)
            r2["status"] = status
            r2["motivo"] = "[triagem manual] " + motivo
            if status == "included":
                promoted_included.append(r2)
            elif status == "excluded":
                promoted_excluded.append(r2)
            else:
                new_mr.append(r2)
        else:
            still_pending.append(r)
            new_mr.append(r)

    incl_final = [dict(x, status="included") for x in incl] + promoted_included
    excl_final = [dict(x, status="excluded") for x in excl] + promoted_excluded

    dump_csv(incl_p, incl_final, CSV_COLS)
    dump_csv(excl_p, excl_final, CSV_COLS)
    dump_csv(mr_p, new_mr, CSV_COLS)

    # Atualiza o resumo por base/string
    agg = defaultdict(lambda: defaultdict(int))
    for r in incl_final:
        agg[(r["base"], r["string_id"])]["included"] += 1
    for r in excl_final:
        agg[(r["base"], r["string_id"])]["excluded"] += 1
    for r in new_mr:
        agg[(r["base"], r["string_id"])]["manual_review"] += 1
    dup_rows = load_csv(CONSOL / "duplicatas_identificadas.csv")
    for r in dup_rows:
        agg[(r["base"], r["string_id"])]["duplicate"] += 1

    base_pretty = {
        "IEEE": "IEE", "Scopus": "Scopus", "Web of Science": "Web-of-Science",
    }
    # Resumo atualizado
    resumo = CONSOL / "resumo_por_base_string.csv"
    with resumo.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow([
            "base", "string_id", "titulo_interpretativo_string",
            "registros_documento", "registros_bibtex",
            "incluidos", "excluidos", "duplicatas", "revisao_manual",
        ])
        for base_dir, meta in BASES.items():
            for s_id, s_meta in meta["strings"].items():
                a = agg[(meta["pretty"], s_id)]
                total_bib = (
                    a["included"] + a["excluded"] + a["duplicate"] + a["manual_review"]
                )
                w.writerow([
                    meta["pretty"], s_id, s_meta["titulo"],
                    s_meta["registros_documento"], total_bib,
                    a["included"], a["excluded"], a["duplicate"], a["manual_review"],
                ])

    # Atualiza bib consolidado adicionando promovidos para included que não estavam
    bib_path = CONSOL / "todos_artigos_refinados_sem_duplicatas.bib"
    raw_bib = bib_path.read_text(encoding="utf-8")
    existing_keys = set()
    for m in __import__("re").finditer(r"@\w+\s*\{\s*([^,]+),", raw_bib):
        existing_keys.add(m.group(1).strip())
    additions = []
    for r in promoted_included:
        key = r["bibtex_key_original"]
        if key in existing_keys:
            continue
        base_dir = base_pretty[r["base"]]
        e = _find_raw_entry(base_dir, r["string_id"], key)
        if e:
            additions.append(e)
    if additions:
        db = bibtexparser.bibdatabase.BibDatabase()
        db.entries = additions
        writer = BibTexWriter()
        writer.indent = "  "
        bib_path.write_text(raw_bib + "\n" + writer.write(db), encoding="utf-8")

    # Atualiza per-S bib + log
    # Para cada entrada promovida para 'included', adicionar ao bib da S correspondente
    # e reescrever o screening_log
    for r in promoted_included + promoted_excluded + new_mr:
        pass  # handled below per-folder

    # Regenera screening_log por S e artigos_refinados.bib por S, agora usando todas as
    # informações atualizadas.
    # Constroi índice {(base,S): list[rec]}
    by_bs: dict[tuple[str, str], list[dict]] = defaultdict(list)
    # Incluídos + excluídos + MR + duplicados
    for r in incl_final:
        by_bs[(r["base"], r["string_id"])].append(r)
    for r in excl_final:
        by_bs[(r["base"], r["string_id"])].append(r)
    for r in new_mr:
        by_bs[(r["base"], r["string_id"])].append(r)
    for r in dup_rows:
        by_bs[(r["base"], r["string_id"])].append(r)

    for base_dir, meta in BASES.items():
        for s_id in meta["strings"]:
            recs = by_bs[(meta["pretty"], s_id)]
            out_dir = OUT_ROOT / base_dir / s_id
            out_dir.mkdir(parents=True, exist_ok=True)

            # screening_log
            log_cols = [
                "base", "string_id", "titulo_interpretativo_string",
                "bibtex_key_original", "title", "authors", "year",
                "doi", "venue", "status", "motivo", "origens", "observacoes",
            ]
            with (out_dir / "screening_log.csv").open("w", newline="", encoding="utf-8") as f:
                w = csv.DictWriter(f, fieldnames=log_cols)
                w.writeheader()
                for rec in recs:
                    row = {c: rec.get(c, "") for c in log_cols}
                    row.setdefault("observacoes", "")
                    w.writerow(row)

            # bib refinado (apenas included nessa S)
            inc_here = [r for r in recs if r["status"] == "included"]
            entries = []
            for rec in inc_here:
                e = _find_raw_entry(base_dir, s_id, rec["bibtex_key_original"])
                if e:
                    entries.append(e)
            db = bibtexparser.bibdatabase.BibDatabase()
            db.entries = entries
            writer = BibTexWriter()
            writer.indent = "  "
            writer.order_entries_by = ("ID",)
            (out_dir / "artigos_refinados.bib").write_text(
                writer.write(db), encoding="utf-8"
            )

    # Atualiza summary json
    totais = {
        "bruto_total": len(incl_final) + len(excl_final) + len(new_mr) + len(dup_rows),
        "incluidos": len(incl_final),
        "excluidos": len(excl_final),
        "duplicatas": len(dup_rows),
        "revisao_manual": len(new_mr),
    }
    totais["apos_dedup"] = totais["bruto_total"] - totais["duplicatas"]
    summary = json.loads((CONSOL / "_summary.json").read_text(encoding="utf-8"))
    summary["totais"] = totais
    summary["triagem_manual_aplicada"] = {
        "decisoes_aplicadas": len(triage),
        "promovidos_incluidos": len(promoted_included),
        "promovidos_excluidos": len(promoted_excluded),
        "ainda_em_manual_review": len(new_mr),
    }
    # Recalcula por base/string
    for item in summary["por_base_string"]:
        a = agg[(item["base"], item["string_id"])]
        item["incluidos"] = a["included"]
        item["excluidos"] = a["excluded"]
        item["duplicatas"] = a["duplicate"]
        item["revisao_manual"] = a["manual_review"]
    (CONSOL / "_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    print("[OK] Triagem manual aplicada.")
    print(json.dumps(totais, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
