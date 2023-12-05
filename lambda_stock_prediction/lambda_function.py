import boto3
import io
import json
import joblib
import pandas as pd
import numpy as np
from datetime import datetime
import traceback  # Importe o módulo traceback
from sklearn.preprocessing import MinMaxScaler
from boto3.dynamodb.conditions import Key
from pandas import to_datetime

# Função para codificar data em formato cosseno
def cos_encode(value, max_val):
    return np.cos(value * (2 * np.pi / max_val))

# Função para carregar objetos do S3
def load_from_s3(bucket, key):
    s3 = boto3.client('s3')
    with io.BytesIO() as f:
        s3.download_fileobj(Bucket=bucket, Key=key, Fileobj=f)
        f.seek(0)
        obj = joblib.load(f)
    return obj

# Handler da função Lambda
def handler(event, context):
    try:
        # Recebendo parâmetros via método GET
        params = event['queryStringParameters']

        # Verifica se os parâmetros necessários estão presentes
        if 'ticker' not in params:
            return {
                'statusCode': 400,
                'body': json.dumps("Erro: Parâmetro 'ticker' não fornecido.")
            }

        if 'initial_date' not in params:
            return {
                'statusCode': 400,
                'body': json.dumps("Erro: Parâmetro 'initial_date' não fornecido.")
            }

        ticker = params['ticker']
        initial_date = params['initial_date']
        forecast_days = int(params.get('forecast_days', 1))

        # Validar e converter initial_date
        initial_date = datetime.strptime(initial_date, '%Y-%m-%d')

        # Conectar ao DynamoDB e buscar dados
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table('StockPrices')
        response = table.query(
            KeyConditionExpression=Key('Ticker').eq(ticker),
            ScanIndexForward=True
        )

        # Processar os dados
        data = response['Items']
        if not data:
            return {
                'statusCode': 404,
                'body': json.dumps(f"Nenhum dado encontrado para o ticker {ticker}")
            }

        df = pd.DataFrame(data)
        df['Date'] = pd.to_datetime(df['Date'])

        # Filtrar dados até initial_date
        original_df = df.copy()
        df = df[df['Date'] < initial_date]

        df['Date'] = pd.to_datetime(df['Date'])
        df['Day'] = df['Date'].dt.day
        df['Month'] = df['Date'].dt.month
        df['Year'] = df['Date'].dt.year
        df['Day_enc'] = df['Day'].apply(cos_encode, max_val=31)
        df['Month_enc'] = df['Month'].apply(cos_encode, max_val=12)
        df['Year_enc'] = df['Year'].apply(cos_encode, max_val=2023)
        X = df[['ClosePrice', 'Day_enc', 'Month_enc', 'Year_enc']].values

        # Carregar scalers e modelo do S3
        scaler_X = load_from_s3('companies-ticker', 'scaler_X.pkl')
        scaler_y = load_from_s3('companies-ticker', 'scaler_y.pkl')
        model = load_from_s3('companies-ticker', 'esn_model.pkl')

        # Normalização dos dados de entrada
        X_scaled = scaler_X.transform(X)

        # Fazer previsões em lote
        predicted_scaled_batch = model.predict(X_scaled)
        predicted_prices = scaler_y.inverse_transform(predicted_scaled_batch).flatten()

        result = []
        for index in range(len(predicted_prices) - 1):
            predicted_price = predicted_prices[index]
            data_date = df.iloc[index + 1]['Date']
            result.append({
                'Date': data_date.strftime('%Y-%m-%d'),
                'Ticker': ticker,
                'ClosePrice': df.iloc[index + 1]['ClosePrice'],
                'Prediction': predicted_price
            })

        # Adicionar previsões futuras
        extended_X_scaled = np.array(X_scaled)  # Cria uma cópia de X_scaled
        last_date = df.iloc[-1]['Date']
        last_index = len(predicted_prices) - 2
        last_date_np = np.datetime64(last_date, 'D')

        for i in range(1, forecast_days + 1):
            future_date = np.busday_offset(last_date_np, i, roll='forward')
            future_date_datetime = to_datetime(future_date)  # Converter para datetime

            future_date_str = future_date_datetime.strftime('%Y-%m-%d')

            # Faz a previsao usando todo o extended_X_scaled
            predicted_scaled = model.predict(extended_X_scaled)
            predicted_price = scaler_y.inverse_transform(predicted_scaled)[-1][0]  # Pega a última previsão

            # Antes de fazer o append, imprima a forma de extended_X_scaled para verificar
            print("Shape of extended_X_scaled before append:", extended_X_scaled.shape)

            future_input = np.array([
                [predicted_scaled[-1][0], 
                cos_encode(future_date_datetime.day, 31), 
                cos_encode(future_date_datetime.month, 12), 
                cos_encode(future_date_datetime.year, 2023)]
            ])

            # Verifique se as formas são compatíveis
            print("Shape of future_input:", future_input.shape)

            # Faça o append
            extended_X_scaled = np.append(extended_X_scaled, future_input, axis=0)

            # Verifique a forma após o append
            print("Shape of extended_X_scaled after append:", extended_X_scaled.shape)

            result_entry = {
                'Date': future_date_str,
                'Ticker': ticker,
                'Prediction': predicted_price
            }

             # Verificar se o índice está dentro dos limites do DataFrame
            if last_index + i + 1 < len(original_df):
                result_entry['ClosePrice'] = original_df.iloc[last_index + i + 1]['ClosePrice']

            # Adicionar o dicionário à lista de resultados
            result.append(result_entry)


        print("Processamento concluído com sucesso.")  # Print de sucesso
        return {
            'statusCode': 200,
            'body': json.dumps(result)
        }

    except Exception as e:
        print(f"Erro interno: {e}")
        print(traceback.format_exc())  # Print do stacktrace
        return {
            'statusCode': 500,
            'body': json.dumps(f"Erro interno: {e}")
        }
