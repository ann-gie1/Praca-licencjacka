###Katz-Penfold Formula (najgorszy scenariusz)

'''import numpy as np
import pandas as pd

# -------------------------------------------------------
# Zmienne i funkcje fizyczne (połączone z poprzednich kroków)
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

def compute_r(E):
    return 0.412 * E**(1.265 - 0.0954 * np.log(E))

def compute_X(E):
    return (compute_r(E) / rho) * 10  # wynik w mm

def sample_energies(E0, Z, N):
    """Losowanie energii z widma metodą odwróconej dystrybuanty (Inverse Transform Sampling)"""
    E_grid = np.linspace(0.01, E0, 5000)
    spectrum = beta_plus_spectrum(E_grid, E0, Z)
    cdf = np.cumsum(spectrum)
    cdf = cdf / cdf[-1]
    
    random_vals = np.random.rand(N)
    # Interpolacja losowych wartości na siatkę energii
    return np.interp(random_vals, cdf, E_grid)

# -------------------------------------------------------
# Symulacja Monte Carlo
# -------------------------------------------------------
# ... (część z definicją funkcji pozostaje bez zmian) ...

np.random.seed(42)
results_18F = []
results_44Sc = []

for iso, (E0, Z) in isotopes.items():
    for d in diameters_mm:
        R_sphere = d / 2.0
        
        # 1. Losowanie pozycji (równomiernie w sferze)
        r_pos = R_sphere * np.random.rand(N_sim)**(1/3)
        theta_pos = 2 * np.pi * np.random.rand(N_sim)
        cos_phi_pos = 1 - 2 * np.random.rand(N_sim)
        sin_phi_pos = np.sqrt(1 - cos_phi_pos**2)
        
        x0 = r_pos * sin_phi_pos * np.cos(theta_pos)
        y0 = r_pos * sin_phi_pos * np.sin(theta_pos)
        z0 = r_pos * cos_phi_pos
        
        # 2. Losowanie kierunku (izotropowo)
        theta_dir = 2 * np.pi * np.random.rand(N_sim)
        cos_phi_dir = 1 - 2 * np.random.rand(N_sim)
        sin_phi_dir = np.sqrt(1 - cos_phi_dir**2)
        
        dx = sin_phi_dir * np.cos(theta_dir)
        dy = sin_phi_dir * np.sin(theta_dir)
        dz = cos_phi_dir
        
        # 3. Zasięg (z widma)
        E_sampled = sample_energies(E0, Z, N_sim)
        X_range = compute_X(E_sampled)
        
        # 4. Pozycja końcowa
        xf = x0 + X_range * dx
        yf = y0 + X_range * dy
        zf = z0 + X_range * dz
        Rf = np.sqrt(xf**2 + yf**2 + zf**2)
        
        # 5. Metryki + PVE (Spill-out)
        max_R = np.max(Rf)
        mean_R = np.mean(Rf)
        median_R = np.median(Rf)
        
        # Obliczenie odsetka pozytonów, które wyleciały poza sferę
        spill_out_percent = (np.sum(Rf > R_sphere) / N_sim) * 100.0
        
        row = {
            "Średnica sfery [mm]": d,
            "Max R końcowy [mm]": round(max_R, 3),
            "Średni R końcowy [mm]": round(mean_R, 3),
            "Mediana R końcowego [mm]": round(median_R, 3),
            "Spill-out PVE [%]": round(spill_out_percent, 1)
        }
        
        if iso == "18F":
            results_18F.append(row)
        else:
            results_44Sc.append(row)

# Wyświetlanie tabel
df_18F = pd.DataFrame(results_18F)
df_44Sc = pd.DataFrame(results_44Sc)

print("\n=== WYNIKI DLA FLUORU (18F) ===")
print(df_18F.to_string(index=False))
print("\n=== WYNIKI DLA SKANDU (44Sc) ===")
print(df_44Sc.to_string(index=False))'''

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
N_sim = 5000

def momentum(E): # założenie: liczymy tylko dla elektronu
    return np.sqrt(E**2 + 2 * m_e * E) # liczenie pędu

def fermi_function_allowed(Z, E):  
    alpha = 1/137
    p = momentum(E)
    p = np.where(p==0, 1e-9, p)
    eta = alpha * Z * (E + m_e) / p
    return (2 * np.pi * eta) / (1 - np.exp(-2 * np.pi * eta))

def beta_plus_spectrum(E, E0, Z):  # (energia, energia maksymalna, liczba atomowa)
    p = momentum(E)
    F = fermi_function_allowed(Z, E)
    return p * E * (E0 - E)**2 * F

def compute_r(E): # TUTAJ NAPISAĆ SKĄD WZÓR
    return 0.412 * E**(1.265 - 0.0954 * np.log(E)) # zwraca odpowiedź w [cm]

