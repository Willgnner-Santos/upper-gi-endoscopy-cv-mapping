"""
Pipeline de refinamento de revisão de literatura para tese de Anonymous
em visão computacional aplicada a imagens endoscópicas digestivas altas.

Entrada:  E:/Anonymous/Revisão-Literatura/{IEE,Scopus,Web-of-Science}/S*/<*.bib>
Saída:    E:/Anonymous/Revisão-Literatura-refinada/
"""

from __future__ import annotations

import csv
import json
import re
import unicodedata
from collections import defaultdict
from pathlib import Path

import bibtexparser
from bibtexparser.bparser import BibTexParser
from bibtexparser.bwriter import BibTexWriter
from bibtexparser.customization import convert_to_unicode

# ======================================================================
# Configuração
# ======================================================================
ROOT_ORIG = Path("E:/Anonymous/Revisão-Literatura")
ROOT_OUT = Path("E:/Anonymous/Revisão-Literatura-refinada")
ROOT_OUT.mkdir(parents=True, exist_ok=True)

BASES = {
    "IEE": {
        "pretty": "IEEE",
        "strings": {
            "S1": {
                "titulo": "IEEE S1 — String principal: IA/DL em imagens de endoscopia digestiva alta",
                "objetivo": "Buscar trabalhos de IA, deep learning, CNN e visão computacional aplicados a imagens/vídeos de endoscopia digestiva alta ou gastroscopia.",
                "registros_documento": 61,
            },
            "S2": {
                "titulo": "IEEE S2 — String focada em deep learning/CNN para endoscopia alta",
                "objetivo": "Reduzir trabalhos genéricos de IA e focar em redes neurais profundas (ResNet/DenseNet/EfficientNet/MobileNet) diretamente relacionadas ao pipeline do projeto.",
                "registros_documento": 25,
            },
            "S3": {
                "titulo": "IEEE S3 — Lesões e alterações gástricas analisadas por IA",
                "objetivo": "Recuperar estudos sobre alterações gástricas, lesões, pólipos, úlceras, erosões e neoplasias analisados por IA em endoscopia.",
                "registros_documento": 25,
            },
            "S4": {
                "titulo": "IEEE S4 — Pólipos gástricos em endoscopia com IA",
                "objetivo": "Verificar trabalhos específicos sobre pólipos gástricos, especialmente pólipos de glândulas fúndicas, em endoscopia com IA.",
                "registros_documento": 8,
            },
            "S5": {
                "titulo": "IEEE S5 — IA aplicada à endoscopia com dados brasileiros / latino-americanos",
                "objetivo": "Buscar trabalhos que combinem IA, endoscopia e dados brasileiros/latino-americanos.",
                "registros_documento": 18,
            },
            "S6": {
                "titulo": "IEEE S6 — Datasets brasileiros/latino-americanos de endoscopia",
                "objetivo": "Buscar especificamente datasets, bases anotadas ou bases clínicas brasileiras/latino-americanas de endoscopia.",
                "registros_documento": 9,
            },
        },
    },
    "Scopus": {
        "pretty": "Scopus",
        "strings": {
            "S1": {
                "titulo": "Scopus S1 — String principal: IA/DL em imagens de endoscopia digestiva alta",
                "objetivo": "Recuperar trabalhos de IA, machine learning e deep learning aplicados à classificação, detecção ou diagnóstico em imagens/vídeos de endoscopia digestiva alta ou gastroscopia.",
                "registros_documento": 109,
            },
            "S2": {
                "titulo": "Scopus S2 — Lesões e alterações gástricas por IA",
                "objetivo": "Recuperar estudos sobre IA aplicada à identificação de lesões, anormalidades e achados gástricos (pólipos, úlceras, erosões, neoplasias, ectasia vascular, micronodularidade).",
                "registros_documento": 294,
            },
            "S3": {
                "titulo": "Scopus S3 — Pólipos gástricos em endoscopia com IA",
                "objetivo": "Buscar especificamente IA aplicada a pólipos gástricos e pólipos de glândulas fúndicas em imagens endoscópicas.",
                "registros_documento": 60,
            },
            "S4": {
                "titulo": "Scopus S4 — IA em endoscopia com dados brasileiros / latino-americanos",
                "objetivo": "Verificar trabalhos com dados brasileiros, latino-americanos ou sul-americanos em IA aplicada à endoscopia.",
                "registros_documento": 8,
            },
            "S5": {
                "titulo": "Scopus S5 — Datasets brasileiros/latino-americanos de endoscopia",
                "objetivo": "Buscar especificamente bases de dados, datasets anotados ou datasets clínicos brasileiros/latino-americanos de endoscopia.",
                "registros_documento": 1,
            },
        },
    },
    "Web-of-Science": {
        "pretty": "Web of Science",
        "strings": {
            "S1": {
                "titulo": "WoS S1 — String principal: IA/DL em imagens de endoscopia digestiva alta",
                "objetivo": "Recuperar trabalhos sobre IA, machine learning e deep learning aplicados à classificação, detecção ou diagnóstico em imagens/vídeos de endoscopia digestiva alta ou gastroscopia.",
                "registros_documento": 200,
            },
            "S2": {
                "titulo": "WoS S2 — Lesões e alterações gástricas por IA",
                "objetivo": "Recuperar trabalhos focados em lesões, anormalidades e alterações gástricas analisadas por IA em endoscopia alta.",
                "registros_documento": 144,
            },
            "S3": {
                "titulo": "WoS S3 — Pólipos gástricos em endoscopia com IA",
                "objetivo": "Recuperar estudos diretamente relacionados a pólipos gástricos, especialmente pólipos de glândulas fúndicas, em imagens endoscópicas com IA.",
                "registros_documento": 20,
            },
            "S4": {
                "titulo": "WoS S4 — IA em endoscopia com dados brasileiros / latino-americanos",
                "objetivo": "Verificar a existência de estudos com dados brasileiros, latino-americanos ou sul-americanos em IA aplicada à endoscopia.",
                "registros_documento": 4,
            },
            "S5": {
                "titulo": "WoS S5 — Dataset brasileiro/latino-americano de endoscopia",
                "objetivo": "Buscar especificamente trabalhos que mencionem datasets, bases de dados ou imagens médicas brasileiras/latino-americanas em endoscopia.",
                "registros_documento": 1,
            },
            "S6": {
                "titulo": "WoS S6 — Datasets de endoscopia gástrica (qualquer origem)",
                "objetivo": "Mapear datasets de imagens endoscópicas gástricas, independentemente do país de origem.",
                "registros_documento": 17,
            },
        },
    },
}

