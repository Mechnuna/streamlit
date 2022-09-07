import streamlit as st
import pandas as pd
import numpy as np
import json
import copy
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

model_recommendation = {} # Словарь для хранения рекомендаций по модели
gold_standart = {} # Словарь для хранения рекомендаций по золотому стандарту
numbers_gs = {} # Словарь для хранения только оценок релевантности по золотому стандарту

def parse_csv(new_data):
	global gold_standart
	global numbers_gs
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
					parse_csv(shows)
					all_db = all_db.merge(shows, left_on='name',right_on='name')
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

options = st.radio("Посмотреть получившийся массив?", ['Нет', 'Да'], key='algorithm_radio')

if options == 'Да':
	st.write(gold_standart)

print("==============")
print(gold_standart['4356'])
print(gold_standart['108996'])


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

