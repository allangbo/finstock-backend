import boto3
import io
import json
import joblib
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from sklearn.preprocessing import MinMaxScaler
from boto3.dynamodb.conditions import Key

def cos_encode(x, max_val):
    return np.cos(x * (2 * np.pi / max_val))

def load_from_s3(bucket, key):
    s3 = boto3.client('s3')
    with io.BytesIO() as f:
        s3.download_fileobj(Bucket=bucket, Key=key, Fileobj=f)
        f.seek(0)
        obj = joblib.load(f)
    return obj

def handler(event, context):
    # Verifica se o parametro ticker esta presente
    if 'ticker' not in event:
        print("Erro: Parametro 'ticker' eh obrigatorio.")
        return {
            'statusCode': 400,
            'body': json.dumps("Erro: Parametro 'ticker' nao fornecido.")
        }

    ticker = event['ticker']
    x = int(event.get('x', 1))  # Numero de dias para previsao futura com default 1

    try:
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
            print(f"Nenhum dado encontrado para o ticker {ticker}")
            return {
                'statusCode': 404,
                'body': json.dumps(f"Nenhum dado encontrado para o ticker {ticker}")
            }

        df = pd.DataFrame(data)
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

        # Normalizacaoo dos dados de entrada
        X_scaled = scaler_X.transform(X)

        # Fazer previsoes em lote
        predicted_scaled_batch = model.predict(X_scaled)
        predicted_prices = scaler_y.inverse_transform(predicted_scaled_batch).flatten()

        result = []
        for index, predicted_price in enumerate(predicted_prices):
            result.append({
                'Date': df.iloc[index]['Date'].strftime('%Y-%m-%d'),
                'Ticker': ticker,
                'ClosePrice': df.iloc[index]['ClosePrice'],
                'Prediction': predicted_price
            })

        # Adicionar previsões futuras
        last_date = df.iloc[-1]['Date']
        future_inputs = X_scaled[-1].copy()
        for i in range(1, x + 1):
            future_date = last_date + timedelta(days=i)
            future_inputs[1] = cos_encode(future_date.day, 31)
            future_inputs[2] = cos_encode(future_date.month, 12)
            future_inputs[3] = cos_encode(future_date.year, 2023)
            predicted_scaled = model.predict(future_inputs.reshape(1, -1))
            predicted_price = scaler_y.inverse_transform(predicted_scaled)[0][0]

            result.append({
                'Date': future_date.strftime('%Y-%m-%d'),
                'Ticker': ticker,
                'Prediction': predicted_price
            })

        print("Previsao concluida com sucesso.")
        return {
            'statusCode': 200,
            'body': json.dumps(result)
        }
    except Exception as e:
        print(f"Erro ao processar a previsao: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps(f"Erro interno: {e}")
        }
