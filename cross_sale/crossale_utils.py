import pandas as pd
import numpy as np
import streamlit as st


'''Функция для сортировки строчки датафрейма'''
def f(x):
    return pd.Series(x.sort_values(ascending=False).values, index=x.sort_values().index)


'''Функция для возвращения offer_id товара'''
def return_id(url):
	return url[url.rfind('/') + 1 : url.find('-')]


'''
Функция для сортировки Золотого Стандарта и возвращеннии массивов с именами ,оценкой релевантности и попарным массивом

>>> dict_ = {'леска 4':0.1,'леска 1':0.9128,'зарядка':1.0,'АК 24':0.213}

Попарно зассовываем в tuple и сортируем
>>> sort_arr = [(1.0, 'зарядка'), (0.9128, 'леска 1'), (0.213, 'АК 24'), (0.1, 'леска 4')]
Разбиваем на отдельные масивы
>>> name_ = ['зарядка', 'леска 1', 'АК 24', 'леска 4']
>>> grade_ = [1.0, 0.9128, 0.213, 0.1]

'''
def dict_to_sort_list(dict_):
    grade_ = []
    name_ = []
    sort_arr = [(v, k) for k,v in dict_.items()]
    sort_arr.sort(reverse=True)
    for v,k in sort_arr:
      grade_.append(v)
      name_.append(k)
    return grade_, name_, sort_arr


'''
Функция для вывода и наглядного сравнения Золотого Стандарта и рекомендации модели
'''
def print_top5(metrics, metrics_name, gold_standart, min_k=10, count=10, print_=True):
	new_metrics = {} # создаем новый словрь для отсортированного Золотого Стандарта
	gs_name = {}
	for offer_id, grade_mass in metrics.items():
			grade, name, new_metrics[offer_id] = dict_to_sort_list(gold_standart[offer_id])
			gs_name[offer_id] = name
			if len(metrics[offer_id]) >= min_k and print_:
				st.markdown(f'<h3 style="color:#FF422A;font-size:20px;"> OFFER ID {offer_id}</h3>', unsafe_allow_html=True)
				st.text("Модель            " + str(metrics_name[offer_id][:count + 1]))
				st.text("Золотой стандарт  " + str(name[:count + 1]))
				st.text("")
				st.text("")
				st.text("ОЦЕНКА РЕЛЕВАНТНОСТИ")
				st.text("Модель          " + str(metrics[offer_id][:count + 1]))
				st.text("Золотой стандарт  " + str(grade[:count + 1]))
	return(new_metrics, gs_name)


'''
ДЛЯ ПЕРВОГО АЛГОРИТМА ВАРИАНТ 1
(Сравнивает имена)
Создаем из двух словарей массивы с массивами
В первом массиве лежат уникальные значения всех элементов
Во втором массиве лежат уникальные значения только валидных товаров

Товар валиден если:
1 - Он стоит на том же месте ,что и в Золотом Стандарте
2 - Он в пределах +- 3(окошка регулируется) позиции от своей

metrics = [1,7,5,2,3,8]
gold = [8,7,6,5,4,3]

Валидные товары - 7,5
'''
def valid_product(metrics_name, name_gs, m, window=3):
  final_model_rec = []
  final_gold_standart = []
  for met in metrics_name:
    gs_mini = []
    for i in range(len(metrics_name[met])):
      if i < window:
        mini = 0
      else:
        mini = i - window
      if i + window > len(metrics_name[met]):
        maxs = len(metrics_name[met])
      else:
        maxs = i + window
      if metrics_name[met][i] == name_gs[met][i]:
        m[met][i] = i
        gs_mini.append(i)
      elif metrics_name[met][i] in name_gs[met][mini:maxs]:
        m[met][i] = i
        gs_mini.append(i)
      else:
        m[met][i] = i
    final_gold_standart.append(gs_mini)
    final_model_rec.append(m[met])
  return final_gold_standart, final_model_rec


'''
ДЛЯ ПЕРВОГО АЛГОРИТМА ВАРИАНТ 2
(Сравнивает значения)
Создаем из двух словарей массивы с массивами
В первом массиве лежат уникальные значения всех элементов
Во втором массиве лежат уникальные значения только валидных товаров

Товар валиден если:
1 - Он стоит на том же месте ,что и в Золотом Стандарте
2 - Он в пределах +- 3(окошка регулируется) позиции от своей
3 - Если его релевантность равна релевантности элемента,
который стоит на этом же месте в Золотом Стандарте

metrics_name = [1,7,5,2,3,8]
gold_name = [8,7,6,5,4,3]

metrics_goal = [0.1,0.94,0.78,0.1234,0.345,1.0]
gold_goal = [1.0, 0.94,0.81,0.78,0.345,0.345]

Валидные товары - 7,5,3
'''

def valid_product_value(metrics, numbers_gs, m, window=3):
  final_model_rec = []
  final_gold_standart = []
  for met in metrics:
    gs_mini = []
    for i in range(len(metrics[met])):
      if i < window:
        mini = 0
      else:
        mini = i - window
      if i + window > len(metrics[met]):
        maxs = len(metrics[met])
      else:
        maxs = i + window
      if metrics[met][i] == numbers_gs[met][i]:
        m[met][i] = i
        gs_mini.append(i)
      elif metrics[met][i] in numbers_gs[met][mini:maxs]:
        m[met][i] = i
        gs_mini.append(i)
      else:
        m[met][i] = i
    final_gold_standart.append(gs_mini)
    final_model_rec.append(m[met])
  return final_gold_standart, final_model_rec

if __name__ == "__main__":
	None