# Stock Price Prediction

Este repositório contém uma função Lambda AWS para previsão de preços de ações, utilizando um modelo treinado no Google Colab e integrado com a AWS API Gateway para fornecer dados a um frontend.

## Estrutura do Repositório

├── Dockerfile
├── lambda_function.py
├── requirements.txt
├── pyESN.py

## Descrição da Função Lambda

A função `lambda_function.py` é projetada para realizar previsões de preços de ações baseadas em dados históricos. Ela utiliza um modelo de aprendizado de máquina treinado externamente e armazenado no S3, além de interagir com o DynamoDB para buscar dados.

### Processo de Previsão

1. **Recebimento de Parâmetros**: A função recebe parâmetros via método GET, incluindo o ticker da ação, a data inicial e o número de dias para previsão.

2. **Validação e Conversão de Dados**: Valida e converte a data inicial para o formato adequado.

3. **Busca de Dados no DynamoDB**: Conecta-se ao DynamoDB para buscar dados históricos do ticker especificado.

4. **Preparação dos Dados**: Processa e codifica os dados em formato adequado para o modelo.

5. **Carregamento de Modelos e Scalers do S3**: Carrega o modelo de previsão e os scalers necessários do S3.

6. **Normalização e Previsão**: Normaliza os dados e realiza previsões de preço.

7. **Formatação e Retorno dos Resultados**: Formata os resultados e os retorna via API Gateway.

## Como compilar a imagem Docker e carregá-la no ECR da AWS

1. **Autenticação no AWS ECR**:

aws ecr get-login-password --region <YOUR_REGION> | docker login --username AWS --password-stdin <YOUR_ECR_REPO_URL>

Substitua `<YOUR_REGION>` pela região da AWS em que o ECR foi criado.
Substitua `<YOUR_ECR_REPO_URL>` pela URL do repositório ECR.

2. **Construir a imagem Docker**:

docker build -t stock-prediction .

3. **Taggear a imagem para o ECR**:

docker tag stock-prediction:latest <YOUR_ECR_REPO_URL>:latest

Substitua `<YOUR_ECR_REPO_URL>` pelo URL do repositório ECR.

4. **Enviar a imagem para o ECR**:

docker push <YOUR_ECR_REPO_URL>:latest

## Como criar e implementar a Lambda usando a imagem do ECR

1. Vá para o AWS Lambda e clique em "Criar função".
2. Escolha "Container Image".
3. Forneça o nome da função e selecione a imagem do ECR que acabou de ser enviada.
4. Complete a criação da função.

## Integração com API Gateway

A função Lambda é configurada para ser acessada através da AWS API Gateway. Isso permite que um frontend faça chamadas HTTP para obter as previsões de preços de ações.

### Configuração

1. **Crie um recurso e método GET na API Gateway**:
   
   Conecte este método à função Lambda criada para que as requisições GET possam ser processadas pela função.

2. **Defina os parâmetros de consulta**:

   Configure a API para aceitar parâmetros como `ticker`, `initial_date` e `forecast_days`.

3. **Implante a API**:

   Após a configuração, implante a API para torná-la acessível publicamente.

## Treinamento do Modelo no Google Colab

O modelo de previsão de preços de ações é treinado separadamente no Google Colab. Esta abordagem permite o uso de recursos computacionais avançados e a flexibilidade do ambiente Colab para experimentação e otimização do modelo.

### Etapas de Treinamento

1. **Preparação dos Dados**: Colete e processe os dados históricos das ações.

2. **Treinamento do Modelo**: Utilize algoritmos de aprendizado de máquina para treinar o modelo com os dados.

3. **Validação e Testes**: Teste e valide o modelo para garantir sua precisão e confiabilidade.

4. **Exportação do Modelo e Scalers**: Exporte o modelo treinado e os scalers para serem utilizados na função Lambda.

5. **Upload para o S3**: Faça upload dos arquivos do modelo e scalers para o bucket S3 apropriado.

## Uso e Invocação da Função Lambda

Para invocar a função Lambda:

1. **Faça uma chamada GET para a API Gateway**:
   
   Inclua os parâmetros necessários, como `ticker`, `initial_date` e `forecast_days`.

2. **Receba as Previsões**:

   O resultado será uma lista de previsões de preços para as datas especificadas, incluindo preços reais (para os dias disponíveis) e previstos.
