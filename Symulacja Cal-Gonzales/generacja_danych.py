## poprawka na średnice
import numpy as np
import pandas as pd

# -------------------------------------------------------
# Zmienne i funkcje fizyczne
# -------------------------------------------------------
m_e = 0.511                 # masa elektronu w [MeV/c2]
rho_water = 1.0           # gęstość wody [g/cm^3]
rho_plastic = 1.18        # gęstość plastiku (np. PMMA/Akryl) [g/cm^3]
wall_thickness_mm = 1.0   # Grubość ścianki w [mm] (zmień na 10.0 jeśli serio miały to być "cm")

isotopes = {"18F": (0.634, 8), "44Sc": (1.474, 20)} # max energia emisji, liczba atomowa isotopu <<< DO SPRAWDZENIA :)
diameters_mm = [10, 13, 17, 22, 28, 37] # Średnice WEWNĘTRZNE (woda)
N_sim = 1000000

def momentum(E): # założenie: liczymy tylko dla elektronu
    return np.sqrt(E**2 + 2 * m_e * E) # liczenie pędu

def fermi_function_allowed(Z, E):  
    alpha = 1/137
    p = momentum(E)
    p = np.where(p==0, 1e-9, p)
    eta = - alpha * Z * (E + m_e) / p
    return (2 * np.pi * eta) / (1 - np.exp(-2 * np.pi * eta))

def beta_plus_spectrum(E, E0, Z):  # (energia, energia maksymalna, liczba atomowa)
    p = momentum(E)
    F = fermi_function_allowed(Z, E)
    return p * (E + m_e) * (E0 - E)**2 * F

def compute_R_mean(E):
    fromMMtoCM = 10
    # Obliczamy bazowy zasięg dla wody. Korekta na plastik nastąpi w pętli.
    return (0.108 * E**1.14 / rho_water) * fromMMtoCM

def sample_energies(E0, Z, N): # energia maksymalna, liczba atomowa  i liczba sampli
    startOfRange = 0.01
    endOfRange = 5000
    # TO DO, dodać liczenie maksymalnej energii emisji
    E_grid = np.linspace(startOfRange, E0, endOfRange)
    spectrum = beta_plus_spectrum(E_grid, E0, Z)
    cdf = np.cumsum(spectrum)
    cdf = cdf / cdf[-1]

    return np.interp(np.random.rand(N), cdf, E_grid)

# -------------------------------------------------------
# Symulacja Monte Carlo z geometrią sfery (woda -> plastik -> woda)
# -------------------------------------------------------
list_of_hist_df = []
list_of_df = []
global_idx = 0
for iso, (E0, Z) in isotopes.items():
    for d in diameters_mm:
        # DODAĆ SYMULACJĘ EVENT BY EVENT < - niski priorytet
        R_in = d / 2.0
        R_out = R_in + wall_thickness_mm
        
        # 1. Losowanie pozycji początkowej (tylko w wewnętrznej wodzie)
        r_pos = R_in * np.random.rand(N_sim)**(1/3)
        theta_pos = 2 * np.pi * np.random.rand(N_sim)
        cos_phi_pos = 1 - 2 * np.random.rand(N_sim)
        sin_phi_pos = np.sqrt(1 - cos_phi_pos**2)
        
        x0 = r_pos * sin_phi_pos * np.cos(theta_pos)
        y0 = r_pos * sin_phi_pos * np.sin(theta_pos)
        z0 = r_pos * cos_phi_pos
        
        phi_pos = np.arccos(cos_phi_pos)

        # 2. Losowanie kierunku
        theta_dir = 2 * np.pi * np.random.rand(N_sim)
        cos_phi_dir = 1 - 2 * np.random.rand(N_sim)
        sin_phi_dir = np.sqrt(1 - cos_phi_dir**2)
        
        dx = sin_phi_dir * np.cos(theta_dir)
        dy = sin_phi_dir * np.sin(theta_dir)
        dz = cos_phi_dir
            # --- Koniec generacji
        n = np.arange(global_idx, global_idx + N_sim)

                # Wyciągamy tylko parametry przestrzenne do weryfikacji
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

        # 3. Zasięg bazowy (wodny)
        E_sampled = sample_energies(E0, Z, N_sim)
        X_range = compute_R_mean(E_sampled)

        # --- Koniec generacji
        n = np.arange(global_idx, global_idx + N_sim)
        data = {'Index': n, 'Izotop': iso,'Srednica_mm': d,'x': x0, 'y': y0, 'z': z0, 'dx': dx, 'dy': dy, 'dz': dz, 'Energia-wylosowana': E_sampled, 'Range': X_range}
        df = pd.DataFrame(data)

        list_of_df.append(df)

        global_idx += N_sim


final_df = pd.concat(list_of_df)
final_df.to_csv("../dane_symulacja_cal_gonzales/Generacja_danych_c-g_1mln.csv", index=False)
final_hist_df = pd.concat(list_of_hist_df)
final_hist_df.to_csv("../dane_symulacja_cal_gonzales/histogramy_weryfikacja_1mln.csv", index=False)
# TODO: Inny plik
#TO DO WYRYSOWAĆ X0, Y0, Z0, r_pos, theta_pos, cos_phi_pos, sin_phi_pos
# #Jak w :194 zrobić rysunki kontrolne - wektorki kierunku