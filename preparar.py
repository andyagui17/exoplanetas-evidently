from pathlib import Path
import pandas as pd
carpeta = Path('datos')
referencia = carpeta / 'referencia.csv'
actual = carpeta / 'actual.csv'
if referencia.exists() or actual.exists():
    raise SystemExit('Los CSV ya existen. No se sobrescriben para conservartus cambios.')
original = pd.read_csv(carpeta / 'exoplanetas.csv')
datos = original[['pl_rade', 'pl_orbper']].apply(pd.to_numeric,
errors='coerce')
datos = datos.dropna()
datos = datos[(datos > 0).all(axis=1)]
datos.to_csv(referencia, index=False)
datos.to_csv(actual, index=False)
print(f'Creados dos CSV iguales con {len(datos)} exoplanetas.')