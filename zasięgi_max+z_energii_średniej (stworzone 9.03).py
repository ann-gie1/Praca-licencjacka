'''import numpy as np
import matplotlib.pyplot as plt

# -------------------------------------------------------
# Parametry fizyczne
# -------------------------------------------------------
m_e = 0.511        # masa elektronu/pozytonu [MeV]
rho = 1.0          # gęstość wody [g/cm^3]

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
    if np.any(p == 0):
        p = np.where(p==0, 1e-9, p)
    eta = alpha * Z * (E + m_e) / p
    return (2 * np.pi * eta) / (1 - np.exp(-2 * np.pi * eta))

def beta_plus_spectrum(E, E0, Z):
    p = momentum(E)
    F = fermi_function_allowed(Z, E)
    return p * E * (E0 - E)**2 * F

def compute_r(E):
    return 0.412 * E**(1.265 - 0.0954 * np.log(E))

def compute_X(E):
    r = compute_r(E)
    return (r / rho) * 10

# Przeliczenie energii średnich przed rysowaniem
mean_energies = {}
for iso, (E0, Z) in isotopes.items():
    E = np.linspace(0.001, E0, 600)
    spectrum = beta_plus_spectrum(E, E0, Z)
    E_mean = np.sum(E * spectrum) / np.sum(spectrum)
    mean_energies[iso] = E_mean

# =======================================================
# 2. WYKRES X(E) - ZASIĘG DLA E_MAX ORAZ E_MEAN
# =======================================================
plt.figure(figsize=(10,6))

max_E0 = max(data[0] for data in isotopes.values())
E_global = np.linspace(0.001, max_E0 * 1.05, 1000)
X_global = compute_X(E_global)

plt.plot(E_global, X_global, color='gray', alpha=0.6, label='Range X(E) in water (Katz-Penfold)')

colors = ['red', 'green', 'blue']

for i, (iso, (E0, Z)) in enumerate(isotopes.items()):
    color = colors[i]
    E_mean = mean_energies[iso]
    
    # Obliczenia zasięgów
    X_max = compute_X(E0)
    X_mean = compute_X(E_mean)
    
    # Rysowanie punktu dla E_max (kółka)
    plt.scatter(E0, X_max, color=color, marker='o', s=80, zorder=5, 
                label=f"{iso} $E_{{max}}$")
    plt.vlines(E0, 0, X_max, color=color, linestyle='--', alpha=0.5)
    plt.text(E0, X_max * 1.05, f"({E0:.3f}, {X_max:.2f} mm)", 
             ha='center', va='bottom', color=color, fontweight='bold', fontsize=9)
    
    # Rysowanie punktu dla E_mean (kwadraty)
    plt.scatter(E_mean, X_mean, color=color, marker='s', s=80, zorder=5, 
                label=f"{iso} $\\langle E \\rangle$")
    plt.vlines(E_mean, 0, X_mean, color=color, linestyle=':', alpha=0.8)
    plt.text(E_mean, X_mean * 1.05, f"({E_mean:.3f}, {X_mean:.2f} mm)", 
             ha='center', va='bottom', color=color, fontweight='bold', fontsize=9)

plt.xlabel("Positron Energy E [MeV]")
plt.ylabel("Positron range X [mm]")
plt.title("Positron range: Maximum vs Mean Energy (Katz-Penfold)")
plt.grid(True, which='both', linestyle='--', alpha=0.7)
plt.ylim(0, max(X_global) * 1.2)
plt.xlim(0, max_E0 * 1.1)
plt.legend()
plt.tight_layout()
plt.show()'''
#wersja czterech zasięgów

