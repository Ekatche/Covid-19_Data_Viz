import streamlit as st
import pandas as pd
import numpy as np
import zipfile
import plotly.express as px
import plotly.graph_objects as go
import pycountry
from geopy.exc import GeocoderTimedOut, GeocoderUnavailable
from geopy.geocoders import Nominatim

st.title('COVID-19 2020 Data visualisation')
st.header('World Graphs')

with zipfile.ZipFile('coronavirus.zip', 'r') as zip_ref:
    zip_ref.extractall('corona')


@st.cache_data()
def Load_data(nrows):
    df = pd.read_csv('corona/covid_19_data.csv', sep=',', index_col='SNo', nrows=nrows)
    df.columns = ['Observation_date', 'Province_state', 'Country_Region', 'Last_Update', 'Confirmed', 'Deaths',
                  'Recovered']

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
    # replace na data of province_state column by unknown
    df['Province_state'] = df['Province_state'].fillna('Unknown')

    # Data processing
    dfose = df.sort_values(by=['Country_Region', 'Province_state', 'Observation_date'],
                           ascending=True).reset_index().copy()
    # Modify datatype
    dfose['Confirmed'] = dfose['Confirmed'].astype(int)
    dfose['Deaths'] = dfose['Deaths'].astype(int)
    dfose['Recovered'] = dfose['Recovered'].astype(int)
    # create empty lists
    confirmed = [0] * len(dfose["Confirmed"])
    deaths = [0] * len(dfose["Confirmed"])
    recovered = [0] * len(dfose["Confirmed"])

    for i in range(len(dfose["Confirmed"])):
        if i == 0:

            confirmed[i] = dfose["Confirmed"][i]
            deaths[i] = dfose["Deaths"][i]
            recovered[i] = dfose["Recovered"][i]

        elif (dfose['Province_state'][i] == dfose['Province_state'][i - 1]) and (
                dfose['Country_Region'][i] != dfose['Country_Region'][i - 1]):
            confirmed[i] = dfose["Confirmed"][i]
            deaths[i] = dfose["Deaths"][i]
            recovered[i] = dfose["Recovered"][i]

        elif (dfose['Province_state'][i] != dfose['Province_state'][i - 1]) and (
                dfose['Country_Region'][i] == dfose['Country_Region'][i - 1]):
            confirmed[i] = dfose["Confirmed"][i]
            deaths[i] = dfose["Deaths"][i]
            recovered[i] = dfose["Recovered"][i]

        elif (dfose['Province_state'][i] != dfose['Province_state'][i - 1]) and (
                dfose['Country_Region'][i] != dfose['Country_Region'][i - 1]):
            confirmed[i] = dfose["Confirmed"][i]
            deaths[i] = dfose["Deaths"][i]
            recovered[i] = dfose["Recovered"][i]
        else:
            confirmed[i] = abs(dfose["Confirmed"][i] - dfose["Confirmed"][i - 1])
            recovered[i] = abs(dfose["Recovered"][i] - dfose["Recovered"][i - 1])
            deaths[i] = abs(dfose["Deaths"][i] - dfose["Deaths"][i - 1])

    dfose['confirmed'] = confirmed
    dfose['deaths'] = deaths
    dfose['recovered'] = recovered

    dfose[dfose['confirmed'] < 0] = 0
    dfose[dfose['deaths'] < 0] = 0
    dfose[dfose['recovered'] < 0] = 0

    dfose = dfose.drop(columns=['Confirmed', 'Deaths', 'Recovered', 'SNo'])
    return dfose


# Analyse
dfose = Load_data(156292)


df0 = dfose.copy()
df0['Observation_date'] = pd.to_datetime(df0['Observation_date'])
df0['Observation_date'] = df0['Observation_date'].dt.strftime('%m/%Y')

df1 = df0.groupby(['Observation_date'])[['confirmed', 'recovered', 'deaths']].sum().reset_index()
df1.sort_values(by='Observation_date')



