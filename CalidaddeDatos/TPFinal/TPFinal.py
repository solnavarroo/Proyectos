#%% Imports
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import geopandas as gpd
from shapely.geometry import Point, shape
from shapely import wkt
import json
from sklearn.ensemble import IsolationForest

pozos = pd.read_csv('capitulo-iv-pozos.csv')
noConvencionales = pd.read_csv('produccin-de-pozos-de-gas-y-petrleo-no-convencional.csv')
convencionales = pd.read_csv('produccin-de-pozos-de-gas-y-petrleo-2024.csv', low_memory=False)

#%%% Analisis unicidad
#%%
repesidpozo = pozos['idpozo'].duplicated().sum()
print(f'Repetidos por idpozos en pozos: {repesidpozo}')
repesidpozo_mes = convencionales[['idpozo', 'mes']].duplicated().sum()
print(f'Repetidos por idpozos y mes en pozos convencionales: {repesidpozo_mes}')
repesidpozo_anio_mes = noConvencionales[['idpozo', 'anio','mes']].duplicated().sum()
print(f'Repetidos por idpozos, año y mes en pozos no convencionales: {repesidpozo_anio_mes}')

#%% Coordenadas duplicadas
duplicados = pozos.duplicated(subset=['geojson'], keep=False)
filas_duplicadas = pozos[duplicados].shape[0]
print(f'Cantidad de pozos con coordenadas duplicadas en pozos: {filas_duplicadas}')

coord_repetidas = noConvencionales.groupby(['coordenadax', 'coordenaday'])['idpozo'].nunique()
coord_repetidas = coord_repetidas[coord_repetidas > 1]
cantidad = coord_repetidas.shape[0]
print(f'Cantidad de pozos con coordenadas duplicadas en no convencionales: {cantidad}')

#%% Datos repetidos sin contar el Id
# pozos
columnas = pozos.columns.difference(['idpozo'])
igualessinid = pozos[pozos.duplicated(subset=columnas, keep=False)]
print(f'Cantidad de repetidos sin el id en pozos: {len(igualessinid)}')
igualessinid = igualessinid.iloc[:, :5].head(5)

# convencionales
columnas = convencionales.columns.difference(['idpozo'])
igualessinidconv = convencionales[convencionales.duplicated(subset=columnas, keep=False)]
igualessinidconv = igualessinidconv.sort_values(by='sigla')
print(f'Cantidad de repetidos sin el id en convencionales: {len(igualessinidconv)}')
igualessinidconv = igualessinidconv.iloc[:, :5].head(2)

# noConvencionales
columnas = noConvencionales.columns.difference(['idpozo'])
igualessinidnocon = noConvencionales[noConvencionales.duplicated(subset=columnas, keep=False)].shape[0]
print(f'Cantidad de repetidos sin el id en no convencionales: {igualessinidnocon}')

#%% Limpieza de estos datos
columnas = pozos.columns.difference(['idpozo'])
dupli = pozos.duplicated(subset=columnas, keep=False)
duplicados = pozos[dupli]
unicos = pozos[~dupli]

duplicados = (
    duplicados.sort_values(by='idpozo')
    .drop_duplicates(subset=columnas, keep='first')  
)
pozos = pd.concat([unicos, duplicados], ignore_index=True)

columnas = convencionales.columns.difference(['idpozo'])
dupli = convencionales.duplicated(subset=columnas, keep=False)
duplicados = convencionales[dupli]
unicos = convencionales[~dupli]

duplicados = (
    duplicados.sort_values(by='idpozo')
    .drop_duplicates(subset=columnas, keep='first')  
)
convencionales = pd.concat([unicos, duplicados], ignore_index=True)

