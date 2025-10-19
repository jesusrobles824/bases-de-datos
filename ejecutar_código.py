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




id = 1
url = f"https://api.bcra.gob.ar/estadisticas/v3.0/monetarias/{id}"
hasta = pd.Timestamp.today().strftime('%Y-%m-%d')
params = {"desde": "2022-12-30", "hasta": hasta}
response = requests.get(url, params=params, verify=False)

if response.status_code == 200:
    data = response.json()
    Reservas_Brutas = pd.DataFrame(data['results'])[['fecha', 'valor']]
    Reservas_Brutas = Reservas_Brutas.rename(columns={'valor': 'Reservas_Brutas'})
    Reservas_Brutas['fecha'] = pd.to_datetime(Reservas_Brutas['fecha'])
    Reservas_Brutas.set_index('fecha', inplace=True)
    Reservas_Brutas = Reservas_Brutas[::-1]  # orden cronológico ascendente
    def cortos(fecha):
        if fecha.year == 2022 and fecha.month == 12:
            return 1852.97 
        elif fecha.year == 2023 and fecha.month == 1:
            return 1789.32 
        elif fecha.year == 2023 and fecha.month == 2:
            return 1813.97
        elif fecha.year == 2023 and fecha.month == 3:
            return 1837.34
        elif fecha.year == 2023 and fecha.month == 4:
            return 1843.72
        elif fecha.year == 2023 and fecha.month == 5:
            return 1808.53 
        elif fecha.year == 2023 and fecha.month == 6:
            return 1818.86
        elif fecha.year == 2023 and fecha.month == 7:
            return 1835.49
        elif fecha.year == 2023 and fecha.month == 8:
            return 1851.24
        elif fecha.year == 2023 and fecha.month == 9:
            return 1850.17
        elif fecha.year == 2023 and fecha.month == 10:
            return 1858.70    
        elif fecha.year == 2024 and fecha.month == 11:
            return 1965.70 
        elif fecha.year == 2024 and fecha.month == 12:
            return 1974.28 
        elif fecha.year == 2025 and fecha.month == 1:
            return 2073.10
        elif fecha.year == 2025 and fecha.month == 2:
            return 2080.24 
        elif fecha.year == 2025 and fecha.month == 3:
            return 2094.49 
        elif fecha.year == 2025 and fecha.month == 4:
            return 2102.05 
        elif fecha.year == 2025 and fecha.month == 5:
            return 2106.09
        elif fecha.year == 2025 and fecha.month == 6:
            return 2267.66
        elif fecha.year == 2025 and fecha.month == 7:
            return 2278.4
        elif fecha.year == 2025 and fecha.month == 8:
            return 2287.02
        else:
            return None
    ultimos_dias = Reservas_Brutas.groupby([Reservas_Brutas.index.year, Reservas_Brutas.index.month]).tail(1)
    Reservas_Brutas['Cortos'] = np.nan
    for fecha in ultimos_dias.index:
        ajuste = cortos(fecha)
        if ajuste is not None:
            Reservas_Brutas.loc[fecha, 'Cortos'] = ajuste

Reservas_Brutas.loc[Reservas_Brutas.index>'2025-08-31', 'Cortos'] = 2287.02
Reservas_Brutas['Cortos'] = pd.to_numeric(Reservas_Brutas['Cortos'], errors='coerce')
ultimo1 = Reservas_Brutas.loc['2022-12'].index.max()
ultimo2 = Reservas_Brutas.loc['2025-08'].index.max()
mask = (Reservas_Brutas.index >= ultimo1) & (Reservas_Brutas.index <= ultimo2)
ajuste_rango = Reservas_Brutas.loc[mask, 'Cortos'].copy()
ajuste_rango_interp = ajuste_rango.interpolate(method='linear')
Reservas_Brutas.loc[mask, 'Cortos'] = ajuste_rango_interp
Reservas_Brutas.loc[Reservas_Brutas.index > '2025-04-14', 'Reservas_Brutas'] -= 12396.3755085719
Reservas_Brutas.loc[Reservas_Brutas.index > '2025-08-01', 'Reservas_Brutas'] -= 2072.8

url = "https://www.bcra.gob.ar/Pdfs/PublicacionesEstadisticas/Serieanual.xls"
response = requests.get(url, verify=False)

balance_23 = pd.read_excel(BytesIO(response.content), sheet_name='serie semanal 2023',skiprows=3).iloc[[74,107]]
balance_23 = balance_23.T
balance_23.columns = balance_23.iloc[0]
balance_23 = balance_23.drop(balance_23.index[0])
balance_23.columns.name= None
balance_23.index.name = "fecha"
balance_23 = balance_23.reset_index()
balance_23['fecha'] = pd.to_datetime(balance_23['fecha'], errors='coerce')
balance_23.loc[balance_23.index[-1], 'fecha'] = pd.Timestamp("2023-12-31")
balance_23.set_index('fecha',inplace=True)
balance_23['obligaciones_ooii'] = balance_23['OBLIGACIONES CON ORGANISMOS INTERNACIONALES '] / (1000*balance_23['Tipo de Cambio'])
balance_23 = balance_23[['obligaciones_ooii']]

