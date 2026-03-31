import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
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

# -------------------------------------------------------
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
nazwa_pliku = f"./dane_symulacja_CSDA/histogram_{wybrany_izotop}_{wybrana_srednica}mm.png"

# Zapis wykresu do pliku PNG (dodano dpi=300 dla wysokiej jakości)
plt.savefig(nazwa_pliku, format='png', dpi=300)

# Zamknięcie figury (brak wyświetlania w oknie)
plt.close()

# 1. Zbieranie danych do wspólnej tabeli
dane_wykres = []

for d in diameters_mm:
    df_d = df_merged[df_merged['Srednica_mm'] == d]
    r_in = d / 2.0
    r_out = r_in + wall_thickness_mm
    
    for izotop in ['18F', '44Sc']:
        rf = df_d[df_d['Izotop'] == izotop]['R_f']
        if len(rf) > 0:
            dane_wykres.append({
                'Średnica': f'{d} mm',
                'Izotop': izotop,
                'Miejsce': 'Wewnątrz sfery\n(woda)',
                'Udział [%]': (np.sum(rf < r_in) / len(rf)) * 100
            })
            dane_wykres.append({
                'Średnica': f'{d} mm',
                'Izotop': izotop,
                'Miejsce': 'Ściana sfery\n(PMMA)',
                'Udział [%]': (np.sum((rf >= r_in) & (rf <= r_out)) / len(rf)) * 100
            })
            dane_wykres.append({
                'Średnica': f'{d} mm',
                'Izotop': izotop,
                'Miejsce': 'Poza sferą\n(woda)',
                'Udział [%]': (np.sum(rf > r_out) / len(rf)) * 100
            })

df_plot = pd.DataFrame(dane_wykres)
# Tworzenie połączonej etykiety do legendy
df_plot['Grupa'] = df_plot['Średnica'] + ' - ' + df_plot['Izotop']

# 2. Rysowanie wspólnego wykresu
plt.figure(figsize=(14, 7))

# Używamy seaborn do automatycznego pogrupowania słupków obok siebie
ax = sns.barplot(
    data=df_plot, 
    x='Miejsce', 
    y='Udział [%]', 
    hue='Grupa', 
    edgecolor='black'
)

# Funkcja do dodawania etykiet na słupkach
for p in ax.patches:
    height = p.get_height()
    # seaborn tworzy puste słupki (nan) tam, gdzie nie ma danych, więc trzeba to obsłużyć
    if not np.isnan(height) and height > 0:
        ax.annotate(f'{height:.1f}%', 
                    (p.get_x() + p.get_width() / 2., height),
                    ha='center', va='bottom', fontsize=8, fontweight='bold', 
                    xytext=(0, 3), textcoords='offset points', rotation=90)

# Formatowanie
plt.title('Miejsce anihilacji pozytonów - Wszystkie średnice (18F vs 44Sc)', fontsize=14, fontweight='bold')
plt.ylabel('Udział [%]', fontsize=12)
plt.xlabel('')
plt.legend(title='Średnica - Izotop', bbox_to_anchor=(1.01, 1), loc='upper left', fontsize=10)
plt.grid(axis='y', linestyle='--', alpha=0.7)

# Dynamiczne skalowanie osi Y
max_y = df_plot['Udział [%]'].max() if not df_plot.empty else 100
plt.ylim(0, max_y + 15)

plt.tight_layout()

# Zapis zbiorczego wykresu
plt.savefig('./dane_symulacja_CSDA/porownanie_anihilacji_wszystkie.png', format='png', dpi=300)
plt.close()