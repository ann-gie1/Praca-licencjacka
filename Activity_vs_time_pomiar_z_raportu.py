'''import numpy as np
import matplotlib.pyplot as plt

# --- DANE ---
# T1/2 przeliczone na minuty
t_half_sc = 4.042 * 60  # 242.52 min
t_half_f = 109.734      # 109.73 min

# Czas: 0 do 300 minut (5h), aby oba przeszły przez 50%
t = np.linspace(0, 300, 500)

# --- OBLICZENIA ---
# Funkcja zaniku: A(t) = 100% * exp(-ln(2)*t / T1/2)
decay_sc = 100 * np.exp(-np.log(2) * t / t_half_sc)
decay_f = 100 * np.exp(-np.log(2) * t / t_half_f)

# --- WYKRES ---
plt.figure(figsize=(10, 6))

plt.plot(t, decay_sc, label=f"44Sc (T1/2 = {t_half_sc:.2f} min)", color='blue', lw=2.5)
plt.plot(t, decay_f, label=f"18F (T1/2 = {t_half_f:.2f} min)", color='red', lw=2.5)

# Linie pomocnicze dla 50% aktywności
plt.axhline(50, color='black', linestyle='--', alpha=0.3)
plt.axvline(t_half_f, color='red', linestyle=':', alpha=0.5)
plt.axvline(t_half_sc, color='blue', linestyle=':', alpha=0.5)

# Dodanie punktów przecięcia dla czytelności
plt.scatter([t_half_f, t_half_sc], [50, 50], color='black', zorder=5)

# Opis osi i formatowanie
plt.title("Porównanie zaniku aktywności 44Sc i 18F")
plt.xlabel("Czas [minuty]")
plt.ylabel("Pozostała aktywność [%]")
plt.xlim(0, 300)
plt.ylim(0, 105)
plt.grid(True, linestyle=':', alpha=0.6)
plt.legend()

plt.tight_layout()
plt.show()'''

#----całkowita aktywność vs czas----

'''import numpy as np
import matplotlib.pyplot as plt

# --- PHYSICAL PARAMETERS ---
t_half_sc = 4.042 * 60  # 242.52 min
t_half_f = 109.734      # min

# Total initial activities [MBq]
a0_sc = 9.1245 + 3.955 + 1.9185  # Exactly 14.998
a0_f = 2.01 + 0.93 + 0.43        # Exactly 3.37

# Time: 0 to 300 minutes
t = np.linspace(0, 300, 500)

# --- CALCULATIONS ---
def get_activity(a0, t_half, time):
    lam = np.log(2) / t_half
    return a0 * np.exp(-lam * time)

activity_sc = get_activity(a0_sc, t_half_sc, t)
activity_f = get_activity(a0_f, t_half_f, t)

# --- PLOTTING ---
plt.figure(figsize=(10, 7))

# Main decay lines
plt.plot(t, activity_sc, label="Total 44Sc Activity", color='blue', lw=2.5)
plt.plot(t, activity_f, label="Total 18F Activity", color='red', lw=2.5)



# CUSTOM Y-AXIS TICKS
# We define standard ticks and add our exact values
standard_ticks = [0, 2, 4, 6, 8, 10, 12, 14, 16]
# We filter out standard ticks that are too close to 14.998 and 3.37 to avoid overlap
clean_ticks = [val for val in standard_ticks if abs(val - a0_sc) > 0.5 and abs(val - a0_f) > 0.5]
all_ticks = sorted(clean_ticks + [a0_sc, a0_f])

plt.yticks(all_ticks)
# ... (reszta kodu bez zmian) ...

plt.axvline(217, color='black', linestyle='--', linewidth=1.5, label='Time = 217 min')

# 2. Obliczenie wartości
val_sc = get_activity(a0_sc, t_half_sc, 217)
val_f = get_activity(a0_f, t_half_f, 217)

# 3. Rysowanie punktów (kropek) na przecięciu
plt.scatter([217, 217], [val_sc, val_f], color=['blue', 'red'], zorder=5, s=50)

# 4. DODAWANIE PODPISÓW (Z OFFSETEM PIONOWYM)
# Offset pionowy (np. 0.4 MBq w górę), żeby tekst nie nachodził na kropkę/linię
y_offset = 0.4 

plt.text(217, val_sc + y_offset,  # <-- Tutaj dodajemy offset do Y
         f'{val_sc:.3f} MBq', 
         color='blue', 
         fontweight='bold', 
         horizontalalignment='center', # Wyśrodkowanie tekstu względem x=217
         verticalalignment='bottom')   # Tekst "siedzi" na podanej współrzędnej Y

plt.text(217, val_f + y_offset,   # <-- Tutaj dodajemy offset do Y
         f'{val_f:.3f} MBq', 
         color='red', 
         fontweight='bold', 
         horizontalalignment='center',
         verticalalignment='bottom')
# Formatting
plt.title("Total Activity Decay in NEMA IQ Phantom Experiment")
plt.xlabel("Time [minutes]")
plt.ylabel("Total Activity [MBq]")
plt.grid(True, linestyle=':', alpha=0.5)
plt.legend()
plt.xlim(0, 300)
plt.ylim(0, 16.5)

plt.tight_layout()
plt.show()'''

