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
df = pd.read_csv("./dane_symulacja_cal_gonzales/Generacja_danych_c-g.csv")
df1 = pd.read_csv("./dane_symulacja_cal_gonzales/wyniki_symulacji_C-G.csv")

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

for (iso, d), group in grouped_df:
    Rf = group['R_f']
    R_in = d / 2.0
    N_sim = int(len(df)/len(grouped_df))

# Rysowanie histogramu dla JEDNEJ, wybranej średnicy
# -------------------------------------------------------
# 2. Interaktywny wybór w konsoli
print(f"Dostępne izotopy: {df['Izotop'].unique()}")
wybrany_izotop = input("Wpisz nazwę izotopu: ")

print(f"Dostępne średnice sfery (mm): {df['Srednica_mm'].unique()}")
wybrana_srednica = float(input("Wpisz średnicę sfery: "))
# Weryfikacja poprawności wyboru
if wybrana_srednica not in diameters_mm:
    raise ValueError(f"Błąd: Średnica {wybrana_srednica} mm nie występuje w danych. Dostępne to: {diameters_mm}")

# Filtrowanie danych tylko dla wybranej sfery
df_wybrane = df_merged[df_merged['Srednica_mm'] == wybrana_srednica]

# Obliczenie fizycznych granic sfery
r_in = wybrana_srednica / 2.0
r_out = r_in + wall_thickness_mm

# Parametry histogramu (wspólne kosze dla obu izotopów)
max_rf = df_wybrane['R_f'].max()
bins = np.linspace(0, max_rf, 80)

# Generowanie wykresu
plt.figure(figsize=(10, 6))

# Selektywne rysowanie histogramów
if wybrany_izotop in ['18F']:
    rf_18F = df_wybrane[df_wybrane['Izotop'] == '18F']['R_f']
    plt.hist(rf_18F, bins=bins, alpha=0.6, color='royalblue', label='18F', edgecolor='black', linewidth=0.5)

if wybrany_izotop in ['44Sc']:
    rf_44Sc = df_wybrane[df_wybrane['Izotop'] == '44Sc']['R_f']
    plt.hist(rf_44Sc, bins=bins, alpha=0.6, color='crimson', label='44Sc', edgecolor='black', linewidth=0.5)

# Zaznaczenie granic materiałów
plt.axvline(x=r_in, color='black', linestyle='--', linewidth=1.5, label='Krawędź wewn. (woda/PMMA)')
plt.axvline(x=r_out, color='gray', linestyle=':', linewidth=1.5, label='Krawędź zewn. (PMMA/woda)')

# Formatowanie
plt.title(f'1D Histogram zasięgu pozytonów - Sfera {wybrana_srednica} mm ({wybrany_izotop})', fontsize=14, fontweight='bold')
plt.xlabel('Odległość anihilacji od środka (R_f) [mm]', fontsize=12)
plt.ylabel('Liczba zdarzeń', fontsize=12)
plt.legend(fontsize=11)
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.xlim(0, max_rf)

plt.tight_layout()
nazwa_pliku = f"./dane_symulacja_cal_gonzales/histogram_{wybrany_izotop}_{wybrana_srednica}mm.png"

# Zapis wykresu do pliku PNG (dodano dpi=300 dla wysokiej jakości)
plt.savefig(nazwa_pliku, format='png', dpi=300)

# Zamknięcie figury (brak wyświetlania w oknie)
plt.close()