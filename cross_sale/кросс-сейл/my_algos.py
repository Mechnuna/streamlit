import math

def my_dcg(mass: list) -> float:
	dcg = 0
	for num, elem in enumerate(mass):
		dcg += (2**elem - 1) / math.log2(num + 2)
	return dcg

def my_ndcg(score: list, gold_standart: list, k: int = 10) -> float:
	ndcg = 0
	length = len(score)
	for i in range(length):
		if len(score[i]) < k:
			k = len(score[i])
		if len(gold_standart[i]) < len(score[i]) < k:
			k = len(gold_standart[i])
		ndcg += my_dcg(score[i][:k]) / my_dcg(gold_standart[i][:k])
	return ndcg / length