#!/usr/bin/env -S uv run --script
# /// script
# dependencies = [ "scholarly", "polars" ]
# ///
from scholarly import scholarly
import polars as pl
import numpy as np
from time import sleep
import re

# dont need org!? use email instead
def org_stem(org:str) -> str:
    """
    Turn NIH organization value into scholar searchable stem
    >>> org_stem("UNIVERSITY OF ALABAMA AT BIRMINGHAM")
    ALABAMA AT BIRMINGHAM
    >>> org_stem("2MORROW, INC")
    2MORROW
    >>> org_stem("UNIVERSITY OF CALIFORNIA-IRVINE")
    CALIFORNIA-IRVINE
    """
    rm_punc = re.sub('[,.]', ' ', org)
    rm_words = re.sub('UNIVERSITY|[^-0-9A-Za-z ]|of|at|LLC$|INC$', '',
                      rm_punc, flags=re.IGNORECASE)
    return re.sub(' +',' ',rm_words).strip()

def pi_stem(pi: str) -> str:
    rm_id = re.sub('.*:', '', pi)
    dedup_white = re.sub('  +', ' ', rm_id).strip()
    # TODO: consider removing middle name?
    names = dedup_white.split(' ')
    fl=names[-1]
    if fl != names[0]:
        fl=names[0] + " " + names[-1]
    return  fl


## format as fullname, institution
def pi_org_search_str(d: pl.DataFrame) -> list[str]:
    pi_org = [(pi_stem(x[0]), org_stem(x[1]))
              for x in d[:,['pi','org']].iter_rows()
              if x[1]]
    # cobmine psuedo-'stemmed' terms
    all_pis = [f"{pi_stem(pi)}, {org_stem(org)}"
               for (pi,org) in pi_org
               if pi]
    all_pis = np.unique(all_pis)
    return all_pis.tolist()

def scholar_lookup(pi) -> dict:
    search_query = scholarly.search_author(pi)
    try:
        print(f"# search '{pi}'")
        author = next(search_query)
    except StopIteration:
        print(f"# no results for '{pi}'")
        return {}

    author = scholarly.fill(author)
    # TODO: send all columns
    # interst: where in author list, number of pubs
    a_keep = ['scholar_id','name','email_domain',
              'hindex', 'i10index',
              'hindex5y','i10index5y',
              'affiliation']
    a_info =  {k: author[k] for k in a_keep}
    a_info.update({
        'total_cites': sum(author['cites_per_year']),
        'total_pubs': len(author['publications']),
        'query': pi})
    return a_info

def collect_searches(searches :list[str], wait=2) -> pl.DataFrame:
    """
    collect scholar_lookup outputs into a dataframe
    :param searches: list of queries
    :param wait: time to wait between searches (seconds)
    :return: dataframe with columns matching keys from py:func:`scholar_lookup`
    """
    authors = []
    for query in searches:
        if a_info := scholar_lookup(query):
            authors.append(a_info)
            sleep(wait)
    return(pl.DataFrame(authors))

def search_by_pi_org():
    """
    search scholar by first+last+organizaton
    2 in first 6 gets a hit
    """
    d_all = pl.read_csv("./grants_PI-repeat_FY-2001:2025.csv.gz",
                        ignore_errors=True)

    d = d_all.filter(d_all['pklsrc'] == 'data/2024.pkl')
    all_pis = pi_org_search_str(d)
    res_name = collect_searches(all_pis[0:5])
    return res_name


def search_by_email():
    """
    search by 2022 email.
    2 of first 6 gets a hit (when email is lastname@institution)
    """
    mail = pl.read_csv("email/contactpi_emails_all.csv.gz")
    no_at_mails = [x.replace('@',' ') for x in mail['email']]
    res_email = collect_searches(no_at_mails[0:5])
    return res_email

if __name__ == "__main__":
    print("Nothing to see here yet")
