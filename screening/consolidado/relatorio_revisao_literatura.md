# Revisão de Literatura — Tese de Doutorado (V3)

**Tema.** Visão computacional aplicada a imagens de endoscopia digestiva alta (gastroscopia / EGD), com foco em classificação multilabel de achados gástricos/esofágicos, desbalanceamento extremo, artefatos de imagem (saliva, luz) e explicabilidade, sustentada por um dataset brasileiro inédito.

**Diferença em relação às versões anteriores.** A V1 (`Revisão-Literatura-refinada/`) cobriu três bases: IEEE, Scopus e Web of Science. Esta versão **V3** acrescenta **PubMed**, **ScienceDirect**, **Springer Nature Link** e uma etapa complementar **Scopus S6-VLM-FMs** (Foundation Models e Vision-Language Models em endoscopia), totalizando sete fontes de busca. Os exports brutos das três bases anteriores não foram refeitos — a triagem foi reaplicada com pipeline atualizado. Duas camadas de decisões manuais são reaproveitadas automaticamente:

- **Manual V1** (`scripts/manual_triage.csv`, 35 casos, chave BibTeX) — casos triados em 2026-05-06 sobre as 3 bases originais.
- **Manual V3** (`scripts/manual_triage_v3.csv`, 30 casos, chave DOI) — todos os itens que caíram em revisão manual após a inclusão das 3 bases novas (índices editoriais, agregados de pôsteres, falsos positivos da string Springer S4 sobre "Brasil/LatAm").

**Etapa complementar S6-VLM-FMs (2026-05-20).** Três novas strings de busca na Scopus, focadas exclusivamente em Foundation Models e Vision-Language Models aplicados a endoscopia (PUBYEAR > 2021), foram adicionadas como fonte separada `Scopus-VLM-FMs`. A separação mantém rastreabilidade e não sobrescreve os resultados anteriores das strings Scopus S1–S5.

**Processamento.** Última execução em 2026-05-20 (com S6-VLM-FMs integrado). Scripts em [scripts/](../scripts/):

- [refine_literature_v3.py](../../scripts/refine_literature_v3.py) — parseia 6 formatos (BibTeX IEEE/Scopus/WoS/SD; CSV PubMed; CSV Springer), enriquece abstracts vazios via NCBI E-utilities (PMID) e Crossref (DOI), aplica triagem heurística, deduplica e aplica decisões manuais V1+V3 com precedência sobre a heurística automática.
- [analyze_literature_v3.py](../../scripts/analyze_literature_v3.py) — gera estatísticas descritivas (anos, venues, temas) que alimentam este relatório.
- [analyze_dataset.py](../../scripts/analyze_dataset.py) — estatísticas do dataset brasileiro (reaproveitado de V1, planilha não mudou).
- [apply_manual_triage.py](../../scripts/apply_manual_triage.py) e [manual_triage.csv](../../scripts/manual_triage.csv) — decisões manuais V1 (chave BibTeX, 35 itens).
- [manual_triage_v3.csv](../../scripts/manual_triage_v3.csv) — decisões manuais V3 (chave DOI, 30 itens; aplicadas pelo próprio `refine_literature_v3.py`).

Os arquivos originais em [Revisão-Literatura/](../../Revisão-Literatura/) **não foram alterados**. Todos os resultados estão em [Revisão-Literatura-refinada-V3/](../).

---

## A. Visão geral

**Objetivo.** Construir uma base bibliográfica triada, deduplicada e justificada para sustentar a tese, identificando (i) o estado da arte em visão computacional em endoscopia digestiva alta, (ii) brechas científicas exploráveis e (iii) trilhas concretas de publicação com estimativa de estrato Qualis.

**Bases e strings.** Sete fontes de busca agora compõem o corpus:

- **IEEE Xplore** — S1 (principal), S2 (DL/CNN específico), S3 (lesões), S4 (pólipos), S5 (Brasil/LatAm), S6 (datasets BR/LatAm).
- **Scopus** — S1 a S5.
- **Web of Science** — S1 a S6.
- **PubMed** — S2 (DL/CNN focado), S3 (lesões e pólipos), S5 (datasets). S1 e S4 não retornaram exports relevantes (Brasil/LatAm em PubMed = 0 registros).
- **ScienceDirect** — SD1 a SD6, SD8 a SD10 (SD7 = pólipos fúndicos com 0 registros).
- **Springer Nature Link** — S1 a S5.
- **Scopus S6-VLM-FMs** (etapa complementar, 2026-05-20) — S1 (FMs/VLMs conceitual, 151 registros), S2 (modelos nomeados: Endo-FM, LLaVA-Med, BioMedCLIP, MedSAM, etc., 68 registros), S3 (modelos comerciais multimodais: GPT-4V, GPT-4o, Gemini, Claude + endoscopia, 160 registros). Todas com filtro `PUBYEAR > 2021`.

**Totais após triagem (com manual_triage_v3 aplicado + S6-VLM-FMs).**

| Métrica | V1 (3 bases) | V3 (6 bases) | V3 + S6-VLM-FMs |
|---------|---:|---:|---:|
| Registros brutos parseados | 1 004 | 2 172 | **2 551** |
| Após deduplicação por DOI + título normalizado | 749 | 1 435 | **1 734** |
| Incluídos | 717 | 1 358 | **1 621** |
| Excluídos | 32 | 77 | **113** |
| Duplicatas identificadas | 255 | 737 | **817** |
| Pendentes em revisão manual | 0 | 0 | **0** |
| Registros com abstract disponível | — | 1 695 (78 %) | **2 057 / 2 551 (81 %)** |

