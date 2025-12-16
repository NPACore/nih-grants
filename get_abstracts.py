#!/usr/bin/env python3
"""
Write abstract text to giant csv file
"""
import csv
import glob
import pickle
import re

with open('data/abstracts.csv', 'w') as out:
    writer = csv.writer(out, quoting=csv.QUOTE_MINIMAL)
    writer.writerow(['id', 'project', 'year', 'section', 'abstract'])

    for year in glob.glob('data/[12]*.pkl'):
        print(f"# {year}")
        with open(year, 'rb') as f:
            yeardata = pickle.load(f)

        for g in yeardata:
            row = [g['appl_id'],
                   g['project_num'],
                   g['fiscal_year'],
                   re.sub(r'\[.*\]', '',
                          g['full_study_section']['name'] or "no_section"),
                   g['abstract_text']]
            writer.writerow(row)


# inspecing counts for full name (includ srg and sra codes)
# s = {}
# for g in x:
#     n = (
#             (g['full_study_section']['srg_code'] or "no_srg") +
#             "\t" +
#             (g['full_study_section']['sra_designator_code'] or "no_sra") +
#             "\t" + (g['full_study_section']['name'] or "NONE"))
#     c = s.get(n, 0)
#     s[n] = c + 1
# with open('data/study_sections_2025.txt', 'w') as f:
#     for (c, s) in s.items():
#         f.write(f"{c}\t{s}\n")
