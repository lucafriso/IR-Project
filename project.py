import numpy as np
from trectools import TrecQrel, procedures
import os
from collections import defaultdict
import matplotlib.pyplot as plt
from matplotlib.markers import MarkerStyle

#definiamo una funzione per reperire tutte le run che ci occorrono
def upload_runs (path):
    runs = {}
    for r in os.listdir(path):
        r_name = ".".join(r.split(".")[:-1])
        with open(path + "/"+r, "r") as F_run:
                  runs[r_name] = defaultdict(list)
                  for l in F_run.readlines():
                      t, _, doc, pos, score, _ = l.strip().split()
                      runs[r_name][t].append((doc, int(pos)))
                  
    for r in runs:
        for t in runs[r]:
                  runs[r][t] = sorted(runs[r][t], key = lambda x: x[1])
        return runs

#definiamo una funzione di pooling
def pooling(runs, k):
        topics = list(runs[list(runs.keys())[0]].keys())
        pools = {t: [] for t in topics}
        for r in runs:
            for t in topics:
                pools[t] += [d for d, _ in  runs[r][t][:k]]
        pools = {t: list(set(pools[t])) for t in topics}
        return pools

#definiamo una funzione per l'upload dei qrels
def upload_qrels(path):
    topics = list(set([l.split()[0] for l in open(qrels_file, "r").readlines()]))
    topics2qrels = {t: {} for t in topics}
    
    for l in open(qrels_file, "r").readlines():
        l = l.strip().split()
        topics2qrels[l[0]][l[2]] = int(l[3])
        
    return topics2qrels

#definiamo una funzione per il pool dei qrels
def pool_qrels(qrels, pool):
    pooled_qrels = {t: {d:qrels[t][d] for d in qrels[t] if d in pool[t]} for t in qrels}
    return pooled_qrels

#
def sort_system_according_to(measure):
    return sorted(list(metrics.keys()), key = lambda x: metrics[x][measure])

#
def patk(assessed_run, k, max_grade =1):
    if k == 0:
        return o
    return np.sum(assessed_run[:k] / max_grade)

#definiamo rbp
def rbp(p, assessed_run, max_grade = 1, k = -1):
    a_run = assessed_run[:k if k != -1 else len(assessed_run)]
    coefs = np.arange(len(a_run))
    return (1-p) / max_grade*np.sum(a_run*p*coefs)

#definiamo rr
def rr(assessed_run):
    z = np.where(assessed_run == 1)[0]
    if z.size == 0:
        return 0
    else:
        return 1./(z[0]+1)

#definiamo ndcg
def ndcg(assessedr_run, base = 2, k= -1):
    if np.sum(assessed_run) == 0:
        return 0
    k = len(assessed_run) if k == -1 else k
    dcg = np.sum(assessed_run[:k] / np.log2(2 + np.arange(k)))
    return dcg / idcg(assessed_run)

#definiamo idcg
def idcg(k, base = 2):
    return np.sum(sorted(k, reverse = True)/np.log2(2 + np.arange(len(k))))


#definiamo average precision
def ap(assessed_run):
    if np.sum(assessed_run) == 0:
        return 0
    return np.sum([pathk(assessed_run[:i], i)*assessed_run[i-1] for i in range(1, len(assessed_run)+1)])/np.sum(assessed_run)

#inizio codice
qrels_file = "/Users/lucafriso/Desktop/UNIPD/Magistrale/IR/progetto/TREC_03_1994_AdHoc/pool/qrels.151-200.201-250.disk1-3.txt"

topics2qrels = upload_qrels(qrels_file)

path_to_runs = "/Users/lucafriso/Desktop/UNIPD/Magistrale/IR/progetto/TREC_03_1994_AdHoc/runs/automatic"

runs = upload_runs(path_to_runs)

pools10 = pooling(runs, 10)

pooled_qrels10 = pool_qrels(topics2qrels, pools10)

