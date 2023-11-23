import boto3
import csv
import yfinance as yf
import json
from io import StringIO
from datetime import datetime, timedelta

def handler(event, context):
    # Recebe parâmetros do evento
    num_dias = event.get('num_dias')
    start_date = event.get('start_date')
    end_date = event.get('end_date')

    # Verifica se os parâmetros estão de acordo com as regras
    if num_dias and (start_date or end_date):
        raise ValueError("Defina ou num_dias ou um intervalo de datas, mas não ambos.")

    if start_date and end_date:
        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d')
        if (end - start).days > 30:
            raise ValueError("O intervalo de datas não pode ser superior a 30 dias.")

    # Determina o período para download dos dados
    if start_date and end_date:
        period = None
        download_params = {'start': start_date, 'end': end_date}
    else:
        period = num_dias or '1d'  # Valor padrão é 1 dia
        download_params = {'period': period}

    print(f"Coletando dados para o período: {period or f'{start_date} até {end_date}'}")

    # Criar cliente S3 para acessar o bucket e o arquivo CSV
    s3_client = boto3.client('s3')
    bucket_name = 'companies-ticker'
    file_key = 'companies_ticker_b3.csv'
    
    # Ler o arquivo CSV do S3
    csv_obj = s3_client.get_object(Bucket=bucket_name, Key=file_key)
    body = csv_obj['Body']
    csv_string = body.read().decode('utf-8')

    # Criar cliente DynamoDB
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('StockPrices')

    # Iterar sobre os tickers e coletar os dados
    for row in csv.reader(StringIO(csv_string)):
        ticker = row[0]
        data = yf.download(ticker + '.SA', progress=False, **download_params)
        if not data.empty:
            for index, row in data.iterrows():
                date = index.strftime('%Y-%m-%d')
                open_price = row['Open']
                close_price = row['Close']
                volume = row['Volume']

                print(f"Ticker: {ticker}, Date: {date}, Open: {open_price}, Close: {close_price}, Volume: {volume}")

                # Inserir no DynamoDB
                table.put_item(
                    Item={
                        'Ticker': ticker,
                        'Date': date,
                        'OpenPrice': str(open_price),
                        'ClosePrice': str(close_price),
                        'Volume': str(volume)
                    }
                )

    return {
        'statusCode': 200,
        'body': json.dumps('Dados coletados e inseridos com sucesso!')
    }
