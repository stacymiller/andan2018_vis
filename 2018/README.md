# Материалы и алгоритм сбора данных для лекций на мастерской АнДан'2018
[АнДан'2018, визуализационный трек](https://sites.google.com/letnyayashkola.org/andan/shit/vis#h.p_i3a0XjiknYhz)

## Как собрать данные
Запустить сборщик (написан на Python, требует пакет `scrapy`):

```bash
cd scraping
scrapy crawl id
```

Данные будут сохранены в `scraping/data/fics.jsl`, настройки можно менять 
в `scraping/settings.py`.

## Лекция "`ggplot`: the grammar of graphics"

Слайды с теорией и заданиями лежат в `slides/ggplot.pdf`.

Код для предварительного чтения данных лежит в `notebooks/ggplot_helpers.Rmd`.

Тот же код, решения задач, дополнительные задачи и дополнительные примеры лежат 
в `notebooks/ggplot.Rmd`. 

## Мастер-класс "Data wrangling with `dplyr`"

Слайды с теорией и заданиями лежат в `slides/data_wrangling.pdf`.

Код для предварительного чтения данных, более подробные, чем в презентации, 
решения задач и дополнительные задачи лежат в `notebooks/data_wrangling.Rmd`.

## Лекция "Plotly"

Слайдов нет. Лекция проводилась в режиме live coding, опорные теоретические моменты
писались в том же ноутбуке. Все материалы лежат в `notebooks/plotly.Rmd`.


Вопросы, предложения, пожелания принимаются в [ВК](https://vk.com/stacymiller) 
и [на почту](mailto:anastasia.a.miller@gmail.com).
