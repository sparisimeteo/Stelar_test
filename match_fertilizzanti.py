import pandas as pd
import os

# ----- PARAMETRI -----
# Percorsi dei file CSV
csv_npk_path = r"C:\Users\s.parisi\OneDrive - diagramgroup.it\STELAR\MATCH\Dataset_Valori_NPK.csv"
csv_fertilizzanti_path = r"C:\Users\s.parisi\OneDrive - diagramgroup.it\STELAR\MATCH\Dataset_Banca_Dati_Fertilizzanti.csv"
csv_output_path = r"C:\Users\s.parisi\OneDrive - diagramgroup.it\STELAR\MATCH\Valori_NPK_output.csv"

# ----- CARICAMENTO DEI DATI -----
df_npk = pd.read_csv(csv_npk_path)
df_fertilizzanti = pd.read_csv(csv_fertilizzanti_path)

# Controllo che i file abbiano le colonne richieste
required_columns = {"N", "P", "K"}
if not required_columns.issubset(df_npk.columns) or not required_columns.issubset(df_fertilizzanti.columns):
    raise ValueError("I file CSV devono contenere le colonne: 'N', 'P', 'K'.")

# Funzione per calcolare la distanza tra due composizioni NPK
def npk_distance(npk1, npk2):
    return sum((a - b) ** 2 for a, b in zip(npk1, npk2)) ** 0.5

# Aggiungere una colonna per il fertilizzante consigliato
df_npk["Fertilizzante"] = ""

# ----- PROCESSO DI MATCHING -----
for i, row_npk in df_npk.iterrows():
    npk_values = (row_npk["N"], row_npk["P"], row_npk["K"])
    
    best_match = None
    min_dist = float("inf")

    for j, row_fert in df_fertilizzanti.iterrows():
        fert_values = (row_fert["N"], row_fert["P"], row_fert["K"])
        
        # Calcolare la distanza tra le composizioni NPK
        dist = npk_distance(npk_values, fert_values)
        
        if dist < min_dist:
            min_dist = dist
            best_match = row_fert["Nome"]  # Supponiamo che il fertilizzante abbia una colonna 'Nome'

    # Assegnare il miglior fertilizzante
    df_npk.at[i, "Fertilizzante"] = best_match

# ----- SALVATAGGIO DEL RISULTATO -----
df_npk.to_csv(csv_output_path, index=False)

print(f"Processo completato! Il file con il fertilizzante consigliato è stato salvato in: {csv_output_path}")
