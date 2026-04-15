'''import numpy as np
import matplotlib.pyplot as plt

# -------------------------------------------------------
# 1. Parametry fizyczne i symulacji
# -------------------------------------------------------
m_e = 0.511        # masa elektronu/pozytonu [MeV]
rho = 1.0          # gęstość wody [g/cm^3]
N_sim = 5000       # liczba losowań na sferę

isotopes = {
    "18F": (0.634, 8),
    "44Sc": (1.474, 20)
}
diameters_mm = [10, 13, 17, 22, 28, 37]

# -------------------------------------------------------
# 2. Funkcje modelu fizycznego
# -------------------------------------------------------
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

def compute_R_mean(E):
    """Oblicza efektywny średni zasięg R_mean (wzór Cal-Gonzalez), wynik w mm."""
    return (0.108 * E**1.14 / rho) * 10

def sample_energies(E0, Z, N):
    """Losuje energie z widma beta+."""
    E_grid = np.linspace(0.01, E0, 5000)
    spectrum = beta_plus_spectrum(E_grid, E0, Z)
    cdf = np.cumsum(spectrum)
    cdf = cdf / cdf[-1]
    return np.interp(np.random.rand(N), cdf, E_grid)

# -------------------------------------------------------
# 3. Symulacja Monte Carlo
# -------------------------------------------------------
np.random.seed(42) # Dla powtarzalności wyników
pve_18F = []
pve_44Sc = []

print("Rozpoczynam symulację...")

for iso, (E0, Z) in isotopes.items():
    for d in diameters_mm:
        R_sphere = d / 2.0
        
        # Losowanie jednorodnej pozycji wewnątrz sfery
        r_pos = R_sphere * np.random.rand(N_sim)**(1/3)
        theta_pos = 2 * np.pi * np.random.rand(N_sim)
        cos_phi_pos = 1 - 2 * np.random.rand(N_sim)
        sin_phi_pos = np.sqrt(1 - cos_phi_pos**2)
        
        x0 = r_pos * sin_phi_pos * np.cos(theta_pos)
        y0 = r_pos * sin_phi_pos * np.sin(theta_pos)
        z0 = r_pos * cos_phi_pos
        
        # Losowanie izotropowego kierunku emisji
        theta_dir = 2 * np.pi * np.random.rand(N_sim)
        cos_phi_dir = 1 - 2 * np.random.rand(N_sim)
        sin_phi_dir = np.sqrt(1 - cos_phi_dir**2)
        
        dx = sin_phi_dir * np.cos(theta_dir)
        dy = sin_phi_dir * np.sin(theta_dir)
        dz = cos_phi_dir
        
        # Wyznaczanie zasięgu na podstawie wylosowanej energii
        E_sampled = sample_energies(E0, Z, N_sim)
        R_eff = compute_R_mean(E_sampled)
        
        # Obliczanie pozycji końcowej
        xf = x0 + R_eff * dx
        yf = y0 + R_eff * dy
        zf = z0 + R_eff * dz
        Rf = np.sqrt(xf**2 + yf**2 + zf**2)
        
        # Obliczanie frakcji ucieczki ze sfery (Spill-out)
        spill_out = (np.sum(Rf > R_sphere) / N_sim) * 100.0
        
        if iso == "18F":
            pve_18F.append(spill_out)
        else:
            pve_44Sc.append(spill_out)

print("Symulacja zakończona. Generuję wykres...")

# -------------------------------------------------------
# 4. Generowanie i formatowanie wykresu
# -------------------------------------------------------
x = np.arange(len(diameters_mm))
width = 0.35

plt.figure(figsize=(10, 6))
bars1 = plt.bar(x - width/2, pve_18F, width, label='18F', color='royalblue', alpha=0.8, edgecolor='black', linewidth=0.5)
bars2 = plt.bar(x + width/2, pve_44Sc, width, label='44Sc', color='crimson', alpha=0.8, edgecolor='black', linewidth=0.5)

plt.xlabel('Średnica sfery z fantomu NEMA [mm]', fontsize=12, fontweight='bold')
plt.ylabel('Spill-out PVE [%]', fontsize=12, fontweight='bold')
plt.title('Porównanie ucieczki pozytonów ze sfery (Spill-out PVE)\nna podstawie efektywnego zasięgu (R_mean)', fontsize=14)
plt.xticks(x, [f'{d} mm' for d in diameters_mm], fontsize=11)
plt.yticks(fontsize=11)
plt.legend(fontsize=11)
plt.grid(axis='y', linestyle='--', alpha=0.7)

# Dodanie dokładnych wartości nad słupkami
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
plt.show()'''

###poprawka na grubość sfery i plastik

import numpy as np
import matplotlib.pyplot as plt

