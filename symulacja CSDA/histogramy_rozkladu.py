import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# 1. Globalna zmiana rozmiaru czcionek (+12 pkt do wartości domyślnych)
plt.rcParams.update({
    'font.size': 22,          # Ticks (domyślnie 10 -> 22)
    'axes.labelsize': 22,     # Etykiety osi X i Y (domyślnie 10 -> 22)
    'axes.titlesize': 24      # Tytuły poszczególnych wykresów (domyślnie 12 -> 24)
})

# Wczytanie danych
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

# 3. Utworzenie siatki wykresów
# Zwiększono figsize z (15, 10) na (22, 14), aby pomieścić większe teksty
fig, axes = plt.subplots(2, 3, figsize=(22, 14))

# Główny tytuł powiększony z 24 na 36
fig.suptitle(f"Weryfikacja jednorodności przestrzennej Monte Carlo (Sfera {wybrana_srednica} mm)", fontsize=36)

axes = axes.flatten()

# 4. Pętla rysująca
for idx, (nazwa, kolor) in enumerate(zmienne):
    axes[idx].hist(df_plot[nazwa], bins=50, color=kolor, edgecolor='black', alpha=0.7)
    axes[idx].set_title(f"Zmienna: {nazwa}")
    axes[idx].set_xlabel(nazwa)
    axes[idx].set_ylabel("Zliczenia")

# 5. Finalny layout i zapis do pliku
# Skorygowano górny margines (0.93), aby ogromny tytuł główny nie obcinał się na krawędzi
plt.tight_layout(rect=[0, 0.03, 1, 0.93])
plt.savefig(plik_wyjsciowy, dpi=300)

# Zwolnienie pamięci RAM
plt.close(fig)

print(f"Gotowe. Wykres zapisano w: {plik_wyjsciowy}")