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

# Definir la fecha de hoy automáticamente
hoy = (datetime.today()).strftime('%Y-%m-%d')
#hoy = (datetime.today() + timedelta(days=1)).strftime('%Y-%m-%d')

tickers_adrs = ['BBAR', 'BMA', 'CEPU', 'CRESY', 'EDN', 'GGAL', 'IRS','LOMA',
                'PAM', 'SUPV', 'TEO', 'TGS', 'TS', 'TX', 'YPF']

# Descargar datos históricos de los ADRs y el Merval
adrs = yf.download(tickers_adrs, start='2010-01-01', end=hoy)['Close']
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

Tasas = pd.read_excel(BytesIO(response.content), sheet_name='TASAS DE MERCADO', skiprows=8, usecols='A,I,R,S,V,X')

Tasas.columns = ['fecha','TAMAR','Préstamos personales','Adelantos en cuenta corriente','Call en Pesos','Repo a 1 día (excl. BCRA)']
Tasas.set_index('fecha', inplace=True)
Tasas = Tasas[Tasas.index>'2024-05-31']
Tasas = Tasas[::-1]
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









