import matplotlib
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

# --- Konfiguracja ---
matplotlib.use('Agg')

# Globalne powiększenie wszystkich czcionek o kolejne 12 pkt
plt.rcParams.update({
    'font.size': 36,            # Zwiększone z 24 do 36
    'axes.labelsize': 36,       # Rozmiar etykiet osi X i Y
    'axes.titlesize': 36,       # Rozmiar tytułów podwykresów
    'xtick.labelsize': 30,      # Rozmiar wartości na osi X
    'ytick.labelsize': 30       # Rozmiar wartości na osi Y
})

katalog_danych = "../dane_symulacja_CSDA"
nazwa_pliku_wejsciowego = "Generacja_danych_1mln-conc.csv"
nazwa_pliku_wyjsciowego = "histogramy_kierunek_10mm_18F.png"

plik_wejsciowy = os.path.join(katalog_danych, nazwa_pliku_wejsciowego)
plik_wyjsciowy = os.path.join(katalog_danych, nazwa_pliku_wyjsciowego)

izotop_cel = "18F"
srednica_cel = 10

# --- 1. Wczytanie i Filtrowanie Danych ---
print(f"Loading data from: {plik_wejsciowy}")

if not os.path.exists(plik_wejsciowy):
    raise FileNotFoundError(f"Input file not found: {plik_wejsciowy}. Run the data generation script first.")

try:
    df_all = pd.read_csv(plik_wejsciowy)
except Exception as e:
    raise IOError(f"Error reading CSV file: {e}")

print("Data loaded successfully. Filtering for Isotope 18F and Sphere 10mm...")

df = df_all[(df_all['Izotop'] == izotop_cel) & (df_all['Srednica_mm'] == srednica_cel)].copy()

if df.empty:
    raise ValueError(f"No data found matching criteria: Isotope='{izotop_cel}', Diameter={srednica_cel} mm.")

print(f"Found {len(df)} events for Isotope 18F and Sphere 10mm. Calculating angles...")

del df_all

# --- 2. Obliczenie Kątów Kierunku ---
df['phi_dir'] = np.arccos(df['dz'])
theta_raw = np.arctan2(df['dy'], df['dx'])
df['theta_dir'] = (theta_raw + 2 * np.pi) % (2 * np.pi)

print("Angle calculations complete. Generating histograms...")

# --- 3. Generowanie Histogramów ---
# Zwiększono rozmiar z (20, 12) na (30, 18), aby gigantyczne opisy tekstowe się pomieściły
fig, axes = plt.subplots(2, 3, figsize=(30, 18))
overall_title = f"Monte Carlo Directional Uniformity Verification (Isotope: {izotop_cel}, Sphere: {srednica_cel} mm)"
fig.suptitle(overall_title, fontsize=40) # Zwiększone z 28 do 40

# Ukrywamy lewy górny wykres, żeby odwzorować układ (brak 'r')
axes[0, 0].axis('off')

# Konfiguracja zmiennych: (nazwa_kolumny, kolor, obiekt_osi, tytul, os_x, zakres)
zmienne_dir = [
    ('theta_dir', '#4daf4a', axes[0, 1], r'Variable: theta', 'theta (rad)', (0, 2*np.pi)),
    ('phi_dir', '#984ea3', axes[0, 2], r'Variable: phi', 'phi (rad)', (0, np.pi)),
    ('dx', '#e41a1c', axes[1, 0], 'Variable: dx', 'dx', (-1, 1)),
    ('dy', '#ff7f00', axes[1, 1], 'Variable: dy', 'dy', (-1, 1)),
    ('dz', '#a65628', axes[1, 2], 'Variable: dz', 'dz', (-1, 1))
]

bins_count = 50

for var_name, color, ax, title_label, x_label, current_range in zmienne_dir:
    ax.hist(df[var_name], bins=bins_count, color=color, edgecolor='black', alpha=0.8, range=current_range)
    ax.set_title(title_label)
    ax.set_xlabel(x_label)
    ax.set_ylabel("Counts")
    ax.set_xlim(current_range)
    
    # Dodatkowe marginesy osi Y dla czytelności
    y_max = ax.get_ylim()[1]
    ax.set_ylim(0, y_max * 1.1)

# --- 4. Finalny Układ i Zapis ---
# Zmniejszono górny margines z 0.95 na 0.90, aby zapobiec nakładaniu się głównego tytułu na wykresy
plt.tight_layout(rect=[0, 0.03, 1, 0.90])

print(f"Saving plot to: {plik_wyjsciowy}")
plt.savefig(plik_wyjsciowy, dpi=300, bbox_inches='tight')

plt.close(fig)
print(f"Done. Plot saved at: {plik_wyjsciowy}")