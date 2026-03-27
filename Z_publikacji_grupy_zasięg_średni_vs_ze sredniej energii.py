'''import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# -------------------------------------------------------
# Parametry fizyczne
# -------------------------------------------------------
m_e = 0.511        
rho_g = 1.0        # gęstość [g/cm^3]
rho_mg = 1000.0    # gęstość [mg/cm^3]

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

# --- NOWE WZORY Z PUBLIKACJI (Równania 2, 3, 4) ---
def formula_R_mean(E):
    """ Równanie (2) - Średni zasięg dla energii E. Wynik w mm. """
    R_cm = (0.108 * E**1.14) / rho_g
    return R_cm * 10

def formula_R_max(E):
    """ Równania (3) i (4) - Maksymalny zasięg. Wynik w mm. """
    # Równanie 3 (E <= 2.5 MeV)
    n = 1.265 - 0.0954 * np.log(E)
    R_cm_low = (412 * E**n) / rho_mg
    
    # Równanie 4 (E > 2.5 MeV)
    R_cm_high = (530 * E - 106) / rho_mg
    
    # Sklejenie warunków (choć dla F, Sc, Ga używamy tylko low)
    R_cm = np.where(E <= 2.5, R_cm_low, R_cm_high)
    return R_cm * 10

# -------------------------------------------------------
# Obliczenia i Tabela
# -------------------------------------------------------
results = []
plot_data = {}

for iso, (E0, Z) in isotopes.items():
    E = np.linspace(0.01, E0, 10000) 
    spectrum = beta_plus_spectrum(E, E0, Z)
    
    # 1. Energia średnia i mediana
    E_mean = np.sum(E * spectrum) / np.sum(spectrum)
    cdf = np.cumsum(spectrum) / np.sum(spectrum)
    E_median = E[np.argmin(np.abs(cdf - 0.5))]
    
    # 2. Obliczenia Zasięgów ze wzorów Cal-Gonzalez et al.
    R_max_end = formula_R_max(E0)                        # R_max dla E_max (Eq 3)
    R_mean_from_Emean = formula_R_mean(E_mean)           # R_mean dla <E> (Eq 2)
    R_mean_from_Emedian = formula_R_mean(E_median)       # R_mean dla mediany E (Eq 2)
    
    # 3. Prawdziwy Średni Zasięg <R_mean> (Całka Eq 2 po widmie)
    R_mean_array = formula_R_mean(E)
    true_mean_R = np.sum(R_mean_array * spectrum) / np.sum(spectrum)
    
    results.append({
        "Isotope": iso,
        "R_max(E_max) [Eq3]": round(R_max_end, 3),
        "R_mean(<E>) [Eq2]": round(R_mean_from_Emean, 3),
        "<R_mean> (True Mean) [Eq2]": round(true_mean_R, 3),
        "R_mean(E_median) [Eq2]": round(R_mean_from_Emedian, 3)
    })
    
    # Dane do wykresu
    plot_data[iso] = (E, spectrum, R_mean_array)

df = pd.DataFrame(results)
print("\n--- TABELA ZASIĘGÓW (Modele analityczne: Cal-Gonzalez / Katz-Penfold) ---")
print(df.to_string(index=False))
print("--------------------------------------------------------------------------\n")

# -------------------------------------------------------
# WYKRES: Widmo Zasięgów (Annihilation Profile Approximation)
# -------------------------------------------------------
plt.figure(figsize=(10, 6))
colors = ['#1f77b4', '#ff7f0e', '#2ca02c']

for i, iso in enumerate(isotopes.keys()):
    E, spectrum_E, R_array = plot_data[iso]
    
    # Matematycznie poprawna transformacja gęstości prawdopodobieństwa: P(R) = P(E) / dR/dE
    dR = np.gradient(R_array)
    spectrum_R = spectrum_E / dR
    spectrum_R /= np.max(spectrum_R) # Normalizacja do 1
    
    plt.plot(R_array, spectrum_R, color=colors[i], linewidth=2, label=f"{iso}")

plt.xlabel("Positron Penetration Range R [mm]")
plt.ylabel("Probability Density P(R) (normalized)")
plt.title("Positron Range Spectra based on $R_{mean}$ formula")
plt.grid(True, linestyle='--', alpha=0.6)
plt.xlim(0, max([np.max(d[2]) for d in plot_data.values()]) * 1.05)
plt.legend()
plt.tight_layout()
plt.show()'''

#z normalnym wykresem
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# -------------------------------------------------------
# Parametry fizyczne
# -------------------------------------------------------
m_e = 0.511        
rho_g = 1.0        # gęstość [g/cm^3]
rho_mg = 1000.0    # gęstość [mg/cm^3]

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

# --- NOWE WZORY Z PUBLIKACJI (Równania 2, 3, 4) ---
def formula_R_mean(E):
    """ Równanie (2) - Średni zasięg dla energii E. Wynik w mm. """
    R_cm = (0.108 * E**1.14) / rho_g
    return R_cm * 10

