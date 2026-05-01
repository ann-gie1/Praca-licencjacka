import numpy as np
import pandas as pd

# -------------------------------------------------------
# Zmienne i funkcje fizyczne
# -------------------------------------------------------
m_e = 0.511               # masa elektronu w [MeV/c2]
rho_water = 1.0           # gęstość wody [g/cm^3]
rho_plastic = 1.18        # gęstość plastiku (np. PMMA/Akryl) [g/cm^3]
wall_thickness_mm = 1.0   # Grubość ścianki w [mm]

# Z to liczba atomowa jądra pochodnego (córki): O(8) dla 18F, Ca(20) dla 44Sc
isotopes = {"18F": (0.634, 8), "44Sc": (1.474, 20)} 
diameters_mm = [10, 13, 17, 22, 28, 37] # Średnice WEWNĘTRZNE (woda)

# Baza do obliczeń koncentracji
base_diameter_mm = 10.0
base_N_sim = 1000000

def momentum(E):
    return np.sqrt(E**2 + 2 * m_e * E)

def fermi_function_allowed(Z, E):  
    alpha = 1/137
    p = momentum(E)
    p = np.where(p==0, 1e-9, p)
    eta = -alpha * Z * (E + m_e) / p
    return (2 * np.pi * eta) / (1 - np.exp(-2 * np.pi * eta))

def beta_plus_spectrum(E, E0, Z):  
    p = momentum(E)
    F = fermi_function_allowed(Z, E)
    return p * (E + m_e) * (E0 - E)**2 * F

def compute_r(E): 
    return 0.412 * E**(1.265 - 0.0954 * np.log(E)) 

def compute_X(E):
    fromMMtoCM = 10 
    return (compute_r(E) / rho_water) * fromMMtoCM  

def sample_energies(E0, Z, N): 
    startOfRange = 0.01
    endOfRange = 5000

    E_grid = np.linspace(startOfRange, E0, endOfRange)
    spectrum = beta_plus_spectrum(E_grid, E0, Z)
    cdf = np.cumsum(spectrum)
    cdf = cdf / cdf[-1]
    
    return np.interp(np.random.rand(N), cdf, E_grid)

# -------------------------------------------------------
# Symulacja Monte Carlo
# -------------------------------------------------------
list_of_hist_df = []
list_of_df = []
global_idx = 0

for iso, (E0, Z) in isotopes.items():
    for d in diameters_mm:
        
        # Koncentracja: Objętość skaluje się z sześcianem średnicy
        N_sim = int(base_N_sim * (d / base_diameter_mm)**3)
        
        R_in = d / 2.0
        R_out = R_in + wall_thickness_mm
        
        # 1. Losowanie pozycji początkowej 
        r_pos = R_in * np.random.rand(N_sim)**(1/3)
        theta_pos = 2 * np.pi * np.random.rand(N_sim)
        cos_phi_pos = 1 - 2 * np.random.rand(N_sim)
        sin_phi_pos = np.sqrt(1 - cos_phi_pos**2)

        phi_pos = np.arccos(cos_phi_pos)

        x0 = r_pos * sin_phi_pos * np.cos(theta_pos)
        y0 = r_pos * sin_phi_pos * np.sin(theta_pos)
        z0 = r_pos * cos_phi_pos

        # 2. Losowanie kierunku
        theta_dir = 2 * np.pi * np.random.rand(N_sim)
        cos_phi_dir = 1 - 2 * np.random.rand(N_sim)
        sin_phi_dir = np.sqrt(1 - cos_phi_dir**2)
        
        dx = sin_phi_dir * np.cos(theta_dir)
        dy = sin_phi_dir * np.sin(theta_dir)
        dz = cos_phi_dir
        
        # 3. Zasięg bazowy
        E_sampled = sample_energies(E0, Z, N_sim)
        X_range = compute_X(E_sampled)

        # --- Koniec generacji
        n = np.arange(global_idx, global_idx + N_sim)

        data_hist = {
            'Srednica_mm': d,
            'r': r_pos,
            'theta': theta_pos,
            'phi': phi_pos,
            'x': x0,
            'y': y0,
            'z': z0
        }
        df_hist = pd.DataFrame(data_hist)
        list_of_hist_df.append(df_hist)

        data = {
            'Index': n, 
            'Izotop': iso,
            'Srednica_mm': d,
            'x': x0, 
            'y': y0, 
            'z': z0, 
            'dx': dx, 
            'dy': dy, 
            'dz': dz, 
            'Energia-wylosowana': E_sampled, 
            'Range': X_range
        }
        df = pd.DataFrame(data)

        list_of_df.append(df)
        global_idx += N_sim

final_df = pd.concat(list_of_df)
final_df.to_csv("../dane_symulacja_CSDA/Generacja_danych_1mln-conc.csv", index=False)
#final_hist_df = pd.concat(list_of_hist_df)
#final_hist_df.to_csv("../dane_symulacja_CSDA/histogramy_weryfikacja_1mln.csv", index=False)