#%%% Consistencia de tablas
#%% Cantidad de nulos
print('Pozos:')
valoresfaltantes = pozos.isnull().sum()
print(valoresfaltantes[valoresfaltantes > 0])
print('\n')
print('No Convencionales:')
valoresfaltantes = noConvencionales.isnull().sum()
print(valoresfaltantes[valoresfaltantes > 0])
print('\n')
print('Convencionales:')
valoresfaltantes = convencionales.isnull().sum()
print(valoresfaltantes[valoresfaltantes > 0])
#%% Tablas pozos
# Fechas
pozos = pozos[(~(pozos['adjiv_fecha_inicio_perf'].notnull() & pozos['adjiv_fecha_fin_perf'].notnull())) | (pozos['adjiv_fecha_inicio_perf'] <= pozos['adjiv_fecha_fin_perf'])]
pozos = pozos[(~(pozos['adjiv_fecha_inicio_term'].notnull() & pozos['adjiv_fecha_fin_term'].notnull())) | (pozos['adjiv_fecha_inicio_term'] <= pozos['adjiv_fecha_fin_term'])]
# Cota y profundidad
pozos = pozos[pozos['cota'] < 5600]  
pozos = pozos[(pozos['profundidad'] >= 0) & (pozos['profundidad'] < 27100)]

#%% Bokplot
sns.set(style="whitegrid")
fig, axes = plt.subplots(1, 2, figsize=(15, 5))

# Boxplot para 'cota'
sns.boxplot(data=pozos, x='cota', ax=axes[0], color='skyblue')
axes[0].set_xlim(-300, 3250)
axes[0].set_title('Boxplot de Cota')
axes[0].set_xlabel('Cota ')

# Boxplot para 'profundidad'
sns.boxplot(data=pozos, x='profundidad', ax=axes[1], color='salmon')
axes[1].set_xlim(-50, 20000)
axes[1].set_title('Boxplot de Profundidad')
axes[1].set_xlabel('Profundidad')

plt.tight_layout()
plt.show()

#%% Tabla convencionales
porcentajes = convencionales['tipo_de_recurso'].value_counts(normalize=True) * 100
porcentajes = porcentajes.rename({'proportion': 'Porcentajes'})
print(porcentajes)

conv = porcentajes.get('CONVENCIONAL', 0)
otros = 100 - conv

porcentajes = pd.Series([conv, otros], index=['Convencional', 'Otros'])

plt.figure(figsize=(6, 6))
plt.pie(porcentajes, labels=porcentajes.index, autopct='%1.1f%%', startangle=90)

plt.show()
#%% Informacion segun tipo de produccion o de inyeccion o de vida util o de profundidad
numeric_cols = ['prod_pet', 'prod_gas', 'prod_agua', 'iny_agua', 'iny_gas', 'iny_co2', 'iny_otro', 'tef', 'vida_util', 'profundidad']
numeric_stats = convencionales[numeric_cols].describe()

print("\
Estadísticas de columnas numéricas:")
print(numeric_stats)

#%% Limpiamos datos invalidos
convencionales = convencionales[(convencionales['prod_gas'] >= 0) & (convencionales['prod_pet'] >= 0) & (convencionales['prod_agua'] >= 0) & (convencionales['iny_agua'] >= 0) & (convencionales['iny_gas'] >= 0) & (convencionales['iny_co2'] >= 0) & (convencionales['iny_otro'] >= 0)]
convencionales = convencionales.dropna(subset=['prod_gas', 'iny_agua', 'prod_agua', 'prod_pet', 'iny_gas', 'iny_otro'])

#%% No convencionales
noConvencionales = noConvencionales.dropna(subset=['prod_gas', 'iny_agua', 'prod_agua', 'prod_pet', 'iny_gas', 'iny_otro'])

#%% Consistencia entre Noconvencionales y Convencionales
## Sacamos no convencionales de la tabla convencionales
convencionales = convencionales[convencionales['tipo_de_recurso'] == 'CONVENCIONAL']

idsencomun = convencionales['idpozo'].isin(noConvencionales['idpozo'])
cantidad = idsencomun.sum()  
print(f'Pozos en común entre convencionales y no convencionales luego de la limpieza: {cantidad}')

#%% Consistencia entre Convencionales con Pozos
convencionales.rename(columns={'tipo_de_recurso': 'tipo_recurso'}, inplace=True)
convencionales.rename(columns={'idareapermisoconcesion': 'cod_area'}, inplace=True)
convencionales.rename(columns={'areapermisoconcesion': 'area'}, inplace=True)
convencionales.rename(columns={'idareayacimiento': 'cod_yacimiento'}, inplace=True)
convencionales.rename(columns={'areayacimiento': 'yacimiento'}, inplace=True)

