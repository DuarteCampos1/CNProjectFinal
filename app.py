import json
import os
from datetime import datetime

import requests
from flask import Flask, request, render_template

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
    return render_template("index.html")


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
    preWindDir = direcoes.get(forecast_data['predWindDir'], "Direção desconhecida")
    wind_speed_class = wind_speed_classes.get(forecast_data['classWindSpeed'], "Classificação desconhecida")

    pesquisa = {
        "Nome da Cidade": city_name,
        "Temperatura Maxima": tMax,
        "Temperatura Minima": tMin,
        "Direção do vento": preWindDir,
        "Velocidade do vento": wind_speed_class,
        "data_pesquisa": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    # Garantir que o diretório json exista
    os.makedirs("json", exist_ok=True)

    # Abrir ou criar o arquivo JSON
    try:
        with open("json/bd.json", "r", encoding="utf-8") as file:
            data = json.load(file)
    except FileNotFoundError:
        data = []

    # Adicionar a pesquisa ao arquivo JSON
    data.append(pesquisa)

    with open("json/bd.json", "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)

    if response.status_code == 200:
        return render_template("city_result.html", city_name=city_name, forecast=forecast_data, preWindDir=preWindDir,
                               wind_speed_class=wind_speed_class)
    else:
        return render_template("error.html", error_code=response.status_code)


@app.route('/all_searches', methods=['GET'])
def all_searches():
    try:
        with open("json/bd.json", "r", encoding="utf-8") as file:
            data = json.load(file)
    except FileNotFoundError:
        data = []

    page = request.args.get('page', 1, type=int)
    per_page = 6  # Número de resultados por página
    total_results = len(data)
    total_pages = (total_results + per_page - 1) // per_page  # Cálculo do total de páginas

    start = (page - 1) * per_page
    end = start + per_page
    results_to_show = data[start:end]

    return render_template(
        "search_results.html",
        searches=results_to_show,
        total_pages=total_pages,
        current_page=page,
        page_title="Todos os Resultados",
        criteria=""
    )


@app.route('/search_by_date', methods=['POST', 'GET'])
def search_by_date():
    if request.method == 'POST':
        date = request.form['date']
    else:
        date = request.args.get('date')

    try:
        with open("json/bd.json", "r", encoding="utf-8") as file:
            data = json.load(file)
    except FileNotFoundError:
        data = []

    filtered_data = [search for search in data if search["data_pesquisa"].startswith(date)]

    # Contador de pesquisas por cidade
    city_counts = {}
    unique_results = []
    seen_cities = set()

    for search in filtered_data:
        city = search["Nome da Cidade"]
        if city in city_counts:
            city_counts[city] += 1
        else:
            city_counts[city] = 1
            if city not in seen_cities:
                unique_results.append(search)
                seen_cities.add(city)

    # Paginação
    page = request.args.get('page', 1, type=int)
    per_page = 6
    total_results = len(unique_results)
    total_pages = (total_results + per_page - 1) // per_page

    start = (page - 1) * per_page
    end = start + per_page
    results_to_show = unique_results[start:end]

    return render_template(
        "search_results.html",
        searches=results_to_show,
        total_pages=total_pages,
        current_page=page,
        criteria=f"Data: {date}",
        city_counts=city_counts,
        page_title=f"Resultados da Pesquisa no Dia: {date}",
        date=date,  # Passando o valor de date para o template
        is_date_search=True  # Indicando que a pesquisa é por data
    )


@app.route('/search_by_city', methods=['POST', 'GET'])
def search_by_city():
    if request.method == 'POST':
        city_name = request.form['city_name']
    else:
        city_name = request.args.get('city_name')

    try:
        with open("json/bd.json", "r", encoding="utf-8") as file:
            data = json.load(file)
    except FileNotFoundError:
        data = []

    filtered_data = [search for search in data if search["Nome da Cidade"] == city_name]

    # Paginação
    page = request.args.get('page', 1, type=int)
    per_page = 6
    total_results = len(filtered_data)
    total_pages = (total_results + per_page - 1) // per_page

    start = (page - 1) * per_page
    end = start + per_page
    results_to_show = filtered_data[start:end]

    return render_template(
        "search_results.html",
        searches=results_to_show,
        total_pages=total_pages,
        current_page=page,
        criteria=f"Cidade: {city_name}",
        page_title=f"Resultados da Pesquisa na Cidade: {city_name}",
        city_name=city_name,
        is_date_search=False  # Indicando que a pesquisa não é por data
    )


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))