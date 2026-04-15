"""import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

# -------------------------------------------------------
# Parametry i Funkcje
# -------------------------------------------------------
m_e = 0.511
rho = 1.0  # g/cm^3

isotopes = {
    "18F":  (0.634, 8),
    "44Sc": (1.474, 20),
    "68Ga": (1.899, 30)
}

def momentum(E):
    return np.sqrt(E**2 + 2 * m_e * E)

def fermi_function_allowed(Z, E):
    alpha = 1/137
    p = momentum(E)
    if p == 0: return 0 
    eta = alpha * Z * (E + m_e) / p
    if eta > 100: return 1 
    return (2 * np.pi * eta) / (1 - np.exp(-2 * np.pi * eta))

def beta_plus_spectrum(E, E0, Z):
    p = momentum(E)
    F = fermi_function_allowed(Z, E)
    return p * E * (E0 - E)**2 * F

# Funkcja do ciągłej linii (tło)
def compute_X_continuous(E):
    if E <= 1e-9: return 0
    r = 0.412 * E**(1.265 - 0.0954 * np.log(E))
    return (r / rho) * 10

# Wzór (4) ze zdjęcia: Średni zasięg
def formula_R_mean_image(E_mean_val):
    # 0.108 * E^1.14 / rho. Wynik w cm -> *10 na mm
    return (0.108 * (E_mean_val**1.14) / rho) * 10

# Wzór (5) i (6) ze zdjęcia: Maksymalny zasięg
def formula_R_max_image(E_max_val):
    rho_mg = rho * 1000 
    R_cm = 0
    if 0.01 <= E_max_val <= 2.5:
        n = 1.265 - 0.0954 * np.log(E_max_val)
        R_cm = (412 * E_max_val**n) / rho_mg
    elif 2.5 < E_max_val <= 20:
        R_cm = (530 * E_max_val - 106) / rho_mg
    return R_cm * 10

# -------------------------------------------------------
# Obliczenia
# -------------------------------------------------------
results_data = []
percentiles_to_check = [0.1, 0.5, 0.9] # Skrócona lista do tabeli

# Przygotowanie danych do wykresu
plot_data = {}

for name, (E0, Z) in isotopes.items():
    E_space = np.linspace(1e-4, E0, 3000)
    spectrum = np.array([beta_plus_spectrum(e, E0, Z) for e in E_space])
    
    # Percentyle
    cdf = np.cumsum(spectrum)
    cdf = cdf / cdf[-1]
    
    # 1. Obliczenie wartości do tabeli i punktów
    E_mean_spectrum = np.average(E_space, weights=spectrum)
    
    # Zasięgi wg wzorów ze zdjęcia
    R_mean_img = formula_R_mean_image(E_mean_spectrum)
    R_max_img = formula_R_max_image(E0)
    
    # Zbieranie danych do tabeli
    row = {"Izotop": name, "E_max [MeV]": round(E0, 3), "E_mean [MeV]": round(E_mean_spectrum, 3)}
    
    # Dodajemy percentyle do tabeli
    E_perc = np.interp(percentiles_to_check, cdf, E_space)
    X_perc = [compute_X_continuous(e) for e in E_perc]
    for p, x in zip(percentiles_to_check, X_perc):
        row[f"R_{int(p*100)}%"] = round(x, 2)
        
    row["R_mean (Wzór 4)"] = round(R_mean_img, 2)
    row["R_max (Wzór 5/6)"] = round(R_max_img, 2)
    results_data.append(row)
    
    # Zapis danych do późniejszego narysowania
    plot_data[name] = {
        "E_space": E_space,
        "cdf": cdf,
        "E_mean": E_mean_spectrum,
        "R_mean_img": R_mean_img,
        "R_max_img": R_max_img,
        "E0": E0
    }

# -------------------------------------------------------
# EKSPORT TABELI (Przed wykresem!)
# -------------------------------------------------------
df = pd.DataFrame(results_data)
cols = ["Izotop", "E_mean [MeV]", "R_10%", "R_50%", "R_90%", "R_mean (Wzór 4)", "R_max (Wzór 5/6)"]
df_clean = df[cols]

print("--- TABELA WYNIKÓW ---")
print(df_clean.to_string(index=False))

# Zapis do pliku tekstowego
output_file = "tabela_zasiegow.txt"
with open(output_file, "w", encoding="utf-8") as f:
    f.write(df_clean.to_string(index=False))
print(f"\n[INFO] Tabelę zapisano w pliku: {output_file}")

# -------------------------------------------------------
# RYSOWANIE WYKRESU
# -------------------------------------------------------
plt.figure(figsize=(11, 7))
colors = {"18F": "tab:blue", "44Sc": "tab:green", "68Ga": "tab:red"}
percentiles_plot = np.arange(0.1, 1.0, 0.1)

for name, data in plot_data.items():
    col = colors[name]
    
    # 1. Tło (ścieżka percentyli)
    E_p = np.interp(percentiles_plot, data["cdf"], data["E_space"])
    X_p = [compute_X_continuous(e) for e in E_p]
    plt.plot(E_p, X_p, '--', color=col, alpha=0.4)
    plt.scatter(E_p, X_p, color=col, alpha=0.4, s=20)
    
    # 2. PUNKT ZE WZORU 4 (ŚREDNI) - Zółty kwadrat
    plt.scatter(data["E_mean"], data["R_mean_img"], 
                color='yellow', marker='s', s=150, edgecolors='black', linewidth=1.5, zorder=100)
    
    # 3. PUNKT ZE WZORU 5/6 (MAX) - Diament w kolorze izotopu
    plt.scatter(data["E0"], data["R_max_img"], 
                color=col, marker='D', s=120, edgecolors='black', zorder=100)
    
    # Etykiety
    plt.annotate(name, (data["E0"], data["R_max_img"]), xytext=(5, 0), textcoords="offset points", fontweight='bold', color=col)

# Legenda
from matplotlib.lines import Line2D
legend_elements = [
    Line2D([0], [0], marker='s', color='w', markerfacecolor='yellow', markeredgecolor='black', markersize=10, label='Średni zasięg (Wzór mgr. Mryka'),
    Line2D([0], [0], marker='D', color='w', markerfacecolor='gray', markeredgecolor='black', markersize=8, label='Max zasięg (Wzór mgr. Mryka)'),
    Line2D([0], [0], linestyle='--', color='gray', label='Percentyle (10-90%)')
]

plt.legend(handles=legend_elements, loc='upper left')
plt.xlabel("Energia [MeV]")
plt.ylabel("Zasięg [mm]")
plt.title("Weryfikacja wzorów na zasięg pozytonu")
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.show()"""


