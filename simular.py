import sys

import pandas as pd


if len(sys.argv) != 2 or sys.argv[1] not in ['igual', 'cambio', 'error']:
    raise SystemExit('Uso: python simular.py igual|cambio|error')

datos = pd.read_csv('datos/referencia.csv')
escenario = sys.argv[1]

if escenario == 'cambio':
    datos['pl_rade'] = datos['pl_rade'] + 10
elif escenario == 'error':
    datos.loc[0, 'pl_rade'] = -100

datos.to_csv('datos/actual.csv', index=False)

print(f'actual.csv actualizado: {escenario}')