Os 30 itens originalmente em manual_review (pré-S6) foram triados individualmente (ver [manual_triage_v3.csv](../../scripts/manual_triage_v3.csv)): **2 promovidos a incluído** (revisão clínica de condições pré-malignas do estômago em *Best Practice & Research Clinical Gastroenterology* e sistematização de medicina digital em oncologia em *Procedia Computer Science*) e **28 excluídos**, com justificativa individual. Os motivos de exclusão concentraram-se em **agregados editoriais sem trabalho individual** (*Subject Index*, *Full Issue PDF*, *Poster presentations*, *Abstracts from USCAP*, *Proceedings of …*) e **falsos positivos da string Springer S4 "Brasil/LatAm"** (diplomacia climática, energia rural, biologia molecular sem imagem) — esses últimos sugerem que a string Springer S4 é demasiadamente permissiva e poderia ser refeita com termos mais específicos a *image*/*endoscopy* no AND principal.

**Triagem dos itens da S6-VLM-FMs.** A adição das 3 strings de VLM/FMs gerou inicialmente 5 registros em revisão manual (4 da String 1, 1 da String 3). Todos foram triados e **excluídos**: 4 sobre endoscopia nasofaríngea (NPC) e 1 proceedings editorial (BioNLP workshop). As decisões foram adicionadas a [manual_triage_v3.csv](../../scripts/manual_triage_v3.csv) (4 com DOI) e ao classificador via `TITLE_NEGATIVE_TERMS` (1 proceedings sem DOI). **Fila de manual_review = 0.**

**Cobertura de abstracts.** PubMed e Springer não exportam abstract no CSV. O pipeline V3 buscou abstracts faltantes em (i) NCBI E-utilities `efetch` para PMIDs e (ii) API Crossref para DOIs. Resultado: **1 695 dos 2 172 registros (78 %) ficaram com abstract não-vazio** após enriquecimento. Os 477 sem abstract concentram-se em capítulos Springer (Crossref muitas vezes não retorna abstract de capítulo) e atas/proceedings sem DOI individualizado.

**Estratégia para registros sem abstract.** Em vez de jogá-los todos para revisão manual (que era a regra em V1), a V3 confia no operador booleano da string de busca: se a string já restringe explicitamente *(endoscopia alta) AND (IA/DL) NOT (colon\*)*, e o título não traz sinais negativos óbvios (colorectal, retinal, mammograph, etc.), o registro é **incluído com motivo declarado**. Isso é coerente com o padrão PRISMA — a string de busca é o primeiro filtro de inclusão. Strings de Brasil/LatAm são excluídas dessa regra (são propensas a falsos positivos clínico-epidemiológicos, como confirmado pela triagem de Springer S4).

**Fila manual zerada.** Tanto V1 (35 itens) quanto V3 (30 itens) tiveram suas filas zeradas por triagem individual, com justificativa registrada por DOI/chave em CSVs versionados. Isso fecha o ciclo PRISMA *screening → eligibility* com decisões auditáveis.

### Objetivo geral (inalterado em relação a V1)

Desenvolver e avaliar um classificador multilabel de imagens de endoscopia digestiva alta, robusto a artefatos de aquisição e a classes raras, sustentado por um dataset brasileiro curado, com explicabilidade passível de auditoria clínica.

### Objetivos específicos

1. **Curar e publicar um dataset brasileiro** de gastroscopia (≈ 1 990 imagens) com 9 rótulos de patologia + 2 de artefato, documentando decisões de limpeza (duplicatas, linhas órfãs, *missing*) em um datasheet reprodutível.
2. **Formular e avaliar o problema como multilabel explícito**, incorporando a co-ocorrência clínica real (ENANTEMA+EROSÃO, ÚLCERA+EROSÃO) como prior, em contraste com as formulações binárias/multiclasse predominantes na literatura.
3. **Tratar saliva e luz como classes**, quantificando o viés que introduzem e diagnosticando *shortcut learning* em patologias fortemente correlacionadas a esses artefatos (ex.: EROSÃO).
4. **Propor protocolos de avaliação para classes raras extremas** (NEOPLASIA e ECTASIA VASCULAR com 4 imagens cada), incluindo *few-shot*, *loss* assimétrico e reporte honesto de incerteza.
5. **Gerar e validar explicações por rótulo** (mapas de ativação por classe em multilabel), com concordância inter-avaliador por endoscopistas, em vez do Grad-CAM do *top-1* hoje dominante.
6. **Comparar arquiteturas em regime de dados pequeno** (ResNet, EfficientNet, ViT, Swin), reportando sensibilidade por classe e calibração, para entender o que é realista prometer em deploy clínico.

---

## B. Caracterização do problema (a partir de Data/)

Esta seção é toda sustentada por [analyze_dataset.py](../../scripts/analyze_dataset.py) → [dataset_stats.json](dataset_stats.json) e [dataset_cooccurrence.csv](dataset_cooccurrence.csv). Os números abaixo foram extraídos diretamente da pasta `Data/` e do CSV — a planilha não foi alterada desde a V1.

**Volume.**

| Item | Valor |
|------|---:|
| Arquivos `.jpg` em `Data/Imgs/` | 2 007 |
| Linhas na planilha (`IMAGENS ROTULADAS.csv`) | 2 499 (excluindo cabeçalho) |
| Imagens com rótulo e arquivo presente | **1 990** |
| Imagens sem rótulo na planilha | 17 |
| Linhas da planilha sem arquivo correspondente | 498 |
| `image_name` duplicados na planilha | 12 |

**Rótulos (11 colunas binárias).** Codificação original: 1 = presente, 2 = ausente. Após normalização para 0/1:

| Rótulo | Presentes | Ausentes | Missing | Prevalência | Imbalance Ratio |
|--------|---:|---:|---:|---:|---:|
| NORMAL | 968 | 1 022 | 0 | 48,6 % | 1,06 |
| ALTERADO | 1 016 | 974 | 0 | 51,1 % | 0,96 |
| SALIVA (artefato) | 231 | 1 759 | 0 | 11,6 % | 7,61 |
| LUZ (artefato) | 391 | 1 599 | 0 | 19,7 % | 4,09 |
| ENANTEMA | 200 | 1 790 | 0 | 10,1 % | 8,95 |
| PÓLIPO | 50 | 1 940 | 0 | 2,5 % | 38,80 |
| ÚLCERA | 81 | 1 909 | 0 | 4,1 % | 23,57 |
| EROSÃO | 320 | 1 670 | 0 | 16,1 % | 5,22 |
| MICRONODULARIDADE | 34 | 1 956 | 0 | 1,7 % | 57,53 |
| ECTASIA VASCULAR | 4 | 841 | **1 145** | 0,2 % | 210,25 |
| NEOPLASIA | 4 | 1 986 | 0 | 0,2 % | 496,50 |

Três observações críticas:

1. **Desbalanceamento extremo.** NEOPLASIA e ECTASIA VASCULAR têm 4 imagens cada — qualquer modelo que otimize acurácia global aprenderá a ignorá-las.
2. **ECTASIA VASCULAR tem 1 145 valores ausentes.** Possivelmente a coluna foi adicionada tardiamente ou só foi anotada em subconjunto de imagens — precisa decisão explícita: reanotar, descartar a classe ou tratar como MNAR.
3. **Inconsistência NORMAL × ALTERADO.** NORMAL soma 968 e ALTERADO soma 1 016, o que deveria ser complementar (1 990 imagens). Há 959 imagens marcadas apenas como NORMAL e 407 como ALTERADO sem nenhuma patologia específica positiva — ou seja, ~40 % das imagens alteradas não têm o achado específico identificado.

**Distribuição multilabel (rótulos positivos simultâneos por imagem):**

| Rótulos positivos | Imagens |
|---:|---:|
| 0 | 2 |
| 1 | 963 |
| 2 | 777 |
| 3 | 231 |
| 4 | 13 |
| 8 | 1 |
| 9 | 1 |
| 10 | 2 |

Considerando **apenas patologias** (excluindo NORMAL/ALTERADO/SALIVA/LUZ): 1 374 imagens sem patologia positiva, 558 com exatamente uma, 53 com duas, 1 com três, e 4 casos extremos (6 ou 7 patologias) que merecem verificação manual.

**Co-ocorrência de patologias (top 5 pares):**

| Par | Imagens |
|-----|---:|
| ENANTEMA + EROSÃO | 34 |
| ÚLCERA + EROSÃO | 21 |
| ENANTEMA + ÚLCERA | 13 |
| ENANTEMA + PÓLIPO | 4 |
| ENANTEMA + MICRONODULARIDADE | 4 |

**Interação artefato × patologia (top 5):**

| Combinação | Imagens |
|------------|---:|
| LUZ + EROSÃO | 87 |
| LUZ + ENANTEMA | 43 |
| SALIVA + EROSÃO | 31 |
| SALIVA + ENANTEMA | 20 |
| SALIVA + ÚLCERA | 12 |

87 das 320 imagens de EROSÃO (27 %) também apresentam reflexo de luz; 31 (10 %) têm saliva. Quantificar o viés introduzido por artefatos é uma trilha experimental clara.

---

## C. Critérios de triagem (V3)

**Decisão automática** ([refine_literature_v3.py](../../scripts/refine_literature_v3.py)). Cada registro é classificado pelo título, abstract (quando disponível, eventualmente recuperado via NCBI/Crossref), keywords e venue:

- **Incluído:** (a) endoscopia alta **e** componente de visão computacional/DL; **ou** (b) achado do trato GI alto **e** visão computacional; **ou** (c) endoscopia **e** contribuição metodológica útil (multilabel, desbalanceamento, artefatos, explicabilidade); **ou** (d) registro recuperado por *string forte* (operador booleano da própria base já restringe a endoscopia alta + IA + NOT colorretal) sem sinais negativos no título.
- **Excluído:** fora do escopo evidente — colonoscopia pura, outro domínio de imagem médica (MRI, fundus, chest X-ray), NLP sem imagem, ou tema alheio (remote sensing, agricultura).
- **Revisão manual:** títulos sem informação ou ruído (índices de PDFs, abstracts de congressos sem DL, etc.).

**Decisão manual herdada (V1).** As 35 decisões individuais tomadas na V1 (12 incluídos, 23 excluídos) são aplicadas automaticamente quando a chave BibTeX bate. Veja [manual_triage.csv](../../scripts/manual_triage.csv).

**Decisão manual nova (V3).** As 30 decisões adicionais tomadas em 2026-05-18 (2 incluídos, 28 excluídos) são aplicadas pelo próprio `refine_literature_v3.py` quando o DOI bate. Veja [manual_triage_v3.csv](../../scripts/manual_triage_v3.csv). Decisões V3 têm precedência sobre V1 e sobre a heurística automática — ordem: `manual_v3 → manual_v1 → heurística`.

**Enriquecimento de abstracts.**

- **PubMed (PMID → abstract).** `efetch.fcgi` em batches de 150 PMIDs, ~3 req/s. Recupera abstract estruturado e keywords. 325/325 PMIDs processados.
- **Crossref (DOI → abstract).** `api.crossref.org/works/{DOI}`, mailto polite. 527 DOIs sem abstract no export foram consultados — taxa de sucesso ≈ 60 % (capítulos Springer raramente têm abstract no Crossref).
- **Cache.** [_abstract_cache.json](_abstract_cache.json) persiste resultados; reexecução do pipeline não dispara novas requisições.

---

## D. Resultado por base e string (V3)

| Base | String | Reg.doc | Brutos | Inc. | Exc. | Dup. | Manual | Abs.% |
|------|--------|---:|---:|---:|---:|---:|---:|---:|
| IEEE | S1 — Principal IA/DL endoscopia alta | 61 | 61 | 42 | 3 | 16 | 0 | 100 % |
| IEEE | S2 — DL/CNN específico | 25 | 25 | 0 | 0 | 25 | 0 | 100 % |
| IEEE | S3 — Lesões/alterações gástricas | 25 | 25 | 7 | 0 | 18 | 0 | 100 % |
| IEEE | S4 — Pólipos gástricos | 8 | 8 | 6 | 0 | 2 | 0 | 100 % |
| IEEE | S5 — IA endoscopia BR/LatAm | 18 | 18 | 7 | 11 | 0 | 0 | 100 % |
| IEEE | S6 — Dataset BR/LatAm | 9 | 9 | 0 | 0 | 9 | 0 | 100 % |
| **IEEE** | **TOTAL** | **146** | **146** | **62** | **14** | **70** | **0** | — |
| Scopus | S1 — Principal | 109 | 109 | 100 | 0 | 9 | 0 | 99 % |
| Scopus | S2 — Lesões gástricas | 294 | 294 | 289 | 1 | 4 | 0 | 92 % |
| Scopus | S3 — Pólipos gástricos | 60 | 60 | 34 | 1 | 25 | 0 | 98 % |
| Scopus | S4 — IA BR/LatAm | 8 | 8 | 3 | 5 | 0 | 0 | 100 % |
| Scopus | S5 — Dataset BR/LatAm | 1 | 1 | 0 | 0 | 1 | 0 | 100 % |
| **Scopus** | **TOTAL** | **472** | **472** | **426** | **7** | **39** | **0** | — |
| WoS | S1 — Principal | 200 | 200 | 99 | 4 | 97 | 0 | 99 % |
| WoS | S2 — Lesões gástricas | 144 | 144 | 52 | 3 | 89 | 0 | 97 % |
| WoS | S3 — Pólipos gástricos | 20 | 20 | 5 | 0 | 15 | 0 | 100 % |
| WoS | S4 — IA BR/LatAm | 4 | 4 | 1 | 2 | 1 | 0 | 100 % |
| WoS | S5 — Dataset BR/LatAm | 1 | 1 | 0 | 0 | 1 | 0 | 100 % |
| WoS | S6 — Datasets gástricos | 17 | 17 | 9 | 0 | 8 | 0 | 100 % |
| **WoS** | **TOTAL** | **386** | **386** | **166** | **9** | **211** | **0** | — |
| PubMed | S2 — DL/CNN específico | 122 | 122 | 74 | 0 | 48 | 0 | 99 % |
| PubMed | S3 — Lesões e pólipos gástricos | 193 | 193 | 150 | 0 | 43 | 0 | 96 % |
| PubMed | S5 — Datasets gástricos | 10 | 10 | 9 | 0 | 1 | 0 | 100 % |
| **PubMed** | **TOTAL** | **325** | **325** | **233** | **0** | **92** | **0** | — |
| ScienceDirect | SD1 — gastroscopia + DL/CNN | 62 | 62 | 44 | 1 | 17 | 0 | 84 % |
| ScienceDirect | SD2 — gastroscopia + ML/IA | 63 | 63 | 9 | 0 | 54 | 0 | 83 % |
| ScienceDirect | SD3 — upper GI + DL/CNN | 83 | 83 | 61 | 3 | 19 | 0 | 59 % |
| ScienceDirect | SD4 — upper GI + ML/IA | 98 | 98 | 28 | 0 | 70 | 0 | 65 % |
| ScienceDirect | SD5 — Lesões gástricas | 50 | 50 | 23 | 0 | 27 | 0 | 78 % |
| ScienceDirect | SD6 — Pólipos gástricos | 14 | 14 | 5 | 0 | 9 | 0 | 93 % |
| ScienceDirect | SD8 — Datasets gástricos | 43 | 43 | 22 | 6 | 15 | 0 | 98 % |
| ScienceDirect | SD9 — Brasil | 24 | 24 | 3 | 12 | 9 | 0 | 38 % |
| ScienceDirect | SD10 — América Latina | 17 | 17 | 4 | 10 | 3 | 0 | 53 % |
| **ScienceDirect** | **TOTAL** | **454** | **454** | **199** | **32** | **223** | **0** | — |
| Springer | S1 — Principal | 96 | 96 | 75 | 4 | 17 | 0 | 18 % |
| Springer | S2 — Lesões gástricas | 253 | 253 | 192 | 3 | 58 | 0 | 21 % |
| Springer | S3 — Pólipos gástricos | 12 | 12 | 4 | 0 | 8 | 0 | 42 % |
| Springer | S4 — Brasil/LatAm | 23 | 23 | 0 | 8 | 15 | 0 | 13 % |
| Springer | S5 — Datasets gástricos | 5 | 5 | 1 | 0 | 4 | 0 | 0 % |
| **Springer** | **TOTAL** | **389** | **389** | **269** | **15** | **105** | **0** | — |
| Scopus (VLM/FMs) | S1 — FMs/VLMs conceitual | 151 | 151 | 137 | 14 | 0 | 0 | 98 % |
| Scopus (VLM/FMs) | S2 — Modelos nomeados | 68 | 68 | 24 | 10 | 34 | 0 | 100 % |
| Scopus (VLM/FMs) | S3 — Comerciais multimodais | 160 | 160 | 118 | 12 | 30 | 0 | 91 % |
| **Scopus (VLM/FMs)** | **TOTAL** | **379** | **379** | **279** | **36** | **64** | **0** | — |
| **CONSOLIDADO** | **7 fontes** | **2 551** | **2 551** | **1 621** | **113** | **817** | **0** | **81 %** |

**Notas.**

1. **Bases que mais contribuíram com inclusões únicas** (após dedup): Scopus 426, Scopus VLM/FMs 279, Springer 269, PubMed 229, ScienceDirect 197, WoS 161, IEEE 60. A inclusão de PubMed e Springer foi decisiva — juntos somam ~500 incluídos. A etapa S6-VLM-FMs acrescentou **279 artigos novos** focados em foundation models e vision-language models, o tema de maior crescimento recente na área.
2. **Strings de Brasil/LatAm (S4/S5 das três bases originais + SD9/SD10 + Springer S4) somam ~14 inclusões, das quais apenas 3 mencionam afiliação brasileira efetiva** (ver seção F.1). A literatura brasileira em gastroscopia + DL é muito esparsa — confirma a brecha original.
3. **Springer S2 contribuiu com 192 incluídos** (a maior contribuição isolada de qualquer string anterior) — boa parte do efeito de ampliação do corpus vem dessa string ampla cobrindo achados gástricos.
4. **PubMed S3 + S5** trouxeram ~158 inclusões — muito dessa massa é de revisões clínicas e estudos de validação que Scopus/WoS já tinham, mas PubMed agrega trabalhos de revistas clínicas asiáticas pouco indexadas em outras bases.
5. **S6-VLM-FMs S1 (conceitual) contribuiu com 137 incluídos sem duplicatas internas (0 dup)** — indica que a String 1 captura artigos genuinamente novos não cobertos pelas strings anteriores. S2 (modelos nomeados) tem alta taxa de duplicação com S1 (34/68 = 50 %), esperado pois artigos sobre Endo-FM ou LLaVA-Med são um subconjunto. S3 (comerciais) contribui com 118 incluídos, com sobreposição moderada (30 dup).
6. **Taxa de exclusão em S6-VLM-FMs (36/379 = 9,5 %)** é comparável às strings Scopus originais, confirmando que as strings foram bem construídas. Os excluídos são: artigos de endoscopia nasofaríngea/skull base (4, triados manualmente), LLMs em NLP puro sem componente visual/endoscópico, e 1 proceedings editorial.

---

## E. Panorama dos artigos incluídos

**Distribuição temporal dos 1 621 incluídos.**

| Ano | n |
|---:|---:|
| ≤ 2014 | 40 |
| 2015 | 13 |
| 2016 | 11 |
| 2017 | 12 |
| 2018 | 26 |
| 2019 | 64 |
| 2020 | 94 |
| 2021 | 162 |
| 2022 | 163 |
| 2023 | 209 |
| 2024 | 260 |
| 2025 | 334 |
| 2026 | 232 (parcial) |

A produção entre 2021 e 2025 representa ≈ 70 % do corpus (1 128/1 621). O **salto de 2024 (260) e 2025 (334)** reflete o boom de Foundation Models — boa parte dos novos incluídos vem da etapa S6-VLM-FMs e concentra-se nesses anos. O valor alto em 2026 (232) mesmo com coleta parcial (até maio) confirma a aceleração.

**Top 15 venues após canonização (abreviações unidas com forma completa):**

| Venue | n |
|-------|---:|
| Gastrointestinal Endoscopy | 99 |
| Scientific Reports | 38 |
| Digestive Endoscopy | 36 |
| Endoscopy | 35 |
| Gastroenterology | 35 |
| Surgical Endoscopy | 34 |
| World Journal of Gastroenterology | 33 |
| Lecture Notes in Computer Science | 31 |
| Computers in Biology and Medicine | 27 |
| Biomedical Signal Processing and Control | 25 |
| Digestive and Liver Disease | 23 |
| Diagnostics | 20 |
| Medical Image Analysis | 16 |
| Gastric Cancer | 16 |
| BMC Gastroenterology | 15 |

A presença de **Medical Image Analysis** (16), **Computers in Biology and Medicine** (27) e **Lecture Notes in Computer Science** (31) — os dois primeiros A1/A2 em Engenharias IV — sustenta os alvos de publicação A2/A1 das trilhas T4, T7 e T8. O crescimento de LNCS reflete a proliferação de papers de FMs/VLMs em conferências MICCAI e CVPR.

**Temas recorrentes nos 1 621 incluídos** (ocorrência em título/venue):

| Tema | n |
|------|---:|
| Câncer gástrico | 267 |
| Detecção | 253 |
| Esôfago / Barrett / SCC | 239 |
| NEOPLASIA / displasia / EGC (early gastric cancer) | 157 |
| Classificação | 149 |
| Segmentação | 109 |
| Cápsula endoscópica | 84 |
| **Foundation model / VLM** | **74** |
| Pólipo | 64 |
| Tempo real | 58 |
| *H. pylori* | 47 |
| Úlcera | 43 |
| Atenção (mecanismos) | 35 |
| Dataset / benchmark | 32 |
| Metaplasia intestinal | 29 |
| Hemorragia / sangramento | 28 |
| Self-supervised learning | 21 |
| Atrofia gástrica | 20 |
| Anatomical landmarks | 17 |
| Doença celíaca | 15 |
| Vision Transformer | 11 |
| Data augmentation | 10 |
| GAN / aug. sintético | 10 |
| Transfer learning | 10 |
| Qualidade de imagem | 9 |
| Artefato (saliva/luz/blur) | 9 |
| Explicabilidade (Grad-CAM, XAI) | 8 |
| Few-shot | 5 |
| Desbalanceamento (no título) | 4 |
| Calibração / incerteza | 4 |
| Multilabel | 2 |
| Brasil / LatAm | 2 |
| Domain adaptation | 2 |

**Mudança crítica com S6-VLM-FMs: "Foundation model / VLM" saltou de 4 → 74**, passando de tema residual para o **8º mais recorrente** no corpus. Isso confirma que FMs/VLMs em endoscopia são um campo em rápida expansão (quase todos os 74 artigos são de 2023–2026) e justifica uma discussão dedicada na tese. A diferença entre **câncer gástrico (267)**, **detecção (253)** de um lado, e **multilabel (2)**, **desbalanceamento (4)**, **artefato (9)**, **explicabilidade (8)** de outro, continua sendo o mapa de brechas.

---

## F. Brechas da literatura

As brechas F1–F10 herdadas da V1 permanecem **válidas e reforçadas** pela ampliação do corpus. A passagem de 1 358 → 1 621 incluídos (com S6-VLM-FMs) **não diluiu** a baixa cobertura dos temas-alvo da tese — ao contrário, o ganho massivo é concentrado em Foundation Models / VLMs (4 → 74), enquanto multilabel permanece em 2, explicabilidade em 8, artefato em 9. Isso confirma que ampliar a busca trouxe mais artigos das **temáticas dominantes e emergentes**, mas não das brechas específicas da tese.

**Nota sobre Foundation Models / VLMs (F5 atualizada).** Com 74 artigos agora mapeados, FMs/VLMs **deixam de ser brecha no sentido estrito** (poucos trabalhos) e passam a ser **território em expansão rápida** que a tese precisa dialogar, não preencher. A brecha F5 é agora refinada: não é que "não existem trabalhos com FMs em endoscopia" — existem muitos — mas **nenhum dos 74 aplica FMs/VLMs em tarefa multilabel com dataset brasileiro, classes raras extremas (n=4) e artefatos como rótulos**. A contribuição da tese em T6 migra de "explorar FMs pela primeira vez em endoscopia" para "avaliar se FMs (DINOv2, BiomedCLIP) melhoram a classificação multilabel em cenário brasileiro com desbalanceamento extremo" — posicionamento mais forte e defensável.

1. **Datasets brasileiros públicos de endoscopia digestiva alta praticamente não existem.** Nas sete fontes consultadas (incluindo agora PubMed, Springer e Scopus-VLM-FMs), apenas **3 dos 1 621 incluídos** mencionam afiliação ou contexto brasileiro detectável — e nenhum deles publica dataset aberto. A comunidade brasileira continua representada por pouquíssimos trabalhos. O dataset da tese (1 990 imagens, 11 rótulos multilabel) é inédito no recorte brasileiro.
2. **Quase nenhuma formulação explicitamente multilabel em gastroscopia.** Apenas **2/1 621** menções a "multilabel" em título. A literatura trata os achados como tarefas binárias sequenciais ou multiclasses mutuamente exclusivas — não captura os 1 064 casos (53 % do dataset) em que ≥ 2 rótulos coexistem na mesma imagem. Mesmo os 74 artigos novos de VLMs não abordam multilabel explícito.
3. **Análise quantitativa de co-ocorrência de achados é rara.** Nenhum dos 1 621 incluídos apresenta matriz de co-ocorrência clínica usada como prior arquitetônico ou regularizador. No dataset há pares clinicamente ricos (ENANTEMA+EROSÃO = 34, ÚLCERA+EROSÃO = 21) com fenótipo distinto do par isolado.
4. **Artefatos de imagem como rótulos treináveis ainda não são prática.** O corpus trata SALIVA/LUZ/blur como ruído a remover via pré-processamento (9 trabalhos com termo "artefato" no título; 9 com "qualidade de imagem"; total continua baixo mesmo com 1 621 artigos). No dataset da tese, 87 das 320 imagens de EROSÃO (27 %) contêm reflexo de luz — risco real de o modelo aprender o reflexo como *shortcut* para a classe.
5. **Comparação sistemática CNN × Vision Transformer × Foundation Model em gastroscopia multilabel é escassa.** Agora existem **11 trabalhos com Transformer no título** e **74 com FMs/VLMs**, mas nenhum os compara sistematicamente contra ResNet/EfficientNet/DenseNet em tarefa multilabel com classes raras em imagens gástricas. Os 74 artigos de FMs/VLMs focam predominantemente em: detecção/classificação binária, geração de relatórios, VQA, ou segmentação — não em multilabel com desbalanceamento extremo.
6. **Desbalanceamento extremo em classes raras recebe atenção pontual.** Apenas 4 títulos mencionam "imbalance" e 5 "few-shot" no corpus ampliado. No dataset, NEOPLASIA e ECTASIA VASCULAR têm 4 imagens cada (IR > 200) — cenário que nem focal loss simples resolve.
7. **Explicabilidade clínica sistemática ainda falta.** Apenas 8 títulos mencionam Grad-CAM/XAI explicitamente; e nenhum estudo no corpus combina Grad-CAM por rótulo em cabeças multilabel, validação por endoscopistas e análise comparativa entre arquiteturas (CNN vs. ViT vs. Swin). Os artigos de VLMs geram explicações textuais mas sem validação inter-avaliador.
8. **Generalização geográfica (OOD) é assumida, não medida.** Apenas **2/1 621** trabalhos mencionam "domain adaptation" ou "cross-domain". Modelos treinados em Kvasir/HyperKvasir reportam > 95 % em teste, sem avaliar desempenho em datasets latino-americanos. Publicar o dataset brasileiro é condição necessária para medir esse viés.
9. **Protocolos reproduzíveis de curadoria e anotação são raros.** Dos **32 datasets explicitamente mapeados** (label "dataset/benchmark" no título), poucos disponibilizam datasheet ou protocolo de rotulagem multilabel. O dataset da tese já tem 12 duplicatas, 498 linhas órfãs e 1 145 *missing* em ECTASIA VASCULAR — um relato metodológico honesto dessas decisões já é contribuição.
10. **Qualidade de imagem como *gate* pré-classificador está pouco formalizado.** Há trabalhos de *real-time quality control* (58 com termo "tempo real" + 9 com "qualidade de imagem"), mas raramente alimentam um classificador de patologia a jusante. Uma pipeline de duas etapas (quality → classification) com avaliação de impacto ainda é espaço aberto.

---

## G. Narrativa da tese (o que há de inédito)

A pergunta de fundo permanece:

> **Como construir um classificador de imagens de endoscopia digestiva alta, em cenário brasileiro, em que os achados coexistem numa mesma imagem, as classes raras têm 4 exemplos e os artefatos de aquisição (saliva, reflexo de luz) são tão frequentes quanto as próprias patologias?**

Quatro pontos são inéditos no corpus de **1 621 artigos** (incluindo 74 de FMs/VLMs) e costuram as trilhas das seções H e L:

1. **Dataset brasileiro público multilabel em gastroscopia** — inexistente entre os 1 621; é insumo das demais contribuições e pré-requisito para discussão de viés regional em deploy no Brasil.
2. **Rotulagem explícita de artefatos (saliva, luz) como classes** — apenas 2 artigos usam "multilabel" no título e nenhum trata artefatos como rótulos treináveis em endoscopia digestiva alta; tratá-los como classe (e não ruído) é o deslocamento conceitual central da tese. Os 74 artigos de VLMs também não abordam artefatos como classes.
3. **Protocolo honesto para classes raras extremas** — NEOPLASIA e ECTASIA VASCULAR têm 4 imagens cada (IR > 200); nenhum dos trabalhos que mencionam *imbalance* ou *few-shot* no corpus reporta resultados nessa faixa e discute o que é razoável prometer.
4. **Explicabilidade por rótulo em multilabel, validada por endoscopistas** — o corpus usa Grad-CAM do *top-1*; os VLMs geram texto explicativo mas sem validação inter-avaliador em cenário multilabel; nenhum trabalho valida mapas por classe em multilabel com concordância inter-avaliador.

Essas quatro contribuições são a **ambição de longo prazo** (alvo A2 / A1). A estratégia realista é começar pelas trilhas mais simples (A4/A3) que já entregam pedaços inéditos dessa agenda.

---

## H. Trilhas de publicação T1–T9 (preservadas de V1)

### Como ler esta seção

**Trilha = linha de investigação ligada a uma brecha da seção F.** Uma mesma trilha pode render **mais de um artigo** — tipicamente (i) curto em evento Qualis A4 com resultado inicial, (ii) completo em periódico (A3/A2) e, quando houver colaboração clínica madura, (iii) extensão validada em periódico A2/A1. Estratos Qualis referem-se à área Engenharias IV / Ciência da Computação (CAPES 2017–2020) como referência; podem variar por área avaliadora e ciclo vigente.

Estratégia: **volume rápido em A4** nas primeiras trilhas para fixar prioridade do dataset e gerar publicações cedo, deixando as trilhas de maior risco/ambição para quando houver massa crítica de resultados e colaborações clínicas.

As trilhas são marcadas como **(prioritária)** ou **(estratégica)** — as prioritárias devem ser encaradas primeiro; as estratégicas são extensões ou oportunidades paralelas.

### H.0 Núcleo comum experimental

Todas as trilhas partem de uma **versão congelada** do dataset brasileiro (1 990 imagens · 11 rótulos binários: NORMAL, ALTERADO, SALIVA, LUZ, ENANTEMA, PÓLIPO, ÚLCERA, EROSÃO, MICRONODULARIDADE, ECTASIA VASCULAR, NEOPLASIA). O núcleo abaixo é compartilhado — cada trilha só descreve o que *difere* dele.

**Pré-processamento comum.**

- Redimensionamento para 224×224 (baselines leves) ou 384×384 (ViT / Swin / ConvNeXt).
- Normalização com estatísticas do ImageNet (e, em T6, também com estatísticas do próprio dataset para comparação).
- Remoção ou marcação das 12 duplicatas identificadas em [dataset_stats.json](dataset_stats.json).
- Tratamento explícito de valores ausentes (especialmente em ECTASIA VASCULAR: 1 145 *missing*).
- Conversão `1/2 → 1/0`.
- Separação dos rótulos em três grupos: **clínicos** (ENANTEMA, PÓLIPO, ÚLCERA, EROSÃO, MICRONODULARIDADE, ECTASIA VASCULAR, NEOPLASIA), **artefatos** (SALIVA, LUZ) e **auxiliares** (NORMAL, ALTERADO).

**Estratégia de divisão.**

- **Iterative stratification multilabel** para preservar distribuição de rótulos.
- Split treino/validação/teste (ex.: 70/15/15) ou validação cruzada estratificada.
- Múltiplas sementes (≥ 3) para reporte com desvio-padrão.
- Protocolo específico para classes com n = 4 (NEOPLASIA, ECTASIA VASCULAR): *leave-one-case-out*.

**Baselines multilabel comuns.** ResNet50 · DenseNet121 · EfficientNet-B0/B3 · MobileNetV3 · ConvNeXt-Tiny · ViT-B/16 · Swin-T. Perda base: **BCEWithLogitsLoss**.

**Métricas comuns.** F1-macro, F1-micro, F1 por classe, sensibilidade e especificidade por classe, PR-AUC por classe, ROC-AUC por classe, balanced accuracy, matriz de co-ocorrência de erros, calibração (ECE, Brier score), intervalos de confiança por *bootstrap*.

**Ferramental visual compartilhado.** Grad-CAM, Grad-CAM++, Score-CAM, Eigen-CAM, Attention rollout (ViT/Swin), Integrated Gradients. Ferramental verbal (T7): BiomedCLIP, PubMedCLIP, LLaVA-Med.

---

### T1 — Dataset brasileiro e baseline multilabel · **(prioritária)**

- **Brecha:** F1 (dataset BR inexistente) + F9 (protocolos de curadoria raros).
- **Pergunta:** como construir, documentar e avaliar um dataset brasileiro multilabel de endoscopia digestiva alta para classificação automática de achados clínicos e artefatos?
- **Inédito:** primeira base brasileira pública com rotulagem multilabel incluindo artefatos; documentação completa de 12 duplicatas, 498 linhas órfãs, 1 145 *missing* em ECTASIA VASCULAR, 407 imagens "alteradas sem achado".
- **Modelos candidatos.**
  - Baselines leves: ResNet18, MobileNetV3, EfficientNet-B0.
  - Baselines principais: ResNet50, DenseNet121, EfficientNet-B3, ConvNeXt-Tiny.
  - Avançados: ViT-B/16, Swin-T, DINOv2 com *fine-tuning*.
- **Metodologia.** (i) Curar o dataset; (ii) documentar duplicatas, linhas órfãs e inconsistências; (iii) datasheet no modelo de Gebru et al.; (iv) definir splits oficiais; (v) treinar baselines multilabel; (vi) publicar tabelas de prevalência, co-ocorrência e desbalanceamento.
- **Métricas específicas.** F1-macro, F1 por classe, PR-AUC por classe, sensibilidade por classe, n. parâmetros, tempo de inferência.
- **Contribuição.** Dataset brasileiro documentado e baseline inicial para classificação multilabel em gastroscopia.
- **Artigos possíveis.**
  - **P1.1 (evento A4):** relato curto + datasheet + baseline ResNet50, em *SIBGRAPI*, *CBMS* ou *BRACIS*.
  - **P1.2 (A3):** *data descriptor* completo em *Scientific Data* ou *Data in Brief* com dois backbones e estatística detalhada.

---

### T2 — Artefatos (saliva, luz) como classes e *shortcut learning* · **(prioritária)**

- **Brecha:** F4 — artefatos são quase sempre pré-processados, nunca rotulados.
- **Pergunta:** modelos aprendem achados clínicos reais ou usam artefatos visuais (saliva, reflexo de luz) como atalhos? Os dados mostram 87 imagens LUZ+EROSÃO e 31 SALIVA+EROSÃO, o que justifica a investigação.
- **Inédito:** nenhum dos 1 621 artigos (incluindo 74 de VLMs/FMs) rotula artefato como classe treinável em gastroscopia; é o deslocamento conceitual central da tese.
- **Modelos candidatos.**
  - CNNs: ResNet50, DenseNet121, EfficientNet-B0/B3, ConvNeXt-Tiny.
  - Multitask: uma cabeça para patologias e outra para artefatos, sobre EfficientNet e ConvNeXt.
  - Debiasing: DANN (Domain-Adversarial Neural Network), *gradient reversal layer*.
- **Metodologia.** Quatro regimes comparados:
  1. **Pathology-only** — baseline com rótulos clínicos apenas.
  2. **Artefatos como classes multilabel** — SALIVA e LUZ entram no vetor de rótulos.
  3. **Multitask** — cabeças separadas para patologia e artefato.
  4. **Debiasing adversarial** — pressionar o encoder a não codificar artefato.
- **Métricas específicas.** F1 por patologia; **falso positivo de EROSÃO em imagens com LUZ**; falso positivo de EROSÃO em imagens com SALIVA; sensibilidade de patologias com e sem artefato; calibração estratificada; Grad-CAM nos erros.
- **Contribuição.** Mostrar se artefatos funcionam como atalhos e propor estratégia para reduzir o viés.
- **Artigos possíveis.**
  - **P2.1 (evento A4):** 1–2 modelos + evidência visual do *shortcut*.
  - **P2.2 (A3/A2):** estudo ampliado com 3–4 backbones, *debiasing* adversarial e análise de calibração. Alvos: *Computerized Medical Imaging and Graphics*, *Computers in Biology and Medicine*.

---

### T3 — Modelagem multilabel relacional com co-ocorrência clínica · **(estratégica)**

- **Brecha:** F2 + F3.
- **Pergunta:** incorporar relações clínicas entre rótulos (ENANTEMA+EROSÃO = 34, ÚLCERA+EROSÃO = 21, ENANTEMA+ÚLCERA = 13) melhora a classificação multilabel de achados gástricos?
- **Inédito:** 3/1 358 artigos usam "multilabel" no título; nenhum usa co-ocorrência clínica como prior arquitetônico em gastroscopia.
- **Modelos candidatos.**
  - Baselines independentes: ResNet50 + BCE; EfficientNet-B0 + BCE; DenseNet121 + BCE.
  - Modelos relacionais: **classifier chains**, **label embeddings**, **GCN sobre grafo de rótulos**, **graph attention network**, perda com regularização de co-ocorrência.
  - Backbones: ResNet50, EfficientNet-B3, ConvNeXt-Tiny, Swin-T.
- **Metodologia.** (i) Construir matriz de co-ocorrência; (ii) construir grafo clínico de achados; (iii) comparar cabeças independentes × classifier chains × label graph + GCN × loss com penalização de combinações improváveis; (iv) avaliar em rótulos isolados, pares frequentes e imagens com múltiplos achados.
- **Métricas específicas.** F1 por classe, F1 em imagens com ≥ 2 rótulos, F1 em pares específicos, **Hamming loss**, *subset accuracy*, *ranking loss*, PR-AUC por rótulo.
- **Contribuição.** Formulação que aproveita relações clínicas reais entre achados, em vez de tratar cada rótulo como independente.
- **Artigos possíveis.**
  - **P3.1 (evento A4):** análise preliminar de co-ocorrência com UMAP e matriz estratificada.
  - **P3.2 (A2):** estudo metodológico com 3–4 backbones × 4 formulações relacionais. Alvos: *Computers in Biology and Medicine*, *Expert Systems with Applications*.

---

### T4 — Classes raras, incerteza e decisão segura · **(prioritária)**

- **Brecha:** F6 — NEOPLASIA e ECTASIA VASCULAR com 4 imagens cada (IR > 200).
- **Pergunta:** como lidar com classes extremamente raras em classificação multilabel de endoscopia quando há poucos exemplos, reformulando o problema como *segurança* e *incerteza* em vez de maximização de acurácia?
- **Inédito:** literatura trata *imbalance* e *few-shot* separadamente (2/1 358 artigos cada); ninguém combina em gastroscopia multilabel com *abstention* e *conformal prediction*, nem reporta honestamente para n = 4.
- **Modelos candidatos.**
  - Baselines: ResNet50, EfficientNet-B0, DenseNet121.
  - Estratégias para classes raras: **Focal Loss**, **Asymmetric Loss (ASL)**, Class-balanced loss, *oversampling*, **WeightedRandomSampler**, Mixup direcionado.
  - Few-shot / incerteza: **Prototypical Networks**, anomaly detection, **conformal prediction**, **selective classification** (modelo com opção de abstenção).
- **Metodologia.** Protocolo *leave-one-case-out* para classes n=4. Comparar:
  1. BCE padrão.
  2. BCE com pesos por classe.
  3. Focal Loss.
  4. Asymmetric Loss.
  5. Oversampling com Mixup restrito à classe rara.
  6. Modelo com **opção de abstenção** (*selective classification*).
  7. Detecção de anomalia para classes raras.
- **Métricas específicas.** Sensibilidade por classe rara, PR-AUC por classe rara, intervalo de confiança por *bootstrap*, **taxa de abstenção**, erro quando o modelo é obrigado a decidir vs. quando pode encaminhar para revisão humana, calibração.
- **Contribuição.** Reformular classes raras como problema de segurança, incerteza e suporte à decisão, não apenas de acurácia.
- **Artigos possíveis.**
  - **P4.1 (evento A4):** baseline + ASL, discussão honesta do limite.
  - **P4.2 (A2):** estudo completo com pré-treino auto-supervisionado (ganchando em T6), *selective classification* e discussão ética de *deploy* antes de reanotação. Alvos: *Artificial Intelligence in Medicine*, *Computers in Biology and Medicine*.

---

### T5 — Ruído de rótulo, *missing labels* e aprendizado robusto · **(prioritária)**

- **Brecha:** F9 — problemas reais de curadoria (12 duplicatas, 498 linhas órfãs, 17 imagens sem rótulo, 1 145 *missing* em ECTASIA VASCULAR, 407 "alteradas sem achado").
- **Pergunta:** como treinar modelos multilabel em datasets clínicos com rótulos ausentes, inconsistentes ou parcialmente anotados, tratando isso como problema metodológico e não como defeito a esconder?
- **Inédito:** o corpus praticamente ignora a existência de anotação imperfeita; transformar as inconsistências documentadas em contribuição metodológica é novo no recorte gastroscopia BR.
- **Modelos candidatos.**
  - Baselines: ResNet50, EfficientNet-B0, DenseNet121.
  - Estratégias robustas: **label smoothing**, **positive-unlabeled (PU) learning**, **partial label learning**, **generalized cross entropy**, **bootstrapping loss**, **co-teaching**, **semi-supervised learning**, **pseudo-labeling**, *noisy label detection*.
- **Metodologia.** (i) Identificar padrões de inconsistência no CSV; (ii) separar rótulos confiáveis, ausentes e suspeitos; (iii) comparar treinamento ingênuo × remoção de ambíguos × *missing* como "desconhecido" × PU learning × pseudo-labeling × co-teaching; (iv) avaliar impacto em performance e estabilidade.
- **Métricas específicas.** F1-macro, F1 por classe, **robustez entre seeds**, desempenho em subconjunto limpo × subconjunto ruidoso, taxa de rótulos suspeitos corretamente identificados.
- **Contribuição.** Transformar problemas reais de anotação clínica em contribuição metodológica de aprendizado robusto em dados médicos imperfeitos.
- **Artigos possíveis.**
  - **P5.1 (evento A4):** diagnóstico das inconsistências + baseline com *missing* como "unknown".
  - **P5.2 (A2):** comparação PU learning × pseudo-labeling × co-teaching. Alvos: *Artificial Intelligence in Medicine*, *Journal of Biomedical Informatics*.

---

### T6 — Pré-treino auto-supervisionado e modelos fundacionais · **(estratégica → prioritária)**

- **Brecha:** F5 atualizada — agora existem 74 trabalhos de FMs/VLMs em endoscopia, mas nenhum os aplica em tarefa multilabel com dataset brasileiro e classes raras extremas (n=4). A auto-supervisão no domínio (21 menções a self-supervised) também permanece rara em cenário gastroscópico brasileiro.
- **Pergunta:** pré-treino auto-supervisionado ou modelos fundacionais (DINOv2, BiomedCLIP, Endo-FM) melhoram a classificação multilabel em gastroscopia brasileira com poucos dados e desbalanceamento extremo?
- **Inédito:** dos 74 artigos de FMs/VLMs mapeados, nenhum combina BiomedCLIP/DINOv2/Endo-FM com tarefa multilabel em dataset BR com classes raras. O posicionamento passa de "explorar FMs pela primeira vez" para "avaliar se FMs ajudam especificamente no cenário multilabel brasileiro com desbalanceamento" — mais forte e defensável.
- **Modelos candidatos.**
  - Supervisionados tradicionais: ResNet50 ImageNet, EfficientNet-B0 ImageNet, DenseNet121 ImageNet, ConvNeXt-Tiny ImageNet.
  - Auto-supervisionados: **SimCLR**, **MoCo-v3**, **DINO**, **DINOv2**, **MAE**.
  - Fundacionais / visão-linguagem: **BiomedCLIP**, **PubMedCLIP**, **CLIP**, **MedCLIP**.
- **Metodologia.** Comparar:
  1. ImageNet supervised pretraining.
  2. Auto-supervised pretraining no próprio dataset.
  3. Auto-supervised em dataset externo de endoscopia (HyperKvasir, Kvasir-Gastro).
  4. *Fine-tuning* completo vs. *linear probing* vs. *frozen encoder* + classificador multilabel.
  5. VLMs como extratores de embeddings.
- **Métricas específicas.** F1-macro, PR-AUC macro, **desempenho em classes raras**, desempenho com poucos dados (curvas de aprendizado), estabilidade entre seeds, qualidade dos embeddings via UMAP/t-SNE.
- **Contribuição.** Avaliar se modelos fundacionais/auto-supervisionados realmente ajudam em cenário local, pequeno, multilabel e desbalanceado.
- **Artigos possíveis.**
  - **P6.1 (A2):** estudo comparativo pré-treino ImageNet × DINOv2 × BiomedCLIP em 3 backbones. Alvos: *Computers in Biology and Medicine*, *Expert Systems with Applications*.

---

### T7 — Explicabilidade por rótulo com auditoria clínica · **(prioritária)**

- **Brecha:** F7 — Grad-CAM pontual (8/1 358 títulos), sem validação clínica em multilabel.
- **Pergunta:** mapas de explicabilidade por rótulo em modelos multilabel de gastroscopia são clinicamente coerentes segundo especialistas, e a coerência depende da arquitetura? O dataset já foi rotulado por médicos; nesta trilha eles passam a **avaliar** a saída da IA (não re-anotar).
- **Inédito:**
  - Grad-CAM no corpus é sempre do *top-1*; ninguém gera mapas **por classe** em multilabel.
  - Nenhum artigo combina mapa visual + descrição verbal (VLM) com avaliação inter-avaliador em gastroscopia.
  - Endoscopistas como **avaliadores** da saída (não re-anotadores) — papel pouco explorado e que reduz carga clínica.
- **Modelos candidatos.**
  - CNNs: ResNet50, DenseNet121, EfficientNet-B3, ConvNeXt-Tiny.
  - Transformers: ViT-B/16, Swin-T.
  - Métodos de explicabilidade visual: **Grad-CAM**, **Grad-CAM++**, **Score-CAM**, **Eigen-CAM**, **Integrated Gradients**, **Attention rollout**, *occlusion sensitivity*.
  - Explicabilidade verbal (extensão A1): **BiomedCLIP**, **LLaVA-Med** — geração de descrição curta em português das predições.
- **Metodologia.** (i) Treinar modelo multilabel; (ii) gerar explicações **separadas para cada rótulo ativo** (não só o *top-1*); (iii) comparar mapas entre arquiteturas; (iv) selecionar subconjunto de imagens (n ≈ 150–200) para avaliação médica; (v) 2+ endoscopistas avaliam: (a) se o mapa aponta para região clinicamente relevante, (b) se aponta para artefato, (c) se a explicação é compatível com o rótulo; (vi) medir concordância inter-avaliador.
- **Métricas específicas.** Concordância inter-avaliador (**κ-Cohen**), percentual de mapas clinicamente plausíveis, *pointing game*, IoU com marcação clínica (se disponível), **taxa de explicações que focam em artefatos** (diagnóstico de *shortcut*).
- **Contribuição.** Sair do Grad-CAM genérico do *top-1* e propor explicabilidade por rótulo em cenário multilabel com avaliação clínica — opcionalmente combinando explicação visual e verbal (VLM).
- **Artigos possíveis.**
  - **P7.1 (evento A4):** Grad-CAM multilabel preliminar em 2 backbones, avaliação informal com 1 endoscopista.
  - **P7.2 (A2):** estudo **visual-only** completo (4 tipos de mapa × 4 arquiteturas) com κ-Cohen multi-rater. Alvos: *Artificial Intelligence in Medicine*, *Computers in Biology and Medicine*.
  - **P7.3 (A1, extensão):** estudo **visual + VLM (BiomedCLIP / LLaVA-Med) + validação multi-rater**. Alvos: *Medical Image Analysis*, *IEEE TMI*. Candidato ao artigo de fechamento da tese.

---

### T8 — Generalização geográfica e viés regional · **(estratégica)**

- **Brecha:** F8 — 22 datasets gástricos no corpus, quase todos asiáticos; nenhum estudo usa dados latino-americanos como **fonte** para testar modelos asiáticos. Apenas 5 títulos mencionam *domain adaptation*.
- **Pergunta:** modelos treinados em datasets internacionais de endoscopia generalizam para imagens brasileiras, e vice-versa?
- **Inédito:** uso do dataset brasileiro como **fonte** de avaliação de modelos asiáticos, e não só como mais um alvo.
- **Modelos candidatos.** ResNet50, EfficientNet-B0, DenseNet121, ConvNeXt-Tiny, Swin-T, DINOv2, BiomedCLIP.
- **Metodologia.** (i) Selecionar dataset público internacional comparável (HyperKvasir, Kvasir-Gastro, GastroVision); (ii) treinar no internacional, testar no BR; (iii) treinar no BR, testar no internacional; (iv) *fine-tuning* cruzado; (v) medir queda por domínio.
- **Métricas específicas.** F1-macro intra-domínio, F1-macro cross-domain, **queda percentual** de desempenho, calibração por domínio, análise de distribuição de embeddings, distância entre domínios (**FID**, **MMD**).
- **Contribuição.** Quantificar viés geográfico e mostrar a importância de datasets brasileiros para avaliação realista de IA médica no país.
- **Artigos possíveis.**
  - **P8.1 (A2/A1):** estudo cross-dataset completo com recomendações de *deploy*. Alvos: *Medical Image Analysis*, *IEEE TMI* (A1) ou *Journal of Biomedical Informatics* (A2).

---

### T9 — *Active learning* para reanotação médica eficiente · **(estratégica)**

- **Brecha:** F9 — ausência de protocolos *human-in-the-loop* no corpus, mesmo com datasets imperfeitos como o da tese.
- **Pergunta:** como selecionar imagens prioritárias para revisão médica em um dataset multilabel de endoscopia com rótulos ausentes, raros e inconsistentes?
- **Inédito:** nenhum artigo do corpus propõe protocolo *active learning* para reanotação em gastroscopia multilabel brasileira; endoscopistas reanotam apenas o que o modelo indica ser mais incerto ou conflitante.
- **Modelos candidatos.** ResNet50, EfficientNet-B0, ConvNeXt-Tiny, **ensembles de CNNs**, **Monte Carlo Dropout**, **deep ensembles**, modelos bayesianos simples.
- **Metodologia.** Comparar estratégias de seleção:
  1. Amostragem aleatória (baseline).
  2. Maior incerteza (entropia preditiva).
  3. Maior desacordo entre modelos (*query-by-committee*).
  4. Maior probabilidade de erro de rótulo (*label noise detection*).
  5. Diversidade no espaço de embeddings (*core-set*).
  6. Prioridade para classes raras.
  7. Prioridade para imagens com conflito NORMAL/ALTERADO (407 casos candidatos).
- **Métricas específicas.** Ganho de F1 após reanotação, **número de imagens necessárias** para melhorar o modelo, redução de inconsistências, ganho em classes raras, esforço médico estimado (minutos por lote), curva custo-benefício.
- **Contribuição.** Protocolo *human-in-the-loop* para melhorar datasets médicos sem exigir reanotação completa — aplicável a outros grupos brasileiros.
- **Artigos possíveis.**
  - **P9.1 (A2):** comparação de 3–4 estratégias de seleção com métricas de eficiência. Alvos: *Artificial Intelligence in Medicine*, *Journal of Biomedical Informatics*.

---

### Tabela resumida T1–T9

| Trilha | Prior. | Modelos principais | Metodologia central | Métricas principais |
|--------|:---:|--------------------|---------------------|---------------------|
| T1 Dataset + baseline | ★ | ResNet50, EfficientNet-B0, DenseNet121 | Datasheet + splits oficiais + baseline multilabel | F1-macro, PR-AUC, F1/classe |
| T2 Artefatos/shortcut | ★ | ResNet50, EfficientNet, ConvNeXt, DANN | Patologia-only × multitask × debiasing | FP por artefato, F1, calibração |
| T3 Multilabel relacional | ○ | EfficientNet, Swin, GCN, classifier chains | Grafo de rótulos e co-ocorrência | Hamming loss, F1 por par, PR-AUC |
| T4 Classes raras | ★ | ResNet50, EfficientNet, Prototypical Nets | ASL, few-shot, abstention, incerteza | Sensibilidade, PR-AUC, abstention |
| T5 Rótulo ruidoso | ★ | ResNet50, EfficientNet, co-teaching | PU learning, pseudo-labeling, partial label | F1, robustez, erro por ruído |
| T6 Auto-supervisionado + FMs | ★ | DINOv2, BiomedCLIP, Endo-FM, MAE | Pré-treino no domínio + *fine-tuning* multilabel | F1-macro, PR-AUC, estabilidade |
| T7 Explicabilidade | ★ | ResNet, EfficientNet, ViT, Swin + VLM | Grad-CAM por rótulo + avaliação médica | κ-Cohen, plausibilidade clínica |
| T8 Viés regional | ○ | EfficientNet, Swin, DINOv2 | Treino/teste cruzado entre datasets | Queda cross-domain, calibração |
| T9 *Active learning* | ○ | Ensembles, MC Dropout | Seleção de imagens para reanotação | Ganho de F1, esforço médico |

★ = prioritária · ○ = estratégica

---

## I. Artigos incluídos, excluídos e duplicatas

- **Incluídos (1 621):** lista completa em [artigos_incluidos.csv](artigos_incluidos.csv) com base, string, título, autores, ano, DOI, venue, motivo da inclusão, origens (onde o artigo também foi encontrado) e flag *tem_abstract*. Os 279 incluídos de Scopus (VLM/FMs) aparecem com `base = "Scopus (VLM/FMs)"`.
- **Excluídos (113):** [artigos_excluidos.csv](artigos_excluidos.csv). Motivos predominantes: foco em colonoscopia/colorretal; índices/agregados editoriais; outros domínios anatômicos; estudo clínico-epidemiológico sem IA; NLP/remote sensing; falsos positivos da string Springer S4 sobre "Brasil/LatAm"; e **novos em S6-VLM-FMs (36 excluídos)** — endoscopia nasofaríngea/skull base (4 triados manualmente), LLMs aplicados a NLP puro sem componente visual/endoscópico, e 1 proceedings editorial (BioNLP workshop).
- **Duplicatas (817):** [duplicatas_identificadas.csv](duplicatas_identificadas.csv). Marcadas quando o mesmo DOI ou título normalizado aparece em mais de uma S ou base. O ganho de duplicatas (737 → 817, +80) reflete sobreposição entre as strings S6-VLM-FMs (especialmente S2 que é subconjunto temático de S1) e com strings anteriores do Scopus S1–S5 para papers mais antigos que mencionam fundamentos de DL.
- **Revisão manual (0):** fila totalmente zerada. Os 30 itens pré-S6 + 5 itens da etapa S6-VLM-FMs foram todos triados via [manual_triage_v3.csv](../../scripts/manual_triage_v3.csv) e ajuste de heurística (4 nasopharyng excluídos por DOI, 1 proceedings excluído por TITLE_NEGATIVE_TERMS).

---

## J. Limitações da triagem e pontos de atenção

1. **Heurística léxica + confiança em strings.** A decisão automática usa título + abstract (quando disponível) + keywords. Para registros sem abstract de strings *fortes* (operador booleano da própria base já filtra endoscopia alta + IA + NOT colorretal), a inclusão é feita por confiança na string, com motivo declarado em `screening_log.csv`. Isso é PRISMA-coerente, mas o pesquisador deve revisar por amostragem caso queira maior rigor.
2. **Cobertura de abstracts.** 78 % dos registros têm abstract após enriquecimento. Os 22 % sem abstract concentram-se em capítulos Springer e atas/proceedings — são justamente os tipos de publicação onde Crossref raramente entrega o resumo. Para análise de tópicos via embedding, considere filtrar por `tem_abstract=sim` em [artigos_incluidos.csv](artigos_incluidos.csv).
3. **Divergência Scopus S2 (295 documentado vs. 294 efetivo) — investigada.** O arquivo `.bib` do export Scopus contém **282 `@ARTICLE` + 12 `@CONFERENCE` = 294 entradas** parseáveis (verificado por contagem de `@TIPO\{` no arquivo bruto). A documentação da string indica 295; a diferença de 1 entrada é provavelmente artefato do export Scopus (linha perdida no download), **não duplicata**. As 294 entradas efetivas são todas processadas, classificadas e contabilizadas pelo pipeline V3 — a cobertura real é portanto 294/295, ou 99,7 %. Recomenda-se reexportar a string para confirmar, mas o impacto numérico é desprezível.
4. **Dataset com inconsistências reais.** Ver seção B: 498 linhas do CSV órfãs, 17 imagens sem rótulo, 12 `image_name` duplicados, 1 145 valores *missing* em ECTASIA VASCULAR e 407 imagens marcadas como ALTERADO sem nenhuma patologia específica. Essas questões devem ser endereçadas e documentadas no data descriptor da Trilha 1.
5. **Apenas 3 sinais brasileiros inequívocos no corpus de 1 358.** Mesmo após adicionar PubMed e Springer com strings BR/LatAm específicas, a presença brasileira em IA + endoscopia digestiva alta é mínima. O dataset da tese é, portanto, contribuição rara em escala nacional.
6. **Strings PubMed começam em S2 (intencional).** Conforme indicação do usuário, PubMed nesta revisão começa em S2 — não há S1. As strings ativas são S2 (DL/CNN focado, 122 registros), S3 (lesões e pólipos, 193) e S5 (datasets, 10). S4 (Brasil/LatAm) retornou 0 registros segundo o PDF de detalhes e foi corretamente omitida. Cobertura PubMed = 325 brutos, 233 incluídos.

---

## K. Entregáveis

```
E:/Doutorado-V2/Revisão-Literatura-refinada-V3/
├── IEEE/{S1..S6}/{artigos_refinados.bib, screening_log.csv}
├── Scopus/{S1..S5}/{artigos_refinados.bib, screening_log.csv}
├── Scopus-VLM-FMs/{S1,S2,S3}/{artigos_refinados.bib, screening_log.csv}  ← NOVO
├── Web-of-Science/{S1..S6}/{artigos_refinados.bib, screening_log.csv}
├── Pub-Med/{S2,S3,S5}/{artigos_refinados.bib, screening_log.csv}
├── ScienceDirect/{S1..S6,S8..S10}/{artigos_refinados.bib, screening_log.csv}
├── Springer-Nature-Link/{S1..S5}/{artigos_refinados.bib, screening_log.csv}
└── consolidado/
    ├── todos_artigos_refinados_sem_duplicatas.bib
    ├── artigos_incluidos.csv               (1 621)
    ├── artigos_excluidos.csv                (113)
    ├── artigos_duvida_revisao_manual.csv       (0, fila zerada)
    ├── duplicatas_identificadas.csv          (817)
    ├── resumo_por_base_string.csv
    ├── dataset_stats.json
    ├── dataset_cooccurrence.csv
    ├── _summary.json                         (totais e por_base_string)
    ├── _analytics_v3.json                    (anos, venues, temas, brasileiros)
    ├── _abstract_cache.json                  (cache NCBI + Crossref)
    └── relatorio_revisao_literatura.md       (este arquivo)

E:/Doutorado-V2/Revisão-Literatura/
├── ...bases anteriores...
└── Scopus-VLM-FMs/{S1,S2,S3}/*.bib          ← NOVO (dados brutos de entrada)

E:/Doutorado-V2/Revisão-Literatura-refinada-V3/Scopus/S6-VLM-FMs/
├── S1.bib, S2.bib, S3.bib                   ← exports originais do Scopus
├── Detalhe-String-de-Busca.pdf               ← documentação das strings
└── Detalhe-String-de-Busca.docx

E:/Doutorado-V2/scripts/
├── refine_literature.py          — pipeline V1 (3 bases, intacto)
├── refine_literature_v3.py       — pipeline V3 (7 fontes + enriquecimento + manual triages V1+V3)
├── analyze_dataset.py            — estatísticas do dataset BR
├── analyze_literature_v3.py      — estatísticas descritivas V3
├── apply_manual_triage.py        — aplica decisões manuais V1
├── manual_triage.csv             — decisões manuais V1 (chave bibtex, 35 registros)
└── manual_triage_v3.csv          — decisões manuais V3 (chave DOI, 30 registros)
```

Os scripts são idempotentes: podem ser reexecutados após adicionar novas strings ou atualizar o dataset, e o relatório é regenerável a partir dos artefatos em `consolidado/`. O cache de abstracts evita re-chamadas a NCBI/Crossref.

---

## L. Atualizações pós-V3 — refinamentos das trilhas e novas oportunidades

A ampliação para 1 358 incluídos **confirma e fortalece** as trilhas T1–T9. Esta seção registra:

- **L.1** Refinamentos de T1–T9 motivados por achados específicos das três bases novas.
- **L.2** Três trilhas adicionais (T10, T11, T12) que emergem como inéditas após a inclusão de PubMed/SD/Springer.
- **L.3** Cronograma atualizado.

### L.1 Refinamentos das trilhas existentes

**Refinamento de T1 (Dataset).** A inclusão de PubMed expôs que **32 datasets gástricos** estão mapeados no corpus (ganho com S6-VLM-FMs que traz datasets usados por modelos fundacionais: GastroNet-5M, EndoViT, EndoFM pretraining data). Antes de submeter, baixar e tabular os datasets já existentes (Kvasir-Gastro, GastroVision, GastroNet-5M, HyperKvasir, EndoFM pretraining data) é pré-requisito para o *data descriptor* posicionar o dataset BR como **complementar** (origem, espectro de classes, resolução, modalidade NBI vs. WLI), não competitivo.

**Refinamento de T2 (Artefatos).** ScienceDirect contribuiu com vários trabalhos de *quality control* em endoscopia (frame informativo, blur detection) — usar esses como baselines de filtragem é mais robusto do que criar um filtro novo. Novo gancho experimental: comparar (i) artefato como classe vs. (ii) *quality gate* + classificador, em pipeline duas-etapas.

**Refinamento de T3 (Multilabel relacional).** Springer S2 trouxe trabalhos com label-graph para imagens médicas em outros domínios (chest X-ray multi-pathology, dermatologia). Esses não são endoscopia mas ancoram metodologicamente o GCN/classifier chains com referências fora do nicho — útil na revisão de fundamentação do P3.2.

**Refinamento de T4 (Classes raras).** PubMed S2 trouxe *eNCApsulate* (cellular automata para precisão diagnóstica em capsule endoscopy) e trabalhos de *protruding lesion detection* em capsule — modalidade próxima e com problema similar de classes muito raras. Vale citar como ancoragem mesmo sendo capsule (intestino delgado), com cuidado para não confundir o leitor sobre o foco em endoscopia digestiva alta.

**Refinamento de T6 (Modelos fundacionais).** A etapa S6-VLM-FMs trouxe **74 artigos** mapeados ao tema "foundation model / VLM" — salto de 4 → 74. Isso **eleva T6 de estratégica a prioritária**: o campo está em rápida expansão, e a tese precisa se posicionar frente a essa literatura. O posicionamento correto não é mais "explorar FMs pela primeira vez em endoscopia" (já há 74 fazendo isso), mas **"avaliar se FMs (DINOv2, BiomedCLIP, Endo-FM) melhoram a classificação multilabel em cenário brasileiro com desbalanceamento extremo"**. Nenhum dos 74 faz exatamente isso. Modelos-chave identificados: Endo-FM, EndoViT, BiomedCLIP, LLaVA-Med, Med-Flamingo, Med-Gemini, GPT-4V, MedSAM. Recomenda-se incluir ao menos DINOv2/BiomedCLIP/Endo-FM nos baselines de T1 e T4.

**Refinamento de T7 (Explicabilidade).** Apenas 8 títulos com Grad-CAM/XAI nas 7 fontes — ou seja, mesmo com o corpus expandido para 1 621, a brecha permanece quase tão grande quanto na V1. Os artigos de VLMs geram explicações textuais (LLaVA-Med, GPT-4V reports) mas sem validação inter-avaliador em cenário multilabel. **Reforça que P7.2 (A2) e P7.3 (A1) são as apostas mais defensáveis para alvos de topo**, porque o espaço de comparação é muito vazio. P7.3 pode agora incorporar VLMs (LLaVA-Med) como geradores de explicação verbal complementar ao Grad-CAM visual.

**Refinamento de T8 (Viés regional).** Springer S4 e SD9/SD10 mostram que existem **alguns trabalhos asiáticos com indianos/sudeste-asiáticos como público-alvo**, mas o uso *cross-continent* (treinar na Ásia, testar na América do Sul) ainda não foi feito. Reforça a relevância de P8.1 como contribuição metodológica.

### L.2 Trilhas adicionais (T10, T11, T12)

#### T10 — Gate de qualidade de imagem como pré-classificador · **(estratégica)**

- **Brecha:** F10 — 57 trabalhos com "tempo real" e 8 com "qualidade de imagem", mas raramente alimentando classificador de patologia a jusante.
- **Pergunta:** uma pipeline em duas etapas (quality gate → classifier) reduz erros do classificador e melhora calibração em comparação com classificador monolítico?
- **Inédito:** combinação explícita de *frame informativeness* + classificação multilabel de patologia em gastroscopia, com avaliação de impacto no F1 e calibração.
- **Modelos candidatos.**
  - Quality gate: ResNet18/MobileNetV3 binário (informativo vs. não-informativo); pode ser supervisionado pelos próprios artefatos (LUZ/SALIVA do dataset BR + frames "lavar/inserir/retirar" de HyperKvasir).
  - Classifier: ResNet50/EfficientNet-B3/Swin-T multilabel.
- **Metodologia.** (i) Treinar gate em HyperKvasir (frame quality) + dataset BR; (ii) avaliar 3 regimes — sem gate, gate filtra, gate como feature concatenada; (iii) reportar quanto cai a taxa de falsos positivos nas patologias quando frames ruins são removidos.
- **Métricas específicas.** F1 estratificado por qualidade de frame, **redução de FP por classe**, calibração antes/depois do gate, taxa de descarte do gate (fração de frames removidos).
- **Contribuição.** Mostrar que separar qualidade da classificação melhora calibração e reduz FP — gancho prático para deploy.
- **Artigos possíveis.** P10.1 (A2): *Computers in Biology and Medicine*, *Biomedical Signal Processing and Control*.

#### T11 — Extensão para vídeo / temporal · **(estratégica, longa)**

- **Brecha:** os 1 358 incluídos têm 57 menções a "tempo real" mas a esmagadora maioria opera **frame a frame**. A consistência temporal entre frames adjacentes (quando o endoscopista permanece sobre a mesma lesão) é um sinal explorável.
- **Pergunta:** consistência temporal entre frames vizinhos pode ser usada como sinal fraco para reduzir flicker de predição multilabel em vídeo de gastroscopia?
- **Inédito:** tese tem dataset de imagens, não vídeos — mas o protocolo de *test-time temporal smoothing* (mediana móvel sobre logits, *self-distillation* entre frames) pode ser proposto e validado em conjuntos públicos (HyperKvasir tem vídeos), abrindo extensão futura quando o grupo conseguir capturar vídeos brasileiros.
- **Inviável imediatamente** sem coleta de vídeos no Brasil; entra como **trilha futura** que justifica continuidade pós-defesa.
- **Artigos possíveis.** P11.1 (A2/A1) — após coleta de vídeos. Alvos: *Medical Image Analysis*, *IEEE TMI*.

#### T12 — Avaliação clínica utilitarista (decisão suportada) · **(estratégica, alta colaboração clínica)**

- **Brecha:** o corpus (mesmo com 1 358 artigos) raramente avalia o sistema **integrado ao fluxo clínico** — a maioria reporta F1 em teste isolado. Apenas dois trabalhos no corpus mencionam "decision support system" no título.
- **Pergunta:** quando o classificador funciona como sistema de apoio à decisão (não substituto), em que medida ele reduz tempo de exame, aumenta detecção de achados raros (ECTASIA, NEOPLASIA) e como endoscopistas calibram sua confiança nas predições?
- **Inédito:** estudo prospectivo (mesmo pequeno) com endoscopistas usando vs. não usando o sistema, em dataset BR. Cruza com T7 (explicabilidade auditada).
- **Inviável sem aprovação ética e parceria hospitalar formal.** Entra como **trilha de fechamento da tese** com horizonte longo.
- **Artigos possíveis.** P12.1 (A1) — *Lancet Digital Health*, *npj Digital Medicine*. Único alvo plausível para Lancet/npj na agenda.

### L.3 Cronograma atualizado

A V3 não muda o cronograma de V1 — ela **reforça** a viabilidade do bloco prioritário e adiciona horizontes longos:

- **Ano 1 (2026).** P1.1 + P2.1 + P5.1 (três A4) — ainda viáveis e agora mais bem posicionados em relação ao estado da arte expandido.
- **Ano 2 (2027).** P1.2 + P2.2 + P4.1 + P7.1 (mistura A4/A3/A2).
- **Ano 3 (2028).** P4.2 + P5.2 + P7.2 + P3.2 ou P6.1 (todas A2).
- **Pós-defesa / extensão.** P7.3, P8.1, P9.1, **P10.1** (novo, A2), P11.1 e P12.1 (futuras com infraestrutura adicional).

**Capacidade total de publicação.** Com T1–T9 + T10 (e T11/T12 como horizonte): **até ~16 oportunidades de artigos**, distribuídos em A4 (~4), A3 (~2), A2 (~7), A1 (~3). Conservador: assumir que ~70 % se concretizam — ainda dá uma trajetória robusta.

---

## M. Como reproduzir / atualizar o V3

```bash
# 1) (re)executar pipeline — idempotente; usa cache de abstracts
cd E:/Doutorado-V2
python scripts/refine_literature_v3.py

# 2) regerar análise descritiva (anos, venues, temas)
python scripts/analyze_literature_v3.py

# 3) (opcional) regenerar estatísticas do dataset BR
python scripts/analyze_dataset.py
```

Para adicionar uma nova string ou base:

1. Coloque os exports em `Revisão-Literatura/<Base>/<Sx>/`.
2. Acrescente entrada em `BASES` no topo de `refine_literature_v3.py` (com título, objetivo, n esperado).
3. Se a string tem filtro restritivo (endoscopia + IA + NOT colon), adicione-a em `STRONG_STRINGS`.
4. Se necessário, adicione termos específicos em `CV_TERMS` para melhorar a classificação.
5. Reexecute `refine_literature_v3.py` — o cache de abstracts é reaproveitado para registros já vistos e enriquecimento só ocorre para os novos.
6. Reexecute `analyze_literature_v3.py`.

**Exemplo realizado: S6-VLM-FMs (2026-05-20).** Exports do Scopus foram colocados em `Revisão-Literatura/Scopus-VLM-FMs/{S1,S2,S3}/`, a base `Scopus-VLM-FMs` foi adicionada a `BASES`, termos VLM foram incluídos em `CV_TERMS`, e as 3 strings foram marcadas como `STRONG_STRINGS`. O pipeline integrou 379 novos registros ao corpus existente de forma incremental.

---

**Resumo executivo (uma página).** A V3 + S6-VLM-FMs amplia o corpus de 717 → 1 358 → **1 621 incluídos** ao adicionar PubMed, ScienceDirect, Springer Nature Link e uma etapa complementar sobre Foundation Models / Vision-Language Models (379 registros brutos, 279 incluídos). A fila de revisão manual está **totalmente zerada** (35 itens V1 + 30 itens V3 + 5 itens S6-VLM-FMs, todos triados). **Totais finais: 1 621 incluídos / 113 excluídos / 817 duplicatas / 0 manual_review.**

A principal mudança qualitativa é o salto de "Foundation model / VLM" de 4 → **74 artigos** no corpus, tornando-se o 8º tema mais recorrente. Isso atualiza a brecha F5: FMs/VLMs em endoscopia **não são mais escassos** — mas nenhum dos 74 aplica FMs a tarefa multilabel com dataset brasileiro, classes raras extremas (n=4) e artefatos como rótulos. A trilha T6 é **elevada a prioritária** e reposicionada.

As **brechas F1–F10** e as **trilhas T1–T9** seguem válidas — a expansão **reforçou** os números a favor da originalidade da tese: multilabel permanece em 2/1 621, explicabilidade em 8/1 621, artefato como classe em 0/1 621, e artigos brasileiros em endoscopia + DL permanecem minúsculos (3 inequívocos). A V3 mantém **T10 (quality gate), T11 (vídeo) e T12 (decisão clínica suportada)** como horizontes complementares.

O dataset brasileiro de 1 990 imagens × 11 rótulos multilabel **continua sendo o ativo central e inédito da tese**, e o corpus PRISMA-coerente de 1 621 artigos é insumo direto para um futuro **artigo de revisão sistemática** sobre IA em endoscopia digestiva alta.
