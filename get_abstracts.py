#!/usr/bin/env python3
"""
Write abstract text to giant csv file
"""
import csv
import datetime
import glob
import pickle
import re

from read_grant import read_pkl


def study_abstract_info(g: dict):
    """
    Extract abstract and minimal metadata from grant info.

    Skip "Special Emphasis Panel"
    These have SRG (Scientific Review Group) that start with 'Z'.
    """
    srg = g["full_study_section"]["srg_code"]
    if not srg:
        return None

    section = re.sub(r"\[.*\]", "", g["full_study_section"]["name"] or "no_section")

    if srg[0] == "Z" or section == "Special Emphasis Panel":
        return None

    return [
        g["appl_id"],
        g["project_num"],
        g["fiscal_year"],
        srg,
        section,
        g["abstract_text"],
    ]


if __name__ == "__main__":
    with open("data/abstracts.csv", "w") as out:
        writer = csv.writer(out, quoting=csv.QUOTE_MINIMAL)
        colnames = ["id", "project", "year", "srg", "section", "abstract"]
        writer.writerow(colnames)

        for year in glob.glob("data/[12]*.pkl"):
            print(f"# {year} 0 {datetime.datetime.now()}")
            yeardata = read_pkl(year)

            cnt = 0
            for g in yeardata:
                row = study_abstract_info(g)
                if row is None:
                    continue
                writer.writerow(row)
                cnt = cnt + 1
            print(f"{year} {cnt} {datetime.datetime.now()}")

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
