import pandas as pd
import numpy as np
import plotly.graph_objects as go

# 1. Wczytanie danych
df = pd.read_csv("./wygenerowane_dane/Generacja_danych.csv", sep=";")

# 2. Interaktywny wybór w konsoli
print(f"Dostępne izotopy: {df['Izotop'].unique()}")
wybrany_izotop = input("Wpisz nazwę izotopu (np. 18F): ")

print(f"Dostępne średnice sfery (mm): {df['Srednica_mm'].unique()}")
wybrana_srednica = float(input("Wpisz średnicę sfery (np. 10): "))

# Filtrowanie
df_filtr = df[(df['Izotop'] == wybrany_izotop) & (df['Srednica_mm'] == wybrana_srednica)]

if df_filtr.empty:
    print("Brak danych dla podanych parametrów.")
    exit()

fig = go.Figure()

# 3. Rysowanie cząstek (punktów)
fig.add_trace(go.Scatter3d(
    x=df_filtr['x'], y=df_filtr['y'], z=df_filtr['z'],
    mode='markers',
    marker=dict(
        size=4,
        color=df_filtr['Energia-wylosowana'],
        colorscale='Viridis',
        opacity=0.9,
        colorbar=dict(title="Energia")
    ),
    name='Cząstki',
    customdata=np.stack((df_filtr['Izotop'], df_filtr['Energia-wylosowana']), axis=-1),
    hovertemplate=(
        "<b>Izotop:</b> %{customdata[0]}<br>"
        "<b>Energia:</b> %{customdata[1]:.4f}<br>"
        "<b>Współrzędne:</b> (%{x:.2f}, %{y:.2f}, %{z:.2f})<extra></extra>"
    )
))

# 4. Generowanie ultra-cienkich wektorów jako linii
skala_wektora = 0.5  # Zmień tę wartość, aby wydłużyć/skrócić wektory
N = len(df_filtr)

x_lines = np.empty(3 * N)
x_lines[0::3] = df_filtr['x']
x_lines[1::3] = df_filtr['x'] + df_filtr['dx'] * skala_wektora
x_lines[2::3] = None

y_lines = np.empty(3 * N)
y_lines[0::3] = df_filtr['y']
y_lines[1::3] = df_filtr['y'] + df_filtr['dy'] * skala_wektora
y_lines[2::3] = None

z_lines = np.empty(3 * N)
z_lines[0::3] = df_filtr['z']
z_lines[1::3] = df_filtr['z'] + df_filtr['dz'] * skala_wektora
z_lines[2::3] = None

fig.add_trace(go.Scatter3d(
    x=x_lines, y=y_lines, z=z_lines,
    mode='lines',
    line=dict(color='red', width=2),
    name='Wektory kierunku',
    hoverinfo='skip'
))

# 5. Rysowanie "ażurowej" sfery (3 okręgi, zero blokowania myszy)
promien = wybrana_srednica / 2.0
theta = np.linspace(0, 2*np.pi, 100)
zero = np.zeros_like(theta)
x_circ = promien * np.cos(theta)
y_circ = promien * np.sin(theta)

# Okrąg XY
fig.add_trace(go.Scatter3d(x=x_circ, y=y_circ, z=zero, mode='lines', line=dict(color='gray', width=2), hoverinfo='skip', showlegend=False))
# Okrąg XZ
fig.add_trace(go.Scatter3d(x=x_circ, y=zero, z=y_circ, mode='lines', line=dict(color='gray', width=2), hoverinfo='skip', showlegend=False))
# Okrąg YZ
fig.add_trace(go.Scatter3d(x=zero, y=x_circ, z=y_circ, mode='lines', line=dict(color='gray', width=2), hoverinfo='skip', showlegend=False))

# 6. Układ i wyświetlanie
fig.update_layout(
    title=f"Izotop: {wybrany_izotop} | Sfera: {wybrana_srednica} mm",
    scene=dict(aspectmode='data'),
    margin=dict(l=0, r=0, b=0, t=40)
)

fig.show()