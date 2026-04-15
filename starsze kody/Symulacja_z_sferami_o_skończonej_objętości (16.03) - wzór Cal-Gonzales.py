###Cal-Gonzales wzory z publikacji grupy
'''import numpy as np
import pandas as pd

# -------------------------------------------------------
# Parametry fizyczne
# -------------------------------------------------------
m_e = 0.511
rho = 1.0
isotopes = {"18F": (0.634, 8), "44Sc": (1.474, 20)}
diameters_mm = [10, 13, 17, 22, 28, 37]
N_sim = 5000

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

    return (0.108 * E**1.14 / rho) * 10

def sample_energies(E0, Z, N):
    E_grid = np.linspace(0.01, E0, 5000)
    spectrum = beta_plus_spectrum(E_grid, E0, Z)
    cdf = np.cumsum(spectrum)
    cdf = cdf / cdf[-1]
    return np.interp(np.random.rand(N), cdf, E_grid)

# -------------------------------------------------------
# Symulacja Monte Carlo
# -------------------------------------------------------
np.random.seed(42)
results_18F = []
results_44Sc = []

for iso, (E0, Z) in isotopes.items():
    for d in diameters_mm:
        R_sphere = d / 2.0
        
        # 1. Pozycja początkowa
        r_pos = R_sphere * np.random.rand(N_sim)**(1/3)
        theta_pos = 2 * np.pi * np.random.rand(N_sim)
        cos_phi_pos = 1 - 2 * np.random.rand(N_sim)
        sin_phi_pos = np.sqrt(1 - cos_phi_pos**2)
        
        x0 = r_pos * sin_phi_pos * np.cos(theta_pos)
        y0 = r_pos * sin_phi_pos * np.sin(theta_pos)
        z0 = r_pos * cos_phi_pos
        
        # 2. Kierunek
        theta_dir = 2 * np.pi * np.random.rand(N_sim)
        cos_phi_dir = 1 - 2 * np.random.rand(N_sim)
        sin_phi_dir = np.sqrt(1 - cos_phi_dir**2)
        
        dx = sin_phi_dir * np.cos(theta_dir)
        dy = sin_phi_dir * np.sin(theta_dir)
        dz = cos_phi_dir
        
        # 3. Zasięg uwzględniający nieliniowość (R_mean)
        E_sampled = sample_energies(E0, Z, N_sim)
        R_eff = compute_R_mean(E_sampled)
        
        # 4. Pozycja końcowa
        xf = x0 + R_eff * dx
        yf = y0 + R_eff * dy
        zf = z0 + R_eff * dz
        Rf = np.sqrt(xf**2 + yf**2 + zf**2)
        
        # 5. Metryki + PVE
        row = {
            "Średnica sfery [mm]": d,
            "Max R końcowy [mm]": round(np.max(Rf), 3),
            "Średni R końcowy [mm]": round(np.mean(Rf), 3),
            "Mediana R końcowego [mm]": round(np.median(Rf), 3),
            "Spill-out PVE [%]": round((np.sum(Rf > R_sphere) / N_sim) * 100.0, 1)
        }
        
        if iso == "18F":
            results_18F.append(row)
        else:
            results_44Sc.append(row)

# -------------------------------------------------------
# Wyświetlanie
# -------------------------------------------------------
print("\n=== WYNIKI DLA FLUORU (18F) ===")
print(pd.DataFrame(results_18F).to_string(index=False))
print("\n=== WYNIKI DLA SKANDU (44Sc) ===")
print(pd.DataFrame(results_44Sc).to_string(index=False))'''

###Poprawka na grubość ścianki
import numpy as np
import pandas as pd

# -------------------------------------------------------
# Parametry fizyczne i geometria
# -------------------------------------------------------
m_e = 0.511
rho_water = 1.0           # gęstość wody [g/cm^3]
rho_plastic = 1.18        # gęstość plastiku PMMA [g/cm^3]
wall_thickness_mm = 1.0   # Grubość ścianki w mm

isotopes = {"18F": (0.634, 8), "44Sc": (1.474, 20)}
diameters_mm = [10, 13, 17, 22, 28, 37] # Średnice wewnętrzne (woda)
N_sim = 5000

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
    # Obliczamy bazowy zasięg dla wody. Korekta na plastik nastąpi w pętli.
    return (0.108 * E**1.14 / rho_water) * 10

