import streamlit as st
import pandas as pd

options = st.radio("Выберите категорию", ['футболки', 'платья', 'рубашки'], key='algorithm_radio')
go_button = st.button('Изменить категорию')

db = 'tshirt_res.csv'
table = 'tshirt.csv'
	
if go_button:
	if options == 'футболки':
		db = 'tshirt_res.csv'
		table = 'tshirt.csv'
	elif options == 'платья':
		db = 'dress_res.csv'
		table = 'dress.csv'
	elif options == 'рубашки':
		db = 'shirts_res.csv'
		table = 'shirts.csv'

# БД c соотношением похожести товаров
st.write("""## Соотношение похожести""")
df = pd.read_csv(db, index_col='name')
instrument = st.multiselect(
		"Select tool", list(df.index))
if not instrument:
	df
else:
	df.loc[instrument]

with open(db, "rb") as fp:
	btn = st.download_button(
		label="Download SVG",
		data=fp,
		file_name=db
	)


# Все гайковерты
st.write("""## Все товары""")
df = pd.read_csv(table, index_col='offer_id')
instrument2 = st.multiselect(
		"Select tool", list(df.index),key='second')
if not instrument2:
	df
else:
	data = df.loc[instrument2]
	data

with open(table, "rb") as fp:
	btn = st.download_button(
		label="Download SVG",
		data=fp,
		file_name=table
	)