'''import numpy as np
import pandas as pd

# -------------------------------------------------------
# Parametry fizyczne
# -------------------------------------------------------
m_e = 0.511
rho = 1.0  # gęstość wody [g/cm^3]

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
    # Zabezpieczenie przed dzieleniem przez 0
    p = np.where(p==0, 1e-9, p)
    eta = alpha * Z * (E + m_e) / p
    return (2 * np.pi * eta) / (1 - np.exp(-2 * np.pi * eta))

def beta_plus_spectrum(E, E0, Z):
    p = momentum(E)
    F = fermi_function_allowed(Z, E)
    return p * E * (E0 - E)**2 * F

def compute_r(E):
    # Wzór Katza-Penfolda
    return 0.412 * E**(1.265 - 0.0954 * np.log(E))

def compute_X(E):
    return (compute_r(E) / rho) * 10

# -------------------------------------------------------
# Obliczenia statystyczne i tworzenie tabeli
# -------------------------------------------------------
results = []

for iso, (E0, Z) in isotopes.items():
    # Używamy drobniejszej siatki dla precyzji całkowania. 
    # Startujemy od 0.01 MeV, aby ominąć fizyczną i matematyczną osobliwość wzoru Katza dla E bliskich zeru
    E = np.linspace(0.01, E0, 10000) 
    spectrum = beta_plus_spectrum(E, E0, Z)
    
    # 1. Zasięg maksymalny z E_max
    R_max = compute_X(E0)
    
    # 2. Zasięg policzony z energii średniej R(<E>)
    E_mean = np.sum(E * spectrum) / np.sum(spectrum)
    R_E_mean = compute_X(E_mean)
    
    # 3. Rzeczywisty Średni Zasięg <R> (Całka z zasiegów)
    R_array = compute_X(E)
    mean_R = np.sum(R_array * spectrum) / np.sum(spectrum)
    
    # 4. Mediana zasięgu (gdzie zatrzymuje się 50% cząstek)
    # Liczymy dystrybuantę skumulowaną (CDF)
    cdf = np.cumsum(spectrum) / np.sum(spectrum)
    median_idx = np.argmin(np.abs(cdf - 0.5)) # Szukamy miejsca, gdzie CDF najbliżej 0.5
    E_median = E[median_idx]
    R_median = compute_X(E_median)
    
    results.append({
        "Isotope": iso,
        "R(E_max) [mm]": round(R_max, 3),
        "R(<E>) [mm]": round(R_E_mean, 3),
        "<R> (Mean R) [mm]": round(mean_R, 3),
        "R(median) [mm]": round(R_median, 3)
    })

# Wyświetlenie tabeli w konsoli
df = pd.DataFrame(results)
print(df.to_string(index=False))'''

#z rysowaniem wykresu zaznaczony zasięg mediany

'''import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# -------------------------------------------------------
# Parametry fizyczne
# -------------------------------------------------------
m_e = 0.511        # masa elektronu/pozytonu [MeV]
rho = 1.0          # gęstość wody [g/cm^3]

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
    p = np.where(p==0, 1e-9, p)
    eta = alpha * Z * (E + m_e) / p
    return (2 * np.pi * eta) / (1 - np.exp(-2 * np.pi * eta))

def beta_plus_spectrum(E, E0, Z):
    p = momentum(E)
    F = fermi_function_allowed(Z, E)
    return p * E * (E0 - E)**2 * F

def compute_r(E):
    return 0.412 * E**(1.265 - 0.0954 * np.log(E))

def compute_X(E):
    return (compute_r(E) / rho) * 10

# -------------------------------------------------------
# Obliczenia dla wszystkich metryk i tabeli
# -------------------------------------------------------
results = []
plot_data = {}

for iso, (E0, Z) in isotopes.items():
    # Używamy drobniejszej siatki od 0.01 MeV dla stabilności logarytmu Katza-Penfolda
    E = np.linspace(0.01, E0, 10000) 
    spectrum = beta_plus_spectrum(E, E0, Z)
    
    # 1. Max
    R_max = compute_X(E0)
    
    # 2. Średnia Energia (Mean)
    E_mean = np.sum(E * spectrum) / np.sum(spectrum)
    R_E_mean = compute_X(E_mean)
    
    # 3. Średni Zasięg <R>
    R_array = compute_X(E)
    mean_R = np.sum(R_array * spectrum) / np.sum(spectrum)
    
    # 4. Mediana
    cdf = np.cumsum(spectrum) / np.sum(spectrum)
    median_idx = np.argmin(np.abs(cdf - 0.5))
    E_median = E[median_idx]
    R_median = compute_X(E_median)
    
    # Zapis do tabeli
    results.append({
        "Isotope": iso,
        "R(E_max) [mm]": round(R_max, 3),
        "R(<E>) [mm]": round(R_E_mean, 3),
        "<R> (Mean R) [mm]": round(mean_R, 3),
        "R(median) [mm]": round(R_median, 3)
    })
    
    # Zapis do rysowania wykresu
    plot_data[iso] = {
        'E0': E0, 'R_max': R_max,
        'E_mean': E_mean, 'R_E_mean': R_E_mean,
        'E_median': E_median, 'R_median': R_median,
        'mean_R': mean_R
    }

# Wyświetlenie tabeli w terminalu
print("\n--- WYNIKI ZASIĘGÓW ---")
df = pd.DataFrame(results)
print(df.to_string(index=False))
print("-----------------------\n")

# -------------------------------------------------------
# WYKRES X(E) - ZASIĘG DLA E_MAX, E_MEAN oraz E_MEDIAN
# -------------------------------------------------------
plt.figure(figsize=(11,7))

max_E0 = max(data[0] for data in isotopes.values())
E_global = np.linspace(0.01, max_E0 * 1.05, 1000)
X_global = compute_X(E_global)

plt.plot(E_global, X_global, color='gray', alpha=0.5, label='Range X(E) in water')

colors = ['red', 'green', 'blue']

for i, iso in enumerate(isotopes.keys()):
    color = colors[i]
    d = plot_data[iso]
    
    # Punkt dla E_max (kółka)
    plt.scatter(d['E0'], d['R_max'], color=color, marker='o', s=70, zorder=5, 
                label=f"{iso} $E_{{max}}$")
    plt.vlines(d['E0'], 0, d['R_max'], color=color, linestyle='-', alpha=0.3)

    
    # Punkt dla E_mean (kwadraty)
    plt.scatter(d['E_mean'], d['R_E_mean'], color=color, marker='s', s=70, zorder=5, 
                label=f"{iso} $\\langle E \\rangle$")
    plt.vlines(d['E_mean'], 0, d['R_E_mean'], color=color, linestyle='--', alpha=0.5)


    # Punkt dla E_median (trójkąty)
    plt.scatter(d['E_median'], d['R_median'], color=color, marker='^', s=70, zorder=5, 
                label=f"{iso} $E_{{med}}$")
    # Tekst pod punktem, żeby nie zlał się ze średnią
    
    # Punkt dla Średniego Zasięgu <R> (romby)
    # Rysujemy go na osi X w miejscu E_mean, aby pokazać matematyczną różnicę na osi Y
    plt.scatter(d['E_mean'], d['mean_R'], color=color, marker='D', s=70, zorder=6, 
                label=f"{iso} $\\langle R \\rangle$")


plt.xlabel("Positron Energy E [MeV]")
plt.ylabel("Positron range X [mm]")
plt.title("Positron range: Maximum, Mean & Median Energy (Katz-Penfold)")
plt.grid(True, which='both', linestyle='--', alpha=0.6)
plt.ylim(0, max(X_global) * 1.25)
plt.xlim(0, max_E0 * 1.1)

# Kolumny w legendzie dla czytelności
plt.legend(ncol=3, loc='upper left', fontsize=9)
plt.tight_layout()
plt.show()'''