def compute_X(E):
    fromMMtoCM = 10 
    return (compute_r(E) / rho_water) * fromMMtoCM  # Zasięg bazowy ekwiwalentny wodzie w mm, *10 

def sample_energies(E0, Z, N): # energia maksymalna, liczba atomowa  i liczba sampli
    startOfRange = 0.01
    endOfRange = 5000
    # TO DO, dodać liczenie maksymalnej energii emisji
    E_grid = np.linspace(startOfRange, E0, endOfRange)
    print( E_grid )
    spectrum = beta_plus_spectrum(E_grid, E0, Z)
    print( spectrum )
    cdf = np.cumsum(spectrum)
    print (cdf)
    cdf = cdf / cdf[-1]
    print (cdf)
    return np.interp(np.random.rand(N), cdf, E_grid)

# -------------------------------------------------------
# Symulacja Monte Carlo z geometrią sfery (woda -> plastik -> woda)
# -------------------------------------------------------
np.random.seed(42)
results_18F = []
results_44Sc = []

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
        
        #TO DO WYRYSOWAĆ X0, Y0, Z0, r_pos, theta_pos, cos_phi_pos, sin_phi_pos


        # 2. Losowanie kierunku
        theta_dir = 2 * np.pi * np.random.rand(N_sim)
        cos_phi_dir = 1 - 2 * np.random.rand(N_sim)
        sin_phi_dir = np.sqrt(1 - cos_phi_dir**2)
        
        dx = sin_phi_dir * np.cos(theta_dir)
        dy = sin_phi_dir * np.sin(theta_dir)
        dz = cos_phi_dir
        
        #Jak w :194 zrobić rysunki kontrolne

        # 3. Zasięg bazowy (wodny)
        E_sampled = sample_energies(E0, Z, N_sim)
        X_range = compute_X(E_sampled)
        
        # 4. Ray-tracing: Przecięcie promienia ze sferą wewnętrzną i zewnętrzną
        b = x0*dx + y0*dy + z0*dz
        r2 = x0**2 + y0**2 + z0**2
        
        t1 = -b + np.sqrt(b**2 - (r2 - R_in**2))   # Dystans do wewnętrznej ścianki plastiku
        t2 = -b + np.sqrt(b**2 - (r2 - R_out**2))  # Dystans do zewnętrznej ścianki plastiku
        
        # DODAĆ RYSUNKI JAK GRAFICZNIE WYGLĄDA POSZUKIWANIE

        # 5. Obliczanie właściwego dystansu z uwzględnieniem gęstości plastiku
        W_plastic = (t2 - t1) * (rho_plastic / rho_water) # Koszt przejścia przez plastik w ekwiwalencie wodnym
        
        # DO PRZEMYŚLENIA

        d_actual = np.zeros(N_sim)
        
        # Zatrzymuje się w wodzie wewnętrznej
        mask1 = X_range <= t1
        d_actual[mask1] = X_range[mask1]
        
        # Zatrzymuje się w plastiku
        mask2 = (X_range > t1) & (X_range <= t1 + W_plastic)
        d_actual[mask2] = t1[mask2] + (X_range[mask2] - t1[mask2]) * (rho_water / rho_plastic)
        
        # Przebija plastik i anihiluje w wodzie na zewnątrz
        mask3 = X_range > t1 + W_plastic
        d_actual[mask3] = t2[mask3] + (X_range[mask3] - t1[mask3] - W_plastic[mask3])
        
        # 6. Pozycja końcowa
        xf = x0 + d_actual * dx
        yf = y0 + d_actual * dy
        zf = z0 + d_actual * dz
        Rf = np.sqrt(xf**2 + yf**2 + zf**2)
        
        # TUTAJ ZROBIC DUMP DO PLIKU. FORMAT DO USTALENIA

        # 7. Metryki
        # Spill-out dotyczy opuszczenia aktywnej objętości wewnętrznej (R_in)
        spill_out_percent = (np.sum(Rf > R_in) / N_sim) * 100.0
        
        row = {
            "Średnica sfery [mm]": d,
            "Max R końcowy [mm]": round(np.max(Rf), 3),
            "Średni R końcowy [mm]": round(np.mean(Rf), 3),
            "Mediana R końcowego [mm]": round(np.median(Rf), 3),
            "Spill-out PVE [%]": round(spill_out_percent, 1)
        }
        
        if iso == "18F":
            results_18F.append(row)
        else:
            results_44Sc.append(row)

# Wyświetlanie tabel
print("\n=== WYNIKI DLA FLUORU (18F) ===")
print(pd.DataFrame(results_18F).to_string(index=False))
print("\n=== WYNIKI DLA SKANDU (44Sc) ===")
print(pd.DataFrame(results_44Sc).to_string(index=False))
