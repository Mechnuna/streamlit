desc_alg1 = "На вход подаем два массива <br><br>В первом лежат все товары <br>\
Во втором лежат индексы валидных товаров из первого массива <br>\
Рассчитываем dcg для каждого валидного товара\
dcg рассчитывается как <br><br>\
![img](https://hsto.org/getpro/habr/post_images/3c6/cbb/304/3c6cbb304a626dfdf1ee388eda113c99.svg)<br><br>\
dcg - это сумма всех dcg валидных товаров <br>\
max dcg - это сумма dcg первых(N) элементов, где N это количество валидных товаров<br><br>"

desc_alg2 = "На вход подаем два массива <br><br>В первом - рекомендации по моделям <br>\
Во втором - рекомендации по Золотому Стандару <br>\
Рассчитываем dcg для каждого валидного товара\
dcg рассчитывается как <br><br>\
![img](https://hsto.org/getpro/habr/post_images/3c6/cbb/304/3c6cbb304a626dfdf1ee388eda113c99.svg)<br><br>\
Скрипт изначально считал max_dcg - dcg отсортированного массива товаров, но так как у нас есть Золотой Стандарт max_dcg будет dcg массива Золотого Стандарта<br>"

desc_alg3 = "На вход подается два массива <br><br>\
В первом массиве - рекомендации по моделям <br>\
Во втором - рекомендации по Золотому Стандарту <br>\
dcg рассчитывается как <br><br>\
![img](https://hsto.org/getpro/habr/post_images/3c6/cbb/304/3c6cbb304a626dfdf1ee388eda113c99.svg)<br><br>\
Рассчитываем dcg первого массива и делим на идеальный dcg второго массива<br>"