#z zoom na nakładające się punkty
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# -------------------------------------------------------
# Parametry fizyczne (Niezmienione)
# -------------------------------------------------------
m_e = 0.511        # masa elektronu/pozytonu [MeV]
rho = 1.0          # gęstość wody [g/cm^3]

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
    p = np.where(p==0, 1e-9, p)
    eta = alpha * Z * (E + m_e) / p
    return (2 * np.pi * eta) / (1 - np.exp(-2 * np.pi * eta))

def beta_plus_spectrum(E, E0, Z):
    p = momentum(E)
    F = fermi_function_allowed(Z, E)
    return p * E * (E0 - E)**2 * F

def compute_r(E):
    # Wzór Katza-Penfolda
    return 0.412 * E**(1.265 - 0.0954 * np.log(E))

def compute_X(E):
    return (compute_r(E) / rho) * 10

# -------------------------------------------------------
# Obliczenia dla wszystkich metryk i tabeli
# -------------------------------------------------------
results = []
plot_data = {}

for iso, (E0, Z) in isotopes.items():
    # Refining mesh for precision
    E = np.linspace(0.01, E0, 10000)
    spectrum = beta_plus_spectrum(E, E0, Z)

    # 1. R(E_max) - kółko (zawsze leży na krzywej)
    R_max = compute_X(E0)

    # 2. R(<E>) - Zasięg dla E_średniej - kwadrat (leży na krzywej)
    E_mean = np.sum(E * spectrum) / np.sum(spectrum)
    R_E_mean = compute_X(E_mean)

    # 3. <R> - Średni Zasięg widma - romb (NIE leży na krzywej)
    R_array = compute_X(E)
    mean_R = np.sum(R_array * spectrum) / np.sum(spectrum)

    # 4. R(median) - trójkąt ^ (leży na krzywej)
    cdf = np.cumsum(spectrum) / np.sum(spectrum)
    median_idx = np.argmin(np.abs(cdf - 0.5))
    E_median = E[median_idx]
    R_median = compute_X(E_median)

    # Zapis do tabeli (Requirement: nadal produkowana)
    results.append({
        "Isotope": iso,
        "R(E_max) [mm]": round(R_max, 3),
        "R(<E>) [mm]": round(R_E_mean, 3),
        "<R> (Mean R) [mm]": round(mean_R, 3),
        "R(median) [mm]": round(R_median, 3)
    })

    # Zapis do rysowania wykresu
    plot_data[iso] = {
        'E0': E0, 'R_max': R_max,
        'E_mean': E_mean, 'R_E_mean': R_E_mean,
        'E_median': E_median, 'R_median': R_median,
        'mean_R': mean_R  # Added mean_R for the diamond
    }