convencionales.fillna('No informado', inplace=True)
pozos.fillna('No informado', inplace=True)
pozos = pozos.replace({"nan": 'No informado'})
convencionales = convencionales.replace({"nan": 'No informado'})

columnas = ['sigla', 'empresa', 'yacimiento', 'cod_yacimiento', 'formacion', 'profundidad', 'cuenca', 'cod_area', 'area', 'provincia', 'clasificacion', 'subclasificacion', 'tipo_recurso', 'tipopozo', 'tipoextraccion', 'tipoestado']
data = convencionales[['idpozo', 'mes'] + columnas]
data = data.loc[data.groupby(['idpozo'])['mes'].idxmax()]

como = pd.merge(pozos, data, on='idpozo', how='inner')

for columna in columnas:
        como[f'inconsistencia_{columna}'] = como[f'{columna}_x'] != como[f'{columna}_y']

como = como[como[[f'inconsistencia_{col}' for col in columnas]].any(axis=1)]
como = como.loc[:, ~(como == False).all()]
cantidad = como.shape[0]
print(f'Cantidad de inconsistencias inicial entre Pozos y Convencionales: {cantidad}')
columnasinconsistentes = como.select_dtypes(include='bool')
conteodetrue = columnasinconsistentes.sum() 
print(conteodetrue)

pozos = pd.merge(pozos, data[['idpozo','tipo_recurso']], on='idpozo', how='left')
pozos['tipo_recurso_x'] = pozos['tipo_recurso_y'].fillna(pozos['tipo_recurso_x'])

pozos = pozos.drop(columns=['tipo_recurso_y'])
pozos.rename(columns={'tipo_recurso_x': 'tipo_recurso'}, inplace=True)

como = pd.merge(pozos, data, on='idpozo', how='inner')

for columna in columnas:
        como[f'inconsistencia_{columna}'] = como[f'{columna}_x'] != como[f'{columna}_y']

como = como[como[[f'inconsistencia_{col}' for col in columnas]].any(axis=1)]
como = como.loc[:, ~(como == False).all()]
cantidad = como.shape[0]
print(f'Cantidad de inconsistencias entre Pozos y Convencionales luego de limpieza: {cantidad}')
columnasinconsistentes = como.select_dtypes(include='bool')
conteodetrue = columnasinconsistentes.sum() 
print(conteodetrue)

convencionales = convencionales[~convencionales['idpozo'].isin(como['idpozo'])]
pozos = pozos[~pozos['idpozo'].isin(como['idpozo'])]
#%% Consistencia entre no Convencionales con Pozos
noConvencionales.rename(columns={'tipo_de_recurso': 'tipo_recurso'}, inplace=True)
noConvencionales.rename(columns={'idareapermisoconcesion': 'cod_area'}, inplace=True)
noConvencionales.rename(columns={'areapermisoconcesion': 'area'}, inplace=True)
noConvencionales.rename(columns={'idareayacimiento': 'cod_yacimiento'}, inplace=True)
noConvencionales.rename(columns={'areayacimiento': 'yacimiento'}, inplace=True)


noConvencionales.fillna('No informado', inplace=True)
pozos.fillna('No informado', inplace=True)
pozos = pozos.replace({"nan": 'No informado'})
noConvencionales = noConvencionales.replace({"nan": 'No informado'})

columnas = ['sigla', 'empresa', 'yacimiento', 'cod_yacimiento', 'formacion', 'profundidad', 'cuenca', 'cod_area', 'area', 'provincia', 'clasificacion', 'subclasificacion', 'tipo_recurso', 'tipopozo', 'tipoextraccion', 'tipoestado', 'sub_tipo_recurso']
data = noConvencionales[['idpozo', 'mes', 'anio'] + columnas]
ultimoaño = data.groupby('idpozo')['anio'].max().reset_index()
data = data.merge(ultimoaño, on= ['idpozo', 'anio'])
data = data.loc[data.groupby('idpozo')['mes'].idxmax()]


como = pd.merge(pozos, data, on='idpozo', how='inner')

for columna in columnas:
        como[f'inconsistencia_{columna}'] = como[f'{columna}_x'] != como[f'{columna}_y']

