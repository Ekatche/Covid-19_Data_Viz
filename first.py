import streamlit as st
import pandas as pd
import numpy as np
import zipfile
import plotly.express as px
import plotly.graph_objects as go
import pycountry
from geopy.exc import GeocoderTimedOut
from geopy.geocoders import Nominatim

st.title('COVID-19 2020 Data visualisation')
st.header('World Graphs')

with zipfile.ZipFile('coronavirus.zip', 'r') as zip_ref:
    zip_ref.extractall('corona')

@st.cache
def Load_data(nrows):
    df = pd.read_csv('corona/covid_19_data.csv', sep=',', index_col='SNo',nrows=nrows)
    df.columns = ['Observation_date', 'Province_state', 'Country_Region', 'Last_Update', 'Confirmed', 'Deaths', 'Recovered']

    # mettre les dates au meme format
    df['Last_Update'] = pd.to_datetime(df['Last_Update'])
    df['Observation_date'] = pd.to_datetime(df['Observation_date'])
    # Correction des données des pays
    # 'Bahamas'-->'Bahamas, The'
    df.loc[df.Country_Region.str.contains("Bahamas"), 'Country_Region'] = 'Bahamas'
    # 'Gambia '--> 'Gambia, The'
    df.loc[df.Country_Region.str.contains("Gambia"), 'Country_Region'] = 'Gambia'
    # Congo (Brazzaville) --> Republic of the Congo
    df.loc[df.Country_Region.str.contains("Brazzaville"), 'Country_Region'] = 'Republic of the Congo'
    # correction uk --> GB
    df.loc[df.Country_Region.str.contains("UK"), 'Country_Region'] = 'GB'
    # remplacer French Guiana par France dans country region
    df.loc[df.Country_Region.str.contains("French"), 'Country_Region'] = 'France'
    # South Korea--> Korea, Republic of
    df.loc[df.Country_Region.str.contains("South Korea"), 'Country_Region'] = 'Korea, Republic of'
    # Ivory Coast --> Côte d'Ivoire
    df.loc[df.Country_Region.str.contains("Ivory Coast"), 'Country_Region'] = "Côte d'Ivoire"
    # cape verde --> Cabo Verde
    df.loc[df.Country_Region.str.contains("Cape Verde"), 'Country_Region'] = 'Cabo Verde'
    # West Bank and Gaza --> Palestine, State of
    df.loc[df.Country_Region.str.contains("West Bank and Gaza"), 'Country_Region'] = 'Palestine, State of'
    # occupied palestinian territory --> Palestine, State of
    df.loc[df.Country_Region.str.contains("occupied Palestinian territory"), 'Country_Region'] = 'Palestine, State of'
    # Burma (birmanie) --> Republic of Myanmar
    df.loc[df.Country_Region.str.contains("Burma"), 'Country_Region'] = 'Republic of Myanmar'
    # Congo (Kinshasa) --> Congo, The Democratic Republic of the
    df.loc[df.Country_Region.str.contains("Kinshasa"), 'Country_Region'] = 'Congo, The Democratic Republic of the'
    # Macau --> Macao Special Administrative Region of China
    df.loc[df.Country_Region.str.contains("Macau"), 'Country_Region'] = 'Macao Special Administrative Region of China'
    # Laos --> Lao People's Democratic Republic
    df.loc[df.Country_Region.str.contains("Laos"), 'Country_Region'] = "Lao People's Democratic Republic"
    # Republic of Ireland --> Ireland
    df.loc[df.Country_Region.str.contains("Republic of Ireland"), 'Country_Region'] = 'Ireland'
    # North Ireland --> GB
    df.loc[df.Country_Region.str.contains("North Ireland"), 'Country_Region'] = 'GB'
    # East Timor --> Timor-Leste
    df.loc[df.Country_Region.str.contains("East Timor"), 'Country_Region'] = 'Timor-Leste'
    # St. Martin --> Saint Martin (French part)
    df.loc[df.Country_Region.str.contains("St. Martin"), 'Country_Region'] = 'Saint Martin (French part)'
    # Mainland China--> China
    df.loc[df.Country_Region.str.contains("Mainland China"), 'Country_Region'] = "China"
    return df

# Analyse
df = Load_data(156292)

