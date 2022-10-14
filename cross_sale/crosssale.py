import streamlit as st
import pandas as pd
import json
import copy
import zipfile
import os
import re
import datetime
###################################

from st_aggrid import AgGrid
from st_aggrid.grid_options_builder import GridOptionsBuilder
from description import desc_alg1, desc_alg2
from st_aggrid import GridUpdateMode, DataReturnMode
###################################

from functionforDownloadButtons import download_button
from crossale_utils import *
from first_algos import ndcg_at, mean_average_precision, mean_reciprocal_rank
from second_algos import ndcg_at_k
from simlar_utils import similar
from my_algos import my_ndcg
###################################
from typing import Dict, final


@st.cache(allow_output_mutation=True)
def get_static_store() -> Dict:
    """Этот словарь инициализируется один раз и может использоваться для хранения загруженных файлов."""
    return {},{}

def cross_sale(label='name'):
	'''Основная функция для модели похожих товаров'''
	all_db = None
	if st.button("Clear file list"):
		all_db = None
		os.system('cd csv;rm -rf *')

	uploaded_file = st.file_uploader("Upload", type=["zip", "csv"], accept_multiple_files=True)

	if uploaded_file:
		for num, files in enumerate(uploaded_file):
			#если загрузили zip архив, то распаковываем его в папку csv
			if files.type == "application/zip":
				with zipfile.ZipFile(files, "r") as z:
					z.extractall("csv/")
					n = 0
					for filename in os.listdir('csv'):
						#работаем только с файлами csv
						x = re.search('.csv$', filename)
						if x:
							if n == 0:
								all_db = pd.read_csv('csv/'+filename)
								file_container = st.expander("Проверьте ваш загруженный файл .csv")
								files.seek(0)
								file_container.write(all_db)
								n += 1
							else:
								shows = pd.read_csv('csv/'+filename)
								file_container = st.expander("Проверьте ваш загруженный файл .csv")
								all_db = all_db.merge(shows, left_on=label,right_on=label)
								files.seek(0)
								file_container.write(shows)
			#если просто файлы csv
			else:
				if num == 0:
					all_db = pd.read_csv(uploaded_file[0])
					file_container = st.expander("Проверьте ваш загруженный файл .csv")
					files.seek(0)
					file_container.write(all_db)
				else:
					file_container = st.expander("Проверьте ваш загруженный файл .csv")
					shows = pd.read_csv(files)
					all_db = all_db.merge(shows, left_on=label,right_on=label)
					files.seek(0)
					file_container.write(shows)
					

	else:
		st.info(
			f"""
				👆 Загрузите a .csv файл. Например: [biostats.csv](https://people.sc.fsu.edu/~jburkardt/data/csv/biostats.csv)
				"""
		)

		st.stop()
	return all_db



