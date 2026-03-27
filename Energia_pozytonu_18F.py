import numpy as np
import matplotlib.pyplot as plt

# -------------------------------------------------------
# Parametry fizyczne
# -------------------------------------------------------

m_e = 0.511        # masa elektronu/pozytonu [MeV]
rho = 1.0          # gęstość wody [g/cm^3]

# Dane izotopów: (E0, Z końcowe)
isotopes = {
    "18F":  (0.634, 8),
    "44Sc": (1.474, 20),
    "68Ga": (1.899, 30)
}
# ===== Funkcja pędu pozytonu =====
def momentum(E):
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
    return 0.412 * E**(1.265 - 0.0954 * np.log(E))

def compute_X(E):
    r = compute_r(E)
    return (r / rho) * 10

# 1. WYKRES WIDMA β+
plt.figure(figsize=(10,6))

for iso, (E0, Z) in isotopes.items():
    E = np.linspace(0.001, E0, 600)
    spectrum = beta_plus_spectrum(E, E0, Z)
    spectrum /= np.max(spectrum)  # normalizacja dla ładnego porównania
    plt.plot(E, spectrum, label=f"{iso} (E0={E0} MeV)")

plt.xlabel("Positron Energy E [MeV]")
plt.ylabel("β⁺ spectrum (normalized)")
plt.title("Comparison of β⁺ spectra: 18F, 44Sc, 68Ga")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()


# 2. WYKRES X(E) - WERSJA Z PUNKTAMI KOŃCOWYMI
plt.figure(figsize=(10,6))

# 1. Znajdźmy największe E0 spośród izotopów, żeby narysować tło dla wszystkich
max_E0 = max(data[0] for data in isotopes.values())

# Rysujemy jedną, ciągłą krzywą zasięgu od 0 do globalnego max_E0
E_global = np.linspace(0.001, max_E0, 1000)
X_global = compute_X(E_global)

plt.plot(E_global, X_global, color='gray', alpha=0.6, label='Range X(E) in water')

# 2. Dla każdego izotopu zaznaczamy tylko punkt końcowy (E_max)
colors = ['red', 'green', 'blue']  # Kolory dla punktów

for i, (iso, (E0, Z)) in enumerate(isotopes.items()):
    # Obliczamy X tylko dla energii maksymalnej tego izotopu
    X_end = compute_X(E0)
    
    # Rysujemy punkt
    plt.scatter(E0, X_end, color=colors[i], s=80, zorder=5, label=f"{iso} ($E_{{max}}$={E0} MeV)")
    
    # Opcjonalnie: linia pionowa (rzut na oś X) dla lepszej czytelności
    plt.vlines(E0, 0, X_end, color=colors[i], linestyle='--', alpha=0.5)
    # Etykieta nad punktem: (X, Y)
    # Używamy formatowania .2f lub .3f dla czytelności liczb
    label_text = f"({E0:.3f}, {X_end:.3f})"
    plt.text(E0, X_end * 1.05, label_text, 
             ha='center', va='bottom', color=colors[i], fontweight='bold')

plt.xlabel("Positron Energy E [MeV]")
plt.ylabel("Positron mean free path X [mm]")
plt.title("Positron range as a function of energy (spectra endpoints)")
plt.grid(True, which='both', linestyle='--', alpha=0.7)
# Ustawiamy limity osi Y, żeby napisy nad najwyższym punktem nie uciekły poza wykres
plt.ylim(0, max(X_global) * 1.15)
plt.xlim(0, max_E0 * 1.1)
plt.legend()
plt.tight_layout()
plt.show()