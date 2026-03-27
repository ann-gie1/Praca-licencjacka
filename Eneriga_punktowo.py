import numpy as np
import matplotlib.pyplot as plt
# =======================================================
'''# PREAMBUŁA STYLIZACJI (UPSCALE)
# =======================================================
FONT_INCREASE = 10      # O ile pkt zwiększyć czcionkę (bazowo jest ok. 10)
BASE_LINEWIDTH = 3.0    # Bazowa grubość wszystkich linii
SC_EXTRA_WIDTH = 3.0    # O ile dodatkowo pogrubić Skand (razem będzie BASE + EXTRA)

# Aktualizacja globalnych parametrów wykresu
plt.rcParams.update({
    'font.size': 10 + FONT_INCREASE,
    'axes.titlesize': 12 + FONT_INCREASE,
    'axes.labelsize': 10 + FONT_INCREASE,
    'xtick.labelsize': 10 + FONT_INCREASE,
    'ytick.labelsize': 10 + FONT_INCREASE,
    'legend.fontsize': 10 + FONT_INCREASE,
    'lines.linewidth': BASE_LINEWIDTH,
    'figure.figsize': (14, 9) # Nieznacznie zwiększyłem też domyślny rozmiar figury, by pomieścić duże napisy
})
# -------------------------------------------------------
# Parametry i Funkcje (bez zmian)
# -------------------------------------------------------
m_e = 0.511
rho = 1.0

isotopes = {
    "18F":  (0.634, 8),
    "44Sc": (1.474, 20),
    "68Ga": (1.899, 30)
}
'''
'''def momentum(E):
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

def compute_X(E):
    if E <= 1e-9: return 0
    r = 0.412 * E**(1.27 - 0.0954 * np.log(E))
    return (r / rho) * 10

# -------------------------------------------------------
# Obliczenia i Wykres
# -------------------------------------------------------
plt.figure(figsize=(10, 7))
percentiles = np.arange(0.1, 1.0, 0.1)

# Kolory dla czytelności
colors = {"18F": "tab:blue", "44Sc": "tab:green", "68Ga": "tab:red"}

for name, (E0, Z) in isotopes.items():
    # 1. Generowanie widma
    E_space = np.linspace(1e-4, E0, 2000)
    spectrum = np.array([beta_plus_spectrum(e, E0, Z) for e in E_space])
    
    # 2. Obliczenie percentyli (dla tła wykresu)
    cdf = np.cumsum(spectrum)
    cdf = cdf / cdf[-1]
    E_selected = np.interp(percentiles, cdf, E_space)
    X_selected = np.array([compute_X(e) for e in E_selected])
    
    # Rysowanie percentyli (linia i kropki)
    plt.plot(E_selected, X_selected, '--', color=colors[name], alpha=0.4, label=f'{name} (10-90%)')
    plt.scatter(E_selected, X_selected, color=colors[name], alpha=0.4, s=20)

    # 3. OBLICZENIE ŚREDNIEJ (MEAN)
    # Średnia ważona po energii, gdzie wagi to intensywność widma
    E_mean = np.average(E_space, weights=spectrum)
    X_mean = compute_X(E_mean)
    
    # 4. Rysowanie punktu średniego
    plt.scatter(E_mean, X_mean, color=colors[name], marker='*', s=150, edgecolors='black', zorder=10)
    
    # 5. Dodanie tekstu nad punktem (offset w osi Y)
    # textcoords="offset points" pozwala przesunąć napis o konkretną liczbę pikseli
    label_text = f"({E_mean:.3f}, {X_mean:.2f})"
    plt.annotate(label_text, 
                 (E_mean, X_mean),
                 textcoords="offset points", 
                 xytext=(0, 10), # 10 punktów w górę
                 ha='center', 
                 fontsize=9,
                 fontweight='bold',
                 color=colors[name])

plt.xlabel("Energia E [MeV]")
plt.ylabel("Zasięg X [mm]")
plt.title("Zależność Zasięgu od Energii (oznaczona Średnia Energia)")
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.show()'''
# ===== Funkcja pędu pozytonu =====