# ======================================================================
# Heurísticas de inclusão/exclusão
# ======================================================================

# --- Sinais de endoscopia digestiva (alta ou genérica) ---
ENDO_UPPER_TERMS = [
    "gastroscop", "upper gastrointestinal", "upper gi endoscop",
    "esophagogastroduodenoscop", " egd", "gastric endoscop",
    "upper-gi", "gastric image", "stomach image",
]
ENDO_GENERIC_TERMS = [
    "endoscop", "capsule endoscop", "wireless capsule",
    "narrow band imaging", "nbi imaging", "chromoendoscop",
    "white-light endoscop", "endoluminal",
]

# --- Sinais de visão computacional / DL / ML ---
CV_TERMS = [
    "deep learning", "machine learning", "artificial intelligence",
    "convolutional neural", " cnn", "cnn-", "cnn ",
    "vision transformer", " vit ", " vit-", "swin transformer",
    "transfer learning", "resnet", "densenet", "efficientnet", "mobilenet",
    "inception", "alexnet", " vgg", "yolo", "u-net", "unet",
    "computer-aided diagnosis", "computer aided diagnosis", "cadx", " cad ",
    "computer vision", "image classification", "image segmentation",
    "object detection", "lesion detection", "lesion classification",
    "grad-cam", "gradcam", "saliency map", "attention mechanism",
    "self-attention", "attention module", "attention map",
    "fine-grained classification", "coarse-grained classification",
    "backbone network", "ensemble learning", "feature extraction",
    "state-of-the-art", "sota performance",
    "explainable ai", "explainability", " xai",
    "neural network", "self-supervised", "contrastive learning",
    "few-shot", "data augmentation", "generative adversarial", " gan ",
    "federated learning", "semi-supervised", "autoencoder",
    "radiomic", "histopatholog", "whole-slide", "whole slide image",
]

