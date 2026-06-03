import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg') # Tryb bezokienkowy

# 1. Parametry i wczytanie danych
plik_wejsciowy = "../dane_symulacja_CSDA/wyniki_symulacji_1mln-conc_20626.csv"
wall_thickness_mm = 1.0
katalog_wyjsciowy = "../dane_symulacja_CSDA/"

try:
    df = pd.read_csv(plik_wejsciowy)
except FileNotFoundError:
    print(f"Błąd: Nie znaleziono pliku {plik_wejsciowy}. Uruchom najpierw symulację.")
    exit()

# 2. Obliczanie promienia końcowego Rf
df['Rf'] = np.sqrt(df['xf']**2 + df['yf']**2 + df['zf']**2)

# 3. Iteracja po izotopach
izotopy = df['Izotop'].unique()

for iso in izotopy:
    df_iso = df[df['Izotop'] == iso]
    srednice = sorted(df_iso['Srednica_mm'].unique())
    
    # Listy na dane do wykresu
    inside_counts = []
    plastic_counts = []
    outside_counts = []
    
    for d in srednice:
        group = df_iso[df_iso['Srednica_mm'] == d]
        n_total = len(group)
        
        R_in = d / 2.0
        R_out = R_in + wall_thickness_mm
        
        # Klasyfikacja pozycji
        in_sphere = np.sum(group['Rf'] <= R_in)
        in_plastic = np.sum((group['Rf'] > R_in) & (group['Rf'] <= R_out))
        out_system = np.sum(group['Rf'] > R_out)
        
        # Przeliczenie na procenty (opcjonalnie, tutaj zostawiamy surowe zliczenia)
        inside_counts.append(in_sphere)
        plastic_counts.append(in_plastic)
        outside_counts.append(out_system)

    # 4. Tworzenie wykresu
    plt.figure(figsize=(12, 7))
    bar_width = 0.6
    
    # Rysowanie słupków skumulowanych
    p1 = plt.bar(srednice, inside_counts, bar_width, label='Inside the sphere', color='#4CAF50')
    p2 = plt.bar(srednice, plastic_counts, bar_width, bottom=inside_counts, label='Within 1 mm wall', color='#FF9800')
    p3 = plt.bar(srednice, outside_counts, bar_width, bottom=np.array(inside_counts)+np.array(plastic_counts), 
                 label='Spill-out', color='#F44336')

    # Konfiguracja estetyki
    plt.title(f'Spatial distribution of positron stopping points - Isotope: {iso}', fontsize=24)
    plt.xlabel('Sphere diameter [mm] [mm]', fontsize=16)
    plt.ylabel('Simulated positron count', fontsize=16)
    plt.xticks(srednice)
    plt.legend(loc='upper left', bbox_to_anchor=(1, 1))
    plt.grid(axis='y', linestyle='--', alpha=0.6)
    
    # Dodanie etykiet z procentami nad słupkami (opcjonalnie, dla lepszej analizy)
    for idx, d in enumerate(srednice):
        total = inside_counts[idx] + plastic_counts[idx] + outside_counts[idx]
        spill_out_val = (outside_counts[idx] / total) * 100
        plt.text(d, total + (max(outside_counts)*0.02), f'{spill_out_val:.1f}% out', 
                 ha='center', va='bottom', fontsize=9, color='red', fontweight='bold')

    plt.tight_layout()
    
    # 5. Zapis
    nazwa_pliku = f"histogram_miejsce_stop_{iso}_20626.png"
    sciezka_zapisu = f"{katalog_wyjsciowy}{nazwa_pliku}"
    plt.savefig(sciezka_zapisu, dpi=300)
    plt.close()
    print(f"Zapisano wykres dla {iso} w: {sciezka_zapisu}")

print("\nAnaliza zakończona pomyślnie.")