def formula_R_max(E):
    """ Równania (3) i (4) - Maksymalny zasięg. Wynik w mm. """
    # Równanie 3 (E <= 2.5 MeV)
    n = 1.265 - 0.0954 * np.log(E)
    R_cm_low = (412 * E**n) / rho_mg
    
    # Równanie 4 (E > 2.5 MeV)
    R_cm_high = (530 * E - 106) / rho_mg
    
    # Sklejenie warunków
    R_cm = np.where(E <= 2.5, R_cm_low, R_cm_high)
    return R_cm * 10

# -------------------------------------------------------
# Obliczenia i Tabela
# -------------------------------------------------------
results = []

for iso, (E0, Z) in isotopes.items():
    E = np.linspace(0.01, E0, 10000) 
    spectrum = beta_plus_spectrum(E, E0, Z)
    
    # 1. Energia średnia i mediana
    E_mean = np.sum(E * spectrum) / np.sum(spectrum)
    cdf = np.cumsum(spectrum) / np.sum(spectrum)
    E_median = E[np.argmin(np.abs(cdf - 0.5))]
    
    # 2. Obliczenia Zasięgów ze wzorów Cal-Gonzalez et al.
    R_max_end = formula_R_max(E0)                        # R_max dla E_max (Eq 3)
    R_mean_from_Emean = formula_R_mean(E_mean)           # R_mean dla <E> (Eq 2)
    R_mean_from_Emedian = formula_R_mean(E_median)       # R_mean dla mediany E (Eq 2)
    
    # 3. Prawdziwy Średni Zasięg <R_mean> (Całka Eq 2 po widmie)
    R_mean_array = formula_R_mean(E)
    true_mean_R = np.sum(R_mean_array * spectrum) / np.sum(spectrum)
    
    results.append({
        "Isotope": iso,
        "R_max(E_max) [Eq3]": round(R_max_end, 3),
        "R_mean(<E>) [Eq2]": round(R_mean_from_Emean, 3),
        "<R_mean> (True Mean) [Eq2]": round(true_mean_R, 3),
        "R_mean(E_median) [Eq2]": round(R_mean_from_Emedian, 3)
    })

df = pd.DataFrame(results)
print("\n--- TABELA ZASIĘGÓW (Modele analityczne: Cal-Gonzalez / Katz-Penfold) ---")
print(df.to_string(index=False))
print("--------------------------------------------------------------------------\n")

# -------------------------------------------------------
# WYKRES: Zasięg w funkcji energii X(E) (POPRAWIONE KOLORY)
# -------------------------------------------------------
plt.figure(figsize=(10, 6))

max_E0 = max(data[0] for data in isotopes.values())
E_global = np.linspace(0.01, max_E0 * 1.05, 1000)

# Rysowanie globalnych krzywych dla obu modeli
R_max_global = formula_R_max(E_global)
R_mean_global = formula_R_mean(E_global)

plt.plot(E_global, R_max_global, color='gray', linestyle='--', alpha=0.6, label='Max Range R_max(E) [Eq. 3/4]')
plt.plot(E_global, R_mean_global, color='black', linestyle='-', alpha=0.6, label='Mean Penetration R_mean(E) [Eq. 2]')

# Słownik przypisujący na sztywno kolory do izotopów
custom_colors = {
    "18F": "blue",
    "44Sc": "orange",
    "68Ga": "green"
}

# Odzyskujemy wartości średnie z wyników tabeli, by nie liczyć ich ponownie
mean_energies = {}
for iso, (E0, Z) in isotopes.items():
    E = np.linspace(0.01, E0, 10000) 
    spectrum = beta_plus_spectrum(E, E0, Z)
    E_mean = np.sum(E * spectrum) / np.sum(spectrum)
    mean_energies[iso] = E_mean

for iso, (E0, Z) in isotopes.items():
    color = custom_colors[iso]
    E_mean = mean_energies[iso]
    
    # 1. Obliczenia dla Max (na E_max)
    R_max_val = formula_R_max(E0)
    
    # 2. Obliczenia dla Mean (na E_mean)
    R_mean_val = formula_R_mean(E_mean)
    
    # Punkt na krzywej R_max (dla E_max)
    plt.scatter(E0, R_max_val, color=color, marker='o', s=60, zorder=5, label=f"{iso} Max ($E_{{max}}$)")
    plt.vlines(E0, 0, R_max_val, color=color, linestyle=':', alpha=0.5)
    
    # Punkt na krzywej R_mean (dla E_mean)
    plt.scatter(E_mean, R_mean_val, color=color, marker='s', s=60, zorder=5, label=f"{iso} Mean ($\\langle E \\rangle$)")
    plt.vlines(E_mean, 0, R_mean_val, color=color, linestyle='--', alpha=0.5)

plt.xlabel("Positron Energy E [MeV]")
plt.ylabel("Range R [mm]")
plt.title("Positron Range vs Energy: $R_{max}(E_{max})$ and $R_{mean}(\\langle E \\rangle)$")
plt.grid(True, linestyle='--', alpha=0.6)
plt.xlim(0, max_E0 * 1.1)
plt.ylim(0, max(R_max_global) * 1.1)

# Czytelna legenda z 2 kolumnami
plt.legend(ncol=2, fontsize=9)
plt.tight_layout()
plt.show()