# Autor: David Betancur Sánchez
# Editor: Pycharm

import pandas as pd
import plotly.plotly as py
import plotly.graph_objs as go
import requests
import time
import random
import datetime
import plotly

plotly.tools.set_credentials_file(username='david.bet.san', api_key='Uqj7UqPTEgafeLxWHwkV')
token = 'EAACEdEose0cBANvjA3SdByNNLI4Da9yU370wY9GdrDYOaLn4ZAgS5W8CSohiDmBQVxjpdVQeLD4ZAPvEaGBX7ZCt2z3gqIHZAh6KZB0Exp7NRt0Sjoo2vBFAqnd3q4MIRyBr4KGTpusA0MBbJGM3wwBe6eeeIyHY9H8pHy2aOFYkVUJ0DiQLVnsNLIlaxanwZD'

def req_facebook(req):
    # Hace el request en la api
    r = requests.get("https://graph.facebook.com/v2.12/" + req, {'access_token' : token})
    return r
def get_fb_data():
    # same as get_insta_data
    today = int(time.time())
    yesterday = str(datetime.date.today() - datetime.timedelta(1))
    yesterday = int(time.mktime(datetime.datetime.strptime(yesterday, "%Y-%m-%d").timetuple()))
    req = '121486525133842/insights?period=lifetime&metric=page_fans_country&until=' + str(today) + '&since=' + str(yesterday) + '&pretty=0'
    r = req_facebook(req)
    results = r.json()
    data = []
    i = 0

    while True:
        try:
            time.sleep(random.randint(2,5))
            data.extend(results['data'])
            r = requests.get(results['paging']['next'])
            results = r.json()
            i += 1
        except:
            print('Terminado')
            break

    return data

def generate_map(info):
    df = pd.DataFrame({'Country':list(info.keys()),
                       'Followers':list(info.values())})
    dfData = pd.read_csv('country_iso.csv')  # My Source data
    dfData = dfData[['Alpha-2 code','Alpha-3 code']]
    df = df.merge(dfData, how='inner', left_on=['Country'], right_on=['Alpha-2 code'])
    print(df)
    data = [dict(
        type='choropleth',
        locations=df['Alpha-3 code'],
        z=df['Followers'],
        text=df['Alpha-3 code'],
        colorscale=[[0, "rgb(172, 10, 5)"], [0.35, "rgb(190, 60, 40)"], [0.5, "rgb(245, 100, 70)"], \
                    [0.6, "rgb(245, 120, 90)"], [0.7, "rgb(247, 137, 106)"], [1, "rgb(220, 220, 220)"]],
        autocolorscale=False,
        reversescale=True,
        marker=dict(
            line=dict(
                color='rgb(180,180,180)',
                width=0.5
            )),
        colorbar=dict(
            tickprefix='$',
            title='Followers per country'),
    )]

    layout = dict(
        title='Followers of your Facebook page<br>Source:\
                <a href="https://www.facebook.com/rojoanteojo">\
                Rojo Anteojo</a>',
        geo=dict(
            showframe=False,
            showcoastlines=False,
            projection=dict(
                type='Mercator'
            )
        )
    )

    fig = dict(data=data, layout=layout)
    py.plot(fig, filename='d3-world-map')

data = get_fb_data()

info = data[0]['values'][0]['value']


generate_map(info)
