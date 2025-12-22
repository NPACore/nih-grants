#!/usr/bin/env python3
"""
Convience functions
"""
import pickle

def read_pkl(pkl_fname="2024.pkl"):
    """read a pickle file. likley from get_grants.py"""
    with open(pkl_fname, "rb") as pkl:
        data = pickle.load(pkl)
    return data