# --- Doenças/achados do trato GI alto (≈ presume-se endoscopia) ---
UPPER_GI_DISEASE_TERMS = [
    "gastric", "stomach", "esophag", "oesophag", "duoden",
    "helicobacter", "barrett", "gastritis", "ulcer", "erosion",
    "gastric polyp", "fundic gland polyp", "stomach polyp",
    "mucosal lesion", "gastric neoplas", "gastric cancer",
    "stomach cancer", "gastric carcinoma", "gastric adenocarc",
    "gastric intestinal metaplasia", "atrophic gastritis",
    "vascular ectasia", "micronodular",
    "signet ring cell", "subepithelial tumor", "hemorrhage",
    "gastrointestinal bleeding", "anatomical landmark",
]

# --- Temas metodologicamente úteis (mesmo sem endoscopia óbvia no texto) ---
USEFUL_METHOD_TERMS = [
    "multilabel", "multi-label", "multi label",
    "multiclass", "multi-class",
    "class imbalance", "imbalanced", "long-tailed",
    "image quality assessment", "artefact", "artifact",
    "explainab", "grad-cam", "gradcam", "saliency",
    "brazilian dataset", "latin american dataset",
]

# --- Exclusões claras ---
# Estes termos só disparam exclusão se NÃO houver sinal de endoscopia/GI alto.
OTHER_MEDICAL_IMG_TERMS = [
    "chest x-ray", "chest xray", "chest radiograph", "chest ct",
    "mammograph", "dermatolog", "retinal fundus", "fundus image",
    "fundus photograph", "diabetic retinopathy", "glaucoma",
    "brain mri", "brain tumor segmentation", "lung ct", "lung nodule",
    "pulmonary nodule", "covid-19 chest", "covid chest",
    "thyroid ultrasound", "breast cancer screening",
    "skin lesion classification", "melanoma classification",
    "cervical cancer screening", "pap smear",
]
NLP_ONLY_TERMS = [
    "natural language processing", "text mining", "sentiment analysis",
    "speech recognition", "machine translation", "chatbot",
    "knowledge graph",
]
OUT_OF_DOMAIN_TERMS = [
    "cryptocurren", "stock market", "cybersecurity", "malware",
    "autonomous driving", "self-driving vehicle", "remote sensing",
    "satellite imag", "agricultural crop", "plant disease classification",
    "animal husbandry", "dredge sediment", "marine sediment",
    "inflammatory bowel disease review",
]

BRAZIL_TERMS = ["brazil", "brazilian", "portuguese", "latin america", "south america"]
DATASET_TERMS = ["dataset", "database", "benchmark", "corpus", "annotated", "labeled", "curated"]

# ======================================================================
# Utilitários
# ======================================================================
def _norm(text: str | None) -> str:
    if not text:
        return ""
    text = text.lower()
    text = unicodedata.normalize("NFKD", text)
    text = "".join(c for c in text if not unicodedata.combining(c))
    text = re.sub(r"\s+", " ", text)
    return text.strip()

def _title_key(title: str | None) -> str:
    t = _norm(title)
    t = re.sub(r"[^a-z0-9 ]", "", t)
    t = re.sub(r"\s+", " ", t).strip()
    return t

def _doi_key(doi: str | None) -> str:
    if not doi:
        return ""
    d = doi.lower().strip()
    d = re.sub(r"^https?://(dx\.)?doi\.org/", "", d)
    d = d.rstrip(".,;")
    return d

def _first_nonempty(entry: dict, keys: list[str]) -> str:
    for k in keys:
        if k in entry and entry[k]:
            return str(entry[k]).strip()
        # case-insensitive fallback
        for kk, vv in entry.items():
            if kk.lower() == k.lower() and vv:
                return str(vv).strip()
    return ""

