# STA520 — Interactive Study App

## Project
Quarto + WebR study reference and exam-prep tracker for STA520 Molecular Epidemiology (Göteborg University, autumn 2026). Built with STA240's app as the template. Content source: `../sta520-study-app-guide_1.md`.

- **Source**: `C:/Users/nepet/Documents/Studier/Masterprogram i tillämpad biostatistik/STA520 Molecular Epidemiology/App/`
- **Stack**: Quarto website, knitr engine (every lecture page sets `engine: knitr`, otherwise pages without `{r}` chunks try Jupyter), WebR for `{webr-r}` cells, plain JS includes.

## Pages
- `lecture1.qmd` … `lecture8.qmd`: one page per lecture
- `dashboard.qmd`: progress per lecture, instructor-flagged rollup, to-do list, export/import/reset
- `exam-practice.qmd`: randomised calculation drills + written exam-style questions with model answers
- `glossary.qmd`: all terms with links to `lectureN.qmd#tN-M`
- `about.qmd`: sources, schedule, flag meaning, what is missing

## Topic sections (drive the checklist and dashboard)
Every checklist item is a level-2 heading in a lecture file:

```markdown
## 7.13 Benjamini–Hochberg: controlling the FDR {#t7-13 .topic flag="instructor"}
## 3.6 Mendelian genetics: vocabulary and laws {#t3-6 .topic flag="inferred"}
## 5.1 The data behind a single-SNP test {#t5-1 .topic}
```

- `flag="instructor"` only for slides that carried the literal "EXAM" marker (Lecture 7 only). Never use it for inferred relevance.
- `flag="inferred"` = AI-inferred exam relevance.
- `build_topics.py` (pre-render) scans these headings and writes `_topics-data.html` (`window.STA520_TOPICS`). Do not edit that file by hand.
- IDs must stay stable: status is stored per ID in localStorage key `sta520_topic_status`. Renaming an ID loses that topic's saved status.

## Includes (after body)
- `_topics-data.html` generated registry
- `_topics.html` status buttons, badges, sidebar counters, dashboard
- `_quiz.html` + `_quiz-filter.lua` quizzes (same format as STA240: `:::: {.quiz}`, bold = correct)
- `_drills.html` randomised drills: `<div class="drill" data-drill="NAME"></div>`, names: `bh, hwe, hwecount, or, logbeta, wald, ivw, log2fc, recomb, ld, qnorm, modt`

## Writing rules
- English content; define abbreviations on first use per page.
- Quiz options roughly equal length; the correct one must not stand out.
- Keep worked examples as tables.

## Render
```powershell
& "C:\Program Files\Quarto\bin\quarto.exe" render
```
Stop any local web server serving `_site` first (it locks the folder on Windows).
