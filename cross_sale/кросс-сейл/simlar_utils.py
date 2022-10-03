import streamlit as st
import pandas as pd
import zipfile
import os
import re
###################################

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
		# st.write(gold_standart)
		with open('newfile.txt', 'w') as f:
			f.write(gold_standart)
			print("ok")
		# print(gold_standart)
		# print("\n\n\n\n\n")

	st.text("")
	return gold_standart, numbers_gs

if __name__ == "__main__":
	pass