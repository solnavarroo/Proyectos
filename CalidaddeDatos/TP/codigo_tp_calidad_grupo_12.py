#TRABAJO PRACTICO CALIDAD DE DATOS
#GRUPO 12 - NAVARRO SOLANA, SUAREZ INES, WITTMUND MONTERO LOURDES
#%% IMPORTS
import pandas as pd
import matplotlib.pyplot as plt

#%%
# Para cargar la base de datos es necesario utilizar al archivo enviado con nombre 'base_con_colores' dado que la base original de la pagina
# la modificamos en excel para agregarle la informacion de los colores y luego el analisis aca lo empezamos directamente con la nueva base.
df = pd.read_excel("base_con_colores.xlsx")

df.columns = df.columns.str.strip()

datos = df[['Date', 'Year', 'Type','Color','Country', 'State', 'Location', 'Activity', 'Name', 'Sex', 'Age', 'Injury', 'Time', 'Species', 'Source' ]]

#%% Grafico validas e invalidas
cantidad = datos['Type'].value_counts()

opcionesValidas = ['Unprovoked', 'Provoked', 'Watercraft', 'Sea Disaster', 'Questionable']

cantidadValidas = cantidad[cantidad.index.isin(opcionesValidas)].sum()

cantidadInvalidas = cantidad[~cantidad.index.isin(opcionesValidas)].sum()

conteo_total = pd.Series([cantidadValidas, cantidadInvalidas], index=['Validos', 'Invalidos'])

conteo_total.plot(kind='pie', autopct='%1.1f%%', colors=['lightgreen', 'lightcoral'])
plt.ylabel('')
plt.show()

#%% Grafico analisis invalidas

cantidadInvalidas = cantidad[~cantidad.index.isin(opcionesValidas)]

cantidadNulos = datos['Type'].isnull().sum()

cantidadInvalidas.loc['Null'] = cantidadNulos

porcentajesInvalidas = (cantidadInvalidas / cantidadInvalidas.sum()) * 100

fig, ax = plt.subplots(figsize=(12,6))
porcentajesInvalidas.sort_values().plot(kind='barh', color='lightcoral', ax=ax)

for i, (value, label) in enumerate(zip(porcentajesInvalidas.sort_values(), porcentajesInvalidas.sort_values().index)):
    ax.text(value + 0.2, i, f'{value:.1f}%', va='center')  

plt.xlabel('')
plt.ylabel('')
plt.xlim(0, 110)
plt.xticks([])  
plt.show()

#%%Muestra colombia
colombiax2 = datos[(datos['Country'] == 'COLOMBIA') | (datos['Country'] == 'COLUMBIA')]
colombiax2 = colombiax2['Country'].value_counts()

print(colombiax2)

#%%Muestra mexico
mexico = datos[(datos['Country'] == 'MEXICO') | (datos['Country'] == 'Mexico') | (datos['Country'] == 'MeXICO')]
mexico = mexico['Country'].value_counts()

print(mexico)

#%% Los primeros 5 y los ultimos 5 

cantidadxpais = datos['Country'].value_counts()
primeros_5 = cantidadxpais.head(5)
ultimos_5 = cantidadxpais.tail(5)

pais_lista = pd.concat([primeros_5, pd.Series(['...'], index=['...']), ultimos_5])

tabla = pd.DataFrame(pais_lista).reset_index()
tabla.columns = ['Países', 'Cantidad']

print(tabla)


#%%Limpieza Type
datos = datos.dropna(how='all')

datos = datos.dropna(subset=['Type'])

invalids = datos[datos['Species'].str.contains('prior', case=False, na=False)]

invalids = invalids.drop([2555, 2556,4863, 5625], axis=0)

invalids['Type'] = 'Questionable'

datos = datos[datos['Type'] != 'Invalid']

datos = pd.concat([datos, invalids])

datos = datos[(datos['Type'] == 'Questionable') | (datos['Type'] == 'Unprovoked') | (datos['Type'] == 'Provoked') | (datos['Type'] == 'Watercraft') | (datos['Type'] == 'Sea Disaster')]
#%%Comparacion de tipos con colores
cant_total = datos.shape[0]