df1 = df.groupby(['Observation_date'])[['Confirmed', 'Recovered', 'Deaths']].sum().reset_index()
df1['Observation_date'] = df1['Observation_date'].dt.strftime('%m/%Y')
df1_bis = df1.groupby('Observation_date').sum()
temp = df1.groupby('Observation_date').sum().reset_index()
temp = temp.melt(id_vars="Observation_date", value_vars=['Deaths', 'Recovered', 'Confirmed'], var_name='Case',
                 value_name='Number of cases')
fig = px.area(temp, x="Observation_date", y="Number of cases", color='Case', height=400,
              title='Global evolution of Covid-19 cases over time ')

# draw graph
st.plotly_chart(fig)

# Graph with widgets
df10 = df.groupby(['Country_Region','Observation_date'])[['Confirmed', 'Recovered', 'Deaths']].sum().reset_index()
df10['Observation_date'] = df10['Observation_date'].dt.strftime('%m/%Y')
df1_Country = pd.DataFrame(df10.groupby(['Country_Region']).Observation_date.count())
df1_Country=df1_Country[df1_Country['Observation_date']>50]
list_countries = list(df1_Country.index.unique())
list_countries.sort()

st.subheader('Evolution over the year per country')

country=st.selectbox('Select a Country',list_countries)
st.write(country)
df10_bis = df10[df10.Country_Region == country ].groupby(['Observation_date'])[['Confirmed','Recovered','Deaths']].sum().reset_index()
df_country = df10_bis.groupby('Observation_date').sum()
st.area_chart(df_country)

# World Analysis

df_C = df.groupby(['Country_Region'])[['Confirmed', 'Deaths', 'Recovered']].sum().reset_index()
df_C = df_C.sort_values(by="Deaths", ascending=False).head(50)
df_C1 = df_C.sort_values(by="Recovered", ascending=False).head(50)
df_C3 = df_C.sort_values(by="Confirmed", ascending=False).head(50)
df_C['% of deaths'] = round(((df_C.Deaths / df_C.Confirmed) * 100), 2)
df_C4 = df_C.sort_values(by="% of deaths", ascending=False).head(50)

#Graph
fig2 = px.scatter(df_C, x='Confirmed', y='Deaths', size='Deaths', color='Country_Region',
                  title='Ranking of countries per number of deaths due to covid (TOP 50)')
st.plotly_chart(fig2)
#Graph
fig3 = px.scatter(df_C1, x='Confirmed', y='Recovered', size='Recovered',
                  color='Country_Region', title='Ranking of countries according to the number <br>'
                                                'of recovery out of the confirmed cases (TOP 50)')
st.plotly_chart(fig3)
#Graph
fig4 = px.scatter(df_C4, x='Confirmed', y='% of deaths', size='% of deaths', color='Country_Region',
                  title='Ranking of countries according to the % of deaths <br>'
                  '<math>\frac{"nb of deaths"}{"Confirmed cases"}</math>')
st.plotly_chart(fig4)
#Graph
fig5 = px.treemap(df_C3, path=['Country_Region'], values='Confirmed', title='World TreeMap - Confirmed cases')
fig5.data[0].textinfo = 'label+text+value'
st.plotly_chart(fig5)


df_md = df.groupby('Country_Region')[['Confirmed', 'Deaths', 'Recovered']].sum().copy().reset_index()
list_countries = df_md['Country_Region'].unique().tolist()
df_md = df_md.sort_values('Deaths', ascending=False)
d_country_code = {}  # To hold the country names and their ISO code 3

for country in list_countries:
    try:
        country_data = pycountry.countries.search_fuzzy(country)
        # country_data is a list of objects of class pycountry.db.Country
        # The first item  ie at index 0 of list is best fit
        # object of class Country have an alpha_3 attribute
        country_code = country_data[0].alpha_3
        d_country_code.update({country: country_code})
    except:
        print('could not add ISO 3 code for ->', country)
        # If could not find country, make ISO code ' '
        d_country_code.update({country: ' '})

# creation d'une colonne iso alpha pour contenu les code iso des pays

df_md['iso_alpha'] = ''

# Remplissage de la colonne iso_alpha
for k, v in d_country_code.items():
    df_md.loc[(df_md.Country_Region == k), 'iso_alpha'] = v

# graph

fig = px.choropleth(data_frame=df_md,
                    locations="iso_alpha",
                    color="Confirmed",  # value in column 'Confirmed' determines color
                    hover_name="Country_Region",
                    color_continuous_scale=px.colors.sequential.Bluyl,  # color scale red, yellow green
                    title='COVID 19 World Map')