"""import numpy as np
import matplotlib.pyplot as plt

# -------------------------------------------------------
# Parametry i Funkcje Fizyczne
# -------------------------------------------------------
m_e = 0.511
rho = 1.0  # g/cm^3

isotopes = {
    "18F":  (0.634, 8),
    "44Sc": (1.474, 20),
    "68Ga": (1.899, 30)
}

def momentum(E):
    return np.sqrt(E**2 + 2 * m_e * E)

def fermi_function_allowed(Z, E):
    alpha = 1/137
    p = momentum(E)
    if p == 0: return 0 
    eta = alpha * Z * (E + m_e) / p
    if eta > 100: return 1 
    return (2 * np.pi * eta) / (1 - np.exp(-2 * np.pi * eta))

def beta_plus_spectrum(E, E0, Z):
    p = momentum(E)
    F = fermi_function_allowed(Z, E)
    return p * E * (E0 - E)**2 * F

# Funkcja ciągła (do rysowania linii percentyli i punktu 50%)
def compute_X_continuous(E):
    if E <= 1e-9: return 0
    r = 0.412 * E**(1.265 - 0.0954 * np.log(E))
    return (r / rho) * 10

# Wzór (4): Średni zasięg
def formula_R_mean_image(E_mean_val):
    return (0.108 * (E_mean_val**1.14) / rho) * 10

# Wzory (5) i (6): Maksymalny zasięg
def formula_R_max_image(E_max_val):
    rho_mg = rho * 1000 
    R_cm = 0
    if 0.01 <= E_max_val <= 2.5:
        n = 1.265 - 0.0954 * np.log(E_max_val)
        R_cm = (412 * E_max_val**n) / rho_mg
    elif 2.5 < E_max_val <= 20:
        R_cm = (530 * E_max_val - 106) / rho_mg
    return R_cm * 10

# -------------------------------------------------------
# RYSOWANIE
# -------------------------------------------------------
plt.figure(figsize=(12, 8))
colors = {"18F": "tab:blue", "44Sc": "tab:green", "68Ga": "tab:red"}
percentiles_plot = np.arange(0.1, 1.0, 0.1)

for name, (E0, Z) in isotopes.items():
    col = colors[name]
    
    # 1. Generowanie danych
    E_space = np.linspace(1e-4, E0, 3000)
    spectrum = np.array([beta_plus_spectrum(e, E0, Z) for e in E_space])
    
    # Dystrybuanta
    cdf = np.cumsum(spectrum)
    cdf = cdf / cdf[-1]
    
    # --- Rysowanie tła (linii percentyli) ---
    E_p = np.interp(percentiles_plot, cdf, E_space)
    X_p = [compute_X_continuous(e) for e in E_p]
    plt.plot(E_p, X_p, '--', color=col, alpha=0.3)
    plt.scatter(E_p, X_p, color=col, alpha=0.3, s=15)

    # ==========================================================
    # PUNKTY CHARAKTERYSTYCZNE I ETYKIETY
    # ==========================================================
    
    # A. PERCENTYL 50% (Mediana) -> GWIAZDKA (*)
    E_50 = np.interp(0.5, cdf, E_space)
    R_50 = compute_X_continuous(E_50)
    
    plt.scatter(E_50, R_50, color=col, marker='*', s=200, edgecolors='black', zorder=10)
    # Etykieta nad gwiazdką
    plt.annotate(f"50%\n({E_50:.2f}, {R_50:.2f})", 
                 (E_50, R_50), xytext=(0, 25), textcoords="offset points", 
                 ha='center', fontsize=8, color=col, fontweight='bold')

    # B. ŚREDNIA ZE WZORU 4 -> ŻÓŁTY KWADRAT (s)
    E_mean_spect = np.average(E_space, weights=spectrum)
    R_mean_img = formula_R_mean_image(E_mean_spect)
    
    plt.scatter(E_mean_spect, R_mean_img, color='yellow', marker='s', s=120, edgecolors='black', zorder=10)
    # Etykieta pod kwadratem (żeby nie zasłaniała gwiazdki, bo są blisko)
    plt.annotate(f"Mean(Wz4)\n({E_mean_spect:.2f}, {R_mean_img:.2f})", 
                 (E_mean_spect, R_mean_img), xytext=(0, -35), textcoords="offset points", 
                 ha='center', fontsize=8, color='black',
                 bbox=dict(boxstyle="round,pad=0.2", fc="white", alpha=0.7)) # dodałem tło pod tekst dla czytelności

    # C. MAKSIMUM ZE WZORU 5/6 -> DIAMENT (D)
    R_max_img = formula_R_max_image(E0)
    
    plt.scatter(E0, R_max_img, color=col, marker='D', s=100, edgecolors='black', zorder=10)
    # Etykieta przy diamencie
    plt.annotate(f"Max(Wz5)\n({E0:.2f}, {R_max_img:.2f})", 
                 (E0, R_max_img), xytext=(0, 15), textcoords="offset points", 
                 ha='center', fontsize=8, color=col, fontweight='bold')

# LEGENDA I RYSOWANIE (Podmień cały koniec skryptu na to)
# -------------------------------------------------------
from matplotlib.lines import Line2D

# 1. Lista kolorów (Izotopy)
isotope_handles = [
    Line2D([0], [0], color=colors[name], lw=3, label=name) for name in isotopes.keys()
]

# 2. Lista symboli (Znaczenie punktów)
symbol_handles = [
    Line2D([0], [0], marker='*', color='w', markerfacecolor='gray', markeredgecolor='black', markersize=12, label='Percentyl 50% (Mediana)'),
    Line2D([0], [0], marker='s', color='w', markerfacecolor='yellow', markeredgecolor='black', markersize=10, label='Średni zasięg (Wzór 4 mgr. Mryka)'),
    Line2D([0], [0], marker='D', color='w', markerfacecolor='gray', markeredgecolor='black', markersize=8, label='Max zasięg (Wzór 5 mgr. Mryka)'),
    Line2D([0], [0], linestyle='--', color='gray', label='Zakres percentyli (10-90%)')
]

# 3. Wyświetlenie legendy (połączenie obu list zmiennych)
plt.legend(handles=isotope_handles + symbol_handles, loc='upper left')

# 4. Reszta ustawień wykresu
plt.xlabel("Energia [MeV]")
plt.ylabel("Zasięg [mm]")
plt.title("Zasięg Pozytonu: Mediana vs Wzory Analityczne")
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.show()"""
import numpy as np
import matplotlib.pyplot as plt

