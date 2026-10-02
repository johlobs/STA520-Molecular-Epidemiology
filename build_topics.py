# build_topics.py
# Quarto pre-render script. Scans lecture*.qmd for topic headings and writes
# _topics-data.html, a <script> that defines window.STA520_TOPICS.
# The dashboard, the sidebar counters and the glossary links all read from it.
#
# Topic heading format (level 2 only):
#   ## 7.4 Observed variation = biology + noise {#t7-4 .topic flag="instructor"}
#   ## 3.6 Mendelian genetics vocabulary {#t3-6 .topic flag="inferred"}
#   ## 5.1 Data structures {#t5-1 .topic}
#
# Flags: instructor (EXAM slide), professor (on the professor's word/concept
# list), professor_unsure (on the list, marked "uncertain about use"),
# keyconcept (on Martin's key-concepts list for GWAS/MR/proteomics),
# inferred (AI-inferred), unclear (GWAS/MR theory not in the computer
# exercises), seminar (seminar content; can also come on the written exam),
# example (running example, not exam focus).

import glob
import json
import os
import re

HEADING = re.compile(r'^## (.+?)\s*\{#(\S+)\s+\.topic(?:\s+flag="(instructor|professor|professor_unsure|keyconcept|inferred|unclear|seminar|example)")?\s*\}\s*$')

here = os.path.dirname(os.path.abspath(__file__))
topics = []

files = sorted(glob.glob(os.path.join(here, "lecture*.qmd")),
               key=lambda f: int(re.search(r"lecture(\d+)", f).group(1)))

# Cross-lecture pages get a group number after the lectures and a short label.
EXTRA_PAGES = [("key-concepts.qmd", 10, "KC"), ("seminar-questions.qmd", 11, "Sem")]

pages = [(path, int(re.search(r"lecture(\d+)", path).group(1)), None) for path in files]
pages += [(os.path.join(here, name), num, label) for name, num, label in EXTRA_PAGES
          if os.path.exists(os.path.join(here, name))]

for path, lecture, label in pages:
    page = os.path.basename(path).replace(".qmd", ".html")
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            m = HEADING.match(line.rstrip("\n"))
            if m:
                topics.append({
                    "id": m.group(2),
                    "title": m.group(1),
                    "lecture": lecture,
                    "label": label or f"L{lecture}",
                    "page": page,
                    "flag": m.group(3) or None,
                })

out = os.path.join(here, "_topics-data.html")
with open(out, "w", encoding="utf-8") as fh:
    fh.write("<script>\nwindow.STA520_TOPICS = ")
    fh.write(json.dumps(topics, ensure_ascii=False, indent=1))
    fh.write(";\n</script>\n")

print(f"build_topics.py: {len(topics)} topics from {len(pages)} pages")
