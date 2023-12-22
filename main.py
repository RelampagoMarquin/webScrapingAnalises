from textblob import TextBlob
import requests
from bs4 import BeautifulSoup
from dash import Dash, html, dcc, dash_table, callback, Output, Input
import pandas as pd
import datetime
import numpy as np
import plotly.express as px
import plotly.graph_objs as go
from collections import deque

app = Dash(__name__)

## url base
url = "http://quotes.toscrape.com/page/"

author_frases = pd.DataFrame({
    "Author": [],
    "Frase": [],
    "Polarity": [],
})

## buscando os dados
for i in range(10):
    urlPage = url + str(i+1)
    response = requests.get(urlPage)
    if response.status_code == 200:
        html_content = response.content
        soup = BeautifulSoup(html_content, 'html.parser')
        cards = soup.find_all('div', class_="quote")
        for card in cards:
            a = card.findChildren('small', class_ = 'author')
            author = a[0].text
            f = card.findChildren('span', class_ = 'text')
            frase = f[0].text
            analysis = TextBlob(frase)
            polarity = analysis.sentiment.polarity
            line = {"Author": author, "Frase": frase, "Polarity": polarity}
            author_frases = author_frases._append(line, ignore_index=True)



## layout
# y = range=[-1, 1]
author_frases_pivot = pd.pivot_table(author_frases, index=["Author"], values=['Polarity'], aggfunc='mean')

author_frases_pivot = author_frases_pivot.reset_index()
fig = px.scatter(author_frases_pivot, x="Author", y="Polarity", range_y=[-1, 1], color="Author")

pesimistAuthor = author_frases_pivot.sort_values('Polarity', ascending=False).iloc[-1]['Author']
otimisticAuthor = author_frases_pivot.sort_values('Polarity', ascending=True).iloc[-1]['Author']
mostPositiveFrases = author_frases.sort_values('Polarity', ascending=True)
mostNegativeFrases = author_frases.sort_values('Polarity', ascending=False)
positiveFrase = mostPositiveFrases.iloc[-1]['Frase']
negativeFrase = mostNegativeFrases.iloc[-1]['Frase']
negativeFraseAuthor = mostNegativeFrases.iloc[-1]['Author']
positiveFraseAuthor = mostPositiveFrases.iloc[-1]['Author']

app.layout = html.Div(
    children=[
        html.Div(children=[
            html.H1(children='Polaridade das Frases dos Autores'),
            dcc.Graph(
                id="full-polarities", figure=fig
            )
        ]),

        html.Div(children=[
            html.H3(children='Autor mais Negativo'),
            html.P(children=pesimistAuthor)
            # dcc.Graph(
            #     id="full-polarities", figure=fig
            # )
        ]),
        html.Div(children=[
            html.H3(children='Autor mais Positivo'),
            html.P(children=otimisticAuthor)
            # dcc.Graph(
            #     id="full-polarities", figure=fig
            # )
        ]),
        html.Div(children=[
            html.H3(children='Frase mais Positiva'),
            html.P(children=positiveFrase),
            html.Small(children=positiveFraseAuthor)
        ]),
        html.Div(children=[
            html.H3(children='Frase mais Negativa'),
            html.P(children=negativeFrase),
            html.Small(children=negativeFraseAuthor)
        ]),
        html.Div(children=[
            html.H3(children='Tabela de Autores, Frases e Polaridade'),
            dash_table.DataTable(data=author_frases.to_dict("records"), page_size=10),
        ]),

    ])

if __name__ == '__main__':
    app.run(debug=True)