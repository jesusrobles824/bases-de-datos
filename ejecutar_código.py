import yfinance as yf
import requests
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
import matplotlib.patches as mpatches
import matplotlib.dates as mdates
import matplotlib.ticker as ticker
from matplotlib.lines import Line2D
import re
from matplotlib.dates import date2num
from matplotlib.ticker import FixedLocator
from io import BytesIO
from dateutil.relativedelta import relativedelta
from pandas.tseries.offsets import MonthEnd
import matplotlib.lines as mlines
from datetime import datetime, timedelta
from pandas_datareader import data as web
from imf_reader import sdr

# Definir la fecha de hoy automáticamente

tickers_adrs = ['BBAR', 'BMA', 'CEPU', 'CRESY', 'EDN', 'GGAL', 'IRS','LOMA',
                'PAM', 'SUPV', 'TEO', 'TGS', 'TS', 'TX', 'YPF']

# Descargar datos históricos de los ADRs y el Merval
adrs = yf.download(tickers_adrs, start='2010-01-01')['Close']
adrs.columns.name = None  # Correcto
adrs.index.name = 'fecha'  # Correcto
adrs = adrs.round(2)

adrs_var = adrs.pct_change() * 100  # en %
adrs_var = adrs_var.round(2)
adrs_var = adrs_var[::-1]
adrs_var.to_csv('ADRs_variacion_porcentual_diaria.csv', index=True)

adrs = adrs[::-1]
adrs.to_csv('ADRs_Precios.csv', index=True)




hasta = hasta = pd.Timestamp.today()
url = "https://www.bcra.gob.ar/Pdfs/PublicacionesEstadisticas/diar_bas.xls"
response = requests.get(url, verify=False)
diar_bas = pd.read_excel(BytesIO(response.content), 
                         sheet_name='Serie_diaria', 
                         skiprows=26, 
                         usecols='A,AF,AG,AI')
diar_bas.columns = ['fecha', 'Depósitos del tesoro en pesos', 'Depósitos_del_tesoro_en_usd', 
                    'TC']
diar_bas.set_index('fecha', inplace=True)
diar_bas = diar_bas.iloc[:-3]
diar_bas = diar_bas[(diar_bas.index > pd.Timestamp('2024-12-31')) & (diar_bas.index <= diar_bas.index[-1])]
diar_bas['Depósitos del tesoro en usd'] = diar_bas['Depósitos_del_tesoro_en_usd'] / diar_bas['TC']
diar_bas = diar_bas[['Depósitos del tesoro en pesos', 'Depósitos del tesoro en usd']]
diar_bas = diar_bas.round(2)

diar_bas_var = diar_bas.diff()
diar_bas_var = diar_bas_var.round(2)
diar_bas_var = diar_bas_var.iloc[1:]
diar_bas_var = diar_bas_var[::-1]
diar_bas_var.to_csv('Depósitos_tesoro_variación_diaria.csv', index=True)

diar_bas = diar_bas[::-1]
diar_bas.to_csv('Depósitos_tesoro.csv', index=True)




url = "https://www.bcra.gob.ar/Pdfs/PublicacionesEstadisticas/series.xlsm"
response = requests.get(url, verify=False)

Tasas = pd.read_excel(BytesIO(response.content), sheet_name='TASAS DE MERCADO', skiprows=8, usecols='A,B,I,L,O,R,S,V,X')

Tasas.columns = ['fecha','Plazo fijo','TAMAR','BADLAR','TM20','Préstamos personales','Adelantos en cuenta corriente','Call en Pesos','Repo a 1 día (excl. BCRA)']
Tasas.set_index('fecha', inplace=True)
Tasas = Tasas[Tasas.index>'2024-05-31']
Tasas = Tasas[::-1]
Tasas = Tasas.round(2)
Tasas.to_csv('Principales_Tasas_de_Interés.csv', index=True)




url = "https://www.bcra.gob.ar/Pdfs/PublicacionesEstadisticas/series.xlsm"
response = requests.get(url, verify=False)
Variacion_Reservas = pd.read_excel(BytesIO(response.content), sheet_name='RESERVAS', skiprows=8, usecols='A,G,H,I,J,K,L,Q')
Variacion_Reservas.columns = ['fecha', 'Reservas Internacionales', 'Compra de Divisas', 'OOII', 'Otras Operaciones del Sector Público', 'Efectivo Mínimo', 'Otros (incl. pases pasivos en USD con el exterior)', 'Tipo de serie']
Variacion_Reservas = Variacion_Reservas.loc[Variacion_Reservas["Tipo de serie"] == "D"]
Variacion_Reservas.set_index('fecha', inplace=True)
Variacion_Reservas = Variacion_Reservas.drop(columns=['Tipo de serie'])
Variacion_Reservas = Variacion_Reservas[Variacion_Reservas.index>'2023-12-10']
Variacion_Acumulada = Variacion_Reservas.cumsum()

Variacion_Reservas = Variacion_Reservas.round(1)
Variacion_Reservas = Variacion_Reservas[::-1]
Variacion_Reservas.to_csv('Variación_RRII_Factores_Explicación.csv',index=True)

Variacion_Acumulada = Variacion_Acumulada.round(1)
Variacion_Acumulada = Variacion_Acumulada[::-1]

Variacion_Acumulada.to_csv('Variación_Acumulada_RRII_Factores_Explicación.csv',index=True)




url = "https://www.bcra.gob.ar/Pdfs/PublicacionesEstadisticas/series.xlsm"
response = requests.get(url, verify=False)