temp = df1
del df0
del df1

temp = temp.melt(id_vars="Observation_date", value_vars=['deaths', 'recovered', 'confirmed'], var_name='Case',
                 value_name='Number of cases')
fig = px.area(temp, x="Observation_date", y="Number of cases", color='Case', height=400,
              title='Global evolution of Covid-19 cases over time ')

# draw graph
st.plotly_chart(fig)

# Graph with widgets

df10 = dfose.groupby(['Country_Region', 'Observation_date'])[['confirmed', 'recovered', 'deaths']].sum().reset_index()
df10['Observation_date'] = pd.to_datetime(df10['Observation_date'])
df10['Observation_date'] = df10['Observation_date'].dt.strftime('%m/%Y')
df1_Country = pd.DataFrame(df10.groupby(['Country_Region']).Observation_date.count())
df1_Country = df1_Country[df1_Country['Observation_date'] > 50]
list_countries = list(df1_Country.index.unique())
list_countries.sort()

st.subheader('Evolution over the year per country')

country = st.selectbox('Select a Country', list_countries)
st.write(country)
df10_bis = df10[df10.Country_Region == country].groupby(['Observation_date'])[
    ['confirmed', 'recovered', 'deaths']].sum().reset_index()
df_country = df10_bis.groupby('Observation_date').sum()
st.area_chart(df_country)

# World Analysis

df_C = dfose.groupby(['Country_Region'])[['confirmed','deaths','recovered']].sum().reset_index()
df_C= df_C.sort_values(by="deaths", ascending= False).head(50)
df_C1 = df_C.sort_values(by="recovered", ascending=False).head(50)
df_C3 = df_C.sort_values(by="confirmed", ascending=False).head(50)
df_C['% of deaths'] = round(((df_C.deaths / df_C.confirmed) * 100), 2)
df_C4 = df_C.sort_values(by="% of deaths", ascending=False).head(50)

# Graph
fig2 = px.scatter(df_C, x='confirmed', y='deaths', size='deaths', color='Country_Region',
                  title='Ranking of countries per number of deaths due to covid (TOP 50)')
st.plotly_chart(fig2)
# Graph
fig3 = px.scatter(df_C1, x='confirmed', y='recovered', size='recovered',
                  color='Country_Region', title='Ranking of countries according to the number <br>'
                                                'of recovery out of the confirmed cases (TOP 50)')
st.plotly_chart(fig3)
# Graph
fig4 = px.scatter(df_C4, x='confirmed', y='% of deaths', size='% of deaths', color='Country_Region',
                  title='Ranking of countries according to the % of deaths')
st.plotly_chart(fig4)
# Graph
fig5 = px.treemap(df_C3, path=['Country_Region'], values='confirmed', title='World TreeMap - Confirmed cases')
fig5.data[0].textinfo = 'label+text+value'
st.plotly_chart(fig5)

df_md = dfose.groupby('Country_Region')[['confirmed','deaths','recovered']].sum().copy().reset_index()
list_countries = df_md['Country_Region'].unique().tolist()
df_md = df_md.sort_values('deaths', ascending=False)
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

dfmd = df_md.groupby(['iso_alpha']).sum().reset_index()

# graph

fig = px.choropleth(data_frame=dfmd,
                    locations="iso_alpha",
                    color="confirmed",  # value in column 'Confirmed' determines color
                    hover_name="iso_alpha",
                    color_continuous_scale=px.colors.sequential.Bluyl,  # color scale red, yellow green
                    title='COVID 19 World Map')
st.plotly_chart(fig)

fig = px.scatter_geo(df_md, locations="iso_alpha", hover_name="Country_Region",
                     color="confirmed", size="confirmed",
                     projection="natural earth")

st.plotly_chart(fig)

# Header

st.subheader('Focus USA')

df_US=dfose[dfose['Country_Region']=='US'].copy()

