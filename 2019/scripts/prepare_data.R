Sys.setlocale('LC_CTYPE', 'UTF-8')  # if for any reason this is not default
library(jsonlite)
df <- stream_in(file('data/fics.jsl'))
library(dplyr)
library(tidyr)
library(readr)
df %>% mutate(
  translated = translators %>% lapply(length) > 0
) %>% select(
  id, title, translated, published, last_update, size_cat, size_kb, rating
) %>% write_csv('data/fics_simple.csv')