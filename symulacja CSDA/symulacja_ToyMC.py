import numpy as np
import pandas as pd

# -------------------------------------------------------
# Zmienne i funkcje fizyczne
# -------------------------------------------------------
m_e = 0.511                 # masa elektronu w [MeV/c2]
rho_water = 1.0           # gęstość wody [g/cm^3]
rho_plastic = 1.18        # gęstość plastiku (np. PMMA/Akryl) [g/cm^3]
wall_thickness_mm = 1.0   # Grubość ścianki w [mm]

isotopes = {"18F": (0.634, 8), "44Sc": (1.474, 20)} 
diameters_mm = [10, 13, 17, 22, 28, 37] # Średnice WEWNĘTRZNE (woda)

# -------------------------------------------------------
# Symulacja Monte Carlo z geometrią sfery
# -------------------------------------------------------
results_18F = []
results_44Sc = []
list_of_df = []

print("Rozpoczynam wczytywanie pliku CSV (to może potrwać kilka minut)...")
df = pd.read_csv("../dane_symulacja_CSDA/Generacja_danych_1mln-conc20626.csv")
print(f"Pomyślnie wczytano dane: {len(df)} wierszy. Rozpoczynam grupowanie...")

grouped_df = df.groupby(['Izotop', 'Srednica_mm'])
total_groups = len(grouped_df)
print(f"Dane pogrupowane (liczba grup: {total_groups}). Start symulacji ray-tracingu...\n" + "-"*50)

# Używamy enumerate, żeby mieć licznik postępu (i)
for i, ((iso, d), group) in enumerate(grouped_df, 1):
    if iso not in isotopes or d not in diameters_mm:
        continue
    
    current_N_sim = len(group)
    print(f"[{i}/{total_groups}] Przetwarzam: Izotop {iso}, Sfera {d} mm (liczba zdarzeń: {current_N_sim})...")
    
    R_in = d / 2.0
    R_out = R_in + wall_thickness_mm
    
    n = group['Index']
    x0 = group['x']
    y0 = group['y']
    z0 = group['z']
    dx = group['dx']
    dy = group['dy']
    dz = group['dz']
    X_range = group['Range']

    # 4. Ray-tracing
    b = x0*dx + y0*dy + z0*dz
    r2 = x0**2 + y0**2 + z0**2
    
    t1 = -b + np.sqrt(b**2 - (r2 - R_in**2))   
    t2 = -b + np.sqrt(b**2 - (r2 - R_out**2))  
    
    # 5. Obliczanie właściwego dystansu
    W_plastic = (t2 - t1) * (rho_plastic / rho_water) 
    
    d_actual = np.zeros(current_N_sim)
    
    mask1 = X_range <= t1
    d_actual[mask1] = X_range[mask1]
    
    mask2 = (X_range > t1) & (X_range <= t1 + W_plastic)
    d_actual[mask2] = t1[mask2] + (X_range[mask2] - t1[mask2]) * (rho_water / rho_plastic)
    
    mask3 = X_range > t1 + W_plastic
    d_actual[mask3] = t2[mask3] + (X_range[mask3] - t1[mask3] - W_plastic[mask3])
    
    # 6. Pozycja końcowa
    xf = x0 + d_actual * dx
    yf = y0 + d_actual * dy
    zf = z0 + d_actual * dz
    Rf = np.sqrt(xf**2 + yf**2 + zf**2)
    
    data = {'Index': n, 'Izotop': iso,'Srednica_mm': d,'xf': xf, 'yf': yf, 'zf': zf}
    df_MC = pd.DataFrame(data)

    list_of_df.append(df_MC)

    # 7. Metryki
    spill_out_percent = (np.sum(Rf > R_in) / current_N_sim) * 100.0
    
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

print("-" * 50)
print("Łączenie i zapisywanie wyników końcowych do pliku CSV...")
final_df = pd.concat(list_of_df)
final_df.to_csv("../dane_symulacja_CSDA/wyniki_symulacji_1mln-conc20626.csv", index=False)
print("Gotowe!")