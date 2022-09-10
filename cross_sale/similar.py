import streamlit as st
import pandas as pd
import numpy as np
import json
import copy
import zipfile
import os
import re
###################################

from st_aggrid import AgGrid
from st_aggrid.grid_options_builder import GridOptionsBuilder
from st_aggrid.shared import JsCode
from description import desc_alg1, desc_alg2,desc_alg3
###################################

from functionforDownloadButtons import download_button
from crossale_utils import *
from first_algos import ndcg_at, mean_average_precision, mean_reciprocal_rank
from second_algos import ndcg_at_k, map_mass, mrr

###################################
from simlar_utils import *
from typing import Dict

'''Функция парсит csv файлы и возвращает два словаря Золотого стандарта'''
def parse_csv(new_data, gold_standart, numbers_gs):

			all_trimmer = new_data.index #url всех триммеров
			all_rec = new_data.columns #названия всех товаров для кросс-сейла
			all_rec = all_rec[1:]
			#запускаем цикл по ДатаФрейму
			for url in all_trimmer:
				gold_standart_pair = {}
				numbers_gs_mass = []

				one_line = new_data.loc[url]
				for name_rec in all_rec:
					gold_standart_pair[name_rec.strip()]=new_data[name_rec][url]/100 # Засовываем название и оценку релевантности в словарь
					numbers_gs_mass.append(new_data[name_rec][url]/100)

				offer_id = str(url)
				numbers_gs_mass.sort(reverse=True) # сортируем все элементы по возрастанию
				gold_standart[offer_id] = gold_standart_pair # Засовываем по offer_id словарь с оценкой релевантности товаров
				numbers_gs[offer_id] = numbers_gs_mass
			return (gold_standart, numbers_gs)


'''Основная функция для модели похожих товаров'''
def similar(gold_standart,numbers_gs):
	if st.button("Clear file list"):
		gold_standart.clear()
		numbers_gs.clear()
		os.system('rm -rf csv/*.csv')

	uploaded_file = st.file_uploader("Upload", type=["zip", "csv"], accept_multiple_files=True)

	if uploaded_file:
		for files in uploaded_file:
			if files.type == "application/zip":
				with zipfile.ZipFile(files, "r") as z:
					z.extractall("csv/")
					for filename in os.listdir('csv'):
						x = re.search('.csv$', filename)
						if x:
							print(filename)
							shows = pd.read_csv('csv/'+filename,index_col='url_number')
							file_container = st.expander("Проверьте ваш загруженный файл .csv")
							gold_standart, numbers_gs = parse_csv(shows, gold_standart, numbers_gs)
							files.seek(0)
							file_container.write(shows)
			else:
				file_container = st.expander("Проверьте ваш загруженный файл .csv")
				shows = pd.read_csv(files,index_col='url_number')
				gold_standart, numbers_gs = parse_csv(shows, gold_standart, numbers_gs)
				files.seek(0)
				file_container.write(shows)
	else:
		st.info(
			f"""
				👆 Загрузите .csv файлы. Или zip архив. Например: [biostats.csv](https://people.sc.fsu.edu/~jburkardt/data/csv/biostats.csv)
				"""
		)

		st.stop()


	options = st.radio("Посмотреть получившийся массив?", ['Нет', 'Да'], key='yes_no')

	if options == 'Да':
		st.write(gold_standart)

	st.text("")
	return gold_standart, numbers_gs

