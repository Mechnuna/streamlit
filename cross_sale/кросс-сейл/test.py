from time import time
from memory_profiler import memory_usage



def dec(func):
	def funct():
		start = time()
		func()
		end = time()
		print(end-start)
	return funct

@dec
def f1():
	num = []
	for i in range(1000):
		num.append(i)

@dec
def f2():
	num = [0] * 1000
	for i in range(len(num)):
		num[i]=i

if __name__ == "__main__":
	for i in range(20):
		f1()
		f2()
		print("=======")
	mf1=memory_usage((f1))
	print()
	mf2=memory_usage((f2))
	print(f"F1 memory:{mf1}")
	print(f"F2 memory:{mf2}")