st.plotly_chart(fig)

fig = px.scatter_geo(df_md, locations="iso_alpha", color="Confirmed",
                     hover_name="Country_Region", size="Confirmed",
                     projection="natural earth")

st.plotly_chart(fig)

#Header

st.subheader('Focus USA')

df_US = df[df['Country_Region'] == 'US'].copy()

df_US_A = df_US.groupby(['Province_state'])[['Confirmed', 'Deaths', 'Recovered']].sum()

df_US_A = df_US_A.sort_values('Confirmed', ascending=False).reset_index()

df_US_A = df_US_A.drop(197, axis=0)

# declare an empty list to store
# latitude and longitude values
longitude = []
latitude = []

geolocator = Nominatim(user_agent="geoapiExercises")

@st.cache
def findGeocode(Province_state):
    # try and catch is used to overcome
    # the exception thrown by geolocator
    # using geocodertimedout
    try:
        # Specify the user_agent as your
        # app name it should not be none
        geolocator = Nominatim(user_agent="your_app_name")

        return geolocator.geocode(Province_state)
    except GeocoderTimedOut:
        return findGeocode(Province_state)
    # each value from city column

# will be fetched and sent to
# function find_geocode

for i in (df_US_A["Province_state"]):

    if findGeocode(i) != None:

        loc = findGeocode(i)

        # coordinates returned from
        # function is stored into
        # two separate list
        latitude.append(loc.latitude)
        longitude.append(loc.longitude)

        # if coordinate for a city not
    # found, insert "NaN" indicating
    # missing value
    else:
        latitude.append(np.nan)
        longitude.append(np.nan)

    # of city column
df_US_A['Longitude'] = longitude
df_US_A['Latitude'] = latitude

df_US_A['text'] = df_US_A['Province_state'] + '<br> Number of confirmed cases ' + (df_US_A['Confirmed']).astype(str)

affichage = [(40, 105), (16, 39), (5, 15), (0, 4)]
limite = [(50, 1), (21, 50), (11, 20), (0, 10)]
seuil = [(0, 5), (6, 20), (21, 50), (51, 198)]
scale = 50000

fig6 = go.Figure()
for i in range(len(seuil)):
    # lim = limits[i]
    aff = affichage[i]
    lim = seuil[i]
    df_sub = df_US_A[lim[0]:lim[1]]
    fig6.add_trace(go.Scattergeo(
        locationmode='USA-states',
        lon=df_sub['Longitude'],
        lat=df_sub['Latitude'],
        text=df_sub['text'],
        marker=dict(
            autocolorscale=True,
            line_color='rgb(40,10,40,20)',
            size=df_sub['Confirmed'] / scale,
            line_width=0.5,
            sizemode='area'), name='{} - {}'.format(aff[0], aff[1])))

fig6.update_layout(
    title_text='2020 - Covid confirmed cases in the US (legend in million) <br>(Click legend to toggle traces)',
    showlegend=True,
    geo=dict(
        scope='usa', landcolor='rgb(217,217,210)'))

st.plotly_chart(fig6)

st.header('Animated Graphs')

df_md_gbd_1 = df.copy()

df_md_gbd_1['observation_date'] = pd.to_datetime(df_md_gbd_1['Observation_date'])

df_md_gbd_1['observation_date'] = df_md_gbd_1['observation_date'].dt.strftime('%m/%Y')

df_md_gbd_1 = df_md_gbd_1.groupby(['Country_Region', 'observation_date']).sum().groupby(level=0).cumsum().sort_values(
    by='observation_date').reset_index()

df_md_gbd_1['iso_alpha'] = ''
for k, v in d_country_code.items():
    df_md_gbd_1.loc[(df_md_gbd_1.Country_Region == k), 'iso_alpha'] = v

fig = px.scatter_geo(df_md_gbd_1, locations="iso_alpha", color="Confirmed",
                     hover_name="Country_Region", size="Confirmed",
                     projection="natural earth", animation_frame="observation_date",
                     title='COVID 19 World Map - Evolution of confirmed cases per Months')

st.plotly_chart(fig)

st.header('COVID in 2020')
video_file = open('BarChartRace2.mp4', 'rb')
video_bytes = video_file.read()
st.video(video_bytes)
