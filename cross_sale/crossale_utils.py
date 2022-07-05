import pandas as pd
import numpy as np
import streamlit as st

'''Функция для сортировки строчки датафрейма'''
def f(x):
    return pd.Series(x.sort_values(ascending=False).values, index=x.sort_values().index)

'''Функция для возвращения offer_id товара'''
def return_id(url):
	return url[url.rfind('/') + 1 : url.find('-')]


def peres(arr1, arr2):
	arr = []
	for elem in arr2:
		if int(elem) in arr1:
			arr.append(elem)
	return(arr)

def return_value(dic):
	mass = []
	for k,v in dic.items():
		mass.append(v)
	return(mass)

def print_top5(metrix, mass, gold_standart, top10url_dict, metfix_name):
	new_metrix = {}
	for i in range(len(mass)):
		# if len(metrix[str(mass[i])]) >= 10 and i < 5:
		try:
			if len(metrix[str(mass[i])]) >= 1:
				st.markdown(f'<h3 style="color:#FF422A;font-size:20px;"> OFFER ID {mass[i]}</h3>', unsafe_allow_html=True)
				# st.text(f"OFFER_ID \033[34m{mass[i]}\033[0m")
				st.text("Модель          " + str(metfix_name[mass[i]][:11]))
				st.text("Золотой стандарт" + str(gold_standart[mass[i]][:11]))
				st.text("")
				st.text("")
				st.text("ОЦЕНКА РЕЛЕВАНТНОСТИ")
				st.text("Модель          " + str(metrix[str(mass[i])][:11]))
				st.text("Золотой стандарт" + str(return_value(top10url_dict[mass[i]])[:11])+'\n')
			new_metrix[mass[i]] = metfix_name[str(mass[i])], gold_standart[mass[i]]
		except:
			None

	return(new_metrix)