#całkowita aktywność vs czas upscaled

'''import numpy as np
import matplotlib.pyplot as plt

# =======================================================
# 1. PREAMBUŁA STYLIZACJI (UPSCALE)
# =======================================================
FONT_INCREASE = 10       # O ile pkt zwiększyć czcionkę
BASE_LINEWIDTH = 3.0     # Bazowa grubość linii (taka sama dla obu)

plt.rcParams.update({
    'font.size': 10 + FONT_INCREASE,
    'axes.titlesize': 14 + FONT_INCREASE,
    'axes.labelsize': 12 + FONT_INCREASE,
    'xtick.labelsize': 10 + FONT_INCREASE,
    'ytick.labelsize': 10 + FONT_INCREASE,
    'legend.fontsize': 10 + FONT_INCREASE,
    'lines.linewidth': BASE_LINEWIDTH,
    'figure.figsize': (16, 8) 
})

# =======================================================
# 2. PARAMETRY FIZYCZNE I OBLICZENIA
# =======================================================
t_half_sc = 4.042 * 60  
t_half_f = 109.734      

# Total initial activities [MBq]
a0_sc = 9.1245 + 3.955 + 1.9185  # ~14.998
a0_f = 2.01 + 0.93 + 0.43        # ~3.37

# Time
t = np.linspace(0, 300, 500)

def get_activity(a0, t_half, time):
    lam = np.log(2) / t_half
    return a0 * np.exp(-lam * time)

activity_sc = get_activity(a0_sc, t_half_sc, t)
activity_f = get_activity(a0_f, t_half_f, t)

# =======================================================
# 3. RYSOWANIE WYKRESU
# =======================================================
plt.figure()

# Kolory zgodne ze spectrum: Sc=Orange, F=Blue
color_sc = 'tab:orange'
color_f = 'tab:blue'

# --- GŁÓWNE LINIE ROZPADU ---
# Obie linie mają tę samą grubość (BASE_LINEWIDTH)
plt.plot(t, activity_sc, label="Total 44Sc Activity", color=color_sc, 
         linewidth=BASE_LINEWIDTH)

plt.plot(t, activity_f, label="Total 18F Activity", color=color_f, 
         linewidth=BASE_LINEWIDTH)

# --- CUSTOM Y-AXIS TICKS ---
standard_ticks = [0, 2, 4, 6, 8, 10, 12, 14, 16]
clean_ticks = [val for val in standard_ticks if abs(val - a0_sc) > 0.5 and abs(val - a0_f) > 0.5]
all_ticks = sorted(clean_ticks + [a0_sc, a0_f])

plt.yticks(all_ticks)

# --- WYRÓŻNIENIE SPECJALNYCH WARTOŚCI NA OSI Y ---
# Pobieramy aktualne osie i etykiety
ax = plt.gca()
yticks = ax.get_yticks()
ylabels = ax.get_yticklabels()

# Iterujemy i pogrubiamy tylko te, które są naszymi a0
for val, label in zip(yticks, ylabels):
    if np.isclose(val, a0_sc) or np.isclose(val, a0_f):
        label.set_fontweight('bold')
        # Opcjonalnie można też zmienić kolor etykiety na kolor pierwiastka:
        # if np.isclose(val, a0_sc): label.set_color(color_sc)
        # if np.isclose(val, a0_f): label.set_color(color_f)

# --- LINIA PIONOWA I PUNKTY ---
plt.axvline(217, color='black', linestyle='--', linewidth=BASE_LINEWIDTH, label='Time = 217 min')

val_sc = get_activity(a0_sc, t_half_sc, 217)
val_f = get_activity(a0_f, t_half_f, 217)

# Punkty w kolorach odpowiadających liniom
plt.scatter([217, 217], [val_sc, val_f], color=[color_sc, color_f], zorder=5, s=200)

# --- PODPISY PUNKTÓW ---
y_offset = 0.6 

plt.text(217, val_sc + y_offset, 
         f'{val_sc:.3f} MBq', 
         color=color_sc, 
         fontweight='bold', 
         horizontalalignment='center', 
         verticalalignment='bottom')

plt.text(217, val_f + y_offset, 
         f'{val_f:.3f} MBq', 
         color=color_f, 
         fontweight='bold', 
         horizontalalignment='center',
         verticalalignment='bottom')

# --- FORMATOWANIE KOŃCOWE ---
plt.title("Total Activity Decay in NEMA IQ Phantom Experiment")
plt.xlabel("Time [minutes]")
plt.ylabel("Total Activity [MBq]")
plt.grid(True, linestyle=':', alpha=0.5, linewidth=1.5)
plt.xlim(0, 300)
plt.ylim(0, 16.5)

# Legenda na zewnątrz
plt.legend(bbox_to_anchor=(1.02, 1), loc='upper left', borderaxespad=0)

plt.tight_layout()
plt.show()'''

