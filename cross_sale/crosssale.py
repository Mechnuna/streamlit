import streamlit as st
import pandas as pd
import json
import copy
###################################

from st_aggrid import AgGrid
from st_aggrid.grid_options_builder import GridOptionsBuilder
from description import desc_alg1, desc_alg2
###################################

from functionforDownloadButtons import download_button
from crossale_utils import *
from first_algos import ndcg_at, mean_average_precision, mean_reciprocal_rank
from second_algos import ndcg_at_k, map_mass, mrr

###################################


def main():

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

	c29, c30, c31 = st.columns([1, 6, 1])

	with c30:

		number = st.slider('Сколько дата фреймов нужно склеить?',1,5,key='database_count')
		all_db = None

		uploaded_file = st.file_uploader(
			"",
			key="1",
			help="To activate 'wide mode', go to the hamburger menu > Settings > turn on 'wide mode'",
		)

		if uploaded_file is not None:
			file_container = st.expander("Проверьте ваш загруженный файл .csv")
			all_db = pd.read_csv(uploaded_file)
			uploaded_file.seek(0)
			file_container.write(all_db)
			if st.session_state['database_count'] != 1:

				for i in range(st.session_state['database_count'] - 1):
					uploaded_file = st.file_uploader(
						"",
						key=str(i+2),
					)

					if uploaded_file is not None:
						file_container = st.expander("Проверьте ваш загруженный файл .csv")
						shows = pd.read_csv(uploaded_file,index_col='name')
						all_db = all_db.merge(shows, left_on="name",right_on="name")
						uploaded_file.seek(0)
						file_container.write(shows)
					else:
						st.stop()

		else:
			st.info(
				f"""
					👆 Загрузите a .csv файл. Например: [biostats.csv](https://people.sc.fsu.edu/~jburkardt/data/csv/biostats.csv)
					"""
			)

			st.stop()

	from st_aggrid import GridUpdateMode, DataReturnMode

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
		df = df.set_index('name')
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



	st.text("")

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

	model_recommendation = {} # Словарь для хранения рекомендаций по модели
	gold_standart = {} # Словарь для хранения рекомендаций по золотому стандарту
	numbers_gs = {} # Словарь для хранения только оценок релевантности по золотому стандарту

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

	json_elem = js["recommendations"]
	# Находим рекомендаций для каждого товара
	for elem in json_elem:
		model_recommendation_mass = []
		url_json_elem = return_id(elem['urlLink'])
		mass_rec_id = elem["recommendItems"]
		
		for offer_id in mass_rec_id:
			model_recommendation_mass.append(offer_id['name'])
		model_recommendation[url_json_elem] = model_recommendation_mass

	#Выдаем всем товарам из сгенерированного JSON оценку релевантности из Золотого Стандарта
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
					q = 0
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


	windows = st.number_input("Задать окошко валидности", key="win1_r",value=3,step=1,
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


if __name__ == '__main__':
	main()