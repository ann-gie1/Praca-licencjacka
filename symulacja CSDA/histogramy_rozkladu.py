import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# 1. Wczytanie danych
plik_wejsciowy = "./dane_symulacja_CSDA/histogramy_weryfikacja.csv"
plik_wyjsciowy = "./dane_symulacja_CSDA/histogramy_weryfikacja.png"

df = pd.read_csv(plik_wejsciowy)

# Wybieramy tylko jedną średnicę, żeby r się nie nałożyły z różnych kul
wybrana_srednica = df['Srednica_mm'].unique()[0]
df_plot = df[df['Srednica_mm'] == wybrana_srednica]

print(f"Rysowanie histogramów dla średnicy: {wybrana_srednica} mm ({len(df_plot)} cząstek)")

# 2. Utworzenie siatki wykresów 2 wiersze x 3 kolumny
fig = make_subplots(
    rows=2, cols=3, 
    subplot_titles=("Zmienna: r", "Zmienna: Theta (azymut)", "Zmienna: Phi (polarny)", 
                    "Zmienna: X", "Zmienna: Y", "Zmienna: Z")
)

# Konfiguracja parametrów dla każdej zmiennej
zmienne = [
    ('r', 1, 1, 'blue'),
    ('theta', 1, 2, 'green'),
    ('phi', 1, 3, 'purple'),
    ('x', 2, 1, 'red'),
    ('y', 2, 2, 'orange'),
    ('z', 2, 3, 'brown')
]

# 3. Pętla rysująca
for nazwa, wiersz, kolumna, kolor in zmienne:
    fig.add_trace(
        go.Histogram(
            x=df_plot[nazwa], 
            nbinsx=50, 
            marker_color=kolor, 
            name=nazwa,
            showlegend=False
        ),
        row=wiersz, col=kolumna
    )
    # Dodanie opisów osi
    fig.update_xaxes(title_text=nazwa, row=wiersz, col=kolumna)
    fig.update_yaxes(title_text="Zliczenia", row=wiersz, col=kolumna)

# 4. Finalny layout
fig.update_layout(
    title_text=f"Weryfikacja jednorodności przestrzennej Monte Carlo (Sfera {wybrana_srednica} mm)",
    height=700, width=1200,
    template="plotly_white"
)

# 5. Zapis do pliku zamiast wyświetlania
fig.write_image(plik_wyjsciowy)
print(f"Gotowe. Wykres zapisano w: {plik_wyjsciowy}")