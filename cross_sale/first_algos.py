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
except NameError:
    xrange = range


def _require_positive_k(k):
    if k <= 0:
        raise ValueError("ranking position k should be positive")


def _mean_ranking_metric(predictions, labels, metric):
    return np.mean([
        metric(np.asarray(prd), np.asarray(labels[i]))
        for i, prd in enumerate(predictions)
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
            if not assume_unique:
                lab = np.unique(lab)

            n_lab = lab.shape[0]
            n_pred = pred.shape[0]
            n = min(max(n_pred, n_lab), k)
            arange = np.arange(n, dtype=np.float32)
            arange = arange[:n_pred]
            denom = np.log2(arange + 2.)
            gains = 1. / denom

            dcg_mask = np.in1d(pred[:n], lab, assume_unique=assume_unique)
            dcg = gains[dcg_mask].sum()
            max_dcg = gains[arange < n_lab].sum()
            st.write(f"dcg:{dcg}, max_dcg:{max_dcg}")
            return dcg / max_dcg

        else:
            return _warn_for_empty_labels()

    return _mean_ranking_metric(predictions, labels, _inner_ndcg)