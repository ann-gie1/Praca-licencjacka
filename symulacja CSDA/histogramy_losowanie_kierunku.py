import matplotlib
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

# --- Konfiguracja ---
matplotlib.use('Agg') # Tryb bezokienkowy - kluczowe dla działania na serwerze lub w tle

# Ścieżki - oparte na strukturze Twojego kodu generującego dane
katalog_danych = "../dane_symulacja_CSDA"
nazwa_pliku_wejsciowego = "Generacja_danych_1mln-conc.csv"
nazwa_pliku_wyjsciowego = "histogramy_kierunek_10mm_18F.png"

plik_wejsciowy = os.path.join(katalog_danych, nazwa_pliku_wejsciowego)
plik_wyjsciowy = os.path.join(katalog_danych, nazwa_pliku_wyjsciowego)

# Docelowe kryteria
izotop_cel = "18F"
srednica_cel = 10

# --- 1. Wczytanie i Filtrowanie Danych ---
print(f"Podejmowanie próby wczytania danych z: {plik_wejsciowy}")

# Sprawdzenie, czy plik istnieje
if not os.path.exists(plik_wejsciowy):
    raise FileNotFoundError(f"Nie znaleziono pliku wejściowego: {plik_wejsciowy}. Uruchom najpierw kod generujący dane.")

try:
    # Wczytujemy dane
    df_all = pd.read_csv(plik_wejsciowy)
except Exception as e:
    raise IOError(f"Błąd podczas odczytu pliku CSV: {e}")

print("Pomyślnie wczytano dane. Rozpoczynam filtrowanie dla Izotopu 18F i Sfery 10mm...")

# Filtrowanie dla konkretnego izotopu i średnicy
# Używamy boolean indexing dla pewności
df = df_all[(df_all['Izotop'] == izotop_cel) & (df_all['Srednica_mm'] == srednica_cel)].copy()

# Sprawdzenie, czy znaleziono dane
if df.empty:
    raise ValueError(f"Nie znaleziono danych pasujących do kryteriów: Izotop='{izotop_cel}', Srednica_mm={srednica_cel}.")

print(f"Znaleziono {len(df)} zdarzeń dla Izotopu 18F i Sfery 10mm. Przechodzę do obliczeń kątów...")

# Usuwamy dużą ramkę danych, aby zwolnić pamięć
del df_all

# --- 2. Obliczenie Kątów Kierunku ---
# Plik CSV przechowuje dx, dy, dz. Musimy je przeliczyć z powrotem na kąty sferyczne.
# Na podstawie fizyki z Twojego kodu generującego:
# dx = sin_phi_dir * cos_theta_dir
# dy = sin_phi_dir * sin_theta_dir
# dz = cos_phi_dir

# 2a. Kąt Polarny (phi, zakres: 0, pi)
# dz = cos(phi) -> phi = arccos(dz)
df['phi_dir'] = np.arccos(df['dz'])

# 2b. Kąt Azymutalny (theta, zakres: 0, 2pi)
# dy/dx = tan(theta) -> theta = arctan2(dy, dx)
# arctan2 zwraca kąt w zakresie (-pi, pi]
theta_raw = np.arctan2(df['dy'], df['dx'])
# Przesuwamy zakres do 0, 2pi, aby pasował do losowania w kodzie generującym
df['theta_dir'] = (theta_raw + 2 * np.pi) % (2 * np.pi)

print("Obliczenia kątów zakończone. Generowanie histogramów...")

# --- 3. Generowanie Histogramów (Adaptacja Logiki Odniesienia) ---

# Konfiguracja zmiennych do wykresów, pasujących do żądanych kątów kierunku
zmienne_dir = [
    # (nazwa_kolumny, kolor, etykieta_osi_x, etykieta_tytułu, opis_zakresu)
    ('theta_dir', 'green', r'Kąt Azymutalny (radians)', r'Direction ($\theta_{dir}$)', '(Zakres: 0, 2$\pi$)'),
    ('phi_dir', 'purple', r'Kąt Polarny (radians)', r'Direction ($\phi_{dir}$)', '(Zakres: 0, $\pi$)')
]

# Utworzenie siatki wykresów 2 wiersze x 1 kolumna
fig, axes = plt.subplots(2, 1, figsize=(10, 12), sharey=False)
overall_title = f"Weryfikacja jednorodności kierunku Monte Carlo (Izotop: {izotop_cel}, Sfera: {srednica_cel} mm)"
fig.suptitle(overall_title, fontsize=16)

# Pętla rysująca (używając enumerate dla subplotów i listy zmiennych)
bins_count = 50 # Utrzymano standard z kodu odniesienia

for idx, (var_name, color, x_label, title_label, range_label) in enumerate(zmienne_dir):
    # Ustawienie zakresu, jeśli to możliwe, dla weryfikacji wizualnej
    current_range = None
    if var_name == 'theta_dir':
        current_range = (0, 2*np.pi)
    elif var_name == 'phi_dir':
        current_range = (0, np.pi)

    axes[idx].hist(df[var_name], bins=bins_count, color=color, edgecolor='black', alpha=0.7, range=current_range)
    axes[idx].set_title(f"Zmienna: {title_label} {range_label}", fontsize=12)
    axes[idx].set_xlabel(x_label, fontsize=10)
    axes[idx].set_ylabel("Zliczenia", fontsize=10)
    axes[idx].grid(axis='y', alpha=0.5)

# --- 4. Finalny Układ i Zapis ---
# Dopasowanie logiczne tight_layout z kodu odniesienia
plt.tight_layout(rect=[0, 0.03, 1, 0.95])

print(f"Zapisywanie wykresu do: {plik_wyjsciowy}")
plt.savefig(plik_wyjsciowy, dpi=300)

# Zwolnienie pamięci RAM
plt.close(fig)

print(f"Gotowe. Wykres zapisano w: {plik_wyjsciowy}")