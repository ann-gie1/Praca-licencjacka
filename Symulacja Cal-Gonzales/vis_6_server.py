import pandas as pd
import numpy as np
import plotly.graph_objects as go
import os

# Limit punktów do wyświetlenia NA KATEGORIĘ (żeby nie spalić przeglądarki)
MAX_PUNKTOW_NA_KATEGORIE = 300 

print("Wczytywanie i łączenie danych...")
df = pd.read_csv("../dane_symulacja_cal_gonzales/Generacja_danych_c-g_1mln-conc.csv")
df1 = pd.read_csv("../dane_symulacja_cal_gonzales/wyniki_symulacji_C-G_1mln-conc.csv")

df_all = pd.merge(df, df1, on='Index', suffixes=('', '_wyniki'))

dostepne_izotopy = df_all['Izotop'].unique()
print(f"Znalezione izotopy do wygenerowania: {dostepne_izotopy}")

for wybrany_izotop in dostepne_izotopy:
    print(f"Generowanie wizualizacji dla: {wybrany_izotop}...")
    
    df_izotop = df_all[df_all['Izotop'] == wybrany_izotop].copy()

    if df_izotop.empty:
        print(f"Brak danych dla izotopu {wybrany_izotop}.")
        continue 

    unikalne_srednice = sorted(df_izotop['Srednica_mm'].unique())
    n_sfer = len(unikalne_srednice)
    r_layout = max(unikalne_srednice) * 1.25 

    kolory = {'Wewnątrz': 'green', 'W materiale': 'orange', 'Na zewnątrz': 'red'}
    grubosc_scianki = 1.0

    fig = go.Figure()
    dodane_do_legendy = set()

    for i, srednica in enumerate(unikalne_srednice):
        kat = 2 * np.pi * i / n_sfer
        offset_x = r_layout * np.cos(kat)
        offset_y = r_layout * np.sin(kat)
        
        df_sfera = df_izotop[df_izotop['Srednica_mm'] == srednica].copy()
        
        r_f = np.sqrt(df_sfera['xf']**2 + df_sfera['yf']**2 + df_sfera['zf']**2)
        
        r_wew = srednica / 2.0
        r_zew = r_wew + grubosc_scianki
        
        warunki = [r_f < r_wew, r_f <= r_zew]
        wyniki = ['Wewnątrz', 'W materiale']
        df_sfera['Kategoria'] = np.select(warunki, wyniki, default='Na zewnątrz')
        
        for col in ['x', 'xf']: df_sfera[col] += offset_x
        for col in ['y', 'yf']: df_sfera[col] += offset_y

        for kategoria, kolor in kolory.items():
            df_kat = df_sfera[df_sfera['Kategoria'] == kategoria]
            if df_kat.empty: continue

            # --- KLUCZOWA OPTYMALIZACJA: LOSOWE PRÓBKOWANIE ---
            if len(df_kat) > MAX_PUNKTOW_NA_KATEGORIE:
                df_kat = df_kat.sample(n=MAX_PUNKTOW_NA_KATEGORIE, random_state=42)

            pokaz_legende = kategoria not in dodane_do_legendy
            if pokaz_legende:
                dodane_do_legendy.add(kategoria)

            x_l, y_l, z_l = [], [], []
            for _, row in df_kat.iterrows():
                x_l.extend([row['x'], row['xf'], None])
                y_l.extend([row['y'], row['yf'], None])
                z_l.extend([row['z'], row['zf'], None])

            fig.add_trace(go.Scatter3d(
                x=x_l, y=y_l, z=z_l,
                mode='lines', line=dict(color=kolor, width=1),
                name=f"{kategoria}", 
                legendgroup=kategoria,
                showlegend=pokaz_legende,
                opacity=0.4, hoverinfo='skip'
            ))

            fig.add_trace(go.Scatter3d(
                x=df_kat['x'], y=df_kat['y'], z=df_kat['z'],
                mode='markers', marker=dict(size=3, color=kolor, symbol='circle'),
                legendgroup=kategoria, showlegend=False
            ))

            fig.add_trace(go.Scatter3d(
                x=df_kat['xf'], y=df_kat['yf'], z=df_kat['zf'],
                mode='markers', marker=dict(size=4, color=kolor, symbol='cross'),
                legendgroup=kategoria, showlegend=False
            ))

        theta = np.linspace(0, 2*np.pi, 60)
        z_circ = np.zeros_like(theta)
        
        for r_plot, dash in [(r_wew, 'solid'), (r_zew, 'dash')]:
            x_c = r_plot * np.cos(theta)
            y_c = r_plot * np.sin(theta)
            
            kregi = [
                (x_c + offset_x, y_c + offset_y, z_circ),
                (x_c + offset_x, z_circ + offset_y, y_c),
                (z_circ + offset_x, x_c + offset_y, y_c)
            ]
            
            for cx, cy, cz in kregi:
                fig.add_trace(go.Scatter3d(
                    x=cx, y=cy, z=cz,
                    mode='lines', line=dict(color='gray', width=1.5, dash=dash),
                    showlegend=False, hoverinfo='skip'
                ))

    fig.update_layout(
        title=f"Izotop: {wybrany_izotop} - Widok kołowy sfer (Próbka max {MAX_PUNKTOW_NA_KATEGORIE} pkt/kat)",
        scene=dict(aspectmode='data', xaxis_title="X [mm]", yaxis_title="Y [mm]", zaxis_title="Z [mm]"),
        margin=dict(l=0, r=0, b=0, t=40),
        legend=dict(itemsizing='constant', title="Kategorie:")
    )

    sciezka_wyjsciowa = f"../dane_symulacja_cal_gonzales/wizualizacja_cg_{wybrany_izotop}_1mln-conc.html"
    # POPRAWKA: Prawidłowy zapis do pliku HTML
    fig.write_html(sciezka_wyjsciowa)
    print(f"Zapisano wizualizację do pliku: {sciezka_wyjsciowa}")