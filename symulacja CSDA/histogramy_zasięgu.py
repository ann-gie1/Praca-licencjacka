import pandas as pd
import plotly.graph_objects as go

# 1. Wczytanie danych
plik_wejsciowy = "./dane_symulacja_CSDA/Generacja_danych.csv"
df = pd.read_csv(plik_wejsciowy)

# 2. Tworzenie histogramu 1D
fig = go.Figure(data=[go.Histogram(x=df['Range'])])

# 3. Konfiguracja osi i wyglądu
fig.update_layout(
    title='Rozkład zasięgów',
    xaxis_title='zasięg',
    yaxis_title='Liczba zliczeń'
)

# 4. Wyświetlenie wykresu
fig.show()