#!/usr/bin/env python
"""
Generate per grant X PI rows of csv with subset of grant info in pickle from
previous script
"""
import pickle
import polars as pl
import re

def extract_pi(pi: dict) -> str:
    """
    principal_investigators element to strings
    """
    return(str(pi.get("profile_id", "")) + ":" + pi.get("full_name", ""))

def contact_pi(pi_array) -> str:
    """
    get contact from principal_investigators
    """
    for pi in pi_array:
        return extract_pi(pi)
    return ""

def read_all():
    with open('2024.pkl', 'rb') as pkl:
        fy2024 = pickle.load(pkl)
    return fy2024


def main():
    fy2024 = read_all()
    keep = ['project_num','award_type','budget_start','budget_end','direct_cost_amt','indirect_cost_amt','project_start_date','project_end_date', 'award_amount', ]
    per_pi = []
    for grant in fy2024:
        pis_dict = grant['principal_investigators']
        n = len(pis_dict)
        contact = contact_pi(pis_dict)
        pis = [extract_pi(pi) for pi in pis_dict]
        ginfo = {k:v for k,v in grant.items() if k in keep}
        # unnest and add org
        ginfo['org'] = grant.get('organization',{}).get('org_name', '')
        ginfo['web_id'] = re.sub('.*/','',grant.get('project_detail_url',''))
        for pi in pis:
            pi_row = {"pi": pi, 'contact_pi': contact, **ginfo}
            per_pi.extend([pi_row])
    d = pl.DataFrame(per_pi)
    d.write_csv("FY2024_PI-repeat.csv")
    return d

if __name__ == "__main__":
    d = main()
