import pandas as pd
import numpy as np
import plotly.graph_objects as go

# 1. Wczytanie danych
df = pd.read_csv("./wygenerowane_dane/Generacja_danych.csv")
df1 = pd.read_csv("./wygenerowane_dane/wyniki_symulacji.csv")

# 2. Interaktywny wybór w konsoli
print(f"Dostępne izotopy: {df['Izotop'].unique()}")
wybrany_izotop = input("Wpisz nazwę izotopu: ")

print(f"Dostępne średnice sfery (mm): {df['Srednica_mm'].unique()}")
wybrana_srednica = float(input("Wpisz średnicę sfery: "))

# Filtrowanie po wybranych parametrach
df_filtr = df[(df['Izotop'] == wybrany_izotop) & (df['Srednica_mm'] == wybrana_srednica)]
df_filtr1 = df1[(df1['Izotop'] == wybrany_izotop) & (df1['Srednica_mm'] == wybrana_srednica)]

if df_filtr.empty or df_filtr1.empty:
    print("Brak danych dla podanych parametrów.")
    exit()

# Łączenie plików za pomocą unikalnego indeksu
df_merged = pd.merge(df_filtr, df_filtr1, on='Index')

# 3. Kategoryzacja miejsc anihilacji
promien_wewnetrzny = wybrana_srednica / 2.0
grubosc_scianki = 1.0 # Zmień na właściwą grubość ścianki użytej w symulacji
promien_zewnetrzny = promien_wewnetrzny + grubosc_scianki

# Obliczamy promień finalny (odległość punktu anihilacji od środka [0,0,0])
df_merged['R_f'] = np.sqrt(df_merged['xf']**2 + df_merged['yf']**2 + df_merged['zf']**2)

def kategoryzuj_miejsce(r):
    if r < promien_wewnetrzny:
        return 'Wewnątrz'
    elif r <= promien_zewnetrzny:
        return 'W materiale'
    else:
        return 'Na zewnątrz'

df_merged['Kategoria'] = df_merged['R_f'].apply(kategoryzuj_miejsce)

# Zdefiniowanie kolorów
kolory = {
    'Wewnątrz': 'green',     # Zielony dla zdarzeń wewnątrz sfery
    'W materiale': 'orange', # Pomarańczowy dla ścianki
    'Na zewnątrz': 'red'     # Czerwony dla ucieczek (spill-out)
}

fig = go.Figure()

# 4. Rysowanie cząstek i trajektorii dla każdej grupy
for kategoria, kolor in kolory.items():
    df_kat = df_merged[df_merged['Kategoria'] == kategoria]
    if df_kat.empty:
        continue

    # Optymalne rysowanie tysięcy linii w Plotly: przeplatamy współrzędne wartościami None
    x_lines, y_lines, z_lines = [], [], []
    for _, row in df_kat.iterrows():
        x_lines.extend([row['x'], row['xf'], None])
        y_lines.extend([row['y'], row['yf'], None])
        z_lines.extend([row['z'], row['zf'], None])

    # Trajektorie (linie)
    fig.add_trace(go.Scatter3d(
        x=x_lines, y=y_lines, z=z_lines,
        mode='lines',
        line=dict(color=kolor, width=1),
        name=f'Trajektoria ({kategoria})',
        hoverinfo='skip',
        opacity=0.4
    ))

    # Punkty początkowe (okręgi)
    fig.add_trace(go.Scatter3d(
        x=df_kat['x'], y=df_kat['y'], z=df_kat['z'],
        mode='markers',
        marker=dict(size=3, color=kolor, symbol='circle'),
        name=f'Początek ({kategoria})'
    ))

    # Punkty anihilacji (krzyżyki)
    fig.add_trace(go.Scatter3d(
        x=df_kat['xf'], y=df_kat['yf'], z=df_kat['zf'],
        mode='markers',
        marker=dict(size=4, color=kolor, symbol='cross'),
        name=f'Anihilacja ({kategoria})'
    ))

# 5. Rysowanie "ażurowej" sfery 
theta = np.linspace(0, 2*np.pi, 100)
zero = np.zeros_like(theta)

# Krawędź wewnętrzna sfery
x_in = promien_wewnetrzny * np.cos(theta)
y_in = promien_wewnetrzny * np.sin(theta)

for x, y, z in [(x_in, y_in, zero), (x_in, zero, y_in), (zero, x_in, y_in)]:
    fig.add_trace(go.Scatter3d(x=x, y=y, z=z, mode='lines', line=dict(color='gray', width=2), hoverinfo='skip', showlegend=False))

# Krawędź zewnętrzna sfery (grubość materiału) - linia przerywana
x_out = promien_zewnetrzny * np.cos(theta)
y_out = promien_zewnetrzny * np.sin(theta)

for x, y, z in [(x_out, y_out, zero), (x_out, zero, y_out), (zero, x_out, y_out)]:
    fig.add_trace(go.Scatter3d(x=x, y=y, z=z, mode='lines', line=dict(color='lightgray', width=1, dash='dash'), hoverinfo='skip', showlegend=False))

# 6. Układ i wyświetlanie
fig.update_layout(
    title=f"Izotop: {wybrany_izotop} | Średnica wewn: {wybrana_srednica} mm",
    scene=dict(aspectmode='data'),
    margin=dict(l=0, r=0, b=0, t=40),
    legend=dict(itemsizing='constant')
)

fig.show()