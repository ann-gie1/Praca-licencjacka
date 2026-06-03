import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os
import scipy.integrate as integrate

# --- 1. Plotting Configuration ---
plt.rcParams.update({
    'font.size': 16,
    'axes.titlesize': 20,
    'axes.labelsize': 18,
    'xtick.labelsize': 16,
    'ytick.labelsize': 16,
    'legend.fontsize': 16
})

# --- 2. Physical Parameters & Theoretical Functions ---
m_e = 0.511

isotopes = {
    "18F":  (0.634, 8),
    "44Sc": (1.474, 20),
    "68Ga": (1.899, 30)
}

def momentum(E):
    return np.sqrt(E**2 + 2 * m_e * E)

def fermi_function_allowed(Z, E):
    alpha = 1/137
    p = momentum(E)
    eta = - alpha * Z * (E + m_e) / p
    return (2 * np.pi * eta) / (1 - np.exp(-2 * np.pi * eta))

def beta_plus_spectrum(E, E0, Z):
    # POPRAWKA FIZYCZNA: Zmiana z p * E na p * (E + m_e)
    p = momentum(E)
    F = fermi_function_allowed(Z, E)
    return p * (E + m_e) * (E0 - E)**2 * F

# --- 3. Data Loading ---
plik_wejsciowy = "../dane_symulacja_CSDA/Generacja_danych_1mln-conc20626.csv"
katalog_wyjsciowy = "../dane_symulacja_CSDA/"

df = pd.read_csv(plik_wejsciowy)

if 'Izotop' not in df.columns or 'Energia-wylosowana' not in df.columns:
    raise ValueError("CSV file missing required columns: 'Izotop' or 'Energia-wylosowana'")

izotopy = df['Izotop'].unique()

# --- 4. Generating Plots in a Loop ---
for izotop in izotopy:
    df_izotop = df[df['Izotop'] == izotop]
    
    plt.figure(figsize=(12, 8))
    
    counts, bins, _ = plt.hist(df_izotop['Energia-wylosowana'], bins=100, 
                               edgecolor='black', alpha=0.65, label='Simulated Data (Histogram)')
    
    if izotop in isotopes:
        E0, Z = isotopes[izotop]
        E = np.linspace(0.001, E0, 500)
        spectrum = beta_plus_spectrum(E, E0, Z)
        
        # POPRAWKA NORMALIZACJI: Skalowanie do pola pod histogramem
        bin_width = bins[1] - bins[0]
        total_counts = len(df_izotop['Energia-wylosowana'])
        
        # Całkowanie numeryczne widma, aby uzyskać PDF o polu powierzchni = 1
        integral = integrate.trapz(spectrum, E)
        pdf = spectrum / integral
        
        # Właściwe skalowanie widma do parametrów histogramu
        normalized_spectrum = pdf * total_counts * bin_width
        
        plt.plot(E, normalized_spectrum, color='red', linewidth=3, 
                 label=f'Theoretical Spectrum ({izotop})')

    plt.title(f'Energy Distribution - {izotop}')
    plt.xlabel('Energy [MeV]')
    plt.ylabel('Counts')
    plt.grid(axis='y', alpha=0.5)
    plt.legend()

    bezpieczna_nazwa_izotopu = str(izotop).replace(" ", "_").replace("/", "_")
    nazwa_pliku = f"20626_energy_histogram_{bezpieczna_nazwa_izotopu}.png"
    plik_wyjsciowy = os.path.join(katalog_wyjsciowy, nazwa_pliku)
    
    plt.tight_layout()
    plt.savefig(plik_wyjsciowy, dpi=300)
    plt.close()
    
    print(f"Generated: {plik_wyjsciowy}")

print("Done. All plots have been saved.")