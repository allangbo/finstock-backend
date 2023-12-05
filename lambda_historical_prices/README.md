# Historical Prices

Este repositório contém uma solução para coletar preços históricos de ações usando AWS Lambda, AWS DynamoDB e AWS S3, com a função sendo invocada diretamente do console da AWS e através de tarefas agendadas no CloudWatch Events.

## Estrutura do Repositório

├── Dockerfile
├── lambda_function.py
├── companies_ticker_b3.csv
└── requirements.txt

## Funcionamento Interno da Função Lambda para Coleta de Dados

### Fluxo de Execução

1. **Inicialização e Verificação de Parâmetros**:
   
   - A função começa verificando os parâmetros de entrada, como `num_dias`, `start_date` e `end_date`, para determinar o período para o qual os dados devem ser coletados.
   - Ela também valida se os parâmetros estão corretos e se enquadram nas regras definidas (como o limite de 30 dias para um intervalo de datas).

2. **Leitura de Tickers do Arquivo CSV no S3**:

   - A função usa o cliente S3 do `boto3` para acessar e ler o arquivo `companies_ticker_b3.csv` armazenado em um bucket do S3.
   - Cada linha do arquivo CSV representa um ticker de ação (por exemplo, `PETR4`, `VALE3`).

3. **Coleta de Dados Históricos de Ações**:

   - Para cada ticker lido do CSV, a função utiliza a biblioteca `yfinance` para baixar os dados do mercado financeiro.
   - Os parâmetros `start_date`, `end_date` e `num_dias` são usados para definir o período de coleta dos dados.
   - A função itera sobre os dados baixados, coletando informações importantes como preço de abertura (`Open`), preço de fechamento (`Close`) e volume (`Volume`).

4. **Inserção de Dados no DynamoDB**:

   - Após coletar os dados, a função insere cada registro no DynamoDB.
   - Cada item inserido contém o `Ticker`, a `Date`, o `OpenPrice`, o `ClosePrice` e o `Volume`.

## Como compilar a imagem Docker e carregá-la no ECR da AWS

1. **Autenticação no AWS ECR**:

aws ecr get-login-password --region <YOUR_REGION> | docker login --username AWS --password-stdin <YOUR_ECR_REPO_URL>

Substitua `<YOUR_REGION>` pela região da AWS em que o ECR foi criado.
Substitua `<YOUR_ECR_REPO_URL>` pela URL do repositório ECR.

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

## Configurar CloudWatch Events para Agendamento

1. **Crie uma nova regra no CloudWatch Events**:

Defina um cronograma usando uma expressão cron para executar a função Lambda de acordo com a frequência desejada. Nesse caso, todos os dias, ao final do dia.

2. **Conecte a regra à função Lambda**:

Selecione a função Lambda criada anteriormente como o alvo da regra.

## Invocação e Uso da Função Lambda

A função Lambda pode ser invocada de duas maneiras:

1. **Diretamente através do Console AWS Lambda**:

Você pode testar e invocar a função diretamente pelo console, passando os parâmetros necessários (`num_dias`, `start_date`, `end_date`) no formato JSON.

2. **Automatização via CloudWatch Events**:

Através das regras configuradas no CloudWatch Events, a função será invocada automaticamente conforme a expressão cron definida, permitindo a coleta regular de dados.

### Parâmetros da Função Lambda:

- `num_dias` (opcional): Número de dias para os quais os dados históricos devem ser recuperados. Por exemplo: `5d`.
- `start_date` e `end_date` (opcionais): Intervalo de datas para recuperar os dados históricos. As datas devem estar no formato `YYYY-MM-DD`. Por exemplo: `start_date=2023-01-01&end_date=2023-01-05`.

Note que você deve fornecer ou `num_dias` ou o par de `start_date` e `end_date`, mas não ambos.

## Uso do Arquivo companies_ticker_b3.csv no S3

O arquivo `companies_ticker_b3.csv` define os tickers de ações para os quais os dados de preços históricos serão coletados. Este arquivo está armazenado no AWS S3 e é acessado pela função Lambda durante a execução.

### Estrutura do Arquivo CSV

O arquivo `companies_ticker_b3.csv` deve seguir a estrutura abaixo:

- Cada linha do arquivo representa um ticker de ação.
- A primeira coluna de cada linha contém o ticker da ação.

Exemplo:

PETR4
VALE3
ITUB4

### Configuração no S3

1. **Armazenamento do Arquivo**:

   O arquivo deve ser armazenado em um bucket do S3. O nome do bucket e a chave do arquivo são referenciados no código da função Lambda.

   Exemplo:

   - Nome do Bucket: `companies-ticker`
   - Chave do Arquivo: `companies_ticker_b3.csv`

2. **Permissões de Acesso**:

   Garanta que a função Lambda tenha as permissões necessárias para ler o arquivo do bucket do S3.