# -------------------------------------------------------
# Parametry i Funkcje Fizyczne
# -------------------------------------------------------
m_e = 0.511
rho = 1.0  # g/cm^3

isotopes = {
    "18F":  (0.634, 8),
    "44Sc": (1.474, 20),
    "68Ga": (1.899, 30)
}

def momentum(E):
    return np.sqrt(E**2 + 2 * m_e * E)

def fermi_function_allowed(Z, E):
    alpha = 1/137
    p = momentum(E)
    if p == 0: return 0 
    eta = alpha * Z * (E + m_e) / p
    if eta > 100: return 1 
    return (2 * np.pi * eta) / (1 - np.exp(-2 * np.pi * eta))

def beta_plus_spectrum(E, E0, Z):
    p = momentum(E)
    F = fermi_function_allowed(Z, E)
    return p * E * (E0 - E)**2 * F

# Funkcja ciągła (CSDA) - używana do linii tła i "R analitycznego"
def compute_X_continuous(E):
    if E <= 1e-9: return 0
    r = 0.412 * E**(1.265 - 0.0954 * np.log(E))
    return (r / rho) * 10 # mm

# Wzór (4): Średni zasięg
def formula_R_mean_image(E_mean_val):
    return (0.108 * (E_mean_val**1.14) / rho) * 10 # mm

