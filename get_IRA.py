from speakeasypy import Speakeasy, Chatroom
from typing import List
import time
#lib about RDF
import rdflib
from rdflib.namespace import Namespace, RDF, RDFS, XSD
from rdflib.term import URIRef, Literal
import csv
import json
import networkx as nx
import pandas as pd
import rdflib
from rdflib.plugins.sparql.parser import parseQuery
from rdflib.plugins.sparql import prepareQuery
from collections import defaultdict, Counter
import re
import numpy as np
import os
import pandas as pd
from sklearn.metrics import pairwise_distances
import random
import spacy
#nlp = spacy.load("en_core_web_trf")
from extract_entity import extract_entity
from extract_relation import extract_relation
#from extract_number import extract_number
from indentify_question import return_type
from sklearn.metrics import cohen_kappa_score

import csv
import json
import pandas as pd
from statistics import mean, stdev
#from statsmodels.stats import inter_rater as irr

crowd = pd.read_csv('../processed_crowd',sep=',')

respond_counts = crowd.groupby(["HITId","AnswerLabel"]).count().HITTypeId
d = respond_counts.to_dict()

majority_vote = {}
for (qid, ans), v in d.items():
    if qid not in majority_vote:
        if v > 1:
            res = {"result": ans}
            if ans == 'CORRECT':
                res["distribution"] = (v, 3 - v)
            else:
                res["distribution"] = (3 - v, v)
            majority_vote[qid] = res

for qid, res in majority_vote.items():
    print(f"Question ID: {qid}")
    print(f"  Result: {res['result']}")
    print(f"  Distribution: {res.get('distribution', 'N/A')}")
    print("-" * 20)


def cal_fleiss_kappa(orig):
    # aggregate_raters() returns a tuple of ([data], [categories])
    # aggregate_raters() is assuming raters as columns
    dats, cats = irr.aggregate_raters(orig)
    return irr.fleiss_kappa(dats, method='fleiss')

# group output by batch
batches = crowd.groupby(["HITTypeId"])
fleiss_kappa_list = []
q_id = []
last = 0
for b_id, df_b in batches:
    o = df_b.groupby(["HITId"]).apply(lambda b: b.AnswerID.to_list()).to_numpy()
    a = [i for i in o]
    q_id.append([last+i+1 for i in range(len(a))])
    last = q_id[-1][-1]
    fleiss_kappa_list.append(cal_fleiss_kappa(np.array(a)))

#get the fleiss_kappa score
print(fleiss_kappa_list)
