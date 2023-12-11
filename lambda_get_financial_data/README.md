
# AWS Lambda para Coleta de Dados Financeiros de Ações

Este projeto implementa uma função AWS Lambda que coleta dados financeiros de ações de um arquivo CSV armazenado no AWS S3. A função é configurada para filtrar os dados com base em um ticker de ação específico e uma data de referência, fornecidos como parâmetros.

## Estrutura do Repositório

- `lambda_function.py`: Script principal que contém a lógica da função Lambda.
- `Dockerfile`: Arquivo para construir uma imagem Docker da função Lambda.
- `companies_ticker_b3.csv`: Arquivo CSV com a lista de tickers de ações.
- `requirements.txt`: Dependências necessárias para o script.

## Funcionamento da Função Lambda

A função é acionada com dois parâmetros: um ticker de ação e uma data. Ela realiza as seguintes operações:

1. **Leitura de Parâmetros**: A função começa lendo os parâmetros `ticker` e `date` passados no evento de invocação.

2. **Acesso ao Arquivo no S3**: Utilizando o cliente `boto3`, a função acessa um bucket S3 específico (`companies-ticker`) e lê o arquivo `stocks_financial_data.csv`.

3. **Processamento dos Dados**:
   - O conteúdo do arquivo é lido em um DataFrame do Pandas.
   - A coluna 'Date' é convertida para o formato datetime.
   - Os dados são filtrados para encontrar as entradas correspondentes ao ticker fornecido e à data mais recente que não seja futura em relação à data fornecida.

4. **Retorno dos Dados**:
   - Se dados relevantes são encontrados, a entrada mais próxima da data fornecida é retornada.
   - Caso contrário, é retornado um status indicando que nenhum dado foi encontrado.

## Implantação e Uso

- **Implantação**: A função pode ser implantada na AWS Lambda, com a imagem Docker construída a partir do `Dockerfile` fornecido.
- **Uso**: A função é invocada através de eventos AWS, passando os parâmetros `ticker` e `date`. Pode ser integrada com outros serviços AWS para automação e agendamento de tarefas.

## Considerações de Segurança e Acesso

- Garantir que a função Lambda tenha as permissões adequadas para acessar o bucket S3 especificado.
- Assegurar a segurança dos dados no S3 e durante a transmissão.
