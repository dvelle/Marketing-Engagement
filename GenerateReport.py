# Author: David Betancur Sánchez
# Created on 18/04/2018

import pandas as pd
import plotly.plotly as py
import plotly.graph_objs as go
import requests
import time
import random
from tkinter import filedialog
from tkinter import *

token = 'token'
desde = '2018-04-01'
hasta = '2018-04-13'


def req_facebook(req):
    print()
    r = requests.get("https://graph.facebook.com/v2.12/" + req, {'access_token' : token})
    return r
def get_insta_data():
    req = '17841406251079989/media?fields=like_count,comments_count,caption,ig_id,media_url,timestamp,permalink'
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
def get_fb_data():
    req = 'me/feed?fields=comments.limit(1).summary(true),likes.limit(1).summary(true),shares,permalink_url'
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
def likes_comments_reaches_insta():
    data = get_insta_data()

    i = 0
    reaches = [None]*len(data)
    comments = [None]*len(data)
    likes = [None]*len(data)
    engagement = [None]*len(data)
    post_url = [None] * len(data)
    date = [None]*len(data)

    for each_post in data:
        comments[i] = each_post['comments_count']
        likes[i] = each_post['like_count']
        post_url[i] = each_post['permalink']
        date[i] = each_post['timestamp'][0:10]
        req = each_post['id'] + '/insights?metric=reach'
        r = req_facebook(req)
        info = r.json()
        reach = info['data'][0]['values'][0]['value']
        reaches[i] = reach

        if reaches[i] == 0:
            engagement[i] = 0
            print('El alcance del post es cero, por lo tanto el engagement se pone en 0')
        else:
            engagement[i] = (likes[i] + (2 * comments[i])) / reaches[i]
        i += 1

    return likes,comments,reaches,engagement,post_url,date
def likes_comments_reaches_fb():
    data = get_fb_data()

    i = 0
    reaches = [None]*len(data)
    comments = [None]*len(data)
    likes = [None]*len(data)
    shares = [None]*len(data)
    engagement = [None]*len(data)
    post_url = [None] * len(data)
    date = [None]*len(data)

    for each_post in data:
        comments[i] = each_post['comments']['summary']['total_count']
        likes[i] = each_post['likes']['summary']['total_count']

        try:
            shares[i] = each_post['shares']['count']
        except:
            shares[i] = 0

        post_url[i] = each_post['permalink_url']

        # =======Esta parte es para sacar la fecha unicamente====
        req = each_post['id']
        r = req_facebook(req)
        info = r.json()
        date[i] = info['created_time'][0:10]
        # =========================================================

        # =========Aqui se sacan los alcances por post ==================
        req = each_post['id'] + '/insights?metric=post_impressions_unique'
        r = req_facebook(req)
        info = r.json()
        reach = info['data'][0]['values'][0]['value']
        reaches[i] = reach
        # ================================================================
        # ===============Engagement=====================================
        if reaches[i] == 0:
            engagement[i] = 0
            print('El alcance del post es cero, por lo tanto el engagement se pone en 0')
        else:
            engagement[i] = (likes[i] + (2*comments[i]) + (2*shares[i])) / reaches[i]
        i += 1

    return likes,comments,shares,reaches,engagement,post_url,date
def generate_instagram_df(folder_selected):
    likes, comments, reaches, engagement, post_url, date = likes_comments_reaches_insta()
    data = {'likes': likes, 'comments': comments, 'reaches': reaches, 'engagements': engagement, 'post_url': post_url,
            'date': date}
    df = pd.DataFrame.from_dict(data)
    df.fillna(value=0, inplace=True)
    nombre = folder_selected + '/Insta_Engagement.csv'
    df.to_csv(nombre)
    return df
def generate_facebook_df(folder_selected):
    likes, comments, shares, reaches, engagement, post_url, date = likes_comments_reaches_fb()
    data = {'likes': likes, 'comments': comments, 'shares': shares, 'reaches': reaches, 'engagements': engagement,
            'post_url': post_url, 'date': date}
    df = pd.DataFrame.from_dict(data)
    df.fillna(value=0, inplace=True)
    nombre = folder_selected + '/Facebook_Engagement.csv'
    df.to_csv(nombre)
    return df