# Wzory (5) i (6): Maksymalny zasięg (Empiryczne ze zdjęcia)
def formula_R_max_image(E_max_val):
    rho_mg = rho * 1000 
    R_cm = 0
    if 0.01 <= E_max_val <= 2.5:
        n = 1.265 - 0.0954 * np.log(E_max_val)
        R_cm = (412 * E_max_val**n) / rho_mg
    elif 2.5 < E_max_val <= 20:
        R_cm = (530 * E_max_val - 106) / rho_mg
    return R_cm * 10 # mm

# -------------------------------------------------------
# OBLICZENIA I GENEROWANIE TABELI
# -------------------------------------------------------
table_rows = []
percentiles_plot = np.arange(0.1, 1.0, 0.1)

# Przygotowanie danych do rysowania
plot_data = {} 

print("\n" + "="*95)
print(f"{'IZOTOP':<8} | {'E_max':<6} | {'E_mean':<6} |{'R_median':<12}| {'R_mean(Wz4)':<12} | {'R_max(Wz5)':<12} || {'R_analyt(Emax)':<15} | {'Delta(%)':<8}")
print("-" * 95)

for name, (E0, Z) in isotopes.items():
    # 1. Widmo
    E_space = np.linspace(1e-4, E0, 3000)
    spectrum = np.array([beta_plus_spectrum(e, E0, Z) for e in E_space])
    
    # Dystrybuanta do wykresu
    cdf = np.cumsum(spectrum)
    cdf = cdf / cdf[-1]
    
    # --- DODANE: Obliczenie mediany (50%) ---
    E_50 = np.interp(0.5, cdf, E_space)
    R_50 = compute_X_continuous(E_50)
    
    # 2. Obliczenia punktów kluczowych
    E_mean_spect = np.average(E_space, weights=spectrum)
    
    # Wzory ze zdjęcia
    R_mean_img = formula_R_mean_image(E_mean_spect)
    R_max_img = formula_R_max_image(E0)
    
    # Analityczne "100%" (czyli podstawiamy E_max do wzoru ciągłego CSDA)
    R_analyt_100 = compute_X_continuous(E0)
    
    # Różnica procentowa między wzorem 5 (zdjęcie) a analitycznym (CSDA)
    delta_proc = 100 * (R_max_img - R_analyt_100) / R_analyt_100
    
    # Wypisanie wiersza tabeli (teraz R_50 jest zdefiniowane)
    print(f"{name:<8} | {E0:<6.3f} | {E_mean_spect:<6.3f} |{R_50:<12.2f}| {R_mean_img:<12.2f} | {R_max_img:<12.2f} || {R_analyt_100:<15.2f} | {delta_proc:+.1f}%")
    
    # Zapis danych do słownika (dla wykresu)
    plot_data[name] = {
        "E_space": E_space,
        "cdf": cdf,
        "E0": E0,
        "E_mean": E_mean_spect,
        "R_mean_img": R_mean_img,
        "R_max_img": R_max_img
    }

