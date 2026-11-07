from pathlib import Path
from datetime import datetime, timezone
import html
import math
import os

import pandas as pd
from evidently import DataDefinition, Dataset, Report
from evidently.presets import DataDriftPreset


COLUMNAS = ['pl_rade', 'pl_orbper']


def leer_validar(ruta):
    datos = pd.read_csv(ruta)

    if list(datos.columns) != COLUMNAS:
        raise ValueError(
            f'{ruta}: se esperan las columnas {COLUMNAS}, en ese orden.'
        )

    if len(datos) < 100:
        raise ValueError(
            f'{ruta}: se necesitan al menos 100 filas para esta practica.'
        )

    for columna in COLUMNAS:
        for fila, valor in enumerate(datos[columna], start=2):
            try:
                numero = float(valor)
            except (ValueError, TypeError):
                raise ValueError(
                    f'{ruta}, fila {fila}, {columna}: debe ser numerico.'
                )

            if not math.isfinite(numero) or numero <= 0:
                raise ValueError(
                    f'{ruta}, fila {fila}, {columna}: '
                    'debe ser finito y mayor que cero.'
                )

        datos[columna] = pd.to_numeric(datos[columna])

    return datos


def main():
    referencia = leer_validar('datos/referencia.csv')
    actual = leer_validar('datos/actual.csv')

    esquema = DataDefinition(numerical_columns=COLUMNAS)

    ref = Dataset.from_pandas(
        referencia,
        data_definition=esquema
    )
    act = Dataset.from_pandas(
        actual,
        data_definition=esquema
    )

    resultado = Report([DataDriftPreset()]).run(
        current_data=act,
        reference_data=ref
    )

    salida = Path('public')
    salida.mkdir(exist_ok=True)

    resultado.save_html(str(salida / 'comparacion.html'))

    filas = ''.join(
        f'<tr><td>{c}</td><td>{referencia[c].mean():,.2f}</td>'
        f'<td>{actual[c].mean():,.2f}</td></tr>'
        for c in COLUMNAS
    )

    fecha = datetime.now(timezone.utc).isoformat(timespec='seconds')
    commit = html.escape(os.getenv('GITHUB_SHA', 'local'))

    pagina = f'''<!doctype html>
<html lang="es">
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Monitoreo de exoplanetas</title>
<style>
body{{font:17px system-ui;max-width:900px;margin:40px auto;padding:20px;line-height:1.6}}
td,th{{padding:12px;border:1px solid #ccc}}
table{{border-collapse:collapse}}
a{{color:#1454b5}}
</style>
<h1>Monitoreo de datos de exoplanetas</h1>
<p>Copia educativa de NASA Exoplanet Archive con cambios simulados. No son nuevas mediciones reales.</p>
<p>pl_rade: radio en radios terrestres; pl_orbper: periodo orbital en dias.</p>
<p>Filas de referencia: {len(referencia)}. Filas actuales: {len(actual)}.</p>
<table>
<tr><th>Variable</th><th>Media de referencia</th><th>Media actual</th></tr>
{filas}
</table>
<p><a href="comparacion.html">Abrir comparacion de Evidently</a></p>
<p>Generado: {fecha} (UTC)</p>
<p>Commit: {commit}</p>
<p>Fuente: <a href="https://exoplanetarchive.ipac.caltech.edu/">NASA Exoplanet Archive</a>.
Atribucion: NASA Exoplanet Archive, operado por Caltech para NASA.
<a href="https://exoplanetarchive.ipac.caltech.edu/docs/acknowledge.html">Indicaciones de atribucion</a>.</p>
</html>'''

    (salida / 'index.html').write_text(pagina, encoding='utf-8')

    print('CSV validos. Informe generado en public/index.html.')
    print(
        'La deteccion de drift no bloquea CD en esta practica: '
        'debes interpretarla.'
    )


if __name__ == '__main__':
    try:
        main()
    except (ValueError, FileNotFoundError) as error:
        raise SystemExit(str(error))