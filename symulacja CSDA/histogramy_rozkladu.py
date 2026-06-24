import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# 1. Globalna zmiana rozmiaru czcionek (zgodnie z poprzednim skryptem)
plt.rcParams.update({
    'font.size': 36,
    'axes.labelsize': 36,
    'axes.titlesize': 36,
    'xtick.labelsize': 30,
    'ytick.labelsize': 30
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

# 3. Utworzenie siatki wykresów (powiększony rozmiar)
fig, axes = plt.subplots(2, 3, figsize=(30, 18))

# Główny tytuł po angielsku
fig.suptitle(f"Monte Carlo Spatial Uniformity Verification (Sphere {wybrana_srednica} mm)", fontsize=40)

axes = axes.flatten()

# 4. Pętla rysująca
for idx, (nazwa, kolor) in enumerate(zmienne):
    axes[idx].hist(df_plot[nazwa], bins=50, color=kolor, edgecolor='black', alpha=0.7)
    axes[idx].set_title(f"Variable: {nazwa}")
    axes[idx].set_xlabel(nazwa)
    axes[idx].set_ylabel("Counts")
    
    # Dodatkowy margines na osi Y dla czytelności
    y_max = axes[idx].get_ylim()[1]
    axes[idx].set_ylim(0, y_max * 1.1)

# 5. Finalny layout i zapis do pliku
plt.tight_layout(rect=[0, 0.03, 1, 0.90])
plt.savefig(plik_wyjsciowy, dpi=300, bbox_inches='tight')

# Zwolnienie pamięci RAM
plt.close(fig)

print(f"Gotowe. Wykres zapisano w: {plik_wyjsciowy}")