def _authors(entry: dict) -> str:
    a = _first_nonempty(entry, ["author", "Author"])
    a = a.replace("\n", " ").replace("  ", " ")
    a = re.sub(r"\s+and\s+", "; ", a, flags=re.IGNORECASE)
    return a.strip()

def _year(entry: dict) -> str:
    y = _first_nonempty(entry, ["year", "Year"])
    m = re.search(r"(19|20)\d{2}", y)
    return m.group(0) if m else y

def _venue(entry: dict) -> str:
    v = _first_nonempty(entry, ["journal", "Journal", "booktitle", "Booktitle", "publisher", "Publisher"])
    return v

def _abstract(entry: dict) -> str:
    return _first_nonempty(entry, ["abstract", "Abstract"])

def _keywords(entry: dict) -> str:
    return _first_nonempty(entry, ["keywords", "Keywords", "author_keywords", "Author_keywords"])

def _title(entry: dict) -> str:
    t = _first_nonempty(entry, ["title", "Title"])
    return re.sub(r"\s+", " ", t).strip()

def _doi(entry: dict) -> str:
    return _first_nonempty(entry, ["doi", "DOI"])


# ======================================================================
# Parsing tolerante
# ======================================================================
def parse_bib_file(path: Path) -> list[dict]:
    """Parse BibTeX tolerante a erros; retorna lista de dicts (entry)."""
    try:
        raw = path.read_text(encoding="utf-8", errors="replace")
    except Exception as e:
        print(f"[ERRO leitura] {path}: {e}")
        return []

    # Normaliza quebras entre entradas coladas (IEEE exporta várias entries em 1 linha).
    # Insere \n antes de cada @TIPO{ que venha logo após },
    raw = re.sub(r"\}\s*@", "}\n\n@", raw)

    # Sanitiza chaves BibTeX com caracteres problemáticos (espaços, apóstrofes):
    # ex.: "@ARTICLE{Kabilesh Kumar2025," → "@ARTICLE{Kabilesh_Kumar2025,"
    # O bibtexparser do PyPI (1.x) descarta silenciosamente entradas com chave contendo espaço.
    def _sanitize_key(m: re.Match) -> str:
        prefix = m.group(1)  # @TYPE{
        key = m.group(2)
        safe = re.sub(r"[^A-Za-z0-9_\-:+/.]", "_", key.strip())
        return f"{prefix}{safe},"
    raw = re.sub(r"(@\w+\s*\{\s*)([^,\n]+),", _sanitize_key, raw)

    parser = BibTexParser(common_strings=True)
    parser.ignore_nonstandard_types = False
    parser.homogenize_fields = False
    parser.customization = convert_to_unicode

    try:
        db = bibtexparser.loads(raw, parser=parser)
        entries = db.entries
    except Exception as e:
        print(f"[ERRO parse] {path}: {e} — tentando regex fallback")
        entries = _regex_fallback(raw)

    # Enriquecer com metadado de origem
    for e in entries:
        e["_source_file"] = str(path)
    return entries


def _regex_fallback(raw: str) -> list[dict]:
    """Fallback grosseiro caso o parser principal falhe."""
    entries = []
    # Captura blocos @TIPO{KEY, ... } balanceado simples
    for m in re.finditer(r"@(\w+)\s*\{\s*([^,\n]+),\s*([\s\S]*?)\n\}\s*(?=@|\Z)", raw):
        etype, ekey, body = m.groups()
        d = {"ENTRYTYPE": etype.lower(), "ID": ekey.strip()}
        for fm in re.finditer(r"([A-Za-z_\-]+)\s*=\s*[{\"]([\s\S]*?)[}\"]\s*,", body):
            d[fm.group(1).strip().lower()] = fm.group(2).strip()
        entries.append(d)
    return entries


# ======================================================================
# Classificação heurística
# ======================================================================
def _contains_any(text: str, terms: list[str]) -> bool:
    return any(t in text for t in terms)


