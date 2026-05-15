import os
import csv
import matplotlib.pyplot as plt
import numpy as np
from collections import defaultdict

def generate_nema_plots(results_dir="./diameters", thresholds=[ 40, 50, 80]):
    nema_spheres = [10, 13, 17, 22, 28, 37]
    
    # Proste i twarde mapowanie: 1 to największa (37 mm), 6 to najmniejsza (10 mm)
    diam_map = {
        "sphere_1": 37,
        "sphere_2": 28,
        "sphere_3": 22,
        "sphere_4": 17,
        "sphere_5": 13,
        "sphere_6": 10
    }
    
    # Struktura: data_plot[case_name][threshold][true_diameter] = (measured_diameter, error)
    data_plot = defaultdict(lambda: defaultdict(dict))

    # 1. WCZYTYWANIE I MAPOWANIE DANYCH
    for th in thresholds:
        csv_path = os.path.join(results_dir, f"wyniki_sfer_dim_{th}.csv")
        if not os.path.exists(csv_path): continue
            
        with open(csv_path, mode="r", encoding="utf-8") as f:
            reader = csv.reader(f, delimiter=';')
            next(reader) 
            
            for row in reader:
                if len(row) < 5: continue
                file_name, _, _, diam_mm_str, err_mm_str = row
                if "DEBUG" in file_name: continue
                    
                # Identyfikacja przypadku
                if "nema_max" in file_name: case_name = "Eksperyment"
                elif "cal_gonzales_18F" in file_name: case_name = "sym_C-G_18F"
                elif "cal_gonzales_44Sc" in file_name: case_name = "sym_C-G_44Sc"
                elif "CSDA_18F" in file_name: case_name = "sym_CSDA_18F"
                elif "CSDA_44Sc" in file_name: case_name = "sym_CSDA_44Sc"
                else: continue

                # Przypisanie rzeczywistej średnicy z nazwy (od sphere_1 do sphere_6)
                true_diam = None
                for key, val in diam_map.items():
                    if key in file_name:
                        true_diam = val
                        break
                        
                if true_diam is None: continue
                    
                diam_mm = float(diam_mm_str)
                err_mm = float(err_mm_str)
                
                if diam_mm > 0:
                    data_plot[case_name][th][true_diam] = (diam_mm, err_mm)

    # 2. RYSOWANIE WYKRESÓW
    for case_name, th_data in data_plot.items():
        plt.figure(figsize=(10, 6))
        ideal_x = np.linspace(8, 40, 100)
        plt.plot(ideal_x, ideal_x, 'k--', alpha=0.6, label="Idealne dopasowanie (y=x)")

        markers = {40: 'o', 50: 's', 80: 'v'}
        
        for th in thresholds:
            if th not in th_data or not th_data[th]: continue
            
            sorted_true = sorted(th_data[th].keys())
            measured = [th_data[th][x][0] for x in sorted_true]
            errors = [th_data[th][x][1] for x in sorted_true]
            
            plt.errorbar(
                sorted_true, measured, yerr=errors, 
                fmt=f'-{markers.get(th, "o")}', capsize=5, capthick=1.5, 
                label=f"Próg {th}%"
            )
            
        plt.title(f"Zrekonstruowana vs Rzeczywista średnica sfer\n{case_name}")
        plt.xlabel("Rzeczywista średnica sfery NEMA [mm]")
        plt.ylabel("Zmierzona średnica [mm]")
        plt.xticks(nema_spheres)
        plt.grid(True, linestyle=':', alpha=0.7)
        plt.legend()
        
        out_plot_path = os.path.join(results_dir, f"wykres_40_50_80_{case_name}.png")
        plt.savefig(out_plot_path, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"Zapisano wykres: {out_plot_path}")

# Uruchomienie
generate_nema_plots()