df_USA= df_US.groupby(['Province_state'])[['confirmed','deaths','recovered']].sum().reset_index()

df_USA=df_USA.sort_values('confirmed', ascending=False).reset_index()

df_USA=df_USA.drop(196,axis=0)

# declare an empty list to store
# latitude and longitude values
longitude = []
latitude = []

# geolocator = Nominatim(user_agent="geoapiExercises")
geolocator = Nominatim(user_agent="streamlitApp")

@st.cache_data()
def findGeocode(Province_state):
    # try and catch is used to overcome
    # the exception thrown by geolocator
    # using geocodertimedout
    try:
        # Specify the user_agent as your
        # app name it should not be none
        find_loc = geolocator.geocode(Province_state)
        return find_loc
    except GeocoderTimedOut:
        return findGeocode(Province_state)
    # each value from city column
    except GeocoderUnavailable: 
        # if the location is not found return none
        pass

# will be fetched and sent to
# function find_geocode

for i in (df_USA["Province_state"]):

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
df_USA['Longitude'] = longitude
df_USA['Latitude'] = latitude

assert isinstance(df_USA, object)
df_USA['text'] = df_USA['Province_state'] + '<br> Number of confirmed cases ' + (df_USA['confirmed']/1e6).astype(str) + ' million'

limits = [(0,13),(14,33),(34,49)]
affichage = [('2.6e5','1e6'),('1e5','2.5e5'),('1e4','9e4')]
colors = ["royalblue","crimson","lightseagreen","lightgrey"]
scale = 1000

fig = go.Figure()
for i in range(len(limits)):
    lim = limits[i]
    aff=affichage[i]
    df_sub = df_USA[lim[0]:lim[1]]
    fig.add_trace(go.Scattergeo(
            locationmode = 'USA-states',
            lon = df_sub['Longitude'],
            lat = df_sub['Latitude'],
            text = df_sub['text'],
            marker = dict(
                autocolorscale=True,
                color=colors[i],
                size = df_sub['confirmed']/scale,
                line_width=0.5,
                sizemode = 'area'),name = '{} - {}'.format(aff[0],aff[1])))

fig.update_layout(
        title_text = '2020 Covid confirmed cases in the US <br>(Click legend to toggle traces)',
        showlegend = True,
        geo = dict(
            scope = 'usa',landcolor = 'rgb(217,217,210)'))

st.plotly_chart(fig)

st.header('Animated Graphs')

df_md_gbd_1=dfose.copy()

df_md_gbd_1['observation_date'] = pd.to_datetime(df_md_gbd_1['Observation_date'])
# st.dataframe(df_md_gbd_1)
# df_md_gbd_1['observation_date'] = df_md_gbd_1['observation_date'].dt.strftime('%m/%Y')]
# df_md_gbd_1 = df_md_gbd_1.groupby(['Country_Region', ).sum().groupby(level=0)[['confirmed','deaths','recovered']].cumsum().sort_values(
#     by='observation_date').reset_index()

# Group by 'Country_Region' and 'observation_date' and sum the numeric columns
df_md_gbd_1 = df_md_gbd_1.groupby(['Country_Region', df_md_gbd_1['observation_date'].dt.strftime('%m/%Y')])[['confirmed','deaths','recovered']].sum().reset_index()


df_md_gbd_1['iso_alpha'] = ''
for k, v in d_country_code.items():
    df_md_gbd_1.loc[(df_md_gbd_1.Country_Region == k), 'iso_alpha'] = v

fig = px.scatter_geo(df_md_gbd_1, locations="iso_alpha", color="confirmed",
                     hover_name="Country_Region",size="confirmed",
                     projection="natural earth",animation_frame="observation_date")

st.plotly_chart(fig)

st.header('COVID in 2020')
video_file = open('BarChartRace.mp4', 'rb')
video_bytes = video_file.read()
st.video(video_bytes)
