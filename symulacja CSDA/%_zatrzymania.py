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

for (iso, d), group in grouped_df:
    Rf = group['R_f']
    R_in = d / 2.0
    N_sim = int(len(df)/len(grouped_df))

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
# Tworzenie połączonej etykiety do legendy (nie jest już kluczowa, ale zostawiamy)
df_plot['Grupa'] = df_plot['Średnica'] + ' - ' + df_plot['Izotop']

# 2. Rysowanie wykresów w siatce 2x3
fig, axes = plt.subplots(nrows=2, ncols=3, figsize=(18, 12))
axes = axes.flatten()  # Spłaszczamy tablicę osi, aby ułatwić iterację

for i, d in enumerate(diameters_mm):
    ax = axes[i]
    # Filtrowanie danych tylko dla konkretnej średnicy
    df_sub = df_plot[df_plot['Średnica'] == f'{d} mm']
    
    sns.barplot(
        data=df_sub, 
        x='Miejsce', 
        y='Udział [%]', 
        hue='Izotop',  # Średnicę mamy w tytule, więc tu grupujemy tylko po izotopie
        edgecolor='black',
        ax=ax
    )

    # Funkcja do dodawania etykiet na słupkach dla danego podwykresu
    for p in ax.patches:
        height = p.get_height()
        if not np.isnan(height) and height > 0:
            ax.annotate(f'{height:.1f}%', 
                        (p.get_x() + p.get_width() / 2., height),
                        ha='center', va='bottom', fontsize=9, fontweight='bold', 
                        xytext=(0, 3), textcoords='offset points')

    # Formatowanie pojedynczego podwykresu
    ax.set_title(f'Średnica: {d} mm', fontsize=12, fontweight='bold')
    ax.set_xlabel('')
    ax.set_ylabel('Udział [%]' if i % 3 == 0 else '') # Y label tylko dla lewej kolumny
    
    # Stała oś Y [0, 110] na wszystkich wykresach dla rzetelnego porównania
    ax.set_ylim(0, 110) 
    ax.grid(axis='y', linestyle='--', alpha=0.7)
    
    # Zostawiamy legendę tylko na pierwszym wykresie, aby nie śmiecić
    if i == 0:
        ax.legend(title='Izotop', loc='upper right')
    else:
        ax.get_legend().remove()

# Tytuł główny dla całej figury
plt.suptitle('Miejsce anihilacji pozytonów (18F vs 44Sc) w zależności od średnicy sfery', fontsize=16, fontweight='bold')
plt.tight_layout()

# Zapis zbiorczego wykresu
plt.savefig('./dane_symulacja_CSDA/porownanie_anihilacji_siatka.png', format='png', dpi=300)
plt.close()