def slice_df(desde, hasta, df_fb, df_insta):

    mask_fb = (df_fb['date'] > desde) & (df_fb['date'] <= hasta)
    df_fb_slice = df_fb.loc[mask_fb]
    mask_insta = (df_insta['date'] > desde) & (df_insta['date'] <= hasta)
    df_insta_slice = df_insta.loc[mask_insta]

    return df_fb_slice, df_insta_slice
def generate_engagement_plot_url(df,num):
    # num es el numero de la grafica
    trace1 = go.Bar(
        x='Post ' + df.index.map(str) + ' del ' + df['date'],
        y=df['engagements'],
        xaxis='x2',
        yaxis='y2',
        marker=dict(color='rgb(250,0,0)', line=dict(color='rgb(0,0,0)',width=1.5,))
    )
    data = [trace1]
    layout = go.Layout(
        title='Engagement por post',xaxis=dict(domain=[0, 0.45]),yaxis=dict(domain=[0, 0.45],)
     )

    fig = go.Figure(data=data, layout=layout)
    filename = 'file' + str(num) + '.html'
    plot_url = py.plot(fig, filename=filename)
    return plot_url
def generate_matrix(df_f):
    by_likes = list(df_f.sort_values(by=['likes'], axis=0, ascending=False).head(n=3)['post_url'])
    by_comments = list(df_f.sort_values(by=['comments'], axis=0, ascending=False).head(n=3)['post_url'])
    by_shares = list(df_f.sort_values(by=['shares'], axis=0, ascending=False).head(n=3)['post_url'])
    by_engagement = list(df_f.sort_values(by=['engagements'], axis=0, ascending=False).head(n=3)['post_url'])

    likes_html = [  '''<p><a href="''' + e + '''"><img border="0" alt="W3Schools" src=
                        "http://www.clker.com/cliparts/Y/m/I/5/C/V/red-ball-md.png" width="100" height=
                        "100" class="center"></a></p>''' for e in by_likes]

    comments_html = ['''<p><a href="''' + e + '''"><img border="0" alt="W3Schools" src=
                            "http://www.clker.com/cliparts/Y/m/I/5/C/V/red-ball-md.png" width="100" height=
                            "100" class="center"></a></p>''' for e in by_comments]

    shares_html = ['''<p><a href="''' + e + '''"><img border="0" alt="W3Schools" src=
                            "http://www.clker.com/cliparts/Y/m/I/5/C/V/red-ball-md.png" width="100" height=
                            "100" class="center"></a></p>''' for e in by_shares]

    engagements_html = ['''<p><a href="''' + e + '''"><img border="0" alt="W3Schools" src=
                            "http://www.clker.com/cliparts/Y/m/I/5/C/V/red-ball-md.png" width="100" height=
                            "100" class="center"></a></p>''' for e in by_engagement]

    matrix_html = '''<html>
<style>
.row {
    display: -ms-flexbox; /* IE 10 */
    display: flex;
    -ms-flex-wrap: wrap; /* IE 10 */
    flex-wrap: wrap;
    padding: 0 4px;
}

.column {
    -ms-flex: 15%; /* IE 10 */
    flex: 15%;
    padding: 0 4px;
}

</style>

<!-- Header -->
<div class="header" id="myHeader">
  <h1>Image Grid</h1>
</div>

<!-- Photo Grid -->
<div class="row"> 

    <div class="column">
  	<h1>Position</h1>
	<p><img src="https://cdn.pixabay.com/photo/2015/04/04/19/13/one-706897_960_720.jpg" width="100" height="100" class="center"></p>
    <p><img src="https://cdn.pixabay.com/photo/2015/04/04/19/13/two-706896_960_720.jpg" width="100" height="100" class="center"></p>
    <p><img src="https://cdn.pixabay.com/photo/2015/04/04/19/13/three-706895_960_720.jpg" width="100" height="100" class="center"></p>
	</div><div class="column">
  	<h1>Likes</h1>''' + likes_html[0] + likes_html[1] + likes_html[2] + '''  </div>

  <div class="column">
  	<h1>Comments</h1>''' + comments_html[0] + \
                  comments_html[1] + comments_html[2] + '''</div>

    <div class="column">
  	<h1>Shares</h1>''' + shares_html[0] + shares_html[1] + shares_html[2] +\
                  '''</div><div class="column"><h1>Engagement</h1>''' + engagements_html[0] + engagements_html[1] +\
                  engagements_html[2]+ '''</div></div>'''

    return matrix_html