#activity przez objetosć pierwiastków

import numpy as np
import matplotlib.pyplot as plt

# =======================================================
# 1. PREAMBUŁA STYLIZACJI (UPSCALE)
# =======================================================
FONT_INCREASE = 10       # O ile pkt zwiększyć czcionkę
BASE_LINEWIDTH = 3.0     # Bazowa grubość linii (taka sama dla obu)

plt.rcParams.update({
    'font.size': 10 + FONT_INCREASE,
    'axes.titlesize': 14 + FONT_INCREASE,
    'axes.labelsize': 12 + FONT_INCREASE,
    'xtick.labelsize': 10 + FONT_INCREASE,
    'ytick.labelsize': 10 + FONT_INCREASE,
    'legend.fontsize': 10 + FONT_INCREASE,
    'lines.linewidth': BASE_LINEWIDTH,
    'figure.figsize': (16, 8) 
})

# =======================================================
# 2. PARAMETRY FIZYCZNE I OBLICZENIA
# =======================================================
t_half_sc = 4.042 * 60  
t_half_f = 109.734      

# Total initial activities [MBq]
a0_sc = 9.1245 + 3.955 + 1.9185  # ~14.998
a0_f = 2.01 + 0.93 + 0.43        # ~3.37

# UZUPEŁNIJ WŁAŚCIWE OBJĘTOŚCI (w mL)
vol_sc = 26.50804+11.48882+5.5724
vol_f = 2.57114+1.14976+0.52333

# Time
t = np.linspace(0, 300, 500)

