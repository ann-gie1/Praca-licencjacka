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

# -------------------------------------------------------
# Symulacja Monte Carlo z geometrią sfery (woda -> plastik -> woda)
# -------------------------------------------------------
results_18F = []
results_44Sc = []
list_of_df =[]

df = pd.read_csv("../dane_symulacja_CSDA/Generacja_danych.csv")
grouped_df = df.groupby(['Izotop', 'Srednica_mm'])
N_sim = int(len(df)/len(grouped_df))
for (iso, d), group in grouped_df:
    # Skip if the group doesn't match your target isotopes or diameters
    if iso not in isotopes or d not in diameters_mm:
        continue

    R_in = d / 2.0
    R_out = R_in + wall_thickness_mm
    
    n = group['Index']
    # Extract data directly from the subset (O(1) operation)
    x0 = group['x']
    y0 = group['y']
    z0 = group['z']
    dx = group['dx']
    dy = group['dy']
    dz = group['dz']
    X_range = group['Range']

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
    data = {'Index': n, 'Izotop': iso,'Srednica_mm': d,'xf': xf, 'yf': yf, 'zf': zf}
    df_MC = pd.DataFrame(data)

    list_of_df.append(df_MC)

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

final_df = pd.concat(list_of_df)
final_df.to_csv("../dane_symulacja_CSDA/wyniki_symulacji.csv", index=False)
