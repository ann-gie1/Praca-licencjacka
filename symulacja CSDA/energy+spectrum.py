import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg') # Key setting for background server execution
import matplotlib.pyplot as plt
import os

# --- 1. Plotting Configuration ---
# Set font sizes: Max font 20 for titles, scaling down proportionally for readability
plt.rcParams.update({
    'font.size': 16,
    'axes.titlesize': 20,
    'axes.labelsize': 18,
    'xtick.labelsize': 16,
    'ytick.labelsize': 16,
    'legend.fontsize': 16
})

# --- 2. Physical Parameters & Theoretical Functions ---
m_e = 0.511  # electron/positron mass [MeV]

# Isotope data: (E0, final Z)
isotopes = {
    "18F":  (0.634, 8),
    "44Sc": (1.474, 20),
    "68Ga": (1.899, 30)
}

def momentum(E):
    """Relativistic momentum vs kinetic energy."""
    return np.sqrt(E**2 + 2 * m_e * E)

def fermi_function_allowed(Z, E):
    """Fermi function approximation for allowed β± transitions."""
    alpha = 1/137
    p = momentum(E)
    eta = alpha * Z * (E + m_e) / p
    return (2 * np.pi * eta) / (1 - np.exp(-2 * np.pi * eta))

def beta_plus_spectrum(E, E0, Z):
    """Calculates the theoretical shape of the β+ spectrum."""
    p = momentum(E)
    F = fermi_function_allowed(Z, E)
    return p * E * (E0 - E)**2 * F

# --- 3. Data Loading ---
plik_wejsciowy = "../dane_symulacja_CSDA/Generacja_danych_1mln.csv"
katalog_wyjsciowy = "../dane_symulacja_CSDA/"

df = pd.read_csv(plik_wejsciowy)

if 'Izotop' not in df.columns or 'Energia-wylosowana' not in df.columns:
    raise ValueError("CSV file missing required columns: 'Izotop' or 'Energia-wylosowana'")

izotopy = df['Izotop'].unique()

# --- 4. Generating Plots in a Loop ---
for izotop in izotopy:
    df_izotop = df[df['Izotop'] == izotop]
    
    plt.figure(figsize=(12, 8))
    
    # Create the 1D histogram and capture the bin counts to scale the theoretical curve
    counts, bins, _ = plt.hist(df_izotop['Energia-wylosowana'], bins=100, 
                               edgecolor='black', alpha=0.65, label='Simulated Data (Histogram)')
    
    # Overlay the theoretical spectrum if parameters for this isotope exist
    if izotop in isotopes:
        E0, Z = isotopes[izotop]
        # Generate energy points up to E0
        E = np.linspace(0.001, E0, 500)
        spectrum = beta_plus_spectrum(E, E0, Z)
        
        # Scale the theoretical spectrum so its peak matches the highest histogram bin
        max_bin_count = np.max(counts)
        normalized_spectrum = (spectrum / np.max(spectrum)) * max_bin_count
        
        plt.plot(E, normalized_spectrum, color='red', linewidth=3, 
                 label=f'Theoretical Spectrum ({izotop})')

    # Axis configuration and styling
    plt.title(f'Energy Distribution - {izotop}')
    plt.xlabel('Energy [MeV]')
    plt.ylabel('Counts')
    plt.grid(axis='y', alpha=0.5)
    plt.legend()

    # File saving
    bezpieczna_nazwa_izotopu = str(izotop).replace(" ", "_").replace("/", "_")
    nazwa_pliku = f"energy_histogram_{bezpieczna_nazwa_izotopu}.png"
    plik_wyjsciowy = os.path.join(katalog_wyjsciowy, nazwa_pliku)
    
    plt.tight_layout()
    plt.savefig(plik_wyjsciowy, dpi=300)
    plt.close()
    
    print(f"Generated: {plik_wyjsciowy}")

print("Done. All plots have been saved.")