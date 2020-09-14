# coding: utf-8
import codecs
import argparse
import datetime
import requests
import unicodedata
from json import dumps
from bs4 import BeautifulSoup
from kafka import KafkaProducer
from requests.exceptions import ConnectionError


def download_html(url, numero_tentativas=2):
    print("Downloading page:", url)
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv: 80.0) Gecko/20100101 Firefox/80.0'
        }
        req = requests.get(url, headers=headers)
        if req.status_code != 200:
            if numero_tentativas > 0:
                print("Impossible to download the page. Error:", req.status_code)
                print("\nTrying again:")
                return download_html(url, numero_tentativas - 1)
            else:
                print("Number of tries exceeded. Error: {}".format(req.status_code))
                html = None
                return html
        return codecs.encode(req.text, 'utf-8').decode()
    except ConnectionError as e:
        print("Download error:", e)
        html = None


def remove_acento(string_velha):
    string_nova = ''.join(caracter for caracter in unicodedata.normalize('NFKD', string_velha)
                          if not unicodedata.combining(caracter))
    return string_nova.replace('-', '').replace('.', '')


def normaliza_string(string_velha):
    return string_velha.replace(' ', '_').replace('/', '').replace('(', '').replace(')', '').lower()


def table_without_header(html_table):
    rows = html_table.find_all('tr')
    values = {}
    for row in rows:
        columns = row.find_all('td')
        for index, column in enumerate(columns):
            if index % 2 == 0:
                for label_field in column.find_all('span'):
                    label = normaliza_string(remove_acento(label_field.text))
            else:
                for data_field in column.find_all('span'):
                    data_raw = data_field
                    data = data_raw.text.replace('\n', '').strip()
                values[label] = remove_acento(data) if data else 'null'
    return values


def table_header(html_table):
    rows = html_table.find_all('tr')
    values = {}
    for row_number, row in enumerate(rows):
        if row_number > 0:
            columns = row.find_all('td')
            for index, column in enumerate(columns):
                if index % 2 == 0:
                    prefix = 'oscilacoes_' if index == 0 else 'indicadores_fundamentalistas_'
                    for label_field in column.find_all('span'):
                        label = normaliza_string(remove_acento(prefix + label_field.text))
                else:
                    for data_field in column.find_all('span'):
                        data_raw = data_field
                        data = data_raw.text.replace('\n', '').strip()
                    values[label] = remove_acento(data) if data else 'null'
    return values


def table_header2(html_table):
    rows = html_table.find_all('tr')
    values = {}
    prefix = 'balanco_patrimonial_'
    for row_number, row in enumerate(rows):
        if row_number > 0:
            columns = row.find_all('td')
            for index, column in enumerate(columns):
                if index % 2 == 0:
                    for label_field in column.find_all('span'):
                        label = normaliza_string(remove_acento(prefix + label_field.text))
                else:
                    for data_field in column.find_all('span'):
                        data_raw = data_field
                        data = data_raw.text.replace('\n', '').strip()
                    values[label] = remove_acento(data) if data else 'null'
    return values


def table_double_header(html_table):
    rows = html_table.find_all('tr')
    values = {}
    for row_number, row in enumerate(rows):
        if row_number > 1:
            columns = row.find_all('td')
            for index, column in enumerate(columns):
                if index % 2 == 0:
                    prefix = '_ultimos_12_meses' if index == 0 else '_ultimos_3_meses'
                    for label_field in column.find_all('span'):
                        label = normaliza_string(remove_acento(label_field.text + prefix))
                else:
                    for data_field in column.find_all('span'):
                        data_raw = data_field
                        data = data_raw.text.replace('\n', '').strip()
                    values[label] = remove_acento(data) if data else 'null'
    return values


def parse_html(html):
    bs = BeautifulSoup(html, "html.parser")
    tables = bs.find_all('table', class_="w728")

    if not tables:
        return None

    process_type = {
        '0': table_without_header,
        '1': table_without_header,
        '2': table_header,
        '3': table_header2,
        '4': table_double_header
    }

    all_data = {'process_date': datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}
    for table_number, table in enumerate(tables):
        # table_id = 'table_'+str(table_number)
        all_data.update(process_type[str(table_number)](table))

    all_data.pop('oscilacoes_') if all_data.get('oscilacoes_') else None
    all_data.pop('indicadores_fundamentalistas_') if all_data.get('indicadores_fundamentalistas_') else None
    all_data.pop('') if all_data.get('') else None
    return all_data


def send_to_kafka(data, host, topic):
    print(data)
    producer = KafkaProducer(bootstrap_servers=[f'{host}:9092'], value_serializer=lambda x: dumps(x).encode('utf-8'))
    producer.send(topic, value=data)
    producer.flush()


def main(stock_code, kafka_host, topic_name):
    url = f'https://www.fundamentus.com.br/detalhes.php?papel={stock_code}'
    html = download_html(url)
    data_from_html = parse_html(html)
    if data_from_html:
        send_to_kafka(data_from_html, kafka_host, topic_name)
    else:
        print(f'Nenhum papel encontrado!')


# import sys; sys.argv=['']; del sys
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--stocks', type=str, help='List of stock code to perform download of data')
    parser.add_argument('-k', '--kafka', type=str, help='IP where your kafka server is running.')
    parser.add_argument('-t', '--topic', type=str, help="A topic to be read from kafka server.")
    args = parser.parse_args()

    STOCK_STRING = args.stocks
    KAFKA_HOST = args.kafka
    KAFKA_TOPIC = args.topic
    STOCK_LIST = STOCK_STRING.split(',')
    # ["PETR4","VALE3","JBSS3","MGLU3","FLRY3","NATU3","ITUB4","ITSA4","RENT3","LREN3","GOLL4"]
    # KAFKA_HOST = '10.142.0.44'
    # KAFKA_TOPIC = 'Stocks'
    for stock_code in STOCK_LIST:
        main(stock_code, KAFKA_HOST, KAFKA_TOPIC)