def main():
	'''Главная функция'''
	def _max_width_():
		max_width_str = f"max-width: 1800px;"
		st.markdown(
			f"""
		<style>
		.reportview-container .main .block-container{{
			{max_width_str}
		}}
		</style>    
		""",
			unsafe_allow_html=True,
		)

	st.set_page_config(page_icon="🐈", page_title="CSV Wrangler")

	st.image(
		"https://emojipedia-us.s3.dualstack.us-west-1.amazonaws.com/thumbs/120/apple/325/paw-prints_1f43e.png",
		width=100,
	)

	options = st.radio("Выберите алгоритм", ['Кросс-сейл/Альтернативные', 'Похожие'], key='algorithm_')
	
	model_recommendation = {} # Словарь для хранения рекомендаций по модели
	gold_standart,numbers_gs = get_static_store() # Словарь для хранения рекомендаций по золотому стандарту  и оценок релевантности по золотому стандарту
	
	c29, c30, c31 = st.columns([1, 6, 1])

	with c30:
		if options == 'Кросс-сейл/Альтернативные':
			all_db = cross_sale()
			label = 'name'
		elif options == 'Похожие':
			gold_standart, numbers_gs = similar(gold_standart, numbers_gs)

	if options == 'Кросс-сейл/Альтернативные':

		gb = GridOptionsBuilder.from_dataframe(all_db)

		gb.configure_default_column()
		gb.configure_selection(selection_mode="multiple", use_checkbox=True)
		gb.configure_side_bar()
		gridOptions = gb.build()

		st.success(
			f"""
				💡 Подсказка! Удерживайте shift чтобы выбрать несколько строк!
				"""
		)

		response = AgGrid(
			all_db,
			gridOptions=gridOptions,
			enable_enterprise_modules=True,
			update_mode=GridUpdateMode.MODEL_CHANGED,
			data_return_mode=DataReturnMode.FILTERED_AND_SORTED,
			fit_columns_on_grid_load=False,
		)

		df = pd.DataFrame(response["selected_rows"])

		try:
			df = df.set_index(label)
		except:
			st.write("Выберите хотя бы один товар")

		st.subheader("Посмотреть на результат 👇 ")
		st.text("")

		but1, but2, _ = st.columns(3)

		with but1:
			show_table = st.button("Показать таблицу")
		with but2:
			hide_table = st.button("Скрыть таблицу")

		if show_table:
			st.table(df)

			c29, c30, c31 = st.columns([1, 1, 2])

			with c29:

				CSVButton = download_button(
					df,
					"File.csv",
					"Download to CSV",
				)

			with c30:
				CSVButton = download_button(
					df,
					"File.csv",
					"Download to TXT",
				)
			st.stop()
		new_data = df

		all_trimmer = new_data.index #url всех триммеров
		all_rec = new_data.columns #названия всех товаров для кросс-сейла

		#запускаем цикл по ДатаФрейму
		for url in all_trimmer:
			gold_standart_pair = {}
			numbers_gs_mass = []

			one_line = new_data.loc[url]
			for name_rec in all_rec:
				gold_standart_pair[name_rec.strip()]=new_data[name_rec][url]/100 # Засовываем название и оценку релевантности в словарь
				numbers_gs_mass.append(new_data[name_rec][url]/100)

			offer_id = return_id(url) # вырезаем offer_id из ссылки 
			numbers_gs_mass.sort(reverse=True) # сортируем все элементы по возрастанию
			gold_standart[offer_id] = gold_standart_pair # Засовываем по offer_id словарь с оценкой релевантности товаров
			numbers_gs[offer_id] = numbers_gs_mass


	'''Загружаем JSON с рекомендацией от модели и парсим его'''

	st.text("")
	st.write("Загрузите JSON")
	rec = None
	offers = None
	json_file = st.file_uploader(
			"",
			key="json",
			type=["zip", "json", "csv"], 
			accept_multiple_files=True
		)
	json_flag = 0
	#Typeapplication/json
	if json_file:
		for file_rec in json_file:
			if len(json_file) == 1:
				if file_rec.type == "application/zip":
					with zipfile.ZipFile(file_rec, "r") as z:
							z.extractall("json/")
							dir_name = 'json'
							for filename in os.listdir(dir_name):
								if filename == 'rec.csv':
									json_flag = 2
									rec = pd.read_csv(dir_name + '/rec.csv')
								elif filename == 'offers.csv':
									offers = pd.read_csv(dir_name + '/offers.csv',index_col="OFFERID")
				elif file_rec.type == "application/json":
					json_flag = 1
					js = json.load(file_rec)
				else:
					print(file_rec.type)
			else:
				if file_rec.name == 'rec.csv':
					json_flag = 2
					rec = pd.read_csv(file_rec)
				elif file_rec.name == 'offers.csv':
					offers = pd.read_csv(file_rec,index_col="OFFERID")

	else:
		st.info(
			f"""
				👆 Загрузите сгенерированный каталог с рекомендациями в формате json или zip с файлами csv
				"""
		)
		st.stop()
	
	if json_flag == 2:
		for i in rec.index:
			name = rec.iloc[i]['SOMEID']
			id_product = return_id(offers.loc[name]['URL'])
			name2 = rec.iloc[i]['RECOMMENDATIONOFFERID']
			if options == 'Похожие':
				try:
					model_recommendation[id_product].append(str(int(name2)))
				except:
					model_recommendation[id_product] = []
					model_recommendation[id_product].append(str(int(name2)))
			else:
				try:
					model_recommendation[id_product].append(offers.loc[name2]['NAME'].strip())
				except:
					model_recommendation[id_product] = []
					model_recommendation[id_product].append(offers.loc[name2]['NAME'].strip())
	
	if json_flag == 1:
		json_elem = js["recommendations"]
		# Находим рекомендаций для каждого товара
		for elem in json_elem:
			model_recommendation_mass = []
			url_json_elem = return_id(elem['urlLink'])
			mass_rec_id = elem["recommendItems"]
			
			for offer_id in mass_rec_id:
				if options == 'Похожие':
					model_recommendation_mass.append(return_id(offer_id['urlLink']))
				else:
					model_recommendation_mass.append(offer_id['name'])
			model_recommendation[url_json_elem] = model_recommendation_mass
	
	if options == 'Похожие':
		show_mass = st.radio("Посмотреть получившийся массив?", ['Нет', 'Да'], key='yes_no2')
		if show_mass == 'Да':
			st.write(model_recommendation)

	#Выдаем всем товарам из сгенерированного JSON оценку релевантности из Золотого Стандарта
	metrics = {} # словарь для хранения оценки релевантности к каждому товару 
	metrics_name = {} # словарь для хранения названий товаров

	for offer_id, rec_mass in model_recommendation.items():
		metrics_dic = []
		names = []
		for product in rec_mass:
				try:
					metrics_dic.append(gold_standart[offer_id][product])
					names.append(product)
				except:
					pass
		if metrics_dic:
			metrics[offer_id] = metrics_dic
		if names:
			metrics_name[offer_id] = names

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
	windows //= 2
	go_button = st.button('Подсчитать')

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

				final = my_ndcg(final_model_rec, final_gold_standart)
				# sums = 0
				# expan_l = st.expander("Посмотреть DCG, MAX DCG")
				# with expan_l:
				# 	for i in range(len(final_model_rec)):
				# 		l = ndcg_at_k(final_model_rec[i], final_gold_standart[i], 10, 1)
				# 		sums += l
				st.write("Сравнение по релевантности из Золотого Стандарта")
				# final = sums/len(final_model_rec)
				st.write('NDCG',final)

				if final >= 0.4:
					st.markdown("### ВСЕ ХОРОШО")
				else:
					st.markdown("### БЫЛО ПОЛУЧШЕ")


if __name__ == '__main__':
	try:
		main()
	finally:
		os.system('rm -rf *.csv')