def get_activity(a0, t_half, time):
    lam = np.log(2) / t_half
    return a0 * np.exp(-lam * time)

# NOWA FUNKCJA: Dzielenie aktywności przez objętość
def get_activity_per_volume(activity, volume):
    return activity / volume

# Obliczanie aktywności
activity_sc = get_activity(a0_sc, t_half_sc, t)
activity_f = get_activity(a0_f, t_half_f, t)

# Obliczanie aktywności na jednostkę objętości (stężenia)
conc_sc = get_activity_per_volume(activity_sc, vol_sc)
conc_f = get_activity_per_volume(activity_f, vol_f)

# Wartości początkowe stężeń (do osi Y)
c0_sc = get_activity_per_volume(a0_sc, vol_sc)
c0_f = get_activity_per_volume(a0_f, vol_f)

# =======================================================
# 3. RYSOWANIE WYKRESU
# =======================================================
plt.figure()

color_sc = 'tab:orange'
color_f = 'tab:blue'

# Plotowanie stężeń (Activity/Volume)
plt.plot(t, conc_sc, label="44Sc Activity/Volume", color=color_sc, linewidth=BASE_LINEWIDTH)
plt.plot(t, conc_f, label="18F Activity/Volume", color=color_f, linewidth=BASE_LINEWIDTH)

# --- CUSTOM Y-AXIS TICKS ---
ax = plt.gca()
default_ticks = ax.get_yticks()
y_range = max(default_ticks) - min(default_ticks)

# Filtrujemy ticki, żeby nie nachodziły na nasze c0_sc i c0_f
clean_ticks = [val for val in default_ticks if abs(val - c0_sc) > (y_range*0.05) and abs(val - c0_f) > (y_range*0.05)]
all_ticks = sorted(clean_ticks + [c0_sc, c0_f])

plt.yticks(all_ticks)

# Pogrubienie początkowych stężeń na osi Y
yticks = ax.get_yticks()
ylabels = ax.get_yticklabels()

for val, label in zip(yticks, ylabels):
    if np.isclose(val, c0_sc) or np.isclose(val, c0_f):
        label.set_fontweight('bold')

# --- LINIA PIONOWA I PUNKTY ---
plt.axvline(217, color='black', linestyle='--', linewidth=BASE_LINEWIDTH, label='Time = 217 min')

val_sc_conc = get_activity_per_volume(get_activity(a0_sc, t_half_sc, 217), vol_sc)
val_f_conc = get_activity_per_volume(get_activity(a0_f, t_half_f, 217), vol_f)

plt.scatter([217, 217], [val_sc_conc, val_f_conc], color=[color_sc, color_f], zorder=5, s=200)

# --- PODPISY PUNKTÓW ---
y_offset = y_range * 0.03 # dynamiczny offset zależny od skali

plt.text(217, val_sc_conc + y_offset, 
         f'{val_sc_conc:.3f} MBq/mL', 
         color=color_sc, 
         fontweight='bold', 
         horizontalalignment='center', 
         verticalalignment='bottom')

plt.text(217, val_f_conc + y_offset, 
         f'{val_f_conc:.3f} MBq/mL', 
         color=color_f, 
         fontweight='bold', 
         horizontalalignment='center',
         verticalalignment='bottom')

# --- FORMATOWANIE KOŃCOWE ---
plt.title("Activity Concentration Decay in NEMA IQ Phantom Experiment")
plt.xlabel("Time [minutes]")
plt.ylabel("Activity / Volume [MBq/mL]")
plt.grid(True, linestyle=':', alpha=0.5, linewidth=1.5)
plt.xlim(0, 300)
plt.ylim(bottom=0) # Usunięto górny limit (16.5), aby wykres poprawnie się skalował do nowych jednostek

plt.legend(bbox_to_anchor=(1.02, 1), loc='upper left', borderaxespad=0)
plt.tight_layout()
plt.show()