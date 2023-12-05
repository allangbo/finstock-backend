import boto3
import csv
import io
import json
from botocore.exceptions import ClientError
from google_news_feed import GoogleNewsFeed
from boto3.dynamodb.conditions import Key
from datetime import datetime, timedelta
import pytz

def handler(event, context):
    print("Evento recebido:", event)

    # Verifica se a requisição é para buscar e salvar noticias
    save = bool(event.get('save_news', False))
    if save:
        return handle_news_fetching(event, context)

    # Caso contrário, assume que é uma requisição GET para retornar notícias
    return handle_news_retrieval(event)

def handle_news_fetching(event, context):
    print("Iniciando a busca e salvamento de notícias")

    bucket_name = 'companies-ticker'
    csv_file_name = event.get('csv_file_name')
    if not csv_file_name:
        print("Nome do arquivo CSV não fornecido.")
        return {"status": "Nome do arquivo CSV não fornecido"}

    time_filter = event.get('time_filter', None)  # Exemplo: None ou '60m'

    s3_client = boto3.client('s3')
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('StockNews')

    gnf = GoogleNewsFeed(language='pt', country='BR', resolve_internal_links=True, run_async=False)

    # Definir a data/hora de início para o filtro de tempo se time_filter for fornecido
    time_threshold = None
    if time_filter:
        time_delta = int(time_filter.rstrip('m'))
        time_threshold = datetime.now(pytz.utc) - timedelta(minutes=time_delta)

    try:
        csv_object = s3_client.get_object(Bucket=bucket_name, Key=csv_file_name)
        csv_content = csv_object['Body'].read().decode('utf-8')
    except ClientError as e:
        print("Erro ao acessar o arquivo CSV no S3:", e)
        return {"status": "Erro ao acessar o arquivo CSV no S3"}

    reader = csv.reader(io.StringIO(csv_content))
    queries = [row[0] for row in reader]

    for query in queries:
        results = gnf.query(query)

        # Contar as notícias encontradas
        news_count = 0

        for article in results:
            # Verifica se a data da notícia está dentro do limite de tempo
            if time_threshold is None or article.pubDate >= time_threshold:
                # Formatar a data para string no formato ISO 8601 para salvar no DynamoDB
                published_date_str = article.pubDate.isoformat()

                item = {
                    'Ticker': query.split(':')[-1],
                    'PublishedDate#Source': published_date_str + '#' + article.source,
                    'Title': article.title,
                    'URL': article.link,
                    'Description': article.description,
                    'Source': article.source
                }
                try:
                    table.put_item(Item=item)
                    news_count += 1 
                except ClientError as e:
                    print("Erro ao salvar o item no DynamoDB:", e)
                
        print(f"Quantidade de notícias encontradas para a consulta '{query}': {news_count}")

    print("Busca e salvamento de notícias completados")
    return {"status": "Completo"}

def handle_news_retrieval(event):
    print("Iniciando a recuperação de notícias")

    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('StockNews')

    ticker = event['queryStringParameters']['ticker']
    date = event.get('queryStringParameters', {}).get('date', None)

    try:
        if date:
            response = table.query(
                KeyConditionExpression=Key('Ticker').eq(ticker) & Key('PublishedDate#Source').begins_with(date)
            )
        else:
            response = table.query(
                KeyConditionExpression=Key('Ticker').eq(ticker)
            )

        processed_items = []
        for item in response['Items']:
            processed_item = {}

            for key, value in item.items():
                if key != 'PublishedDate#Source':
                    processed_item[key] = value

            processed_item['PublishedDate'] = item['PublishedDate#Source'].split('#')[0]
            
            processed_items.append(processed_item)

        print("Notícias recuperadas com sucesso")
        return {
            'statusCode': 200,
            'body': json.dumps(processed_items),
            'headers': {'Content-Type': 'application/json'}
        }
    except ClientError as e:
        print("Erro ao consultar o DynamoDB:", e)
        return {'statusCode': 500, 'body': json.dumps({"error": "Erro interno"})}


