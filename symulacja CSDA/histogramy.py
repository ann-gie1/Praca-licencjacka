import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
# -------------------------------------------------------
# Zmienne i funkcje fizyczne
# -------------------------------------------------------
m_e = 0.511                 # masa elektronu w [MeV/c2]
rho_water = 1.0           # gęstość wody [g/cm^3]
rho_plastic = 1.18        # gęstość plastiku (np. PMMA/Akryl) [g/cm^3]
wall_thickness_mm = 1.0   # Grubość ścianki w [mm] 

isotopes = {"18F": (0.634, 8), "44Sc": (1.474, 20)} 
diameters_mm = [10, 13, 17, 22, 28, 37]

# -------------------------------------------------------
# Przetwarzanie danych
# -------------------------------------------------------
df = pd.read_csv("./dane_symulacja_CSDA/Generacja_danych.csv")
df1 = pd.read_csv("./dane_symulacja_CSDA/wyniki_symulacji.csv")

# Łączenie plików ZA ZANIM zaczniemy liczyć i grupować
df_merged = pd.merge(df, df1, on=['Index', 'Izotop', 'Srednica_mm'])

# Obliczamy promień finalny
df_merged['R_f'] = np.sqrt(df_merged['xf']**2 + df_merged['yf']**2 + df_merged['zf']**2)

# Kategoryzacja wektorowa (zależna od średnicy w danym wierszu)
df_merged['R_in'] = df_merged['Srednica_mm'] / 2.0
df_merged['R_out'] = df_merged['R_in'] + wall_thickness_mm

conditions = [
    df_merged['R_f'] < df_merged['R_in'],
    df_merged['R_f'] <= df_merged['R_out']
]
choices = ['Wewnątrz', 'W materiale']
df_merged['Kategoria'] = np.select(conditions, choices, default='Na zewnątrz')

# Grupowanie na POŁĄCZONYM DataFrame
grouped_df = df_merged.groupby(['Izotop', 'Srednica_mm'])

results_18F = []
results_44Sc = []

for (iso, d), group in grouped_df:
    Rf = group['R_f']
    R_in = d / 2.0
    N_sim = int(len(df)/len(grouped_df))
    
    # Spill-out
    spill_out_percent = (np.sum(Rf > R_in) / N_sim) * 100.0
    
    row = {
        "Średnica sfery [mm]": d,
        "Max R końcowy [mm]": round(np.max(Rf), 3),
        "Średni R końcowy [mm]": round(np.mean(Rf), 3),
        "Mediana R końcowego [mm]": round(np.median(Rf), 3),
        "Spill-out PVE [%]": round(spill_out_percent, 1)
    }
    
    if iso == "18F":
        results_18F.append(row)
    else:
        results_44Sc.append(row)

print("Symulacja zakończona. Generuję wykres...")        

# Sortowanie wyników dla pewności spójności na osi X
results_18F = sorted(results_18F, key=lambda x: x["Średnica sfery [mm]"])
results_44Sc = sorted(results_44Sc, key=lambda x: x["Średnica sfery [mm]"])

# Ekstrakcja danych do wykresu
pve_18F = [r["Spill-out PVE [%]"] for r in results_18F]
pve_44Sc = [r["Spill-out PVE [%]"] for r in results_44Sc]

# -------------------------------------------------------
# Generowanie i formatowanie wykresu słupkowego
# -------------------------------------------------------
x = np.arange(len(diameters_mm))
width = 0.35

plt.figure(figsize=(10, 6))
bars1 = plt.bar(x - width/2, pve_18F, width, label='18F', color='royalblue', alpha=0.8, edgecolor='black', linewidth=0.5)
bars2 = plt.bar(x + width/2, pve_44Sc, width, label='44Sc', color='crimson', alpha=0.8, edgecolor='black', linewidth=0.5)

plt.xlabel('Średnica wewnętrzna sfery [mm]', fontsize=12, fontweight='bold')
plt.ylabel('Spill-out PVE [%]', fontsize=12, fontweight='bold')
plt.title('Porównanie ucieczki pozytonów ze sfery (Spill-out PVE)\nna podstawie R_mean (uwzględniono ściankę PMMA 1mm)', fontsize=14)
plt.xticks(x, [f'{d} mm' for d in diameters_mm], fontsize=11)
plt.yticks(fontsize=11)
plt.legend(fontsize=11)
plt.grid(axis='y', linestyle='--', alpha=0.7)

def add_labels(bars):
    for bar in bars:
        height = bar.get_height()
        plt.annotate(f'{height:.1f}%',
                     xy=(bar.get_x() + bar.get_width() / 2, height),
                     xytext=(0, 4), 
                     textcoords="offset points",
                     ha='center', va='bottom', fontsize=10)

add_labels(bars1)
add_labels(bars2)

plt.tight_layout()
# Zapis wykresu do pliku PNG (dodano dpi=300 dla wysokiej jakości)
plt.savefig("./dane_symulacja_CSDA/Histogram spill-out.png", format='png', dpi=300)

# Zamknięcie figury (brak wyświetlania w oknie)
plt.close()