def generate_html(url_fb, url_insta, df_f, df_i, folder_selected):
    df_f_orden = df_f.sort_values(by=['likes'], axis=0, ascending=False)
    df_i_orden = df_i.sort_values(by=['likes'], axis=0, ascending=False)
    first_3_f = list(df_f_orden.head(n=3)['post_url'])
    first_3_i = list(df_i_orden.head(n=3)['post_url'])
    print(first_3_f)
    print(first_3_i)
    matrix_html = generate_matrix(df_f)
    html_string = '''
    <html>

        <head>

            <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.1/css/bootstrap.min.css">
            <style>body{ margin:0 100; background:whitesmoke; }</style>
            
            <script async defer src="http://www.instagram.com/embed.js"></script>
            <title> Informe '''+ desde + ''' - ''' + hasta + ''' </title>
        </head>
        <body>
            <h1> Informe '''+ desde + ''' - ''' + hasta + ''' </h1>
            <img src="https://i2.wp.com/rojoanteojo.com/wp-content/uploads/2018/02/cropped-Rojo-Anteojo_Color_SM.png?fit=242%2C250" alt="Rojo Anteojo">
            <img src="https://www.python.org/static/opengraph-icon-200x200.png" alt="Python">

            <!-- *** Instagram *** --->
            <h2>Instagram</h2>
            <iframe width="1000" height="450" frameborder="0" seamless="seamless" scrolling="yes" \
            src="''' + url_insta + '''.embed?width=800&height=450"></iframe>
            <br><br>


            <img src="https://cdn.pixabay.com/photo/2015/04/04/19/13/one-706897_960_720.jpg" alt="Puesto 2 Instagram" width="400" height="400" style="float: left; width: 30%; margin-right: 1%; margin-bottom: 0.5em;">
            <blockquote class="instagram-media" data-instgrm-captioned data-instgrm-permalink="''' + first_3_i[0] + '''" style="float: left; width: 30%; margin-right: 1%; margin-bottom: 0.5em;"></blockquote> 


            <br><p style="clear: both;">

            <img src="https://cdn.pixabay.com/photo/2015/04/04/19/13/two-706896_960_720.jpg" alt="Puesto 2 Instagram" width="400" height="400" style="float: left; width: 30%; margin-right: 1%; margin-bottom: 0.5em;">
            <blockquote class="instagram-media" data-instgrm-captioned data-instgrm-permalink="''' + first_3_i[1] \
                  + '''" style="float: left; width: 30%; margin-right: 1%; margin-bottom: 0.5em;"></blockquote> 


            <br><p style="clear: both;">

            <img src="https://cdn.pixabay.com/photo/2015/04/04/19/13/three-706895_960_720.jpg" alt="Puesto 2 Instagram" width="400" height="400" style="float: left; width: 30%; margin-right: 1%; margin-bottom: 0.5em;">
            <blockquote class="instagram-media" data-instgrm-captioned data-instgrm-permalink="''' + first_3_i[2] + '''" style="float: left; width: 30%; margin-right: 1%; margin-bottom: 0.5em;"></blockquote> 


            <br><p style="clear: both;">

            <!-- *** Facebook *** --->
            <h2>Facebook</h2>
            <iframe width="1000" height="450" frameborder="0" seamless="seamless" scrolling="yes" \
            src="''' + url_fb + '''.embed?width=800&height=450"></iframe>
            <br><br>''' + matrix_html + '''

        </body>
    </html>'''

    nombre = folder_selected + '/Reporte.html'
    f = open(nombre, 'w')
    f.write(html_string)
    f.close()


def Report():
    df_fb = generate_facebook_df(folder_selected)
    print('Facebook DF Generated')
    df_insta = generate_instagram_df(folder_selected)
    print('Instagram DF Generated')

    df_f, df_i = slice_df(desde, hasta, df_fb, df_insta)
    fb_plot_url = generate_engagement_plot_url(df_f, 1)
    insta_plot_url = generate_engagement_plot_url(df_i, 2)

    generate_html(fb_plot_url, insta_plot_url, df_f, df_i, folder_selected)

root = Tk()
root.withdraw()
folder_selected = filedialog.askdirectory(title='Escoja el Directorio donde se guararan los archivos')
Report()

