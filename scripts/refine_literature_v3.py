"""
Pipeline V3 de refinamento de revisão de literatura para tese de doutorado
em visão computacional aplicada a imagens endoscópicas digestivas altas.

Bases: IEEE, Scopus, Web of Science, PubMed, ScienceDirect, Springer Nature Link.

Entrada:  E:/Doutorado-V2/Revisão-Literatura/<Base>/S*/<*.bib|*.csv>
Saída:    E:/Doutorado-V2/Revisão-Literatura-refinada-V3/

Diferenças em relação ao V1 (refine_literature.py):
- Inclui PubMed (CSV), ScienceDirect (BibTeX) e Springer (CSV).
- Enriquece abstracts vazios via NCBI E-utilities (PMID) e Crossref (DOI),
  com cache em consolidado/_abstract_cache.json.
- Reaproveita decisões manuais antigas via manual_triage.csv (match por
  bibtex_key_original / DOI / título normalizado).
"""

from __future__ import annotations

import csv
import html
import json
import re
import time
import unicodedata
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from collections import defaultdict
from pathlib import Path

import bibtexparser
from bibtexparser.bparser import BibTexParser
from bibtexparser.bwriter import BibTexWriter
from bibtexparser.customization import convert_to_unicode

# ======================================================================
# Configuração
# ======================================================================
ROOT_ORIG = Path("E:/Doutorado-V2/Revisão-Literatura")
ROOT_OUT = Path("E:/Doutorado-V2/Revisão-Literatura-refinada-V3")
ROOT_OUT.mkdir(parents=True, exist_ok=True)
CONSOL = ROOT_OUT / "consolidado"
CONSOL.mkdir(parents=True, exist_ok=True)

# Reaproveitamento de decisões manuais antigas (V1, chave bibtex)
MANUAL_TRIAGE_OLD = Path("E:/Doutorado-V2/scripts/manual_triage.csv")
# Decisões manuais específicas do V3 (chave DOI normalizada)
MANUAL_TRIAGE_V3 = Path("E:/Doutorado-V2/scripts/manual_triage_v3.csv")

# Cache de enriquecimento
CACHE_PATH = CONSOL / "_abstract_cache.json"

# Polite contact (NCBI e Crossref recomendam)
CONTACT_EMAIL = "doutorado-revisao@example.com"
USER_AGENT = f"DoutoradoLitReview/3.0 (mailto:{CONTACT_EMAIL})"