como = como[como[[f'inconsistencia_{col}' for col in columnas]].any(axis=1)]
como = como.loc[:, ~(como == False).all()]
cantidad = como.shape[0]
print(f'Cantidad de inconsistencias inicial entre Pozos y No Convencionales: {cantidad}')
columnasinconsistentes = como.select_dtypes(include='bool')
conteodetrue = columnasinconsistentes.sum() 
print(conteodetrue)

noConvencionales = noConvencionales[~noConvencionales['idpozo'].isin(como['idpozo'])]
pozos = pozos[~pozos['idpozo'].isin(como['idpozo'])]

#%%% Ejercicio c
#%%
provincias = pd.read_csv('provincia.csv')

provincias['geom'] = provincias['geom'].apply(wkt.loads)
provincias = gpd.GeoDataFrame(provincias, geometry='geom', crs='EPSG:4326')
provincias['nam'] = provincias['nam'].str.replace('Río Negro', 'Rio Negro', regex=False)
provincias['nam'] = provincias['nam'].str.replace('Provincia de Tierra del Fuego, Antártida e Islas del Atlántico Sur', 'Tierra del Fuego', regex=False)
provincias['nam'] = provincias['nam'].str.replace('Tierra del Fuego, Antártida e Islas del Atlántico Sur', 'Tierra del Fuego', regex=False)

#%% Pozos
pozos['geojson'] = pozos['geojson'].apply(lambda x: shape(json.loads(x)) if isinstance(x, str) else x)

pozos_gdf = gpd.GeoDataFrame(pozos, geometry='geojson', crs='EPSG:4326')
result = gpd.sjoin(pozos_gdf, provincias, how='left', predicate='within')
novalidos = result[result['provincia'] != result['nam']]

cantidad = novalidos.shape[0]

print(f'La cantidad de pozos sin coordenadas validas son: {cantidad}')

# Eliminamos los nulls ya que no pertenecen a una provincia especifica
idsaeliminar = novalidos[novalidos['nam'].isnull()]['idpozo']
pozos = pozos[~pozos['idpozo'].isin(idsaeliminar)]
novalidos = novalidos[~novalidos['nam'].isnull()]

# Modificamos los que estaban mal en la tabla pozos por la provincia correcta a la que pertenece el pozo
pozos_actualizados = pozos.merge(novalidos[['idpozo', 'nam']],
                                 how='left',
                                 on='idpozo',
                                 suffixes=('', '_novalido'))

pozos_actualizados['provincia'] = pozos_actualizados['nam'].combine_first(pozos_actualizados['provincia'])
pozos = pozos_actualizados.drop(columns=['nam'])

#%% No convencionales
noConvencionales['geometry'] = noConvencionales.apply(
    lambda row: Point(row['coordenadax'], row['coordenaday']), axis=1
)

noConvencionales_gdf = gpd.GeoDataFrame(noConvencionales, geometry='geometry', crs='EPSG:4326')
result = gpd.sjoin(noConvencionales_gdf, provincias, how='left', predicate='within')
novalidos = result[result['provincia'] != result['nam']]

cantidad = novalidos.shape[0]
print(f'La cantidad de no Convencionales sin coordenadas válidas son: {cantidad}')

idsaeliminar = novalidos[novalidos['nam'].isnull()]['idpozo']
noConvencionales = noConvencionales[~noConvencionales['idpozo'].isin(idsaeliminar)]


novalidos = novalidos[~novalidos['nam'].isnull()]
noConvencionales_actualizados = noConvencionales.merge(
    novalidos[['idpozo', 'nam']],
    how='left',
    on='idpozo',
    suffixes=('', '_novalido')
)

noConvencionales_actualizados['provincia'] = noConvencionales_actualizados['nam'].combine_first(noConvencionales_actualizados['provincia'])

noConvencionales = noConvencionales_actualizados.drop(columns=['nam', 'geometry'])
#%%% Ejercicio d
#%% No convencionales
noConvencionales2024 = noConvencionales[(noConvencionales['anio'] == 2024)]

noConvencionales2024_prod = noConvencionales2024[(noConvencionales2024['tipoestado'] == 'Extracción Efectiva') | (noConvencionales2024['tipoestado'] == 'Parado Transitoriamente')]

