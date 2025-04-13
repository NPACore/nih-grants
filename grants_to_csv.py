#!/usr/bin/env python
"""
Generate per grant X PI rows of csv with subset of grant info in pickle from
previous script
"""
import glob
import logging
import os
import pickle
import re
import polars as pl
import sys
import gzip

logging.basicConfig(
    level=os.getenv("LOGLEVEL", "DEBUG").upper(),
)
log = logging.getLogger("grants2csv")


def extract_pi(pi: dict) -> str:
    """
    principal_investigators element to strings
    """
    return str(pi.get("profile_id", "")) + ":" + pi.get("full_name", "")


def contact_pi(pi_array) -> str:
    """
    get contact from principal_investigators
    """
    for pi in pi_array:
        return extract_pi(pi)
    return ""


def read_all(pkl_fname="2024.pkl"):
    """read a pickle file. likley from get_grants.py"""
    with open(pkl_fname, "rb") as pkl:
        data = pickle.load(pkl)
    return data


def reshape_grant(grant: dict, data_source="") -> list[dict]:
    """
    subset grant information and reshape into long format
    row per PI instead of row per grant
    :param grant: dict, row of
    :param data_source: provenance information to add (e.g. year)
    :return: row for each PI
    """

    # columns to hold onto
    keep = [
        "project_num",
        "award_type",
        "budget_start",
        "budget_end",
        "direct_cost_amt",
        "indirect_cost_amt",
        "project_start_date",
        "project_end_date",
        "award_amount",
        "funding_mechanism",
    ]
    pi_rows = []
    pis_dict = grant["principal_investigators"]
    n = len(pis_dict)
    contact = contact_pi(pis_dict)
    pis = [extract_pi(pi) for pi in pis_dict]
    ginfo = {k: v for k, v in grant.items() if k in keep}
    # unnest and add org
    ginfo["org"] = grant.get("organization", {}).get("org_name", "")
    ginfo["study_code"] = grant.get("full_study_section", {}).get("srg_code", "")
    ginfo["web_id"] = re.sub(".*/", "", grant.get("project_detail_url", ""))
    ginfo["pklsrc"] = data_source
    for pi in pis:
        pi_row = {"pi": pi, "contact_pi": contact, **ginfo}
        pi_rows.append(pi_row)

    return pi_rows


def main():
    per_pi = []
    files = glob.glob("data/*pkl")
    for pkl_fname in files:
        pkl_data = read_all(pkl_fname)
        for grant in pkl_data:
            pi_rows = reshape_grant(grant, pkl_fname)
            per_pi.extend(pi_rows)
        log.debug("after '%s', total rows %d %.2f Mb", pkl_fname, len(per_pi), sys.getsizeof(per_pi)/1024**2)
    d = pl.DataFrame(per_pi)

    years = [re.search(r"\d{4}", x).group(0) for x in files]
    years = f"{min(years)}:{max(years)}"
    outname = f"grants_PI-repeat_FY-{years}.csv"
    d.write_csv(outname)
    os.system("gzip '{outname}'")
    outname = outname + ".gz"
    log.debug("wrote '%s'", outname)
    return d


if __name__ == "__main__":
    d = main()
