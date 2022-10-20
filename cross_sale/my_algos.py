import math

def my_dcg(mass: list) -> float:
	dcg = 0
	for num, elem in enumerate(mass):
		dcg += (2**elem - 1) / math.log2(num + 2)
	return dcg

def my_ndcg(score: list, gold_standart: list) -> float:
	ndcg = 0
	length = len(score)
	for i in range(length):
		ndcg += my_dcg(score[i]) / my_dcg(gold_standart[i])
	return ndcg / length