print("="*95)
print("* R_analyt(Emax) to zasięg obliczony ze wzoru ciągłego (tło wykresu) dla energii maksymalnej.")
print("* Delta(%) pokazuje różnicę wzoru ze zdjęcia (Wz5) względem analitycznego.\n")

# -------------------------------------------------------
# RYSOWANIE WYKRESU (Bez zmian wizualnych)
# -------------------------------------------------------
plt.figure(figsize=(12, 8))
colors = {"18F": "tab:blue", "44Sc": "tab:green", "68Ga": "tab:red"}

for name, data in plot_data.items():
    col = colors[name]
    
    # 1. Tło (percentyle)
    E_p = np.interp(percentiles_plot, data["cdf"], data["E_space"])
    X_p = [compute_X_continuous(e) for e in E_p]
    plt.plot(E_p, X_p, '--', color=col, alpha=0.3)
    plt.scatter(E_p, X_p, color=col, alpha=0.3, s=15)

    # 2. Percentyl 50% (Mediana)
    E_50 = np.interp(0.5, data["cdf"], data["E_space"])
    R_50 = compute_X_continuous(E_50)
    plt.scatter(E_50, R_50, color=col, marker='*', s=200, edgecolors='black', zorder=10)
    plt.annotate(f"50%\n({E_50:.2f}, {R_50:.2f})", (E_50, R_50), xytext=(0, 25), textcoords="offset points", ha='center', fontsize=8, color=col, fontweight='bold')

    # 3. Średnia (Wzór 4)
    plt.scatter(data["E_mean"], data["R_mean_img"], color='yellow', marker='s', s=120, edgecolors='black', zorder=10)
    plt.annotate(f"Mean(Wz4)\n({data['E_mean']:.2f}, {data['R_mean_img']:.2f})", (data["E_mean"], data["R_mean_img"]), xytext=(0, -35), textcoords="offset points", ha='center', fontsize=8, color='black', bbox=dict(boxstyle="round,pad=0.2", fc="white", alpha=0.7))

    # 4. Max (Wzór 5)
    plt.scatter(data["E0"], data["R_max_img"], color=col, marker='D', s=100, edgecolors='black', zorder=10)
    plt.annotate(f"Max(Wz5)\n({data['E0']:.2f}, {data['R_max_img']:.2f})", (data["E0"], data["R_max_img"]), xytext=(0, 15), textcoords="offset points", ha='center', fontsize=8, color=col, fontweight='bold')

# --- LEGENDA ---
from matplotlib.lines import Line2D
isotope_handles = [Line2D([0], [0], color=colors[name], lw=3, label=name) for name in isotopes.keys()]
symbol_handles = [
    Line2D([0], [0], marker='*', color='w', markerfacecolor='gray', markeredgecolor='black', markersize=12, label='Percentyl 50% (Mediana)'),
    Line2D([0], [0], marker='s', color='w', markerfacecolor='yellow', markeredgecolor='black', markersize=10, label='Średni zasięg (Wzór 4 mgr. Mryka)'),
    Line2D([0], [0], marker='D', color='w', markerfacecolor='gray', markeredgecolor='black', markersize=8, label='Max zasięg (Wzór 5 mgr. Mryka)'),
    Line2D([0], [0], linestyle='--', color='gray', label='Rozkład percentyli (10-90%)')
]

plt.legend(handles=isotope_handles + symbol_handles, loc='upper left')
plt.xlabel("Energia [MeV]")
plt.ylabel("Zasięg [mm]")
plt.title("Zasięg Pozytonu: Weryfikacja Wzorów")
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.show()