# Wyświetlenie tabeli w terminalu (Requirement: nadal produkowana)
print("\n--- WYNIKI ZASIĘGÓW (Tabela referencyjna) ---")
df = pd.DataFrame(results)
print(df.to_string(index=False))
print("-----------------------\n")

# -------------------------------------------------------
# WYKRES X(E) - ZBLIŻENIE (0.25 do 1.0 MeV)
# -------------------------------------------------------
plt.figure(figsize=(12, 8))

# Zdefiniowanie zakresu powiększenia
zoom_start = 0.25
zoom_end = 1.0

# Szara krzywa Katza-Penfolda w powiększeniu
max_E0_global = max(d['E0'] for d in plot_data.values())
E_curve = np.linspace(0.01, max_E0_global * 1.05, 1000)
X_curve = compute_X(E_curve)

plt.plot(E_curve, X_curve, color='gray', alpha=0.5, linestyle='-', label='Krzywa X(E) (Katz-Penfold)')

colors = ['red', 'green', 'blue']

# Collect only relevant isotopes within the zoom
zoomed_isotopes = {k: v for k, v in plot_data.items() if zoom_start <= v['E0']}

for i, iso in enumerate(isotopes.keys()):
    d = plot_data[iso]
    if iso not in zoomed_isotopes:
        continue # Skip isotopes not visible in this zoom

    color = colors[i]

    # Zaznaczenia (Markers) - Tylko punkty w zakresie powiększenia
    # Używamy Paddingu 1.15x dla vlines, żeby sięgały poza krzywą
    if zoom_start <= d['E0'] <= zoom_end:
        # R(E_max) - kółko (zawsze leży na krzywej)
        plt.scatter(d['E0'], d['R_max'], color=color, marker='o', s=80, zorder=5,
                    label=f"{iso} $R(E_{{max}})$")
        plt.vlines(d['E0'], 0, d['R_max'], color=color, linestyle='-', alpha=0.3)

    if zoom_start <= d['E_median'] <= zoom_end:
        # R(median) - trójkąt ^ (leży na krzywej)
        plt.scatter(d['E_median'], d['R_median'], color=color, marker='^', s=80, zorder=5,
                    label=f"{iso} $R(median)$")
        plt.vlines(d['E_median'], 0, d['R_median'], color=color, linestyle=':', alpha=0.8)

    if zoom_start <= d['E_mean'] <= zoom_end:
        # R(<E>) - kwadrat s (leży na krzywej)
        plt.scatter(d['E_mean'], d['R_E_mean'], color=color, marker='s', s=80, zorder=5,
                    label=f"{iso} $R(\\langle E \\rangle)$")
        plt.vlines(d['E_mean'], 0, d['R_E_mean'] * 1.15, color=color, linestyle='--', alpha=0.5)

        # <R> - rąb D (Średni zasięg widma, NIE leży na krzywej, na tej samej pionowej linii)
        plt.scatter(d['E_mean'], d['mean_R'], color=color, marker='D', s=80, zorder=6,
                    label=f"{iso} $\\langle R \\rangle$ (Średni Z.)")

# Ustawienie limitów osi (Powiększenie)
plt.xlim(zoom_start, zoom_end)

# Dynamiczne dopasowanie osi Y na podstawie widocznych punktów
relevant_points_y = []
for d in zoomed_isotopes.values():
    if zoom_start <= d['E0'] <= zoom_end: relevant_points_y.append(d['R_max'])
    if zoom_start <= d['E_median'] <= zoom_end: relevant_points_y.append(d['R_median'])
    if zoom_start <= d['E_mean'] <= zoom_end:
        relevant_points_y.append(d['R_E_mean'])
        relevant_points_y.append(d['mean_R'])

if relevant_points_y:
    min_y = min(relevant_points_y)
    max_y = max(relevant_points_y)
    padding_y = (max_y - min_y) * 0.15 if max_y > min_y else 1.0
    plt.ylim(min_y - padding_y if min_y - padding_y > 0 else 0, max_y + padding_y)

plt.xlabel("Energy E [MeV]")
plt.ylabel("Range X [mm]")
plt.title(f"Zoom in on positron ranges (Katz-Penfold) for energies E $\in$ [0.25, 1.0] MeV\n")
plt.grid(True, which='both', linestyle='--', alpha=0.6)

# Kolumny w legendzie
plt.legend(ncol=4, loc='upper left', fontsize=9, framealpha=0.95)
plt.tight_layout()
plt.show()