'''def momentum(E):

    """

    p = sqrt(E^2 + 2 E m_e)

    Relatywistyczna zależność pędu od energii kinetycznej pozytonu.

    """

    return np.sqrt(E**2 + 2 * m_e * E)





# ===== Dokładniejsze przybliżenie funkcji Fermiego =====

def fermi_function_allowed(Z, E):

    """

    F_allowed(Z, E) = 2*pi*η / (1 - exp(-2*pi*η))

    gdzie η = alpha * Z * (E + m_e) / p



    Jest to dobre przybliżenie funkcji Fermiego dla przejść dozwolonych β±.

    """

    alpha = 1/137

    p = momentum(E)

    eta = alpha * Z * (E + m_e) / p

    return (2 * np.pi * eta) / (1 - np.exp(-2 * np.pi * eta))





# ===== Widmo β+ =====

def beta_plus_spectrum(E, E0, Z):

    """Poprawiona definicja — 3 argumenty"""

    p = momentum(E)

    F = fermi_function_allowed(Z, E)

    return p * E * (E0 - E)**2 * F



# ===== Funkcja przeliczenia r i X =====

def compute_r(E):

    # wzór: r = 0.412 · E^(1.27 - 0.0954 * ln E)

    # zakładamy E w MeV, wynik r w cm (?) – w zależności od jednostek źródła

    return 0.412 * E**(1.27 - 0.0954 * np.log(E))



def compute_X(E):

    r = compute_r(E)

    return r / rho



# 1. WYKRES WIDMA β+

plt.figure(figsize=(10,6))



for iso, (E0, Z) in isotopes.items():
    E = np.linspace(0.001, E0, 600)
    spectrum = beta_plus_spectrum(E, E0, Z)
    spectrum /= np.max(spectrum)  # normalizacja

    # --- LOGIKA WYRÓŻNIANIA SKANDU (Zachowana) ---
    if "44Sc" in iso:
        current_lw = BASE_LINEWIDTH + SC_EXTRA_WIDTH
        zorder = 10  # Rysuj na wierzchu
    else:
        current_lw = BASE_LINEWIDTH
        zorder = 5

    # --- LOGIKA KOLORU DLA GALU ---
    # Jeśli to Gal, ustaw zielony, w przeciwnym razie None (domyślny cykl kolorów)
    line_color = 'green' if "68Ga" in iso else None

    # --- RYSOWANIE ---
    # Dodano argument color=line_color
    plt.plot(E, spectrum, label=f"{iso} (E0={E0} MeV)", 
             linewidth=current_lw, zorder=zorder, color=line_color)

plt.xlabel("Positon energy E [MeV]")

plt.ylabel("β⁺ Spectrum (normalised)")

plt.title("Comparison of β⁺ spectra: 18F, 44Sc, 68Ga")

plt.grid(True)

plt.legend()

plt.tight_layout()
plt.ylim(0, 1.5)  # Zwiększa zakres osi Y do 1.3, tworząc pustą przestrzeń na górze
plt.legend(loc='upper right') # Legenda zostaje w standardowym miejscu
plt.show()'''


#basic version
import numpy as np
import matplotlib.pyplot as plt

# -------------------------------------------------------
# Parametry i Funkcje (Logika fizyczna bez zmian)
# -------------------------------------------------------
m_e = 0.511
rho = 1.0

isotopes = {
    "18F":  (0.634, 8),
    "44Sc": (1.474, 20),
    "68Ga": (1.899, 30)
}

def momentum(E):
    """
    p = sqrt(E^2 + 2 E m_e)
    Relatywistyczna zależność pędu od energii kinetycznej pozytonu.
    """
    return np.sqrt(E**2 + 2 * m_e * E)

def fermi_function_allowed(Z, E):  
    alpha = 1/137
    p = momentum(E)
    # Zabezpieczenie przed dzieleniem przez zero przy E=0 (choć linspace zaczyna od 0.001)
    if np.any(p == 0):
        p = np.where(p==0, 1e-9, p)
        
    eta = alpha * Z * (E + m_e) / p
    return (2 * np.pi * eta) / (1 - np.exp(-2 * np.pi * eta))

# ===== Widmo β+ =====
def beta_plus_spectrum(E, E0, Z):
    """Poprawiona definicja — 3 argumenty"""
    p = momentum(E)
    F = fermi_function_allowed(Z, E)
    return p * E * (E0 - E)**2 * F

# 1. WYKRES WIDMA β+
plt.figure() # Rozmiar brany z rcParams

for iso, (E0, Z) in isotopes.items():
    E = np.linspace(0.001, E0, 600)
    spectrum = beta_plus_spectrum(E, E0, Z)
    spectrum /= np.max(spectrum)  # normalizacja
    

    plt.plot(E, spectrum, label=f"{iso} (E0={E0} MeV)")

plt.xlabel("Positon energy E [MeV]")
plt.ylabel("β⁺ Spectrum (normalised)")
plt.title("Comparison of β⁺ spectra: 18F, 44Sc, 68Ga")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()