balance_24 = pd.read_excel(BytesIO(response.content), sheet_name='serie semanal 2024',skiprows=3).iloc[[74,107]]
balance_24 = balance_24.T
balance_24.columns = balance_24.iloc[0]
balance_24 = balance_24.drop(balance_24.index[0])
balance_24.columns.name= None
balance_24.index = pd.to_datetime(balance_24.index)
balance_24.index.name = "fecha"
balance_24['obligaciones_ooii'] = balance_24['OBLIGACIONES CON ORGANISMOS INTERNACIONALES '] / (1000*balance_24['Tipo de Cambio'])
balance_24 = balance_24[['obligaciones_ooii']]

balance_25 = pd.read_excel(BytesIO(response.content), sheet_name='serie semanal 2025',skiprows=3).iloc[[74,107]]
balance_25 = balance_25.T
balance_25.columns = balance_25.iloc[0]
balance_25 = balance_25.drop(balance_25.index[0])
balance_25.columns.name= None
balance_25.index = pd.to_datetime(balance_25.index)
balance_25.index.name = "fecha"
balance_25['obligaciones_ooii'] = balance_25['OBLIGACIONES CON ORGANISMOS INTERNACIONALES '] / (1000*balance_25['Tipo de Cambio'])
balance_25 = balance_25[['obligaciones_ooii']]

obligaciones_ooii = pd.concat([balance_23, balance_24, balance_25])
obligaciones_ooii.to_excel('obligaciones_ooii.xlsx',index=True)

Reservas_Brutas['obligaciones_ooii'] = obligaciones_ooii['obligaciones_ooii'].reindex(
    Reservas_Brutas.index, method='ffill'
)

Reservas_Brutas.loc[Reservas_Brutas.index<'2023-01-07','obligaciones_ooii'] = 3131.577122

hasta = Reservas_Brutas.index[-1]
url = "https://www.bcra.gob.ar/Pdfs/PublicacionesEstadisticas/diar_bas.xls"
response = requests.get(url, verify=False)
diar_bas = pd.read_excel(BytesIO(response.content), 
                         sheet_name='Serie_diaria', 
                         skiprows=26, 
                         usecols='A,M,AF,AG,AI')
diar_bas.columns = ['fecha','Depósitos en moneda extranjera en el BCRA', 
                    'Depósitos del gobierno en pesos', 
                    'Depósitos del gobierno en usd', 
                    'TC']
diar_bas.set_index('fecha', inplace=True)
diar_bas = diar_bas[(diar_bas.index > pd.Timestamp('2022-12-29')) & (diar_bas.index <= hasta)]
Encajes = pd.DataFrame()
Encajes['Encajes'] = diar_bas['Depósitos en moneda extranjera en el BCRA'] / diar_bas['TC']

# Descargar oro (GC=F)
oro = yf.download("GC=F", start="2022-12-30")[['Close']]
# Descargar tipo de cambio USD/CNY (Yahoo usa "CNY=X" para USD -> CNY)
yuan = yf.download("CNY=X", start="2022-12-30")[['Close']]
# Unir los dos DataFrames por fecha
ajuste = oro.join(yuan, how='inner')  # O how='outer' si querés mantener todas las fechas
# Resetear índice si querés que la fecha quede como columna
ajuste = ajuste.reset_index()
ajuste = ajuste.rename(columns={'Date':'fecha'})
ajuste.set_index('fecha', inplace=True)
ajuste.columns = ajuste.columns.get_level_values(-1)
ajuste = ajuste.rename(columns={'GC=F':'oro_usd', 'CNY=X':'yuan'})
ajuste['ajuste_oro'] = (ajuste['oro_usd']-ajuste.loc['2025-01-31']['oro_usd'])*1.98

RIN = Reservas_Brutas.join(Encajes, how='inner').join(ajuste, how='inner')
RIN['RIN'] = RIN['Reservas_Brutas']-RIN['Encajes']-RIN['Cortos']-130000/RIN['yuan']-RIN['obligaciones_ooii']
RIN['RIN_pp'] = RIN['Reservas_Brutas']-RIN['Encajes']-RIN['Cortos']-130000/RIN['yuan']-RIN['obligaciones_ooii']-RIN['ajuste_oro']
RIN['RIN_va'] = RIN['RIN']-RIN.loc['2024-12-30']['RIN']
RIN['RIN_pp_va'] = RIN['RIN_pp']-RIN.loc['2024-12-30']['RIN_pp']
RIN = RIN[['RIN','RIN_pp','RIN_va','RIN_pp_va']]
RIN = RIN[RIN.index>'2022-12-30']
RIN = RIN[::-1]
RIN.columns = ['RIN','RIN a precios 31/01/25','RIN variación acumulada respecto al 30/12/24','RIN variación acumulada respecto al 30/12/25 a precios 31/01/25']
for col in RIN.columns:
    RIN[col] = pd.to_numeric(RIN[col], errors='coerce')
RIN = RIN.round(2)
RIN.to_csv('Reservas_Netas.csv', index=True)




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