def main2():

	c29, c30, c31 = st.columns([1, 6, 1])
	model_recommendation = {} # Словарь для хранения рекомендаций по модели
	gold_standart,numbers_gs = get_static_store() # Словарь для хранения рекомендаций по золотому стандарту  и оценок релевантности по золотому стандарту
	with c30:
		similar(gold_standart,numbers_gs)
	st.write("Загрузите JSON")

	json_file = st.file_uploader(
			"",
			key="json",
		)

	if json_file is not None:
		js = json.load(json_file)

	else:
		st.info(
			f"""
				👆 Загрузите сгенерированный каталог с рекомендациями в формате json
				"""
		)

		st.stop()

	json_elem = js["recommendations"]
	def return_model_rec(json_elem):
		# Находим рекомендаций для каждого товара
		for elem in json_elem:
			model_recommendation_mass = []
			url_json_elem = return_id(elem['urlLink'])
			mass_rec_id = elem["recommendItems"]
			
			for offer_id in mass_rec_id:
				# model_recommendation_mass.append(offer_id['name'])
				model_recommendation_mass.append(return_id(offer_id['urlLink']))
			model_recommendation[url_json_elem] = model_recommendation_mass
		return model_recommendation
		
	model_recommendation = return_model_rec(json_elem)
	options2 = st.radio("Посмотреть получившийся массив?", ['Нет', 'Да'], key='yes_no2')
	if options2 == 'Да':
		st.write(model_recommendation)
	print("a")
	print(gold_standart['3989'])
	'''
	Выдаем всем товарам из сгенерированного JSON оценку релевантности из Золотого Стандарта
	'''
	def return_name_metrics(model_recommendation,gold_standart):
		metrics = {} # словарь для хранения оценки релевантности к каждому товару 
		metrics_name = {} # словарь для хранения названий товаров

		for offer_id, rec_mass in model_recommendation.items():
			metrics_dic = []
			names = []
			for product in rec_mass:
					zz = 0
					try:
						metrics_dic.append(gold_standart[offer_id][product])
						names.append(product)
					except:
						None
			if metrics_dic:
				metrics[offer_id] = metrics_dic
			if names:
				metrics_name[offer_id] = names
			# print(offer_id,metrics[offer_id])
		return metrics, metrics_name
	metrics, metrics_name = return_name_metrics(model_recommendation, gold_standart)
	but3, but4, _  = st.columns(3)

	with but3:
		show_rec = st.button("Посмотреть рекомендации")
	with but4:
		hide_rec = st.button("Скрыть рекомендации")


	#Посмотреть наглядно что предлагает модель и золотой стандарт
	if show_rec:
		st.markdown('<h2 style="font-size:24px;">ТОП 10 ТОВАРОВ ДЛЯ ТРИММЕРА</h2>', unsafe_allow_html=True)
		new_metrics, name_gs = print_top5(metrics, metrics_name, gold_standart)

	new_metrics, name_gs = print_top5(metrics, metrics_name, gold_standart, print_=False)


	windows = st.number_input("Задать окошко валидности", key="win1_r",value=6,step=1,
	help="Окошко валидности - допустимая погрешность в порядке товара в ленте. Например: \n\
		[1,3,4,5,6,7] при окошке 3 товар под номером 4 может быть на 2,3,4 местах")
	options = st.radio("Выберите алгоритм", ['1', '2'], key='algorithm_radio')
	go_button = st.button('Подсчитать')
	windows //= 2
	if go_button:

		if options == '1':

			st.markdown("# Способ первый")
			st.markdown(desc_alg1,unsafe_allow_html=True)

			ans1, ans2 = st.columns(2)

			with ans1:
				final_gold_standart, final_model_rec = valid_product_value(metrics, numbers_gs, copy.deepcopy(metrics), windows)
				expan_r = st.expander("Посмотреть DCG, MAX DCG")
				with expan_r:
					result_2 = ndcg_at(final_model_rec, final_gold_standart)
				print(len(metrics))
				st.write("Cравнение по значениям")
				st.write("NDCG:",result_2)
				st.write("MAP:",mean_average_precision(final_model_rec, final_gold_standart))	
				st.write("MRR:",mean_reciprocal_rank(final_gold_standart))

				if result_2 >= 0.4:
					st.markdown("### ВСЕ ХОРОШО")
				else:
					st.markdown("### БЫЛО ПОЛУЧШЕ")

		elif options == '2':

			st.markdown("# Способ второй")
			st.markdown(desc_alg2,unsafe_allow_html=True)

			ans1, ans2 = st.columns(2)

			with ans1:
				final_model_rec = []
				final_gold_standart = []
				for offer_id in new_metrics:
					final_model_rec.append(metrics[offer_id])
					final_gold_standart.append(numbers_gs[offer_id])

				sums = 0
				expan_l = st.expander("Посмотреть DCG, MAX DCG")
				with expan_l:
					for i in range(len(final_model_rec)):
						l = ndcg_at_k(final_model_rec[i], final_gold_standart[i], 10, 1)
						sums += l
				st.write("Сравнение по релевантности из Золотого Стандарта")
				final = sums/len(final_model_rec)
				st.write('NDCG',final)

				if final >= 0.4:
					st.markdown("### ВСЕ ХОРОШО")
				else:
					st.markdown("### БЫЛО ПОЛУЧШЕ")

if __name__ == "__main__":
	main2()