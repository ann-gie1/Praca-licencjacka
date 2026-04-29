import pandas as pd
import plotly.graph_objects as go

# 1. Wczytanie danych
plik_wejsciowy = "../dane_symulacja_cal_gonzales/Generacja_danych_c-g_1mln.csv"
plik_wyjsciowy = "../dane_symulacja_cal_gonzales/histogram_energii_1mln.png"
df = pd.read_csv(plik_wejsciowy)

# 2. Tworzenie histogramu 1D
fig = go.Figure(data=[go.Histogram(x=df['Energia-wylosowana'])])

# 3. Konfiguracja osi i wyglądu
fig.update_layout(
    title='Rozkład energii',
    xaxis_title='Energia',
    yaxis_title='Liczba zliczeń'
)

# 4. Wyświetlenie wykresu
fig.write_image(plik_wyjsciowy)
print(f"Gotowe. Wykres zapisano w: {plik_wyjsciowy}")