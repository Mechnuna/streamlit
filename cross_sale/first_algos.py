from __future__ import absolute_import, division

import numpy as np

import warnings

import streamlit as st

__all__ = [
    'mean_average_precision',
    'ndcg_at',
    'precision_at',
]

try:
    xrange
except NameError:  # python 3 does not have an 'xrange'
    xrange = range

def mean_reciprocal_rank(predictions):
    mrr = 0.0
    for mass in predictions:
        if mass:
            mrr += 1/(mass[0] + 1)
    return (mrr/len(predictions))
    
def _require_positive_k(k):
    if k <= 0:
        raise ValueError("ranking position k should be positive")


def _mean_ranking_metric(predictions, labels, metric):
    return np.mean([
          metric(np.asarray(prd), np.asarray(labels[i]))
          for i, prd in enumerate(predictions) # lazy eval if generator
      ])


def _warn_for_empty_labels():
    warnings.warn("Empty ground truth set! Check input data")
    return 0.


def precision_at(predictions, labels, k=10, assume_unique=True):
    _require_positive_k(k)

    def _inner_pk(pred, lab):
        if lab.shape[0] > 0:
            n = min(pred.shape[0], k)
            cnt = np.in1d(pred[:n], lab, assume_unique=assume_unique).sum()
            return float(cnt) / k
        else:
            return _warn_for_empty_labels()

    return _mean_ranking_metric(predictions, labels, _inner_pk)


def mean_average_precision(predictions, labels, assume_unique=True):
    def _inner_map(pred, lab):
        if lab.shape[0]:
            n = pred.shape[0]

            arange = np.arange(n, dtype=np.float32) + 1.  # this is the denom
            present = np.in1d(pred[:n], lab, assume_unique=assume_unique)
            prec_sum = np.ones(present.sum()).cumsum()
            denom = arange[present]
            return (prec_sum / denom).sum() / lab.shape[0]

        else:
            return _warn_for_empty_labels()

    return _mean_ranking_metric(predictions, labels, _inner_map)


def ndcg_at(predictions, labels, k=10, assume_unique=True):
    _require_positive_k(k)

    def _inner_ndcg(pred, lab):
        if lab.shape[0]:
            # if we do NOT assume uniqueness, the set is a bit different here
            if not assume_unique:
                lab = np.unique(lab)

            n_lab = lab.shape[0]
            n_pred = pred.shape[0]
            n = min(max(n_pred, n_lab), k)  # min(min(p, l), k)?

            # similar to mean_avg_prcsn, we need an arange, but this time +2
            # since python is zero-indexed, and the denom typically needs +1.
            # Also need the log base2...
            arange = np.arange(n, dtype=np.float32)  # length n

            # since we are only interested in the arange up to n_pred, truncate
            # if necessary
            arange = arange[:n_pred]
            denom = np.log2(arange + 2.)  # length n
            gains = 1. / denom  # length n
            # compute the gains where the prediction is present in the labels
            dcg_mask = np.in1d(pred[:n], lab, assume_unique=assume_unique)
            dcg = gains[dcg_mask].sum()
            # the max DCG is sum of gains where the index < the label set size
            max_dcg = gains[arange < n_lab].sum()
            st.write(f"DCG: {dcg} MAX DCG: {max_dcg}")
            if max_dcg == 0:
              return 0
            return dcg / max_dcg
        else:
            return _warn_for_empty_labels()
    return _mean_ranking_metric(predictions, labels, _inner_ndcg)