BASES: dict[str, dict] = {
    "IEEE": {
        "pretty": "IEEE",
        "format": "bibtex",
        "strings": {
            "S1": ("IEEE S1 — Principal: IA/DL em endoscopia digestiva alta",
                   "IA, deep learning, CNN e visão computacional aplicados a imagens/vídeos de endoscopia digestiva alta ou gastroscopia.",
                   61),
            "S2": ("IEEE S2 — DL/CNN específico para endoscopia alta",
                   "Reduzir genéricos de IA e focar em redes profundas (ResNet/DenseNet/EfficientNet/MobileNet) no pipeline endoscópico.",
                   25),
            "S3": ("IEEE S3 — Lesões e alterações gástricas por IA",
                   "Estudos sobre alterações gástricas, lesões, pólipos, úlceras, erosões e neoplasias analisados por IA em endoscopia.",
                   25),
            "S4": ("IEEE S4 — Pólipos gástricos em endoscopia com IA",
                   "Trabalhos específicos sobre pólipos gástricos (incl. pólipos de glândulas fúndicas) em endoscopia com IA.",
                   8),
            "S5": ("IEEE S5 — IA em endoscopia com dados brasileiros / latino-americanos",
                   "IA, endoscopia e dados brasileiros / latino-americanos.",
                   18),
            "S6": ("IEEE S6 — Datasets brasileiros/latino-americanos de endoscopia",
                   "Datasets, bases anotadas ou clínicas brasileiras/latino-americanas de endoscopia.",
                   9),
        },
    },
    "Scopus": {
        "pretty": "Scopus",
        "format": "bibtex",
        "strings": {
            "S1": ("Scopus S1 — Principal: IA/DL em endoscopia digestiva alta",
                   "IA, ML e DL aplicados à classificação, detecção ou diagnóstico em imagens/vídeos de endoscopia digestiva alta.",
                   109),
            "S2": ("Scopus S2 — Lesões e alterações gástricas por IA",
                   "IA aplicada a lesões, anormalidades e achados gástricos (pólipos, úlceras, erosões, neoplasias, ectasia, micronodularidade).",
                   294),
            "S3": ("Scopus S3 — Pólipos gástricos em endoscopia com IA",
                   "IA aplicada a pólipos gástricos e pólipos de glândulas fúndicas em imagens endoscópicas.",
                   60),
            "S4": ("Scopus S4 — IA em endoscopia com dados brasileiros / latino-americanos",
                   "Trabalhos com dados brasileiros, latino-americanos ou sul-americanos em IA aplicada à endoscopia.",
                   8),
            "S5": ("Scopus S5 — Datasets brasileiros/latino-americanos de endoscopia",
                   "Bases de dados, datasets anotados ou clínicos brasileiros/latino-americanos de endoscopia.",
                   1),
        },
    },
    "Web-of-Science": {
        "pretty": "Web of Science",
        "format": "bibtex",
        "strings": {
            "S1": ("WoS S1 — Principal: IA/DL em endoscopia digestiva alta",
                   "IA, ML e DL aplicados à classificação, detecção ou diagnóstico em imagens/vídeos de endoscopia digestiva alta.",
                   200),
            "S2": ("WoS S2 — Lesões e alterações gástricas por IA",
                   "Lesões, anormalidades e alterações gástricas analisadas por IA em endoscopia alta.",
                   144),
            "S3": ("WoS S3 — Pólipos gástricos em endoscopia com IA",
                   "Pólipos gástricos, especialmente de glândulas fúndicas, em imagens endoscópicas com IA.",
                   20),
            "S4": ("WoS S4 — IA em endoscopia com dados brasileiros / latino-americanos",
                   "Estudos com dados brasileiros, latino-americanos ou sul-americanos em IA aplicada à endoscopia.",
                   4),
            "S5": ("WoS S5 — Dataset brasileiro/latino-americano de endoscopia",
                   "Datasets, bases de dados ou imagens médicas brasileiras/latino-americanas em endoscopia.",
                   1),
            "S6": ("WoS S6 — Datasets de endoscopia gástrica (qualquer origem)",
                   "Datasets de imagens endoscópicas gástricas, independentemente do país de origem.",
                   17),
        },
    },
    "Pub-Med": {
        "pretty": "PubMed",
        "format": "csv_pubmed",
        "strings": {
            "S2": ("PubMed S2 — DL/CNN específico em endoscopia alta",
                   "Versão focada em DL/CNN: gastroscopia × imagem/vídeo × DL × classificação/detecção/diagnóstico, excluindo colonoscopia.",
                   122),
            "S3": ("PubMed S3 — Lesões, anormalidades e pólipos gástricos",
                   "IA + endoscopia alta + achados clínicos (lesão, anormalidade, pólipo, úlcera, erosão, neoplasia), excluindo colonoscopia.",
                   193),
            "S5": ("PubMed S5 — Datasets de endoscopia gástrica",
                   "Datasets de endoscopia gástrica/imagem endoscópica × IA, excluindo colonoscopia.",
                   10),
        },
    },
    "ScienceDirect": {
        "pretty": "ScienceDirect",
        "format": "bibtex",
        "strings": {
            "S1": ("SD1 — gastroscopia + imagem/vídeo + DL/CNN",
                   "(gastroscopy OR gastric endoscopy) AND (endoscopic image/video) AND (DL/CNN), exclui colonoscopy.",
                   62),
            "S2": ("SD2 — gastroscopia + imagem/vídeo + IA/ML",
                   "(gastroscopy OR gastric endoscopy) AND (endoscopic image/video) AND (ML/AI), exclui colonoscopy.",
                   63),
            "S3": ("SD3 — upper GI endoscopy + DL/CNN",
                   "(upper GI/EGD endoscopy) AND (endoscopic image/video) AND (DL/CNN), exclui colonoscopy.",
                   83),
            "S4": ("SD4 — upper GI endoscopy + IA/ML",
                   "(upper GI/EGD endoscopy) AND (endoscopic image/video) AND (ML/AI), exclui colonoscopy.",
                   98),
            "S5": ("SD5 — Lesões gástricas",
                   "(gastroscopy) AND (gastric/mucosal lesion) AND (DL/ML), exclui colonoscopy.",
                   50),
            "S6": ("SD6 — Pólipos gástricos",
                   "(gastric/fundic gland polyp) AND (gastroscopy) AND (DL/AI), exclui colonoscopy.",
                   14),
            "S8": ("SD8 — Datasets de endoscopia gástrica",
                   "(gastroscopy/endoscopic image dataset) AND (DL/ML/AI), exclui colonoscopy.",
                   43),
            "S9": ("SD9 — Brasil",
                   "(Brazil OR Brazilian) AND (gastroscopy/gastric endoscopy) AND (AI/DL).",
                   24),
            "S10": ("SD10 — América Latina",
                    "(Latin/South America) AND (gastroscopy/gastric endoscopy) AND (AI/DL).",
                    17),
        },
    },
    "Springer-Nature-Link": {
        "pretty": "Springer Nature Link",
        "format": "csv_springer",
        "strings": {
            "S1": ("Springer S1 — Principal: IA/DL em endoscopia digestiva alta",
                   "Endoscopia alta + imagem médica + DL/CNN/transfer learning + classificação/detecção/diagnóstico, exclui colonoscopia/colorretal.",
                   96),
            "S2": ("Springer S2 — Lesões e alterações gástricas",
                   "Endoscopia alta + IA/ML/DL + lesões/anormalidades gástricas/pólipos/úlceras/erosões/neoplasias/ectasia/micronodularidade.",
                   253),
            "S3": ("Springer S3 — Pólipos gástricos",
                   "Pólipos gástricos / fúndicos × endoscopia × IA/CAD, excluindo colorretal.",
                   12),
            "S4": ("Springer S4 — Brasil / América Latina",
                   "Brasil/LatAm × endoscopia alta × dataset × IA/DL/CV.",
                   23),
            "S5": ("Springer S5 — Datasets de endoscopia gástrica",
                   "Datasets de endoscopia gástrica × IA/CV, excluindo colorretal.",
                   5),
        },
    },
    "Scopus-VLM-FMs": {
        "pretty": "Scopus (VLM/FMs)",
        "format": "bibtex",
        "strings": {
            "S1": ("S6-VLM S1 — FMs/VLMs em endoscopia (conceitual)",
                   "Foundation models e vision-language models aplicados a endoscopia: LVLM, MLLM, multimodal foundation models. PUBYEAR > 2021.",
                   151),
            "S2": ("S6-VLM S2 — Modelos nomeados em endoscopia",
                   "Modelos específicos: Endo-FM, GastroNet-5M, LLaVA-Endo, LLaVA-Med, BiomedGPT, BioMedCLIP, MedCLIP, Med-Flamingo, Med-Gemini, Med-PaLM M, MedSAM, SAM. PUBYEAR > 2021.",
                   68),
            "S3": ("S6-VLM S3 — Modelos comerciais multimodais em endoscopia",
                   "GPT-4V, GPT-4o, Gemini, Claude + endoscopia + imagem/vídeo/multimodal/VQA/diagnóstico/classificação/detecção/relatórios. PUBYEAR > 2021.",
                   160),
        },
    },
}