def classify(entry: dict, base: str, string_id: str) -> tuple[str, str]:
    """Retorna (status, motivo). status ∈ {included, excluded, manual_review}.

    Regra de ouro: **conservador** — quando em dúvida, `manual_review`.
    Só exclui quando o texto aponta claramente para fora do escopo.
    """
    title = _norm(_title(entry))
    abstract = _norm(_abstract(entry))
    keywords = _norm(_keywords(entry))
    text = f"{title} {abstract} {keywords}"

    # Sinais de domínio
    has_upper_endo = _contains_any(text, ENDO_UPPER_TERMS)
    has_generic_endo = _contains_any(text, ENDO_GENERIC_TERMS)
    has_endo = has_upper_endo or has_generic_endo
    has_upper_gi_disease = _contains_any(text, UPPER_GI_DISEASE_TERMS)
    has_cv = _contains_any(text, CV_TERMS)
    has_useful_method = _contains_any(text, USEFUL_METHOD_TERMS)

    # Flags de contexto
    is_colon_only = (
        (("colonoscop" in text) or ("colorectal" in text) or ("colonic polyp" in text))
        and not has_upper_endo
        and not has_upper_gi_disease
    )
    brazil_flag = _contains_any(text, BRAZIL_TERMS)
    dataset_flag = _contains_any(text, DATASET_TERMS)

    # (1) Exclusões duras — apenas se NÃO houver vínculo com endoscopia/GI alto
    if not has_endo and not has_upper_gi_disease:
        for term in NLP_ONLY_TERMS:
            if term in text:
                return ("excluded", f"Fora de escopo — NLP/texto ('{term.strip()}') sem vínculo com visão computacional em endoscopia.")
        for term in OTHER_MEDICAL_IMG_TERMS:
            if term in text:
                return ("excluded", f"Outro domínio de imagem médica ('{term.strip()}') sem vínculo com endoscopia digestiva alta.")
        for term in OUT_OF_DOMAIN_TERMS:
            if term in text:
                return ("excluded", f"Tema fora do escopo ('{term.strip()}') — não relacionado a endoscopia/imagens GI.")

    # (2) Título ausente => manual_review
    if not title:
        return ("manual_review", "Título ausente; decisão automática inviável.")

    # (3) Abstract ausente — tentar decidir pelo título + keywords
    if not abstract:
        has_img_tk = any(t in f"{title} {keywords}" for t in ENDO_UPPER_TERMS + ENDO_GENERIC_TERMS)
        has_cv_tk = any(t in f"{title} {keywords}" for t in CV_TERMS)
        has_disease_tk = any(t in f"{title} {keywords}" for t in UPPER_GI_DISEASE_TERMS)
        if (has_img_tk and has_cv_tk) or (has_disease_tk and has_cv_tk):
            return ("included", "Título/keywords indicam DL/CV em endoscopia digestiva alta ou achado GI, mesmo sem abstract.")
        return ("manual_review", "Abstract ausente; título/keywords insuficientes para decisão automática.")

    # (4) Casos de inclusão
    # 4a: endoscopia alta explícita + CV → incluído
    if has_upper_endo and has_cv:
        extras = []
        if brazil_flag:
            extras.append("dados brasileiros/latino-americanos")
        if dataset_flag:
            extras.append("dataset/benchmark")
        extra_s = f" (contexto: {', '.join(extras)})" if extras else ""
        return ("included", f"Visão computacional/DL aplicada a endoscopia digestiva alta{extra_s}.")

    # 4b: endoscopia (genérica) + CV + achado do GI alto → incluído
    if has_generic_endo and has_cv and has_upper_gi_disease and not is_colon_only:
        return ("included", "DL/CV em endoscopia com achado do trato GI alto (gástrico/esofágico/duodenal).")

    # 4c: doença GI alta + CV (sem endoscopia textual) → incluído, pois presume-se imagens endoscópicas/histopatológicas do GI alto
    if has_upper_gi_disease and has_cv and not is_colon_only:
        return ("included", "DL/CV aplicado a achados do trato GI alto — provável pipeline de imagens relevante para a tese.")

    # 4d: endoscopia + método útil (multilabel, desbalanceamento, explicabilidade) → incluído
    if has_endo and has_useful_method:
        return ("included", "Endoscopia com contribuição metodológica relevante (multilabel, desbalanceamento, explicabilidade ou artefatos).")

    # (5) Exclusões secundárias
    if is_colon_only:
        return ("excluded", "Foco exclusivo em colonoscopia/colorretal — fora do escopo gástrico/endoscopia alta.")

    if has_endo and not has_cv and not has_upper_gi_disease:
        return ("manual_review", "Endoscopia sem componente de visão computacional/DL explícito — conferir manualmente se há contribuição metodológica útil.")

    if has_cv and not has_endo and not has_upper_gi_disease:
        return ("excluded", "Visão computacional sem vínculo com endoscopia/achados GI altos.")

    # (6) Qualquer sinal residual → manual_review
    return ("manual_review", "Sinais ambíguos — recomenda-se revisão manual pelo pesquisador.")