# -------------------------------------------------------
# 1. Parametry fizyczne i symulacji
# -------------------------------------------------------
m_e = 0.511        # masa elektronu/pozytonu [MeV]
rho_water = 1.0    # gęstość wody [g/cm^3]
rho_plastic = 1.18 # gęstość plastiku PMMA [g/cm^3]
wall_thickness_mm = 1.0 # Grubość ścianki [mm]
N_sim = 5000       # liczba losowań na sferę

isotopes = {
    "18F": (0.634, 8),
    "44Sc": (1.474, 20)
}
diameters_mm = [10, 13, 17, 22, 28, 37]

# -------------------------------------------------------
# 2. Funkcje modelu fizycznego
# -------------------------------------------------------
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

def compute_R_mean(E):
    """Oblicza bazowy zasięg dla wody (wzór Cal-Gonzalez), wynik w mm."""
    return (0.108 * E**1.14 / rho_water) * 10

def sample_energies(E0, Z, N):
    """Losuje energie z widma beta+."""
    E_grid = np.linspace(0.01, E0, 5000)
    spectrum = beta_plus_spectrum(E_grid, E0, Z)
    cdf = np.cumsum(spectrum)
    cdf = cdf / cdf[-1]
    return np.interp(np.random.rand(N), cdf, E_grid)

# -------------------------------------------------------
# 3. Symulacja Monte Carlo
# -------------------------------------------------------
np.random.seed(42) # Dla powtarzalności wyników
pve_18F = []
pve_44Sc = []

print("Rozpoczynam symulację...")

for iso, (E0, Z) in isotopes.items():
    for d in diameters_mm:
        R_in = d / 2.0
        R_out = R_in + wall_thickness_mm
        
        # Losowanie jednorodnej pozycji wewnątrz sfery (tylko woda)
        r_pos = R_in * np.random.rand(N_sim)**(1/3)
        theta_pos = 2 * np.pi * np.random.rand(N_sim)
        cos_phi_pos = 1 - 2 * np.random.rand(N_sim)
        sin_phi_pos = np.sqrt(1 - cos_phi_pos**2)
        
        x0 = r_pos * sin_phi_pos * np.cos(theta_pos)
        y0 = r_pos * sin_phi_pos * np.sin(theta_pos)
        z0 = r_pos * cos_phi_pos
        
        # Losowanie izotropowego kierunku emisji
        theta_dir = 2 * np.pi * np.random.rand(N_sim)
        cos_phi_dir = 1 - 2 * np.random.rand(N_sim)
        sin_phi_dir = np.sqrt(1 - cos_phi_dir**2)
        
        dx = sin_phi_dir * np.cos(theta_dir)
        dy = sin_phi_dir * np.sin(theta_dir)
        dz = cos_phi_dir
        
        # Wyznaczanie zasięgu na podstawie wylosowanej energii
        E_sampled = sample_energies(E0, Z, N_sim)
        R_eff = compute_R_mean(E_sampled)
        
        # Ray-tracing (przecięcie ze sferami)
        b = x0*dx + y0*dy + z0*dz
        r2 = x0**2 + y0**2 + z0**2
        
        t1 = -b + np.sqrt(b**2 - (r2 - R_in**2))
        t2 = -b + np.sqrt(b**2 - (r2 - R_out**2))
        
        # Koszt przejścia przez plastik
        W_plastic = (t2 - t1) * (rho_plastic / rho_water)
        
        d_actual = np.zeros(N_sim)
        
        # Warunek A: Zatrzymuje się w wodzie
        mask1 = R_eff <= t1
        d_actual[mask1] = R_eff[mask1]
        
        # Warunek B: Zatrzymuje się w plastiku
        mask2 = (R_eff > t1) & (R_eff <= t1 + W_plastic)
        d_actual[mask2] = t1[mask2] + (R_eff[mask2] - t1[mask2]) * (rho_water / rho_plastic)
        
        # Warunek C: Przebija plastik na wylot do wody
        mask3 = R_eff > t1 + W_plastic
        d_actual[mask3] = t2[mask3] + (R_eff[mask3] - t1[mask3] - W_plastic[mask3])
        
        # Obliczanie pozycji końcowej
        xf = x0 + d_actual * dx
        yf = y0 + d_actual * dy
        zf = z0 + d_actual * dz
        Rf = np.sqrt(xf**2 + yf**2 + zf**2)
        
        # Obliczanie frakcji ucieczki ze sfery (Spill-out) - uwzględnia wylot poza R_in
        spill_out = (np.sum(Rf > R_in) / N_sim) * 100.0
        
        if iso == "18F":
            pve_18F.append(spill_out)
        else:
            pve_44Sc.append(spill_out)

print("Symulacja zakończona. Generuję wykres...")

# -------------------------------------------------------
# 4. Generowanie i formatowanie wykresu
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

# Dodanie dokładnych wartości nad słupkami
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
plt.show()