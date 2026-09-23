# build_topics.py
# Quarto pre-render script. Scans lecture*.qmd for topic headings and writes
# _topics-data.html, a <script> that defines window.STA520_TOPICS.
# The dashboard, the sidebar counters and the glossary links all read from it.
#
# Topic heading format (level 2 only):
#   ## 7.4 Observed variation = biology + noise {#t7-4 .topic flag="instructor"}
#   ## 3.6 Mendelian genetics vocabulary {#t3-6 .topic flag="inferred"}
#   ## 5.1 Data structures {#t5-1 .topic}

import glob
import json
import os
import re

HEADING = re.compile(r'^## (.+?)\s*\{#(\S+)\s+\.topic(?:\s+flag="(instructor|inferred)")?\s*\}\s*$')

here = os.path.dirname(os.path.abspath(__file__))
topics = []

files = sorted(glob.glob(os.path.join(here, "lecture*.qmd")),
               key=lambda f: int(re.search(r"lecture(\d+)", f).group(1)))

for path in files:
    lecture = int(re.search(r"lecture(\d+)", path).group(1))
    page = os.path.basename(path).replace(".qmd", ".html")
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            m = HEADING.match(line.rstrip("\n"))
            if m:
                topics.append({
                    "id": m.group(2),
                    "title": m.group(1),
                    "lecture": lecture,
                    "page": page,
                    "flag": m.group(3) or None,
                })

out = os.path.join(here, "_topics-data.html")
with open(out, "w", encoding="utf-8") as fh:
    fh.write("<script>\nwindow.STA520_TOPICS = ")
    fh.write(json.dumps(topics, ensure_ascii=False, indent=1))
    fh.write(";\n</script>\n")

print(f"build_topics.py: {len(topics)} topics from {len(files)} lecture files")
