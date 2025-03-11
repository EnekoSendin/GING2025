import pandas as pd

# hello

df = pd.read_excel('Alonso_2014_SpanishAoA.xls')

df[[' WrittenFreq_Subtlex-ESP_Log', ' WrittenFreq_LEXESP_Log']].corr('pearson')