# ======================================================================
# Heurísticas de inclusão/exclusão (mesmas do V1, com ligeiros ajustes)
# ======================================================================

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
    "explainable ai", "explainability", " xai",
    "neural network", "self-supervised", "contrastive learning",
    "few-shot", "data augmentation", "generative adversarial", " gan ",
    "federated learning", "semi-supervised", "autoencoder",
    "radiomic", "histopatholog", "whole-slide", "whole slide image",
    "foundation model", "vision-language model", "vision language model",
    "large multimodal model", "large language model", "vlm ", " vlm",
    "lvlm", "mllm", "multimodal llm", "biomedclip", "medclip",
    "llava", "med-flamingo", "med-gemini", "med-palm",
    "gpt-4v", "gpt-4 vision", "gpt-4o", "segment anything", "medsam",
    "endo-fm", "endofm", "zero-shot", "few-shot learning",
    "in-context learning", "prompt engineering", "visual question answering",
    " vqa", "cross-modal", "multimodal",
]
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
    "gastrointestinal", "celiac", "coeliac", "intestinal metaplasia",
    "h. pylori",
]
USEFUL_METHOD_TERMS = [
    "multilabel", "multi-label", "multi label",
    "multiclass", "multi-class",
    "class imbalance", "imbalanced", "long-tailed",
    "image quality assessment", "artefact", "artifact",
    "explainab", "grad-cam", "gradcam", "saliency",
    "brazilian dataset", "latin american dataset",
]
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

# Strings cujo operador booleano JÁ garante endoscopia alta + IA (com NOT
# colonoscopy/colorretal). Para registros vindos dessas strings, podemos
# confiar no filtro da própria base e incluir mesmo sem abstract, desde
# que o título não traga sinais negativos óbvios. Strings de Brasil/LatAm
# são propensas a clínico-epidemiológicos e ficam fora desta lista.
STRONG_STRINGS: set[tuple[str, str]] = {
    ("IEEE", "S1"), ("IEEE", "S2"), ("IEEE", "S3"), ("IEEE", "S4"),
    ("Scopus", "S1"), ("Scopus", "S2"), ("Scopus", "S3"),
    ("Web-of-Science", "S1"), ("Web-of-Science", "S2"),
    ("Web-of-Science", "S3"), ("Web-of-Science", "S6"),
    ("Pub-Med", "S2"), ("Pub-Med", "S3"), ("Pub-Med", "S5"),
    ("ScienceDirect", "S1"), ("ScienceDirect", "S2"),
    ("ScienceDirect", "S3"), ("ScienceDirect", "S4"),
    ("ScienceDirect", "S5"), ("ScienceDirect", "S6"),
    ("ScienceDirect", "S8"),
    ("Springer-Nature-Link", "S1"), ("Springer-Nature-Link", "S2"),
    ("Springer-Nature-Link", "S3"), ("Springer-Nature-Link", "S5"),
    ("Scopus-VLM-FMs", "S1"), ("Scopus-VLM-FMs", "S2"), ("Scopus-VLM-FMs", "S3"),
}

# Termos no título que indicam sair do escopo independentemente da string.
TITLE_NEGATIVE_TERMS = [
    "colorectal", "colonoscop", "colon polyp", "colonic ",
    "fundus image", "retinal", "diabetic retinopathy",
    "chest x-ray", "chest ct", "lung nodule", "pulmonary nodule",
    "brain tumor", "brain mri", "skin lesion", "melanoma",
    "mammograph", "breast cancer screening",
    "natural language processing", "remote sensing",
    "endonasal", "skull base", "nasopharyng",
    "proceedings of the workshop",
]

# ======================================================================
# Utilitários
# ======================================================================
def _norm(text: str | None) -> str:
    if not text:
        return ""
    t = text.lower()
    t = unicodedata.normalize("NFKD", t)
    t = "".join(c for c in t if not unicodedata.combining(c))
    t = re.sub(r"\s+", " ", t)
    return t.strip()

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

def _decode_html(text: str | None) -> str:
    if not text:
        return ""
    return html.unescape(str(text)).replace("\xa0", " ")

def _strip_tags(text: str | None) -> str:
    if not text:
        return ""
    t = re.sub(r"<[^>]+>", " ", str(text))
    t = re.sub(r"\s+", " ", t)
    return t.strip()

