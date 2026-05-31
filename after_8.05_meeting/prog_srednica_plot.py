import pandas as pd
import matplotlib.pyplot as plt
import glob
import re

# Powiększenie czcionki o 10 punktów (domyślny rozmiar to zazwyczaj 10)
plt.rcParams.update({'font.size': 20})

diam_map = {
    "sphere_4": 22, 
    "sphere_2": 28, 
    "sphere_1": 37, 
    "sphere_6": 10, 
    "sphere_5": 13, 
    "sphere_3": 17
}

target_diameters = [17, 22]
plot_data = {17: {}, 22: {}}

csv_files = glob.glob("./after_8.05_meeting/dim_finder_csv_fwhm_smoothing/wyniki_sfer_dim_*.csv")

for file in csv_files:
    match = re.search(r'dim_(\d+)', file)
    if not match:
        continue
    
    threshold = int(match.group(1))
    df = pd.read_csv(file, sep=';')
    
    exp_df = df[df['Nazwa_pliku'].str.contains('nema_max', na=False)]
    
    for _, row in exp_df.iterrows():
        filename = row['Nazwa_pliku']
        
        for sphere_id, true_diam in diam_map.items():
            if sphere_id in filename and true_diam in target_diameters:
                plot_data[true_diam][threshold] = row['Srednica_mm']

# Zwiększono rozmiar figury, aby pomieścić większą czcionkę
plt.figure(figsize=(14, 8))
colors = {17: 'blue', 22: 'orange'}

for true_diam in target_diameters:
    thresholds = sorted(list(plot_data[true_diam].keys()))
    measured_diams = [plot_data[true_diam][t] for t in thresholds]
    
    # Eksperckie wyliczenie przecięcia (tylko na zboczu opadającym)
    intersection_x = None
    for i in range(len(thresholds)-1):
        x1, x2 = thresholds[i], thresholds[i+1]
        y1, y2 = measured_diams[i], measured_diams[i+1]
        
        # Szukamy przejścia przez wartość oczekiwaną, ale tylko gdy trend maleje
        if (y1 - true_diam) * (y2 - true_diam) <= 0 and y1 > y2:
            intersection_x = x1 + (true_diam - y1) * (x2 - x1) / (y2 - y1)
            break
            
    # Przygotowanie etykiety z wyliczonym progiem (zaokrąglonym do 1 miejsca po przecinku)
    match_str = f" (matches at ~{intersection_x:.1f}%)" if intersection_x else ""
    
    # Wykres wartości zmierzonej - LINIA PRZERYWANA
    plt.plot(thresholds, measured_diams, marker='o', linestyle='--', 
             color=colors[true_diam], label=f'Measured ({true_diam} mm sphere)')
    
    # Wykres odniesienia - LINIA CIĄGŁA
    plt.axhline(y=true_diam, color=colors[true_diam], linestyle='-', 
                alpha=0.5, label=f'Expected {true_diam} mm{match_str}')

plt.xlabel("Threshold (%)")
plt.ylabel("Measured diameter (mm)")
plt.title("Measured NEMA sphere diameter vs. chosen threshold")

# Dostosowanie legendy - pomniejszona nieznacznie względem reszty tekstu, by nie zasłaniała danych
plt.legend(fontsize=14, loc='upper right') 
plt.grid(True)

plt.tight_layout()
plt.savefig("./after_8.05_meeting/wykres_progi_sfery_ang.png", dpi=300)
# plt.show()