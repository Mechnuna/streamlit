# def parse_csv(new_data):
# 	global gold_standart
# 	global numbers_gs
# 	all_trimmer = new_data.index #url всех триммеров
# 	all_rec = new_data.columns #названия всех товаров для кросс-сейла
# 	all_rec = all_rec[1:]
# 	#запускаем цикл по ДатаФрейму
# 	for url in all_trimmer:
# 		gold_standart_pair = {}
# 		numbers_gs_mass = []

# 		one_line = new_data.loc[url]
# 		for name_rec in all_rec:
# 			gold_standart_pair[name_rec.strip()]=new_data[name_rec][url]/100 # Засовываем название и оценку релевантности в словарь
# 			numbers_gs_mass.append(new_data[name_rec][url]/100)

# 		offer_id = str(url)
# 		numbers_gs_mass.sort(reverse=True) # сортируем все элементы по возрастанию
# 		gold_standart[offer_id] = gold_standart_pair # Засовываем по offer_id словарь с оценкой релевантности товаров
# 		numbers_gs[offer_id] = numbers_gs_mass