#Gas
resultadogasnc = noConvencionales2024_prod.groupby('mes')['prod_gas'].sum().reset_index()
total_prod_gasnc = resultadogasnc['prod_gas'].sum()
resultadogasnc['porcentaje'] = (resultadogasnc['prod_gas'] / total_prod_gasnc) * 100

# Petroleo
resultadopetnc = noConvencionales2024_prod.groupby('mes')['prod_pet'].sum().reset_index()
total_prod_petnc = resultadopetnc['prod_pet'].sum()
resultadopetnc['porcentaje'] = (resultadopetnc['prod_pet'] / total_prod_petnc) * 100

#%% Convencionales
convencionales_prod = convencionales[(convencionales['tipoestado'] == 'Extracción Efectiva') | (convencionales['tipoestado'] == 'Parado Transitoriamente')]

#Gas
resultadogasc = convencionales_prod.groupby('mes')['prod_gas'].sum().reset_index()
total_prod_gasc = resultadogasc['prod_gas'].sum()
resultadogasc['porcentaje'] = (resultadogasc['prod_gas'] / total_prod_gasc) * 100

#Petroleo
resultadopetc = convencionales_prod.groupby('mes')['prod_pet'].sum().reset_index()
total_prod_petnc = resultadopetc['prod_pet'].sum()
resultadopetc['porcentaje'] = (resultadopetc['prod_pet'] / total_prod_petnc) * 100

#%% Gas
meses = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre']
porcentajes_conv = resultadogasc['porcentaje']
porcentajes_nconv = resultadogasnc['porcentaje']

x = range(1, 11)
width = 0.35

plt.figure(figsize=(14, 6))

plt.bar([i - width/2 for i in x], porcentajes_conv, width, label='Convencionales')

plt.bar([i + width/2 for i in x], porcentajes_nconv, width, label='No Convencionales')

plt.xlabel('Meses')
plt.ylabel('Porcentaje de Producción')
plt.title('Producción mensual de Gas (Porcentajes)')
plt.xticks(x, meses) 
plt.legend()

plt.tight_layout()
plt.show()

#%% Petroleo
meses = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre']
porcentajes_conv = resultadopetc['porcentaje']
porcentajes_nconv = resultadopetnc['porcentaje']

x = range(1, 11)
width = 0.35

plt.figure(figsize=(14, 6))

plt.bar([i - width/2 for i in x], porcentajes_conv, width, label='Convencionales')

plt.bar([i + width/2 for i in x], porcentajes_nconv, width, label='No Convencionales')

plt.xlabel('Meses')
plt.ylabel('Porcentaje de Producción')
plt.title('Producción mensual de Petroleo (Porcentajes)')
plt.xticks(x, meses) 
plt.legend()

plt.tight_layout()
plt.show()

#%%Cantidad de gas en convencionales vs no convencionales en el 2024 en total
cantidadgasconv = resultadogasc['prod_gas'].sum()
cantidadgasnoconv = resultadogasnc['prod_gas'].sum()
etiquetas = ['Convencional', 'No convencional']
valores = [cantidadgasconv, cantidadgasnoconv]

plt.pie(valores, labels=etiquetas, autopct='%1.1f%%', startangle=90)
plt.title('Cantidad de produccion de gas')
plt.axis('equal')
plt.show()


#%% Cantidad de petroleo en convencionales vs no convencionales en el 2024 en total
cantidadpetconv = resultadopetc['prod_pet'].sum()
cantidadpetnoconv = resultadopetnc['prod_pet'].sum()
etiquetas = ['Convencional', 'No convencional']
valores = [cantidadpetconv, cantidadpetnoconv]

plt.pie(valores, labels=etiquetas, autopct='%1.1f%%', startangle=90)
plt.title('Cantidad de produccion de petroleo')
plt.axis('equal')
plt.show()

#%% Busqueda casos anomalos
#%% No convencionales
variables = ['prod_pet', 'prod_gas', 'prod_agua']
scaler = StandardScaler()
dataprod = noConvencionales[(noConvencionales['tipoestado'] == 'Extracción Efectiva') | (noConvencionales['tipoestado'] == 'Parado Transitoriamente')]

data = scaler.fit_transform(dataprod[variables].fillna(0))

