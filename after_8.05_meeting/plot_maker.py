import os
import csv
import matplotlib.pyplot as plt
import numpy as np

def get_case_and_true_diam(filename):
    # 1. Ignorowanie plików DEBUG_MASKED
    if "DEBUG" in filename:
        return None, None
        
    # 2. Identyfikacja przypadku i wybór mapowania
    if "nema_max" in filename:
        case = "Eksperyment"
        # Mapowanie dla eksperymentu dopasowane do wyników ze zdjęcia
        diam_map = {
            "sphere_4": 22, 
            "sphere_2": 28, 
            "sphere_1": 37, 
            "sphere_6": 10, 
            "sphere_5": 13, 
            "sphere_3": 17
        }
    else:
        if "18F_cal_gonzales" in filename: case = "sym_C-G_18F"
        elif "44Sc_cal_gonzales" in filename: case = "sym_C-G_44Sc"
        elif "18F_CSDA" in filename: case = "sym_CSDA_18F"
        elif "44Sc_CSDA" in filename: case = "sym_CSDA_44Sc"
        else: return None, None
        
        # Mapowanie dla symulacji (od największej do najmniejszej)
        diam_map = {
            "sphere_1": 37, 
            "sphere_2": 28, 
            "sphere_3": 22, 
            "sphere_4": 17, 
            "sphere_5": 13, 
            "sphere_6": 10
        }

    # 3. Zwrócenie rzeczywistej średnicy dla konkretnej sfery
    for key, true_diam in diam_map.items():
        if key in filename:
            return case, true_diam
            
    return case, None

def generate_nema_plots(results_dir="./after_8.05_meeting/", thresholds=[40, 50, 80]):
    nema_spheres = [10, 13, 17, 22, 28, 37]
    
    # data[case][threshold][true_diameter] = (measured_diameter, error)
    data = {}

    # Wczytywanie danych
    for th in thresholds:
        csv_path = os.path.join(results_dir, f"dim_finder_csv_fwhm_smoothing/wyniki_sfer_dim_{th}.csv")
        if not os.path.exists(csv_path): continue
            
        with open(csv_path, mode="r", encoding="utf-8") as f:
            reader = csv.reader(f, delimiter=';')
            next(reader) 
            
            for row in reader:
                if len(row) < 5: continue
                file_name, _, _, diam_mm_str, err_mm_str = row
                
                case_name, true_diam = get_case_and_true_diam(file_name)
                
                if case_name is None or true_diam is None: continue
                    
                if case_name not in data:
                    data[case_name] = {t: {} for t in thresholds}
                    
                diam_mm = float(diam_mm_str)
                err_mm = float(err_mm_str)
                
                if diam_mm > 0:
                    data[case_name][th][true_diam] = (diam_mm, err_mm)

    # Rysowanie wykresów
    for case_name, th_data in data.items():
        plt.figure(figsize=(10, 6))
        
        ideal_x = np.linspace(8, 40, 100)
        plt.plot(ideal_x, ideal_x, 'k--', alpha=0.6, label="Perfect fit (y=x)")

        markers = {40: 'o', 50: 's', 80: 'v'}
        
        for th in thresholds:
            points = th_data[th]
            if not points: continue
            
            sorted_true = sorted(points.keys())
            measured = [points[x][0] for x in sorted_true]
            errors = [points[x][1] for x in sorted_true]
            
            plt.errorbar(
                sorted_true, measured, yerr=errors, 
                fmt=f'-{markers[th]}', capsize=5, capthick=1.5, 
                label=f"threshold {th}%"
            )
            
        plt.title(f"Reconstructed vs Real sphere diameter")
        plt.xlabel("Real NEMA IQ phantom sphere diameter [mm]")
        plt.ylabel("Reconstructed diameter [mm]")
        plt.xticks(nema_spheres)
        plt.grid(True, linestyle=':', alpha=0.7)
        plt.legend()
        
        out_plot_path = os.path.join(results_dir, f"wykres_ang_{case_name}.png")
        plt.savefig(out_plot_path, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"Zapisano: {out_plot_path}")

# Uruchomienie skryptu (nie trzeba już podawać ścieżek wejściowych)
generate_nema_plots()