
import rasterio
import numpy as np
import pandas as pd
import os
import re

# CONFIG
csv_path = r"C:\Users\s.parisi\OneDrive - diagramgroup.it\STELAR\zonazione\criteri.csv"
input_dir = r"C:\Users\s.parisi\OneDrive - diagramgroup.it\STELAR\zonazione\input"
output_dir = r"C:\Users\s.parisi\OneDrive - diagramgroup.it\STELAR\zonazione\output"
output_nodata = -9999

# Leggi CSV
criteri = pd.read_csv(csv_path)

# Crea cartella output se non esiste
os.makedirs(output_dir, exist_ok=True)

# Per accumulare la somma di tutti gli output
combo_array = None
combo_profilo = None

# Elenco dei raster classificati
output_raster_files = []

# Elabora ogni raster in input
for filename in os.listdir(input_dir):
    if not filename.lower().endswith(".tif"):
        continue

    match = re.match(r"([A-Z]+)_(\d{2})\.tif", filename)
    if not match:
        print(f"Nome file non valido: {filename}, ignorato.")
        continue

    variabile_file = match.group(1)
    mese_file = int(match.group(2))
    input_raster_path = os.path.join(input_dir, filename)
    output_raster_path = os.path.join(output_dir, f"{variabile_file}_{mese_file:02d}_classificato.tif")

    # Filtra criteri
    criteri_filtrati = criteri[
        (criteri['variabile'] == variabile_file) &
        (criteri['mese'] == mese_file)
    ]

    if criteri_filtrati.empty:
        print(f"Nessun criterio per {variabile_file} mese {mese_file}. File ignorato.")
        continue

    with rasterio.open(input_raster_path) as src:
        profilo = src.profile
        dati = src.read(1).astype(float)
        profilo.update(dtype=rasterio.float32, nodata=output_nodata)
        output = np.zeros_like(dati, dtype=float)
        maschera_totale = np.zeros_like(dati, dtype=bool)

    # Applica criteri
    for _, row in criteri_filtrati.iterrows():
        val_min = row['val_min']
        val_max = row['val_max']
        new_val = row['new_val']
        mask = (dati >= val_min) & (dati <= val_max)
        output[mask] += new_val
        maschera_totale |= mask

    output[~maschera_totale] = output_nodata

    # Scrivi output individuale
    with rasterio.open(output_raster_path, 'w', **profilo) as dst:
        dst.write(output.astype(np.float32), 1)

    print(f"Creato: {output_raster_path}")
    output_raster_files.append(output_raster_path)

    # Aggiorna COMBO_OUT
    if combo_array is None:
        combo_array = np.where(output == output_nodata, 0, output)
        combo_profilo = profilo.copy()
    else:
        valid_mask = output != output_nodata
        combo_array[valid_mask] += output[valid_mask]

# Salva COMBO_OUT finale
if combo_array is not None:
    combo_out_path = os.path.join(output_dir, "COMBO_OUT.tif")
    combo_array[np.isnan(combo_array)] = 0  # (opzionale)
    combo_profilo.update(nodata=output_nodata)
    with rasterio.open(combo_out_path, 'w', **combo_profilo) as dst:
        dst.write(combo_array.astype(np.float32), 1)
    print(f"\n✅ COMBO_OUT creato: {combo_out_path}")
else:
    print("⚠️ Nessun raster elaborato. COMBO_OUT non creato.")