kmeans = KMeans(n_clusters=3, random_state=42)
clusters = kmeans.fit_predict(data)

distances = np.linalg.norm(data - kmeans.cluster_centers_[clusters], axis=1)

threshold = np.percentile(distances, 95)
dataprod['anomalias'] = distances > threshold

kmeansanomaliasnoconv = dataprod[dataprod['anomalias']]
print(f"Anomalías detectadas con K-Means en No Convenciales: {len(kmeansanomaliasnoconv)}")

subtipo_recurso_anomalias = kmeansanomaliasnoconv['sub_tipo_recurso'].value_counts()
plt.figure(figsize=(8, 6))
sns.barplot(x=subtipo_recurso_anomalias.index, y=subtipo_recurso_anomalias.values, palette="muted")
plt.title("Distribución de Anomalías por Subtipo de Recurso")
plt.xlabel("Subtipo de Recurso")
plt.ylabel("Cantidad de Anomalías")
plt.show()

#%% Utilizacion de base de datos para mejora de casos anomalos
empresasoperadoras = pd.read_csv('listado-de-pozos-cargados-por-empresas-operadoras.csv', low_memory=False)

empresasoperadoras['adjiv_fecha_inicio'] = pd.to_datetime(empresasoperadoras['adjiv_fecha_inicio'], errors='coerce')
empresasoperadoras = empresasoperadoras[(empresasoperadoras['adjiv_fecha_inicio'].dt.year == 2024) |
                                        (empresasoperadoras['adjiv_fecha_inicio'].dt.year == 2023) |
                                        (empresasoperadoras['adjiv_fecha_inicio'].dt.year == 2022) |
                                        (empresasoperadoras['adjiv_fecha_inicio'].dt.year == 2021) |
                                        (empresasoperadoras['adjiv_fecha_inicio'].dt.year == 2020) |
                                        (empresasoperadoras['adjiv_fecha_inicio'].dt.year == 2019)]
empresasoperadoras = empresasoperadoras[empresasoperadoras['tipo_reservorio']=='NO CONVENCIONAL']
empresasoperadoras = empresasoperadoras[['idempresa', 'idpozo', 'petroleo', 'gas', 'agua', 'provincia']]
empresasoperadoras.rename(columns={'petroleo': 'prod_pet'}, inplace=True)
empresasoperadoras.rename(columns={'gas': 'prod_gas'}, inplace=True)
empresasoperadoras.rename(columns={'agua': 'prod_agua'}, inplace=True)

dataprod = noConvencionales[(noConvencionales['tipoestado'] == 'Extracción Efectiva') | (noConvencionales['tipoestado'] == 'Parado Transitoriamente')]

noConvencionales2024 = dataprod[(dataprod['anio'] == 2024) | 
                                (dataprod['anio'] == 2023) | 
                                (dataprod['anio'] == 2022) |
                                (dataprod['anio'] == 2021) |
                                (dataprod['anio'] == 2020) |
                                (dataprod['anio'] == 2019)]

noConvencionales2024 = noConvencionales2024.groupby(['idempresa', 'idpozo'], as_index=False).agg({
    'prod_gas': 'sum',
    'prod_pet': 'sum',
    'prod_agua': 'sum'
})
hola = noConvencionales2024.value_counts('idpozo')
merged = noConvencionales2024.merge(empresasoperadoras, on=['idempresa', 'idpozo'], how='inner', suffixes=('_noconv', '_operadora'))

merged['anomalia_gas'] = abs(merged['prod_gas_noconv'] - merged['prod_gas_operadora']) >  100
merged['anomalia_pet'] = abs(merged['prod_pet_noconv'] - merged['prod_pet_operadora']) > 100
merged['anomalia_agua'] = abs(merged['prod_agua_noconv'] - merged['prod_agua_operadora']) > 100

anomalias = merged[
    (merged['anomalia_gas']) | 
    (merged['anomalia_pet']) | 
    (merged['anomalia_agua'])]
anomaliasnoConv = anomalias[(anomalias['prod_gas_operadora'] != 0) |
                      (anomalias['prod_pet_operadora'] != 0) |
                      (anomalias['prod_agua_operadora'] != 0)]

cant = anomaliasnoConv.shape[0]
print(f'Cantidad de anomalias utilizando base de datos externa: {cant}')

