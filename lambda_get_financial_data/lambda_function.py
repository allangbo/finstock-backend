import json
import boto3
import pandas as pd
from io import StringIO

def handler(event, context):
    # Parâmetros recebidos pela função
    ticker = event['queryStringParameters']['ticker']
    input_date = event['queryStringParameters']['date']

    print(f"Ticker: {ticker}, Data: {input_date}")

    # Nome do bucket e arquivo no S3
    bucket_name = 'companies-ticker'
    file_key = 'stocks_financial_data.csv'

    # Cliente do S3
    s3_client = boto3.client('s3')

    try:
        # Obtendo o arquivo do S3
        response = s3_client.get_object(Bucket=bucket_name, Key=file_key)
        print("Arquivo obtido com sucesso do S3.")

        # Lendo o conteúdo do arquivo como um DataFrame
        content = response['Body'].read().decode('utf-8')
        df = pd.read_csv(StringIO(content))

        # Convertendo a coluna 'Date' para datetime, se necessário
        df['Date'] = pd.to_datetime(df['Date'])
        input_date_parsed = pd.to_datetime(input_date)

        # Filtrando os dados com base no ticker e garantindo que a data não esteja no futuro
        filtered_data = df[(df['Ticker'] == ticker) & (df['Date'] <= input_date_parsed)]

        if not filtered_data.empty:
            # Encontrando a entrada com a data mais próxima no passado
            closest_date_data = filtered_data.loc[filtered_data['Date'].idxmax()]

            # Convertendo Timestamp para string
            closest_date_data['Date'] = closest_date_data['Date'].strftime('%Y-%m-%d')

            print("Dados encontrados para a data mais próxima no passado.")
            return {
                'statusCode': 200,
                'body': json.dumps(closest_date_data.to_dict())
            }
        else:
            print("Nenhum dado encontrado para o ticker fornecido na data especificada ou anterior.")
            return {
                'statusCode': 404,
                'body': json.dumps("Nenhum dado encontrado para o ticker fornecido na data especificada ou anterior.")
            }

    except Exception as e:
        print(f"Erro: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps(str(e))
        }