validos = datos[((datos['Type'] == 'Questionable') & (datos['Color'] == 'Blue')) | ((datos['Type'] == 'Unprovoked') & (datos['Color'] == 'Tan')) | ((datos['Type'] == 'Provoked') & (datos['Color'] == 'Orange')) | ((datos['Type'] == 'Watercraft') & (datos['Color'] == 'Green')) | ((datos['Type'] == 'Sea Disaster') & (datos['Color'] == 'Yellow'))]

cant_validos = validos.shape[0]

cant_invalidos = cant_total - cant_validos

print(f"La cantidad de datos con color correcto es {cant_validos}")
print(f"La cantidad de datos con color incorrecto es {cant_invalidos}")

#%%Limpieza de colores
datos.loc[(datos['Color'].isna()) & (datos['Type'] == 'Unprovoked'), 'Color'] = 'Tan'
datos.loc[(datos['Color'].isna()) & (datos['Type'] == 'Provoked'), 'Color'] = 'Orange'
datos.loc[(datos['Color'].isna()) & (datos['Type'] == 'Watercraft'), 'Color'] = 'Green'
datos.loc[(datos['Color'].isna()) & (datos['Type'] == 'Sea Disaster'), 'Color'] = 'Yellow'
datos.loc[(datos['Color'].isna()) & (datos['Type'] == 'Questionable'), 'Color'] = 'Blue'

datos.loc[(datos['Color'] == 'Tan'), 'Type'] = 'Unprovoked'
datos.loc[(datos['Color'] == 'Orange'), 'Type'] = 'Provoked'
datos.loc[(datos['Color'] == 'Green'), 'Type'] = 'Watercraft'
datos.loc[(datos['Color'] == 'Yellow'), 'Type'] = 'Sea Disaster'
datos.loc[(datos['Color'] == 'Blue'), 'Type'] = 'Questionable'
#%%Limpieza de Country
datos2 = datos.dropna(subset=['Country'])

datos2.loc[:, 'Country'] = datos2['Country'].str.upper()

datos2.loc[:, 'Country'] = datos2['Country'].str.strip()

datos2 = datos2[~datos2['Country'].str.contains(r"\?", case=False, na=False)]

datos2 = datos2[~datos2['Country'].str.contains("OCEAN", case=False, na=False)]

datos2 = datos2[~datos2['Country'].str.contains("SEA", case=False, na=False)]

datos2 = datos2[~datos2['Country'].str.contains(r"\/", case=False, na=False)]

#%% RESPUESTA PRIMER PREGUNTA: CUANTOS ACCIDENTES HAY DE CADA TIPO
respuesta_tipo = datos2['Type'].value_counts()

colores = {
    'Unprovoked': 'tan',
    'Provoked': '#FF8C00',
    'Watercraft': 'green',
    'Sea Disaster': '#FFD700',
    'Questionable': '#1f77b4'
}

ax = respuesta_tipo.plot(kind='bar', color=[colores.get(x, 'gray') for x in respuesta_tipo.index])

plt.xlabel('Tipo de Incidente')
plt.ylabel('Cantidad')


plt.xticks(rotation=0)

plt.show()

respuesta_tipo = respuesta_tipo.reset_index()
#%% RESPUESTA SEGUNDA PREGUNTA: CUANTOS ACCIDENTES HAY DE CADA TIPO POR PAIS
respuesta_paises = datos2.groupby('Country')['Type'].value_counts()


df = respuesta_paises.reset_index()
df.columns = ['country', 'type', 'count']
colores = {
    'Unprovoked': 'tan',
    'Provoked': '#FF8C00',
    'Watercraft': 'green',
    'Sea Disaster': '#FFD700',
    'Questionable': '#1f77b4'
}

top_countries = df.groupby('country')['count'].sum().nlargest(10).index

df_top = df[df['country'].isin(top_countries)]

df_pivot = df_top.pivot(index='country', columns='type', values='count').fillna(0)
df_pivot = df_pivot.loc[df_pivot.sum(axis=1).sort_values(ascending=False).index]
df_pivot.plot(kind='bar', stacked=True, figsize=(12, 6), color= colores)



plt.xlabel('País', fontsize=14)
plt.ylabel('Cantidad de incidentes', fontsize=14)
plt.legend(title='Tipo de incidente', bbox_to_anchor=(1.05, 1), loc='upper left')
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

respuesta_paises = respuesta_paises.reset_index()

respuesta_paises = respuesta_paises.sort_values(by="count", ascending=False)