# ======================================================================
# Deduplicação
# ======================================================================
def dedup_key(entry: dict) -> tuple[str, str]:
    doi = _doi_key(_doi(entry))
    tkey = _title_key(_title(entry))
    return (doi, tkey)


# ======================================================================
# Pipeline
# ======================================================================
def main() -> None:
    all_records: list[dict] = []  # lista de dicts enriquecidos
    per_sb_counts = defaultdict(lambda: defaultdict(int))  # [base][S] -> métrica

    # 1) Parse tudo
    for base_dir, meta in BASES.items():
        base_path = ROOT_ORIG / base_dir
        for s_id, s_meta in meta["strings"].items():
            s_path = base_path / s_id
            if not s_path.exists():
                print(f"[AVISO] pasta inexistente: {s_path}")
                continue
            bib_files = sorted(s_path.glob("*.bib"))
            for bf in bib_files:
                entries = parse_bib_file(bf)
                per_sb_counts[base_dir][s_id] += len(entries)
                for e in entries:
                    rec = {
                        "base": meta["pretty"],
                        "base_dir": base_dir,
                        "string_id": s_id,
                        "titulo_interpretativo_string": s_meta["titulo"],
                        "objetivo_string": s_meta["objetivo"],
                        "registros_documento": s_meta["registros_documento"],
                        "bibtex_key_original": e.get("ID", ""),
                        "entry_type": e.get("ENTRYTYPE", ""),
                        "title": _title(e),
                        "authors": _authors(e),
                        "year": _year(e),
                        "doi": _doi(e),
                        "venue": _venue(e),
                        "abstract": _abstract(e),
                        "keywords": _keywords(e),
                        "_raw_entry": e,
                        "_source_file": e.get("_source_file", str(bf)),
                    }
                    all_records.append(rec)

    print(f"[OK] Total de registros brutos carregados: {len(all_records)}")

    # 2) Classificação
    for rec in all_records:
        status, motivo = classify(rec["_raw_entry"], rec["base_dir"], rec["string_id"])
        rec["status"] = status
        rec["motivo"] = motivo

    # 3) Deduplicação global (mantém primeira ocorrência mas registra origens)
    by_doi: dict[str, list[dict]] = defaultdict(list)
    by_title: dict[str, list[dict]] = defaultdict(list)
    for rec in all_records:
        doi, tkey = dedup_key(rec["_raw_entry"])
        rec["_doi_key"] = doi
        rec["_title_key"] = tkey
        if doi:
            by_doi[doi].append(rec)
        elif tkey:
            by_title[tkey].append(rec)

    # Marca duplicatas: 1º a aparecer é "canonical"; demais são duplicates.
    duplicate_groups: list[list[dict]] = []

    def _process_group(group: list[dict]) -> None:
        if len(group) <= 1:
            return
        # canonical: preferir entrada com abstract mais longo e classificada como "included"
        group_sorted = sorted(
            group,
            key=lambda r: (
                r["status"] != "included",
                -len(r["abstract"] or ""),
                r["base"],
                r["string_id"],
            ),
        )
        canonical = group_sorted[0]
        canonical["origens"] = sorted(
            {f"{r['base']}/{r['string_id']}" for r in group}
        )
        for dup in group_sorted[1:]:
            dup["status"] = "duplicate"
            dup["motivo"] = f"Duplicata de '{canonical['title'][:80]}...' já presente em {canonical['base']}/{canonical['string_id']}."
            dup["origens"] = [f"{dup['base']}/{dup['string_id']}"]
        duplicate_groups.append(group_sorted)

    for grp in by_doi.values():
        _process_group(grp)
    for grp in by_title.values():
        # se algum item do grupo já foi marcado duplicate via DOI, pular
        if any(r["status"] == "duplicate" for r in grp):
            continue
        _process_group(grp)

    # records com 'origens' já definido; para os demais, origens = base/S
    for rec in all_records:
        if "origens" not in rec:
            rec["origens"] = [f"{rec['base']}/{rec['string_id']}"]

    # 4) Escreve bib refinado por base/string (apenas INCLUDED do próprio S)
    for base_dir, meta in BASES.items():
        for s_id in meta["strings"]:
            out_dir = ROOT_OUT / base_dir / s_id
            out_dir.mkdir(parents=True, exist_ok=True)

            s_records = [
                r for r in all_records
                if r["base_dir"] == base_dir
                and r["string_id"] == s_id
                and r["status"] == "included"
            ]

            # bib
            db = bibtexparser.bibdatabase.BibDatabase()
            seen_keys = set()
            for r in s_records:
                e = dict(r["_raw_entry"])
                e.pop("_source_file", None)
                # garantir chave única
                key = e.get("ID") or f"{base_dir}_{s_id}_{len(seen_keys)+1}"
                base_key = key
                i = 1
                while key in seen_keys:
                    key = f"{base_key}_{i}"
                    i += 1
                seen_keys.add(key)
                e["ID"] = key
                db.entries.append(e)

            writer = BibTexWriter()
            writer.indent = "  "
            writer.order_entries_by = ("ID",)
            (out_dir / "artigos_refinados.bib").write_text(
                writer.write(db), encoding="utf-8"
            )

            # screening_log.csv
            s_all = [
                r for r in all_records
                if r["base_dir"] == base_dir and r["string_id"] == s_id
            ]
            _write_screening_log(out_dir / "screening_log.csv", s_all)

    # 5) Consolidado
    consolidado = ROOT_OUT / "consolidado"
    consolidado.mkdir(parents=True, exist_ok=True)

    # 5a) Bib global sem duplicatas (tudo que não for 'duplicate')
    db_all = bibtexparser.bibdatabase.BibDatabase()
    seen_keys = set()
    for r in all_records:
        if r["status"] == "duplicate":
            continue
        e = dict(r["_raw_entry"])
        e.pop("_source_file", None)
        key = e.get("ID") or f"{r['base_dir']}_{r['string_id']}"
        base_key = key
        i = 1
        while key in seen_keys:
            key = f"{base_key}_{i}"
            i += 1
        seen_keys.add(key)
        e["ID"] = key
        db_all.entries.append(e)
    writer = BibTexWriter()
    writer.indent = "  "
    (consolidado / "todos_artigos_refinados_sem_duplicatas.bib").write_text(
        writer.write(db_all), encoding="utf-8"
    )

    # 5b) CSVs por status
    _write_csv(
        consolidado / "artigos_incluidos.csv",
        [r for r in all_records if r["status"] == "included"],
    )
    _write_csv(
        consolidado / "artigos_excluidos.csv",
        [r for r in all_records if r["status"] == "excluded"],
    )
    _write_csv(
        consolidado / "artigos_duvida_revisao_manual.csv",
        [r for r in all_records if r["status"] == "manual_review"],
    )
    _write_csv(
        consolidado / "duplicatas_identificadas.csv",
        [r for r in all_records if r["status"] == "duplicate"],
    )

    # 5c) Resumo por base/string
    with (consolidado / "resumo_por_base_string.csv").open(
        "w", newline="", encoding="utf-8"
    ) as f:
        w = csv.writer(f)
        w.writerow([
            "base", "string_id", "titulo_interpretativo_string",
            "registros_documento", "registros_bibtex",
            "incluidos", "excluidos", "duplicatas", "revisao_manual",
        ])
        for base_dir, meta in BASES.items():
            for s_id, s_meta in meta["strings"].items():
                s_records = [
                    r for r in all_records
                    if r["base_dir"] == base_dir and r["string_id"] == s_id
                ]
                inc = sum(1 for r in s_records if r["status"] == "included")
                exc = sum(1 for r in s_records if r["status"] == "excluded")
                dup = sum(1 for r in s_records if r["status"] == "duplicate")
                mr = sum(1 for r in s_records if r["status"] == "manual_review")
                w.writerow([
                    meta["pretty"], s_id, s_meta["titulo"],
                    s_meta["registros_documento"],
                    len(s_records),
                    inc, exc, dup, mr,
                ])

    # 5d) Dump JSON para alimentar o relatório
    summary = _build_summary(all_records)
    (consolidado / "_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    print("[OK] Pipeline concluído. Verifique:", ROOT_OUT)
    print(json.dumps(summary["totais"], ensure_ascii=False, indent=2))


def _write_screening_log(path: Path, records: list[dict]) -> None:
    cols = [
        "base", "string_id", "titulo_interpretativo_string",
        "bibtex_key_original", "title", "authors", "year",
        "doi", "venue", "status", "motivo", "origens", "observacoes",
    ]
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for r in records:
            w.writerow({
                "base": r["base"],
                "string_id": r["string_id"],
                "titulo_interpretativo_string": r["titulo_interpretativo_string"],
                "bibtex_key_original": r["bibtex_key_original"],
                "title": r["title"],
                "authors": r["authors"],
                "year": r["year"],
                "doi": r["doi"],
                "venue": r["venue"],
                "status": r["status"],
                "motivo": r["motivo"],
                "origens": "; ".join(r.get("origens", [])),
                "observacoes": "",
            })


def _write_csv(path: Path, records: list[dict]) -> None:
    cols = [
        "base", "string_id", "titulo_interpretativo_string",
        "bibtex_key_original", "title", "authors", "year",
        "doi", "venue", "status", "motivo", "origens",
    ]
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for r in records:
            w.writerow({
                "base": r["base"],
                "string_id": r["string_id"],
                "titulo_interpretativo_string": r["titulo_interpretativo_string"],
                "bibtex_key_original": r["bibtex_key_original"],
                "title": r["title"],
                "authors": r["authors"],
                "year": r["year"],
                "doi": r["doi"],
                "venue": r["venue"],
                "status": r["status"],
                "motivo": r["motivo"],
                "origens": "; ".join(r.get("origens", [])),
            })


def _build_summary(records: list[dict]) -> dict:
    totais = {
        "bruto_total": len(records),
        "incluidos": sum(1 for r in records if r["status"] == "included"),
        "excluidos": sum(1 for r in records if r["status"] == "excluded"),
        "duplicatas": sum(1 for r in records if r["status"] == "duplicate"),
        "revisao_manual": sum(1 for r in records if r["status"] == "manual_review"),
    }
    totais["apos_dedup"] = totais["bruto_total"] - totais["duplicatas"]

    por_bs = []
    for base_dir, meta in BASES.items():
        for s_id, s_meta in meta["strings"].items():
            rs = [r for r in records if r["base_dir"] == base_dir and r["string_id"] == s_id]
            por_bs.append({
                "base": meta["pretty"],
                "string_id": s_id,
                "titulo": s_meta["titulo"],
                "registros_documento": s_meta["registros_documento"],
                "registros_bibtex": len(rs),
                "incluidos": sum(1 for r in rs if r["status"] == "included"),
                "excluidos": sum(1 for r in rs if r["status"] == "excluded"),
                "duplicatas": sum(1 for r in rs if r["status"] == "duplicate"),
                "revisao_manual": sum(1 for r in rs if r["status"] == "manual_review"),
            })
    return {"totais": totais, "por_base_string": por_bs}


if __name__ == "__main__":
    main()
