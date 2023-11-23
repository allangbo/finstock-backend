# Historical Prices

O repositório `historical-prices` contém uma solução para coletar preços históricos de ações usando AWS Lambda, AWS DynamoDB, AWS API Gateway, AWS ECR e CloudWatch Events.

## Estrutura do Repositório

├── Dockerfile
├── lambda_function.py
└── requirements.txt


## Como compilar a imagem Docker e carregá-la no ECR da AWS

1. **Autenticação no AWS ECR**:

aws ecr get-login-password --region <YOUR_REGION> | docker login --username AWS --password-stdin <YOUR_ECR_REPO_URL>

Substitua `<YOUR_REGION>` pela região da AWS em que o ECR foi criado.
Substitua `<YOUR_ECR_REPO_URL>` pela url do repositório ECR.

2. **Construir a imagem Docker**:

docker build -t historical-prices .

3. **Taggear a imagem para o ECR**:

docker tag historical-prices:latest <YOUR_ECR_REPO_URL>:latest


Substitua `<YOUR_ECR_REPO_URL>` pelo URL do repositório ECR.

4. **Enviar a imagem para o ECR**:

docker push <YOUR_ECR_REPO_URL>:latest


## Como criar e implementar a Lambda usando a imagem do ECR

1. Vá para o AWS Lambda e clique em "Criar função".
2. Escolha "Container Image".
3. Forneça o nome da função e selecione a imagem do ECR que acabou de ser enviada.
4. Complete a criação da função.

## Como configurar o AWS API Gateway

1. **Crie um novo recurso API**:

Crie um recurso chamado "stockdata".

2. **Defina um novo método GET para "stockdata"**:

Conecte este método à função Lambda criada anteriormente.

## Configurar CloudWatch Events para Agendamento

1. **Crie uma nova regra no CloudWatch Events**:

Defina um cronograma usando uma expressão cron para executar a função diariamente.

2. **Conecte a regra ao API Gateway**:

Selecione a API e o estágio criado no API Gateway como o alvo da regra.

## Usando a API

- **Consulta de Dados Históricos**:
Faça uma chamada GET para o endpoint `/stockdata`, passando parâmetros como `num_dias`, `start_date` e `end_date` para coletar dados de preços históricos das ações.

### Parâmetros da API:

- `num_dias` (opcional): Número de dias para os quais os dados históricos devem ser recuperados. Por exemplo: `5d`.

- `start_date` e `end_date` (opcionais): Intervalo de datas para recuperar os dados históricos. As datas devem estar no formato `YYYY-MM-DD`. Por exemplo: `start_date=2023-01-01&end_date=2023-01-05`.

Note que você deve fornecer ou `num_dias` ou o par de `start_date` e `end_date`, mas não ambos.


