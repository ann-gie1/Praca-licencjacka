import pandas as pd
import matplotlib
matplotlib.use('Agg') # Kluczowe ustawienie - wymusza tryb bezekranowy
import matplotlib.pyplot as plt

# 1. Wczytanie danych
plik_wejsciowy = "../dane_symulacja_CSDA/histogramy_weryfikacja_1mln.csv"
plik_wyjsciowy = "../dane_symulacja_CSDA/histogramy_weryfikacja_1mln.png"

df = pd.read_csv(plik_wejsciowy)

# Wybieramy tylko jedną średnicę
wybrana_srednica = df['Srednica_mm'].unique()[0]
df_plot = df[df['Srednica_mm'] == wybrana_srednica]

print(f"Rysowanie histogramów dla średnicy: {wybrana_srednica} mm ({len(df_plot)} cząstek)")

# 2. Konfiguracja parametrów dla każdej zmiennej
zmienne = [
    ('r', 'blue'), ('theta', 'green'), ('phi', 'purple'),
    ('x', 'red'), ('y', 'orange'), ('z', 'brown')
]

# 3. Utworzenie siatki wykresów 2 wiersze x 3 kolumny
fig, axes = plt.subplots(2, 3, figsize=(15, 10))
fig.suptitle(f"Weryfikacja jednorodności przestrzennej Monte Carlo (Sfera {wybrana_srednica} mm)", fontsize=16)

# Spłaszczenie tablicy osi, by łatwiej przypisywać wykresy w pętli
axes = axes.flatten()

# 4. Pętla rysująca
for idx, (nazwa, kolor) in enumerate(zmienne):
    axes[idx].hist(df_plot[nazwa], bins=50, color=kolor, edgecolor='black', alpha=0.7)
    axes[idx].set_title(f"Zmienna: {nazwa}")
    axes[idx].set_xlabel(nazwa)
    axes[idx].set_ylabel("Zliczenia")

# 5. Finalny layout i zapis do pliku
plt.tight_layout(rect=[0, 0.03, 1, 0.95])
plt.savefig(plik_wyjsciowy, dpi=300)

# Zwolnienie pamięci RAM
plt.close(fig)

print(f"Gotowe. Wykres zapisano w: {plik_wyjsciowy}")