def _split_packed_authors(packed: str) -> str:
    """Springer concatena autores sem separador. Heurística: insere ' and '
    quando uma minúscula é seguida de maiúscula. Não é perfeita, mas cria
    uma string razoável."""
    s = packed or ""
    s = re.sub(r"([a-z])([A-Z])", r"\1 and \2", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s

# ======================================================================
# Parsers por formato
# ======================================================================
def parse_bib_file(path: Path) -> list[dict]:
    try:
        raw = path.read_text(encoding="utf-8", errors="replace")
    except Exception as e:
        print(f"[ERRO leitura] {path}: {e}")
        return []
    raw = re.sub(r"\}\s*@", "}\n\n@", raw)
    def _sanitize_key(m: re.Match) -> str:
        prefix = m.group(1)
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
        print(f"[ERRO parse] {path}: {e}")
        entries = []
    out = []
    for e in entries:
        out.append({
            "ID": e.get("ID", ""),
            "ENTRYTYPE": e.get("ENTRYTYPE", ""),
            "title": _decode_html(e.get("title", "")),
            "authors": re.sub(r"\s+and\s+", "; ",
                              (e.get("author", "") or "").replace("\n", " "),
                              flags=re.IGNORECASE).strip(),
            "year": (re.search(r"(19|20)\d{2}", e.get("year", "")) or [None])[0]
                    if isinstance(e.get("year", ""), str) and re.search(r"(19|20)\d{2}", e.get("year", ""))
                    else (e.get("year", "") or ""),
            "doi": (e.get("doi", "") or "").strip(),
            "venue": e.get("journal", "") or e.get("booktitle", "") or e.get("publisher", ""),
            "abstract": e.get("abstract", "") or "",
            "keywords": e.get("keywords", "") or e.get("author_keywords", "") or "",
            "pmid": "",
            "_raw_entry": e,
        })
    return out

def parse_pubmed_csv(path: Path) -> list[dict]:
    out = []
    try:
        text = path.read_text(encoding="utf-8-sig", errors="replace")
    except Exception as e:
        print(f"[ERRO leitura] {path}: {e}")
        return []
    reader = csv.DictReader(text.splitlines())
    for row in reader:
        pmid = (row.get("PMID") or "").strip().strip('"')
        title = (row.get("Title") or "").strip().strip('"')
        authors = (row.get("Authors") or "").strip().strip('"')
        year = (row.get("Publication Year") or "").strip().strip('"')
        venue = (row.get("Journal/Book") or "").strip().strip('"')
        doi = (row.get("DOI") or "").strip().strip('"')
        out.append({
            "ID": f"pmid_{pmid}" if pmid else f"pubmed_{len(out)+1}",
            "ENTRYTYPE": "article",
            "title": _decode_html(title),
            "authors": authors,
            "year": year,
            "doi": doi,
            "venue": venue,
            "abstract": "",
            "keywords": "",
            "pmid": pmid,
            "_raw_entry": dict(row),
        })
    return out

def parse_springer_csv(path: Path) -> list[dict]:
    out = []
    try:
        text = path.read_text(encoding="utf-8-sig", errors="replace")
    except Exception as e:
        print(f"[ERRO leitura] {path}: {e}")
        return []
    reader = csv.DictReader(text.splitlines())
    for row in reader:
        title = _decode_html(row.get("Item Title") or "")
        venue = _decode_html(row.get("Publication Title") or "")
        doi = (row.get("Item DOI") or "").strip()
        authors_packed = _decode_html(row.get("Authors") or "")
        authors = _split_packed_authors(authors_packed)
        authors = re.sub(r"\s+and\s+", "; ", authors, flags=re.IGNORECASE)
        year = (row.get("Publication Year") or "").strip()
        ctype = (row.get("Content Type") or "").strip()
        key = (doi or title)[:80].replace("/", "_").replace(" ", "_")
        out.append({
            "ID": f"sp_{key}" if key else f"springer_{len(out)+1}",
            "ENTRYTYPE": "inproceedings" if "Conference" in ctype else "article",
            "title": title,
            "authors": authors,
            "year": year,
            "doi": doi,
            "venue": venue,
            "abstract": "",
            "keywords": "",
            "pmid": "",
            "_raw_entry": dict(row),
        })
    return out

# ======================================================================
# Enriquecimento de abstracts (NCBI E-utilities + Crossref)
# ======================================================================
def _http_get(url: str, timeout: int = 30) -> bytes | None:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "*/*"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.read()
    except Exception as e:
        print(f"[HTTP {url[:90]}...] {e}")
        return None

def fetch_pubmed_batch(pmids: list[str], cache: dict) -> None:
    """Lote NCBI E-utilities efetch. Atualiza cache in-place: cache[pmid] = {...}."""
    todo = [p for p in pmids if p and p not in cache.get("pubmed", {})]
    if not todo:
        return
    cache.setdefault("pubmed", {})
    BATCH = 150
    for i in range(0, len(todo), BATCH):
        chunk = todo[i:i + BATCH]
        url = (
            "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
            f"?db=pubmed&id={','.join(chunk)}&rettype=abstract&retmode=xml"
            f"&tool=DoutoradoLitReview&email={CONTACT_EMAIL}"
        )
        body = _http_get(url, timeout=60)
        time.sleep(0.4)  # respeitar 3 req/s
        if not body:
            for p in chunk:
                cache["pubmed"][p] = {"abstract": "", "keywords": "", "_status": "http_error"}
            continue
        try:
            root = ET.fromstring(body)
        except ET.ParseError as e:
            print(f"[XML parse error] {e}")
            for p in chunk:
                cache["pubmed"][p] = {"abstract": "", "keywords": "", "_status": "xml_error"}
            continue
        for art in root.findall(".//PubmedArticle"):
            pmid_el = art.find(".//PMID")
            if pmid_el is None:
                continue
            pmid = (pmid_el.text or "").strip()
            abs_parts = []
            for ab in art.findall(".//Abstract/AbstractText"):
                label = ab.attrib.get("Label", "")
                txt = "".join(ab.itertext()).strip()
                if not txt:
                    continue
                abs_parts.append(f"{label}: {txt}" if label else txt)
            abstract = " ".join(abs_parts).strip()
            kws = []
            for kw in art.findall(".//KeywordList/Keyword"):
                t = (kw.text or "").strip()
                if t:
                    kws.append(t)
            cache["pubmed"][pmid] = {
                "abstract": abstract,
                "keywords": "; ".join(kws),
                "_status": "ok",
            }
        # Marca os que não voltaram (ID inválido ou retraído)
        for p in chunk:
            cache["pubmed"].setdefault(p, {"abstract": "", "keywords": "", "_status": "not_found"})
        print(f"[PubMed] enriquecidos {min(i+BATCH, len(todo))}/{len(todo)}")

def fetch_crossref_doi(doi: str, cache: dict) -> dict:
    cache.setdefault("crossref", {})
    key = _doi_key(doi)
    if not key:
        return {"abstract": "", "keywords": ""}
    if key in cache["crossref"]:
        return cache["crossref"][key]
    safe = urllib.parse.quote(key, safe="/")
    url = f"https://api.crossref.org/works/{safe}?mailto={CONTACT_EMAIL}"
    body = _http_get(url, timeout=30)
    time.sleep(0.05)  # polite
    if not body:
        cache["crossref"][key] = {"abstract": "", "keywords": "", "_status": "http_error"}
        return cache["crossref"][key]
    try:
        data = json.loads(body.decode("utf-8", "replace"))
    except Exception:
        cache["crossref"][key] = {"abstract": "", "keywords": "", "_status": "json_error"}
        return cache["crossref"][key]
    msg = (data or {}).get("message", {}) or {}
    abstract = _strip_tags(msg.get("abstract", ""))
    subjects = msg.get("subject") or []
    cache["crossref"][key] = {
        "abstract": abstract,
        "keywords": "; ".join(subjects),
        "_status": "ok",
    }
    return cache["crossref"][key]

def load_cache() -> dict:
    if CACHE_PATH.exists():
        try:
            return json.loads(CACHE_PATH.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"pubmed": {}, "crossref": {}}

def save_cache(cache: dict) -> None:
    CACHE_PATH.write_text(json.dumps(cache, ensure_ascii=False, indent=1), encoding="utf-8")

# ======================================================================
# Classificação (mesma heurística do V1)
# ======================================================================
def _contains_any(text: str, terms: list[str]) -> bool:
    return any(t in text for t in terms)

def classify(rec: dict) -> tuple[str, str]:
    title = _norm(rec.get("title", ""))
    abstract = _norm(rec.get("abstract", ""))
    keywords = _norm(rec.get("keywords", ""))
    text = f"{title} {abstract} {keywords}"
    base_dir = rec.get("base_dir", "")
    string_id = rec.get("string_id", "")
    is_strong_string = (base_dir, string_id) in STRONG_STRINGS

    has_upper_endo = _contains_any(text, ENDO_UPPER_TERMS)
    has_generic_endo = _contains_any(text, ENDO_GENERIC_TERMS)
    has_endo = has_upper_endo or has_generic_endo
    has_upper_gi_disease = _contains_any(text, UPPER_GI_DISEASE_TERMS)
    has_cv = _contains_any(text, CV_TERMS)
    has_useful_method = _contains_any(text, USEFUL_METHOD_TERMS)

    is_colon_only = (
        (("colonoscop" in text) or ("colorectal" in text) or ("colonic polyp" in text))
        and not has_upper_endo
        and not has_upper_gi_disease
    )
    brazil_flag = _contains_any(text, BRAZIL_TERMS)
    dataset_flag = _contains_any(text, DATASET_TERMS)

    if not has_endo and not has_upper_gi_disease:
        for term in NLP_ONLY_TERMS:
            if term in text:
                return ("excluded", f"Fora de escopo — NLP/texto ('{term.strip()}') sem visão computacional em endoscopia.")
        for term in OTHER_MEDICAL_IMG_TERMS:
            if term in text:
                return ("excluded", f"Outro domínio de imagem médica ('{term.strip()}') sem vínculo com endoscopia digestiva alta.")
        for term in OUT_OF_DOMAIN_TERMS:
            if term in text:
                return ("excluded", f"Tema fora do escopo ('{term.strip()}').")

    if not title:
        return ("manual_review", "Título ausente; decisão automática inviável.")

    if any(t in title for t in ["proceedings of the workshop", "proceedings of the conference"]):
        return ("excluded", "Agregado editorial (proceedings/workshop) sem trabalho individual.")

    if not abstract:
        title_keys = f"{title} {keywords}"
        has_img_tk = any(t in title_keys for t in ENDO_UPPER_TERMS + ENDO_GENERIC_TERMS)
        has_cv_tk = any(t in title_keys for t in CV_TERMS)
        has_disease_tk = any(t in title_keys for t in UPPER_GI_DISEASE_TERMS)
        has_negative = any(t in title_keys for t in TITLE_NEGATIVE_TERMS)

        if (has_img_tk and has_cv_tk) or (has_disease_tk and has_cv_tk):
            return ("included", "Título/keywords indicam DL/CV em endoscopia digestiva alta ou achado GI, mesmo sem abstract.")
        if has_img_tk and has_disease_tk:
            return ("included", "Título/keywords indicam endoscopia + achado GI alto; presume-se CAD/análise de imagem.")
        # Confiança no operador booleano da string: se a string já garante
        # (endoscopia alta) AND (IA/DL) AND NOT (colon*), e o título não
        # apresenta sinais negativos, incluir.
        if is_strong_string and not has_negative:
            return ("included",
                    f"Sem abstract; recuperado por string forte ({base_dir}/{string_id}) "
                    f"que já restringe a endoscopia alta + IA/DL e exclui colorretal — confiável.")
        return ("manual_review", "Abstract ausente; título/keywords insuficientes para decisão automática.")

    if has_upper_endo and has_cv:
        extras = []
        if brazil_flag:
            extras.append("dados brasileiros/latino-americanos")
        if dataset_flag:
            extras.append("dataset/benchmark")
        extra_s = f" (contexto: {', '.join(extras)})" if extras else ""
        return ("included", f"Visão computacional/DL aplicada a endoscopia digestiva alta{extra_s}.")
    if has_generic_endo and has_cv and has_upper_gi_disease and not is_colon_only:
        return ("included", "DL/CV em endoscopia com achado do trato GI alto.")
    if has_upper_gi_disease and has_cv and not is_colon_only:
        return ("included", "DL/CV aplicado a achados do trato GI alto — presume-se imagens endoscópicas/histopatológicas.")
    if has_endo and has_useful_method:
        return ("included", "Endoscopia com contribuição metodológica relevante (multilabel, desbalanceamento, explicabilidade ou artefatos).")

    if is_colon_only:
        return ("excluded", "Foco exclusivo em colonoscopia/colorretal — fora do escopo gástrico/endoscopia alta.")

    has_negative_title = any(t in title for t in TITLE_NEGATIVE_TERMS)

    if has_endo and not has_cv and not has_upper_gi_disease:
        if is_strong_string and not has_negative_title:
            return ("included",
                    f"Endoscopia sem CV explícito no abstract, mas recuperado por string forte "
                    f"({base_dir}/{string_id}) que filtra IA/DL — confiável.")
        return ("manual_review", "Endoscopia sem componente de visão computacional/DL explícito.")
    if has_cv and not has_endo and not has_upper_gi_disease:
        return ("excluded", "Visão computacional sem vínculo com endoscopia/achados GI altos.")

    # Fallback final: se a string é forte e o título não é claramente off-topic,
    # incluir. Caso contrário, manual_review.
    if is_strong_string and not has_negative_title:
        return ("included",
                f"Sinais ambíguos no abstract, mas recuperado por string forte "
                f"({base_dir}/{string_id}) com filtro endoscopia alta + IA — confiável.")
    return ("manual_review", "Sinais ambíguos — recomenda-se revisão manual.")

# ======================================================================
# Manual triage antiga
# ======================================================================
def load_manual_triage_old() -> dict:
    """Retorna {bibtex_key: (status, motivo)}. Usado para reaproveitar as
    decisões já tomadas no V1."""
    out: dict[str, tuple[str, str]] = {}
    if not MANUAL_TRIAGE_OLD.exists():
        return out
    with MANUAL_TRIAGE_OLD.open(encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            k = (row.get("bibtex_key_original") or "").strip()
            s = (row.get("final_status") or "").strip()
            m = (row.get("final_motivo") or "").strip()
            if k and s in ("included", "excluded"):
                out[k] = (s, m)
    return out

def load_manual_triage_v3() -> dict:
    """Retorna {doi_key: (status, motivo)}. Decisões manuais V3 indexadas por DOI."""
    out: dict[str, tuple[str, str]] = {}
    if not MANUAL_TRIAGE_V3.exists():
        return out
    with MANUAL_TRIAGE_V3.open(encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            d = _doi_key(row.get("doi") or "")
            s = (row.get("final_status") or "").strip()
            m = (row.get("final_motivo") or "").strip()
            if d and s in ("included", "excluded"):
                out[d] = (s, m)
    return out

# ======================================================================
# Pipeline
# ======================================================================
def main() -> None:
    cache = load_cache()
    manual_old = load_manual_triage_old()
    manual_v3 = load_manual_triage_v3()

    all_records: list[dict] = []
    for base_dir, meta in BASES.items():
        base_path = ROOT_ORIG / base_dir
        if not base_path.exists():
            print(f"[AVISO] base não encontrada: {base_path}")
            continue
        fmt = meta["format"]
        for s_id, (titulo, objetivo, n_doc) in meta["strings"].items():
            s_path = base_path / s_id
            if not s_path.exists():
                print(f"[AVISO] pasta inexistente: {s_path}")
                continue
            if fmt == "bibtex":
                files = sorted(s_path.glob("*.bib"))
                parsed = []
                for f in files:
                    parsed.extend(parse_bib_file(f))
            elif fmt == "csv_pubmed":
                files = sorted(s_path.glob("*.csv"))
                parsed = []
                for f in files:
                    parsed.extend(parse_pubmed_csv(f))
            elif fmt == "csv_springer":
                files = sorted(s_path.glob("*.csv"))
                parsed = []
                for f in files:
                    parsed.extend(parse_springer_csv(f))
            else:
                parsed = []
            for r in parsed:
                rec = dict(r)
                rec.update({
                    "base": meta["pretty"],
                    "base_dir": base_dir,
                    "string_id": s_id,
                    "titulo_interpretativo_string": titulo,
                    "objetivo_string": objetivo,
                    "registros_documento": n_doc,
                    "bibtex_key_original": r.get("ID", ""),
                    "entry_type": r.get("ENTRYTYPE", ""),
                })
                all_records.append(rec)

    print(f"[OK] Brutos carregados: {len(all_records)}")

    # 2) Enriquecer abstracts via PubMed (PMID) e Crossref (DOI)
    pmids_to_fetch = [r.get("pmid") for r in all_records if r.get("pmid") and not r.get("abstract")]
    print(f"[PubMed] PMIDs a enriquecer: {len(pmids_to_fetch)}")
    if pmids_to_fetch:
        fetch_pubmed_batch(pmids_to_fetch, cache)
        save_cache(cache)
    for r in all_records:
        if r.get("pmid") and not r.get("abstract"):
            info = cache.get("pubmed", {}).get(r["pmid"], {})
            if info.get("abstract"):
                r["abstract"] = info["abstract"]
            if info.get("keywords") and not r.get("keywords"):
                r["keywords"] = info["keywords"]

    # Crossref para os que ainda não têm abstract e têm DOI
    crossref_targets = [r for r in all_records if not r.get("abstract") and _doi_key(r.get("doi"))]
    print(f"[Crossref] DOIs a enriquecer: {len(crossref_targets)}")
    for i, r in enumerate(crossref_targets, 1):
        info = fetch_crossref_doi(r["doi"], cache)
        if info.get("abstract"):
            r["abstract"] = info["abstract"]
        if info.get("keywords") and not r.get("keywords"):
            r["keywords"] = info["keywords"]
        if i % 100 == 0:
            print(f"[Crossref] {i}/{len(crossref_targets)}")
            save_cache(cache)
    save_cache(cache)

    # 3) Classificação
    for rec in all_records:
        # 3a) Decisão manual V3 (chave DOI) tem precedência máxima
        v3 = manual_v3.get(_doi_key(rec.get("doi", "")))
        if v3:
            rec["status"], rec["motivo"] = v3[0], f"[manual_v3] {v3[1]}"
            continue
        # 3b) Reaproveitar decisão manual V1, se a chave bibtex bater
        old = manual_old.get(rec.get("bibtex_key_original", ""))
        if old:
            rec["status"], rec["motivo"] = old
            rec["motivo"] = f"[manual_v1] {rec['motivo']}"
            continue
        # 3c) Heurística automática
        rec["status"], rec["motivo"] = classify(rec)

    # 4) Deduplicação global
    by_doi: dict[str, list[dict]] = defaultdict(list)
    by_title: dict[str, list[dict]] = defaultdict(list)
    for rec in all_records:
        doi = _doi_key(rec.get("doi"))
        tkey = _title_key(rec.get("title"))
        rec["_doi_key"] = doi
        rec["_title_key"] = tkey
        if doi:
            by_doi[doi].append(rec)
        elif tkey:
            by_title[tkey].append(rec)

    def _process_group(group: list[dict]) -> None:
        if len(group) <= 1:
            return
        group_sorted = sorted(
            group,
            key=lambda r: (
                r["status"] != "included",
                -len(r.get("abstract") or ""),
                r["base"],
                r["string_id"],
            ),
        )
        canonical = group_sorted[0]
        canonical["origens"] = sorted({f"{r['base']}/{r['string_id']}" for r in group})
        for dup in group_sorted[1:]:
            dup["status"] = "duplicate"
            dup["motivo"] = f"Duplicata de '{canonical['title'][:80]}…' já presente em {canonical['base']}/{canonical['string_id']}."
            dup["origens"] = [f"{dup['base']}/{dup['string_id']}"]

    for grp in by_doi.values():
        _process_group(grp)
    for grp in by_title.values():
        if any(r["status"] == "duplicate" for r in grp):
            continue
        _process_group(grp)

    for rec in all_records:
        if "origens" not in rec:
            rec["origens"] = [f"{rec['base']}/{rec['string_id']}"]

    # 5) Escrita por base/string
    for base_dir, meta in BASES.items():
        for s_id in meta["strings"]:
            out_dir = ROOT_OUT / base_dir / s_id
            out_dir.mkdir(parents=True, exist_ok=True)
            s_records = [
                r for r in all_records
                if r["base_dir"] == base_dir and r["string_id"] == s_id
                and r["status"] == "included"
            ]
            db = bibtexparser.bibdatabase.BibDatabase()
            seen = set()
            for r in s_records:
                e = dict(r.get("_raw_entry") or {})
                # Para entradas vindas de CSV, montar BibTeX mínimo
                if not e or "ENTRYTYPE" not in e:
                    e = {"ENTRYTYPE": r.get("entry_type") or "article"}
                e["ID"] = r.get("bibtex_key_original") or f"{base_dir}_{s_id}_{len(seen)+1}"
                e.setdefault("title", r.get("title", ""))
                e.setdefault("author", r.get("authors", "").replace("; ", " and "))
                e.setdefault("year", str(r.get("year", "")))
                if r.get("doi"):
                    e["doi"] = r["doi"]
                if r.get("venue"):
                    e.setdefault("journal", r["venue"])
                if r.get("abstract"):
                    e["abstract"] = r["abstract"]
                if r.get("keywords"):
                    e["keywords"] = r["keywords"]
                # garantir chave única
                key = e["ID"]
                base_key = key
                i = 1
                while key in seen:
                    key = f"{base_key}_{i}"
                    i += 1
                e["ID"] = key
                seen.add(key)
                # remove campos de controle
                for k in list(e.keys()):
                    if k.startswith("_"):
                        e.pop(k)
                db.entries.append(e)
            writer = BibTexWriter()
            writer.indent = "  "
            writer.order_entries_by = ("ID",)
            (out_dir / "artigos_refinados.bib").write_text(writer.write(db), encoding="utf-8")

            s_all = [r for r in all_records if r["base_dir"] == base_dir and r["string_id"] == s_id]
            _write_screening_log(out_dir / "screening_log.csv", s_all)

    # 6) Consolidado
    db_all = bibtexparser.bibdatabase.BibDatabase()
    seen = set()
    for r in all_records:
        if r["status"] == "duplicate":
            continue
        e = dict(r.get("_raw_entry") or {})
        if not e or "ENTRYTYPE" not in e:
            e = {"ENTRYTYPE": r.get("entry_type") or "article"}
        e["ID"] = r.get("bibtex_key_original") or f"{r['base_dir']}_{r['string_id']}"
        e.setdefault("title", r.get("title", ""))
        e.setdefault("author", r.get("authors", "").replace("; ", " and "))
        e.setdefault("year", str(r.get("year", "")))
        if r.get("doi"):
            e["doi"] = r["doi"]
        if r.get("venue"):
            e.setdefault("journal", r["venue"])
        if r.get("abstract"):
            e["abstract"] = r["abstract"]
        if r.get("keywords"):
            e["keywords"] = r["keywords"]
        key = e["ID"]
        base_key = key
        i = 1
        while key in seen:
            key = f"{base_key}_{i}"
            i += 1
        e["ID"] = key
        seen.add(key)
        for k in list(e.keys()):
            if k.startswith("_"):
                e.pop(k)
        db_all.entries.append(e)
    writer = BibTexWriter()
    writer.indent = "  "
    (CONSOL / "todos_artigos_refinados_sem_duplicatas.bib").write_text(
        writer.write(db_all), encoding="utf-8"
    )

    _write_csv(CONSOL / "artigos_incluidos.csv",
               [r for r in all_records if r["status"] == "included"])
    _write_csv(CONSOL / "artigos_excluidos.csv",
               [r for r in all_records if r["status"] == "excluded"])
    _write_csv(CONSOL / "artigos_duvida_revisao_manual.csv",
               [r for r in all_records if r["status"] == "manual_review"])
    _write_csv(CONSOL / "duplicatas_identificadas.csv",
               [r for r in all_records if r["status"] == "duplicate"])

    with (CONSOL / "resumo_por_base_string.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["base", "string_id", "titulo_interpretativo_string",
                    "registros_documento", "registros_brutos",
                    "incluidos", "excluidos", "duplicatas", "revisao_manual"])
        for base_dir, meta in BASES.items():
            for s_id, (titulo, _obj, n_doc) in meta["strings"].items():
                rs = [r for r in all_records if r["base_dir"] == base_dir and r["string_id"] == s_id]
                inc = sum(1 for r in rs if r["status"] == "included")
                exc = sum(1 for r in rs if r["status"] == "excluded")
                dup = sum(1 for r in rs if r["status"] == "duplicate")
                mr = sum(1 for r in rs if r["status"] == "manual_review")
                w.writerow([meta["pretty"], s_id, titulo, n_doc, len(rs), inc, exc, dup, mr])

    summary = _build_summary(all_records)
    (CONSOL / "_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    save_cache(cache)
    print("[OK] V3 concluído.")
    print(json.dumps(summary["totais"], ensure_ascii=False, indent=2))


def _write_screening_log(path: Path, records: list[dict]) -> None:
    cols = ["base", "string_id", "titulo_interpretativo_string",
            "bibtex_key_original", "title", "authors", "year",
            "doi", "venue", "status", "motivo", "origens", "tem_abstract"]
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for r in records:
            w.writerow({
                "base": r["base"], "string_id": r["string_id"],
                "titulo_interpretativo_string": r["titulo_interpretativo_string"],
                "bibtex_key_original": r["bibtex_key_original"],
                "title": r.get("title", ""), "authors": r.get("authors", ""),
                "year": r.get("year", ""), "doi": r.get("doi", ""),
                "venue": r.get("venue", ""), "status": r.get("status", ""),
                "motivo": r.get("motivo", ""),
                "origens": "; ".join(r.get("origens", [])),
                "tem_abstract": "sim" if r.get("abstract") else "não",
            })

def _write_csv(path: Path, records: list[dict]) -> None:
    cols = ["base", "string_id", "titulo_interpretativo_string",
            "bibtex_key_original", "title", "authors", "year",
            "doi", "venue", "status", "motivo", "origens", "tem_abstract"]
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for r in records:
            w.writerow({
                "base": r["base"], "string_id": r["string_id"],
                "titulo_interpretativo_string": r["titulo_interpretativo_string"],
                "bibtex_key_original": r["bibtex_key_original"],
                "title": r.get("title", ""), "authors": r.get("authors", ""),
                "year": r.get("year", ""), "doi": r.get("doi", ""),
                "venue": r.get("venue", ""), "status": r.get("status", ""),
                "motivo": r.get("motivo", ""),
                "origens": "; ".join(r.get("origens", [])),
                "tem_abstract": "sim" if r.get("abstract") else "não",
            })

def _build_summary(records: list[dict]) -> dict:
    totais = {
        "bruto_total": len(records),
        "incluidos": sum(1 for r in records if r["status"] == "included"),
        "excluidos": sum(1 for r in records if r["status"] == "excluded"),
        "duplicatas": sum(1 for r in records if r["status"] == "duplicate"),
        "revisao_manual": sum(1 for r in records if r["status"] == "manual_review"),
        "com_abstract": sum(1 for r in records if r.get("abstract")),
    }
    totais["apos_dedup"] = totais["bruto_total"] - totais["duplicatas"]
    por_bs = []
    for base_dir, meta in BASES.items():
        for s_id, (titulo, _obj, n_doc) in meta["strings"].items():
            rs = [r for r in records if r["base_dir"] == base_dir and r["string_id"] == s_id]
            por_bs.append({
                "base": meta["pretty"], "string_id": s_id, "titulo": titulo,
                "registros_documento": n_doc, "registros_brutos": len(rs),
                "incluidos": sum(1 for r in rs if r["status"] == "included"),
                "excluidos": sum(1 for r in rs if r["status"] == "excluded"),
                "duplicatas": sum(1 for r in rs if r["status"] == "duplicate"),
                "revisao_manual": sum(1 for r in rs if r["status"] == "manual_review"),
                "com_abstract": sum(1 for r in rs if r.get("abstract")),
            })
    return {"totais": totais, "por_base_string": por_bs}


if __name__ == "__main__":
    main()
