import streamlit as st
import pandas as pd

# БД c соотношением похожести товаров
st.write("""## Соотношение похожести""")
df = pd.read_csv('connections_gajkovyorty.csv',index_col='name')
instrument = st.multiselect(
        "Select tool", list(df.index))
if not instrument:
	df
else:
	df.loc[instrument]

with open("connections_gajkovyorty.csv", "rb") as fp:
    btn = st.download_button(
        label="Download SVG",
        data=fp,
        file_name="data_gaikovert.csv"
    )


# Все гайковерты
st.write("""## Все гайковерты""")
df = pd.read_csv('vseinstrumenty_gajkovyorty.csv',index_col='name')
instrument2 = st.multiselect(
        "Select tool", list(df.index),key='second')
if not instrument2:
	df
else:
	data = df.loc[instrument2]['specifications']
	data

with open("vseinstrumenty_gajkovyorty.csv", "rb") as fp:
    btn = st.download_button(
        label="Download SVG",
        data=fp,
        file_name="data_gaikovert.csv"
    )

##########################################################

# БД c соотношением похожести товаров
st.write("""## Соотношение похожести""")
df = pd.read_csv('connections_dreli_encor.csv',index_col='name')
instrument = st.multiselect(
        "Select tool", list(df.index))
if not instrument:
	df
else:
	df.loc[instrument]

with open("connections_dreli_encor.csv", "rb") as fp:
    btn = st.download_button(
        label="Download SVG",
        data=fp,
        file_name="data_dreli.csv"
    )


# Все дрели
st.write("""## Все дрели""")
df = pd.read_csv('encor_dreli_drop_db.csv',index_col='name')
instrument2 = st.multiselect(
        "Select tool", list(df.index),key='second')
if not instrument2:
	df
else:
	data = df.loc[instrument2]['specifications']
	data

with open("encor_dreli_drop_db.csv", "rb") as fp:
    btn = st.download_button(
        label="Download SVG",
        data=fp,
        file_name="data_dreli.csv"
    )

##########################################################

# БД c соотношением похожести товаров
st.write("""## Соотношение похожести""")
df = pd.read_csv('connections_perforators_encor.csv',index_col='name')
instrument = st.multiselect(
        "Select tool", list(df.index))
if not instrument:
	df
else:
	df.loc[instrument]

with open("connections_perforators_encor.csv", "rb") as fp:
    btn = st.download_button(
        label="Download SVG",
        data=fp,
        file_name="data_perforators.csv"
    )


# Все гайковерты
st.write("""## Все гайковерты""")
df = pd.read_csv('encor_perforators.csv',index_col='name')
instrument2 = st.multiselect(
        "Select tool", list(df.index),key='second')
if not instrument2:
	df
else:
	data = df.loc[instrument2]['specifications']
	data

with open("encor_perforators.csv", "rb") as fp:
    btn = st.download_button(
        label="Download SVG",
        data=fp,
        file_name="data_perforators.csv"
    )

##########################################################