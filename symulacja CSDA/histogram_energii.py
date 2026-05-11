import pandas as pd
import matplotlib
matplotlib.use('Agg') # Kluczowe ustawienie dla serwera w tle
import matplotlib.pyplot as plt
import os

# 1. Wczytanie danych i przygotowanie ścieżek
plik_wejsciowy = "../dane_symulacja_CSDA/Generacja_danych_1mln.csv"
katalog_wyjsciowy = "../dane_symulacja_CSDA/"

df = pd.read_csv(plik_wejsciowy)

# Sprawdzenie, czy kolumny istnieją (dobra praktyka)
if 'izotop' not in df.columns or 'Energia-wylosowana' not in df.columns:
    raise ValueError("Plik CSV nie zawiera wymaganych kolumn: 'izotop' lub 'Energia-wylosowana'")

# Pobranie listy unikalnych izotopów
izotopy = df['izotop'].unique()

# 2. Generowanie wykresów w pętli
for izotop in izotopy:
    # Filtrowanie danych dla bieżącego izotopu
    df_izotop = df[df['izotop'] == izotop]
    
    # Tworzenie histogramu 1D
    plt.figure(figsize=(10, 6))
    plt.hist(df_izotop['Energia-wylosowana'], bins=100, edgecolor='black', alpha=0.75)

    # 3. Konfiguracja osi i wyglądu
    plt.title(f'Rozkład energii - {izotop}', fontsize=14)
    plt.xlabel('Energia', fontsize=12)
    plt.ylabel('Liczba zliczeń', fontsize=12)
    plt.grid(axis='y', alpha=0.5)

    # 4. Zapis do pliku
    # Czyszczenie nazwy izotopu (np. na wypadek znaków specjalnych/spacji)
    bezpieczna_nazwa_izotopu = str(izotop).replace(" ", "_").replace("/", "_")
    nazwa_pliku = f"histogram_energii_{bezpieczna_nazwa_izotopu}.png"
    plik_wyjsciowy = os.path.join(katalog_wyjsciowy, nazwa_pliku)
    
    plt.tight_layout()
    plt.savefig(plik_wyjsciowy, dpi=300)

    # Zwolnienie pamięci RAM
    plt.close()
    print(f"Wygenerowano: {plik_wyjsciowy}")

print("Gotowe. Wszystkie wykresy zostały zapisane.")