Prestamos_pesos = pd.read_excel(BytesIO(response.content),sheet_name='PRESTAMOS',usecols='A,B,C,D,E,F,G,H,I,V',skiprows=8)
Prestamos_pesos.columns = ['fecha','Adelantos','Documentos','Hipotecarios','Prendarios','Personales','Tarjetas','Otros','TOTAL','Tipo de serie']
Prestamos_pesos = Prestamos_pesos.loc[Prestamos_pesos['Tipo de serie'] == 'D']
Prestamos_pesos = Prestamos_pesos.drop(columns=['Tipo de serie'])
Prestamos_pesos.set_index('fecha', inplace=True)
Prestamos_pesos = Prestamos_pesos[::-1]
for col in Prestamos_pesos.columns:
    Prestamos_pesos[col] = pd.to_numeric(Prestamos_pesos[col], errors='coerce').round(0).astype('Int64')
Prestamos_pesos.to_csv('Préstamos_pesos_sector_privado_en_millones_por_tipo.csv', index=True)

Prestamos_usd = pd.read_excel(BytesIO(response.content),sheet_name='PRESTAMOS',usecols='A,J,K,L,M,N,O,P,Q,V',skiprows=8)
Prestamos_usd.columns = ['fecha','Adelantos','Documentos','Hipotecarios','Prendarios','Personales','Tarjetas','Otros','TOTAL','Tipo de serie']
Prestamos_usd = Prestamos_usd.loc[Prestamos_usd['Tipo de serie'] == 'D']
Prestamos_usd = Prestamos_usd.drop(columns=['Tipo de serie'])
Prestamos_usd.set_index('fecha', inplace=True)
Prestamos_usd = Prestamos_usd[::-1]
for col in Prestamos_usd.columns:
    Prestamos_usd[col] = pd.to_numeric(Prestamos_usd[col], errors='coerce').round(0).astype('Int64')
Prestamos_usd.to_csv('Préstamos_usd_sector_privado_en_millones_por_tipo.csv', index=True)

Depositos = pd.read_excel(BytesIO(response.content),sheet_name='DEPOSITOS',usecols='A,AA,AE',skiprows=8)
Depositos.columns = ['fecha','Depósitos en dólares','Tipo de serie']
Depositos = Depositos.loc[Depositos['Tipo de serie'] == 'D']
Depositos = Depositos.drop(columns=['Tipo de serie'])
Depositos.set_index('fecha', inplace=True)

Prestamos = pd.read_excel(BytesIO(response.content),sheet_name='PRESTAMOS',usecols='A,Q,V',skiprows=8)
Prestamos.columns = ['fecha','Préstamos en dólares','Tipo de serie']
Prestamos = Prestamos.loc[Prestamos['Tipo de serie'] == 'D']
Prestamos = Prestamos.drop(columns=['Tipo de serie'])
Prestamos.set_index('fecha', inplace=True)

Prestamos_Depositos_usd = Prestamos.join(Depositos, how='inner')
Prestamos_Depositos_usd = Prestamos_Depositos_usd[::-1]
for col in Prestamos_Depositos_usd.columns:
    Prestamos_Depositos_usd[col] = pd.to_numeric(Prestamos_Depositos_usd[col], errors='coerce').round(0).astype('Int64')
Prestamos_Depositos_usd.to_csv('Préstamos_Depósitos_usd_sector_privado_en_millones.csv',index=True)




Variacion_Reservas = Variacion_Reservas[['OOII','Otras Operaciones del Sector Público']]
diar_bas_var = diar_bas_var.join(Variacion_Reservas, how='inner')
diar_bas_var.to_csv('Depósitos_tesoro_variación_diaria_y_factores_de_explicación.csv', index=True)




# Definir fechas como strings en formato YYYY-MM-DD
#start = "2017-01-01"
#end = "2025-08-01"
# Descargar datos del IPC ajustado estacionalmente (CPIAUCSL) de FRED
#IPC = web.DataReader("CPIAUCSL", "fred", start, end)
#IPC.columns = ['IPC']
#IPC.index.name='fecha'
#IPC.index = pd.to_datetime(IPC.index)
#IPC = IPC / IPC.loc['2025-08-01']
#IPC = IPC[IPC.index<'2025-04-01']
#IPC_trimestral = IPC.resample('Q').mean()
#IPC_trimestral.index = pd.period_range(start='2017Q1', end='2025Q1', freq='Q')
#IPC_trimestral.index.name = 'Trimestre'

#url = "https://www.bcra.gob.ar/Pdfs/PublicacionesEstadisticas/anexo-informe-inversion-extranjera-directa.xlsx"
#response = requests.get(url, verify=False)
#IED = pd.read_excel(BytesIO(response.content), sheet_name='Cuadro 4', skiprows=9, usecols='A:G')
#IED.set_index('Periodo', inplace=True)
#IED = IED.drop(range(2017, 2026), errors='ignore')  
#IED.index = pd.period_range(start='2017Q1', end='2025Q1', freq='Q')
#IED.index.name = 'Trimestre'
#IED['Reinversión de utilidades']=IED['Renta de IED']+IED['Distribución de utilidades']
#IED = IED.drop(columns=['Renta de IED','Distribución de utilidades'])
#IED = IED.rename(columns={'Deuda de IED':'Transacciones de deuda'})
#IED = IED[['Aportes netos de capital',
#           'Fusiones y adquisiciones',
#           'Reinversión de utilidades',
#           'Transacciones de deuda',
#           'Total de Transacciones ']]
#IED.columns = ['Aportes netos de capital','Fusiones y adquisiciones','Reinversión de utilidades','Transacciones de deuda','TOTAL']
#for col in IED.columns:
#   IED[col] = IED[col] / IPC_trimestral['IPC']
#IED = IED.round(2)
#IED = IED[::-1]
#IED.to_csv('Inversión_Extranjera_Directa_Trimestral.csv',index=True)

































