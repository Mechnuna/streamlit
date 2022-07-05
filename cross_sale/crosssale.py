import streamlit as st
import pandas as pd
import numpy as np
import json

###################################

from st_aggrid import AgGrid
from st_aggrid.grid_options_builder import GridOptionsBuilder
from st_aggrid.shared import JsCode

###################################

from functionforDownloadButtons import download_button
from crossale_utils import *
from first_algos import ndcg_at
from second_algos import ndcg_at_k

###################################


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

st.set_page_config(page_icon="✂️", page_title="CSV Wrangler")

# st.image("https://emojipedia-us.s3.dualstack.us-west-1.amazonaws.com/thumbs/240/apple/285/balloon_1f388.png", width=100)
st.image(
    "https://emojipedia-us.s3.dualstack.us-west-1.amazonaws.com/thumbs/240/apple/285/scissors_2702-fe0f.png",
    width=100,
)

st.title("Подсчет метрик модели по кросс-сейлу")

# st.caption(
#     "PRD : TBC | Streamlit Ag-Grid from Pablo Fonseca: https://pypi.org/project/streamlit-aggrid/"
# )


# ModelType = st.radio(
#     "Choose your model",
#     ["Flair", "DistilBERT (Default)"],
#     help="At present, you can choose between 2 models (Flair or DistilBERT) to embed your text. More to come!",
# )

# with st.expander("ToDo's", expanded=False):
#     st.markdown(
#         """
# -   Add pandas.json_normalize() - https://streamlit.slack.com/archives/D02CQ5Z5GHG/p1633102204005500
# -   **Remove 200 MB limit and test with larger CSVs**. Currently, the content is embedded in base64 format, so we may end up with a large HTML file for the browser to render
# -   **Add an encoding selector** (to cater for a wider array of encoding types)
# -   **Expand accepted file types** (currently only .csv can be imported. Could expand to .xlsx, .txt & more)
# -   Add the ability to convert to pivot → filter → export wrangled output (Pablo is due to change AgGrid to allow export of pivoted/grouped data)
# 	    """
#     )
# 
#     st.text("")


c29, c30, c31 = st.columns([1, 6, 1])

with c30:

	number = st.slider('Сколько баз данных нужно склеить?',1,5,key='database_count')
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
# enables pivoting on all columns, however i'd need to change ag grid to allow export of pivoted/grouped data, however it select/filters groups
gb.configure_default_column()
gb.configure_selection(selection_mode="multiple", use_checkbox=True)
gb.configure_side_bar()  # side_bar is clearly a typo :) should by sidebar
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

st.write("Загрузить JSON")

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

# Массив для хранения рекомендаций по золотому стандарту
top10url_dict = {}
gold_standart = {}

# Переменные с offer_id всех товаров 
all_trimmer = df.index
all_rec = df.columns

for offer_id in all_trimmer:
	top10url_mass = []
	gold_standart_mass = []

	top10url = df.loc[offer_id]
	top10url_mass=np.sort(top10url)[::-1]
	dict_mini = {}
	for value in top10url_mass:
		for i in all_rec:
			if df[i][offer_id]==value:
				dict_mini[i] = value
				gold_standart_mass.append(i)
	gold_standart[return_id(offer_id)] = gold_standart_mass
	top10url_dict[return_id(offer_id)] = dict_mini


top25url_dict_rec = {} # Массив для хранения рекомендаций по json
json_elem = js["recommendations"]

# Находим топ рекомендаций для каждого товара из сгенерироованного каталога
for elem in json_elem:
	top25url_mass_rec = []
	url_json_elem = return_id(elem['urlLink'])
	mass_rec_id = elem["recommendItems"]
	for id in mass_rec_id:
		top25url_mass_rec.append(id['name'])
	top25url_dict_rec[url_json_elem] = top25url_mass_rec

all_offer_id =[]
for i in df.index:
	all_offer_id.append(return_id(i))

metrics = {}
metrics_name = {}
for key, item in top25url_dict_rec.items():
	metrics_dic = []
	names = []
	for c in item:
		try:
			zz = 0
			for k,v in top10url_dict[key].items():
				if k.strip() == c:
					metrics_dic.append(v)
					break
				zz+=1
				names.append(c)
			else:
				metrics_dic.append(0)
		except:
			q = 1
	metrics[key] = metrics_dic
	metrics_name[key] = names

but3, but4, _  = st.columns(3)

with but3:
	show_rec = st.button("Посмотреть рекомендации")
with but4:
	hide_rec = st.button("Скрыть рекомендации")

#Посмотреть наглядно что предлагает модель и золотой стандарт
if show_rec:
	st.markdown('<h2 style="font-size:24px;">ТОП 10 ТОВАРОВ ДЛЯ ТРИММЕРА</h2>', unsafe_allow_html=True)
	m = print_top5(metrics,all_offer_id,gold_standart, top10url_dict, metrics_name)

new_mtrix = []
new_gold = []
for k,v in metrics.items():
  if v:
    new = []
    for i in v:
      new.append(i/100)
    new_mtrix.append(new)
    new_gold.append([1 for i in range(len(new))])

options = st.radio("Выберите алгоритм", ['1', '2', '3'], key='algorithm_radio')

go_button = st.button('Подсчитать')

if go_button:
	if options == '1':
		st.write(ndcg_at(new_mtrix,new_gold))
	elif options == '2':
		sum = 0
		for one_trimmer in new_mtrix:
			l = ndcg_at_k(one_trimmer,10,method=1)
			sum += l
		st.write('Итого',sum/len(new_mtrix))