conteo_anomalias = {
    'prod_gas': merged['anomalia_gas'].sum(),
    'prod_pet': merged['anomalia_pet'].sum(),
    'prod_agua': merged['anomalia_agua'].sum()
}
conteo_anomalias = pd.DataFrame(
    list(conteo_anomalias.items()), 
    columns=['Produccion', 'Cantidad de Anomalías']
)
print(conteo_anomalias)


merged_data = pd.merge(
    anomaliasnoConv,
    noConvencionales2024,
    how='left',
    on=['idempresa', 'idpozo']
)

anomalias_por_empresa = merged_data.groupby('idempresa')[['anomalia_gas', 'anomalia_pet', 'anomalia_agua']].sum()

anomalias_por_empresa.plot(
    kind='bar',
    figsize=(10, 6),
    title="Distribución de anomalías por empresa",
    ylabel="Cantidad de anomalías",
    xlabel="Empresa",
    color=['blue', 'orange', 'green']
)
plt.xticks(rotation=90)
plt.legend(title="Tipo de anomalía")
plt.tight_layout()
plt.show()

#%% Convencionales
variables = ['prod_pet', 'prod_gas', 'prod_agua']
scaler = StandardScaler()
dataprod = convencionales[(convencionales['tipoestado'] == 'Extracción Efectiva') | (convencionales['tipoestado'] == 'Parado Transitoriamente')]

data = scaler.fit_transform(dataprod[variables].fillna(0))

kmeans = KMeans(n_clusters=3, random_state=42)
clusters = kmeans.fit_predict(data)

distances = np.linalg.norm(data - kmeans.cluster_centers_[clusters], axis=1)

threshold = np.percentile(distances, 95)
dataprod['anomalias'] = distances > threshold

kmeansanomaliasconv = dataprod[dataprod['anomalias']]
print(f"Anomalías detectadas con K-Means en Convencionales: {len(kmeansanomaliasconv)}")
kmeansanomaliasconv = kmeansanomaliasconv.drop(columns=['anomalias'])

columnaspredominantes = ['proyecto', 'tipopozo']

for column in columnaspredominantes:
    value_counts = kmeansanomaliasconv[column].value_counts()
    labels = value_counts.index
    values = value_counts.values

    plt.figure(figsize=(10, 6))
    plt.barh(labels, values, color='skyblue')
    plt.xlabel('Frecuencia')
    plt.ylabel('Categoría')
    plt.title(f'Distribución de {column}')
    plt.tight_layout()
    plt.show()


#%% Utilizacion de base de datos para mejora de casos anomalos
datos_2023 = pd.read_csv('produccin-de-pozos-de-gas-y-petrleo-2023.csv', low_memory=False)
convencionales_2023 = datos_2023[datos_2023['tipo_de_recurso'] == 'CONVENCIONAL']

datos_2024 = convencionales.dropna().copy() 

datos_2023 = convencionales_2023.copy()  
datos_2023_prod = datos_2023[(datos_2023['tipoestado'] == 'Extracción Efectiva') | (convencionales['tipoestado'] == 'Parado Transitoriamente')]

features_2023 = datos_2023_prod[['prod_agua', 'prod_gas', 'prod_pet']]
model = IsolationForest(contamination=0.05, random_state=42)
model.fit(features_2023)

features_2024 = datos_2024[['prod_agua', 'prod_gas', 'prod_pet']]
datos_2024['anomaly_score'] = model.decision_function(features_2024)
datos_2024['Anomalia'] = model.predict(features_2024) 

datos_2024['Anomalia'] = datos_2024['Anomalia'].replace({
    1: 'No Anomalía',
    -1: 'Anomalía'
})

print(datos_2024['Anomalia'].value_counts())

anomaliasconv = datos_2024[datos_2024['Anomalia'] == 'Anomalía']

mean_2023 = features_2023.mean()
deviations = features_2024 - mean_2023

datos_2024['Cant anomalias por produccion'] = deviations.abs().idxmax(axis=1)

anomaliasconv = datos_2024[datos_2024['Anomalia'] == 'Anomalía']

conteo_anomalias = anomaliasconv['Cant anomalias por produccion'].value_counts()
print(conteo_anomalias)
