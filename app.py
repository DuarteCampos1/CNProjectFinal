from flask import Flask, request, render_template, jsonify
import requests
import json
from datetime import datetime

app = Flask(__name__)

# Mapeamento dos nomes das cidades
cities = {
    1010500: "Viana do Castelo",
    1020500: "Braga",
    1030300: "Vila Real",
    1040200: "Bragança",
    1050200: "Porto",
    1060300: "Aveiro",
    1070500: "Coimbra",
    1080500: "Leiria",
    1081505: "Lisboa",
    1090700: "Castelo Branco",
    1090821: "Santarém",
    1100900: "Portalegre",
    1110600: "Lisboa",
    1121400: "Setúbal",
    1131200: "Viseu",
    1141600: "Guarda",
    1151200: "Évora",
    1151300: "Beja",
    1160900: "Faro",
    1171400: "Ponta Delgada",
    1182300: "Funchal",
    2310300: "Madeira",
    2320100: "Porto Santo",
    3420300: "Horta",
    3430100: "Angra do Heroísmo",
    3470100: "Santa Cruz das Flores",
    3480200: "Ponta Delgada (Açores)",
}

direcoes = {
    "N": "Norte",
    "S": "Sul",
    "W": "Oeste",
    "E": "Este",
    "NE": "Nordeste",
    "NW": "Noroeste",
    "SE": "Sudeste",
    "SW": "Sudoeste",
}

wind_speed_classes = {
    0: "Calmo",
    1: "Fraco",
    2: "Moderado",
    3: "Forte",
    4: "Muito forte",
    5: "Tempestuoso"
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process_city', methods=['POST'])
def process_city():
    url = "https://api.ipma.pt/open-data/forecast/meteorology/cities/daily/hp-daily-forecast-day0.json"
    response = requests.get(url)
    data = response.json()
    city_id = request.form['city']
    forecast_data = next((item for item in data['data'] if str(item['globalIdLocal']) == city_id), None)
    city_name = cities.get(int(city_id), "Cidade desconhecida")
    tMax = forecast_data['tMax']
    tMin = forecast_data['tMin']
    predWindDir = direcoes.get(forecast_data['predWindDir'], "Direção desconhecida")
    wind_speed_class = wind_speed_classes.get(forecast_data['classWindSpeed'], "Classificação desconhecida")

    pesquisa = {
        "Nome da Cidade": city_name,
        "Temperatura Maxima": tMax,
        "Temperatura Minima": tMin,
        "Direção do vento": predWindDir,
        "Velocidade do vento": wind_speed_class
    }

    # Abrir ou criar o arquivo JSON
    try:
        with open("CNProjeto/json/bd.json", "r", encoding="utf-8") as file:
            data = json.load(file)
    except FileNotFoundError:
        data = []

    # Adicionar a pesquisa ao arquivo JSON
    pesquisa["data_pesquisa"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    data.append(pesquisa)

    with open("CNProjeto/json/bd.json", "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)

    if response.status_code == 200:
        forecastDate = data.get('forecastDate', 'Data não disponível')

        html_response = f'''
        <!DOCTYPE html>
        <html lang="pt-PT">
        <head>
            <meta charset="UTF-8">
            <title>Previsão do Tempo para {city_name}</title>
        </head>
        <body>
            <h1>Previsão do Tempo para {city_name}</h1>
            <p>Data da Previsão: {forecastDate}</p>
            <p>Temperatura Máxima: {tMax}°C</p>
            <p>Temperatura Mínima: {tMin}°C</p>
            <p>Direção do Vento: {predWindDir}</p>
            <p>Velocidade do Vento: {wind_speed_class}</p>
            <form action="/">
                <button type="submit">Voltar ao Formulário</button>
            </form>
        </body>
        </html>
        '''
    else:
        html_response = f'''
        <!DOCTYPE html>
        <html lang="pt-PT">
        <head>
            <meta charset="UTF-8">
            <title>Erro</title>
        </head>
        <body>
            <h1>Erro</h1>
            <p>Erro ao acessar a API: {response.status_code}</p>
            <form action="/">
                <button type="submit">Voltar ao Formulário</button>
            </form>
        </body>
        </html>
        '''

    return render_template_string(html_response)

@app.route('/all_searches', methods=['GET'])
def all_searches():
    try:
        with open("CNProjeto/json/bd.json", "r", encoding="utf-8") as file:
            data = json.load(file)
    except FileNotFoundError:
        data = []

    html_response = '''
    <!DOCTYPE html>
    <html lang="pt-PT">
    <head>
        <meta charset="UTF-8">
        <title>Todas as Pesquisas</title>
    </head>
    <body>
        <h1>Todas as Pesquisas</h1>
        <ul>
    '''
    for search in data:
        html_response += f"<li>{search}</li>"
    html_response += '''
        </ul>
        <form action="/">
            <button type="submit">Voltar ao Formulário</button>
        </form>
    </body>
    </html>
    '''
    return render_template_string(html_response)

@app.route('/search_by_date', methods=['POST'])
def search_by_date():
    date = request.form['date']
    try:
        with open("CNProjeto/json/bd.json", "r", encoding="utf-8") as file:
            data = json.load(file)
    except FileNotFoundError:
        data = []

    filtered_data = [search for search in data if search["data_pesquisa"].startswith(date)]

    html_response = '''
    <!DOCTYPE html>
    <html lang="pt-PT">
    <head>
        <meta charset="UTF-8">
        <title>Pesquisas por Data</title>
    </head>
    <body>
        <h1>Pesquisas por Data</h1>
        <ul>
    '''
    for search in filtered_data:
        html_response += f"<li>{search}</li>"
    html_response += '''
        </ul>
        <form action="/">
            <button type="submit">Voltar ao Formulário</button>
        </form>
    </body>
    </html>
    '''
    return render_template_string(html_response)

@app.route('/search_by_city', methods=['POST'])
def search_by_city():
    city_name = request.form['city_name']
    try:
        with open("CNProjeto/json/bd.json", "r", encoding="utf-8") as file:
            data = json.load(file)
    except FileNotFoundError:
        data = []

    filtered_data = [search for search in data if search["Nome da Cidade"] == city_name]

    html_response = '''
    <!DOCTYPE html>
    <html lang="pt-PT">
    <head>