def sample_energies(E0, Z, N):
    E_grid = np.linspace(0.01, E0, 5000)
    spectrum = beta_plus_spectrum(E_grid, E0, Z)
    cdf = np.cumsum(spectrum)
    cdf = cdf / cdf[-1]
    return np.interp(np.random.rand(N), cdf, E_grid)

# -------------------------------------------------------
# Symulacja Monte Carlo
# -------------------------------------------------------
np.random.seed(42)
results_18F = []
results_44Sc = []

for iso, (E0, Z) in isotopes.items():
    for d in diameters_mm:
        R_in = d / 2.0
        R_out = R_in + wall_thickness_mm
        
        # 1. Pozycja początkowa (losowanie tylko w wodzie wewnętrznej)
        r_pos = R_in * np.random.rand(N_sim)**(1/3)
        theta_pos = 2 * np.pi * np.random.rand(N_sim)
        cos_phi_pos = 1 - 2 * np.random.rand(N_sim)
        sin_phi_pos = np.sqrt(1 - cos_phi_pos**2)
        
        x0 = r_pos * sin_phi_pos * np.cos(theta_pos)
        y0 = r_pos * sin_phi_pos * np.sin(theta_pos)
        z0 = r_pos * cos_phi_pos
        
        # 2. Kierunek
        theta_dir = 2 * np.pi * np.random.rand(N_sim)
        cos_phi_dir = 1 - 2 * np.random.rand(N_sim)
        sin_phi_dir = np.sqrt(1 - cos_phi_dir**2)
        
        dx = sin_phi_dir * np.cos(theta_dir)
        dy = sin_phi_dir * np.sin(theta_dir)
        dz = cos_phi_dir
        
        # 3. Zasięg bazowy z modelu Cal-Gonzalez
        E_sampled = sample_energies(E0, Z, N_sim)
        R_eff = compute_R_mean(E_sampled)
        
        # 4. Ray-tracing (przecięcie ze sferami)
        b = x0*dx + y0*dy + z0*dz
        r2 = x0**2 + y0**2 + z0**2
        
        t1 = -b + np.sqrt(b**2 - (r2 - R_in**2))
        t2 = -b + np.sqrt(b**2 - (r2 - R_out**2))
        
        # 5. Koszt przejścia przez plastik
        W_plastic = (t2 - t1) * (rho_plastic / rho_water)
        
        d_actual = np.zeros(N_sim)
        
        # Warunek A: Pozyton zatrzymuje się zanim dotrze do plastiku
        mask1 = R_eff <= t1
        d_actual[mask1] = R_eff[mask1]
        
        # Warunek B: Pozyton zatrzymuje się wewnątrz plastiku
        mask2 = (R_eff > t1) & (R_eff <= t1 + W_plastic)
        d_actual[mask2] = t1[mask2] + (R_eff[mask2] - t1[mask2]) * (rho_water / rho_plastic)
        
        # Warunek C: Pozyton przebija plastik na wylot
        mask3 = R_eff > t1 + W_plastic
        d_actual[mask3] = t2[mask3] + (R_eff[mask3] - t1[mask3] - W_plastic[mask3])
        
        # 6. Pozycja końcowa
        xf = x0 + d_actual * dx
        yf = y0 + d_actual * dy
        zf = z0 + d_actual * dz
        Rf = np.sqrt(xf**2 + yf**2 + zf**2)
        
        # 7. Metryki + PVE
        row = {
            "Średnica sfery [mm]": d,
            "Max R końcowy [mm]": round(np.max(Rf), 3),
            "Średni R końcowy [mm]": round(np.mean(Rf), 3),
            "Mediana R końcowego [mm]": round(np.median(Rf), 3),
            "Spill-out PVE [%]": round((np.sum(Rf > R_in) / N_sim) * 100.0, 1)
        }
        
        if iso == "18F":
            results_18F.append(row)
        else:
            results_44Sc.append(row)

# -------------------------------------------------------
# Wyświetlanie
# -------------------------------------------------------
print("\n=== WYNIKI DLA FLUORU (18F) ===")
print(pd.DataFrame(results_18F).to_string(index=False))
print("\n=== WYNIKI DLA SKANDU (44Sc) ===")
print(pd.DataFrame(results_44Sc).to_string(index=False))