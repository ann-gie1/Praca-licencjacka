import pandas as pd
import numpy as np
import plotly.graph_objects as go
import os

# 1. Wczytanie danych
df = pd.read_csv("../dane_symulacja_CSDA/Generacja_danych_1mln-conc.csv")
df1 = pd.read_csv("../dane_symulacja_cal_gonzales/wyniki_symulacji_C-G_1mln-conc.csv")

# Łączenie plików
df_all = pd.merge(df, df1, on='Index', suffixes=('', '_wyniki'))

# 2. Automatyczne pobranie wszystkich izotopów (bez wpisywania!)
dostepne_izotopy = df_all['Izotop'].unique()
print(f"Znalezione izotopy do wygenerowania: {dostepne_izotopy}")

# PĘTLA GŁÓWNA - tworzy osobny wykres dla każdego izotopu
for wybrany_izotop in dostepne_izotopy:
    print(f"Generowanie wizualizacji dla: {wybrany_izotop}...")
    
    df_izotop = df_all[df_all['Izotop'] == wybrany_izotop].copy()

    if df_izotop.empty:
        print(f"Brak danych dla izotopu {wybrany_izotop}.")
        continue # Pomija i idzie do kolejnego, zamiast zamykać program

    # 3. Parametry układu kołowego i definicje
    unikalne_srednice = sorted(df_izotop['Srednica_mm'].unique())
    n_sfer = len(unikalne_srednice)
    r_layout = max(unikalne_srednice) * 1.25 

    kolory = {'Wewnątrz': 'green', 'W materiale': 'orange', 'Na zewnątrz': 'red'}
    grubosc_scianki = 1.0

    fig = go.Figure()
    dodane_do_legendy = set() # Resetujemy legendę dla każdego nowego okna/izotopu

    # 4. Pętla po średnicach (każda sfera w innym miejscu)
    for i, srednica in enumerate(unikalne_srednice):
        # Obliczanie przesunięcia (offset)
        kat = 2 * np.pi * i / n_sfer
        offset_x = r_layout * np.cos(kat)
        offset_y = r_layout * np.sin(kat)
        
        df_sfera = df_izotop[df_izotop['Srednica_mm'] == srednica].copy()
        
        # Obliczenie promienia anihilacji LOKALNIE
        r_f = np.sqrt(df_sfera['xf']**2 + df_sfera['yf']**2 + df_sfera['zf']**2)
        
        # Kategoryzacja
        r_wew = srednica / 2.0
        r_zew = r_wew + grubosc_scianki
        
        warunki = [r_f < r_wew, r_f <= r_zew]
        wyniki = ['Wewnątrz', 'W materiale']
        df_sfera['Kategoria'] = np.select(warunki, wyniki, default='Na zewnątrz')
        
        # Przesunięcie współrzędnych przestrzennych (aplikowane do całego df_sfera)
        for col in ['x', 'xf']: df_sfera[col] += offset_x
        for col in ['y', 'yf']: df_sfera[col] += offset_y

        # --- RYSOWANIE TRAJEKTORII I MARKERÓW ---
        for kategoria, kolor in kolory.items():
            df_kat = df_sfera[df_sfera['Kategoria'] == kategoria]
            if df_kat.empty: continue

            # Aby legenda była czysta, pokazujemy nazwę kategorii tylko przy pierwszym wystąpieniu
            pokaz_legende = kategoria not in dodane_do_legendy
            if pokaz_legende:
                dodane_do_legendy.add(kategoria)

            # 1. Linie (zoptymalizowane)
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

            # 2. Punkty początkowe (okręgi)
            fig.add_trace(go.Scatter3d(
                x=df_kat['x'], y=df_kat['y'], z=df_kat['z'],
                mode='markers',
                marker=dict(size=3, color=kolor, symbol='circle'),
                name=f'Początek ({kategoria}, D={srednica})',
                legendgroup=kategoria,
                showlegend=False
            ))

            # 3. Punkty anihilacji (krzyżyki)
            fig.add_trace(go.Scatter3d(
                x=df_kat['xf'], y=df_kat['yf'], z=df_kat['zf'],
                mode='markers',
                marker=dict(size=4, color=kolor, symbol='cross'),
                name=f'Anihilacja ({kategoria}, D={srednica})',
                legendgroup=kategoria,
                showlegend=False
            ))

        # --- RYSOWANIE AŻUROWEJ SFERY ---
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

    # 5. Układ i ZAPIS DO PLIKU
    fig.update_layout(
        title=f"Izotop: {wybrany_izotop} - Widok kołowy sfer (z markerami)",
        scene=dict(
            aspectmode='data',
            xaxis_title="X [mm]", yaxis_title="Y [mm]", zaxis_title="Z [mm]"
        ),
        margin=dict(l=0, r=0, b=0, t=40),
        legend=dict(itemsizing='constant', title="Kategorie:")
    )

    # Zapis do pliku HTML zamiast wyświetlania w locie na serwerze
    sciezka_wyjsciowa = f"../dane_symulacja_cal_gonzales/wizualizacja_{wybrany_izotop}_1mln-conc.html"
    fig.write_json(sciezka_wyjsciowa)
    print(f"Zapisano wizualizację do pliku: {sciezka_wyjsciowa}")