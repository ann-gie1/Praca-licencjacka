import pandas as pd
import matplotlib
matplotlib.use('Agg') # Kluczowe ustawienie dla serwera w tle
import matplotlib.pyplot as plt

# 1. Wczytanie danych
plik_wejsciowy = "../dane_symulacja_CSDA/Generacja_danych_1mln.csv"
plik_wyjsciowy = "../dane_symulacja_CSDA/histogram_energii_1mln.png"
df = pd.read_csv(plik_wejsciowy)

# 2. Tworzenie histogramu 1D
plt.figure(figsize=(10, 6))
plt.hist(df['Energia-wylosowana'], bins=100, edgecolor='black', alpha=0.75)

# 3. Konfiguracja osi i wyglądu
plt.title('Rozkład energii', fontsize=14)
plt.xlabel('Energia', fontsize=12)
plt.ylabel('Liczba zliczeń', fontsize=12)
plt.grid(axis='y', alpha=0.5)

# 4. Zapis do pliku
plt.tight_layout()
plt.savefig(plik_wyjsciowy, dpi=300)

# Zwolnienie pamięci RAM
plt.close()

print(f"Gotowe. Wykres zapisano w: {plik_wyjsciowy}")