# Stock News Collection and Retrieval

Este repositório contém uma função Lambda AWS para coletar e recuperar notícias relacionadas a ações financeiras. A função acessa arquivos CSV no S3 para definir queries baseadas em uma lista de ações e utiliza uma API para acessar o Google News.

## Estrutura do Repositório

├── Dockerfile
├── lambda_function.py
├── queries_companhias_ticker_part_1.csv
├── queries_companhias_ticker_part_2.csv
├── queries_companhias_ticker_part_3.csv
├── queries_companhias_ticker_part_4.csv
├── queries_companhias_ticker_part_5.csv
├── queries_companhias_ticker_part_6.csv
├── requirements.txt


## Descrição da Função Lambda

A função é projetada para executar duas operações principais: coletar notícias do Google News relacionadas a ações especificadas e recuperar essas notícias para visualização.

### Coleta de Notícias

1. **Leitura do Arquivo CSV no S3**: A função acessa o S3 para ler arquivos CSV que contém queries relacionadas a ações. Os arquivos CSV estão disponibilizados nesse repositório dividido em 6 partes.

2. **Execução de Queries no Google News**: Utiliza a API Google News Feed para buscar notícias com base nas queries definidas nos arquivos CSV.

3. **Salvamento de Notícias no DynamoDB**: As notícias coletadas são salvas em uma tabela do DynamoDB, incluindo detalhes como título, descrição, URL, data de publicação e fonte.

### Recuperação de Notícias

1. **Consulta de Notícias no DynamoDB**: A função permite a recuperação de notícias a partir do ticker de uma ação, podendo também filtrar por data.

2. **Formatação e Retorno dos Dados**: As notícias são formatadas e retornadas em JSON através de uma requisição GET, prontas para serem consumidas por um frontend.

## Uso e Invocação da Função Lambda

A função Lambda pode ser invocada de duas maneiras:

1. **Para Coletar Notícias**:
   
   - Faça uma invocação direta da função Lambda com o parâmetro `save_news` definido como `true` e forneça o nome do arquivo CSV no S3.

2. **Para Recuperar Notícias**:

   - Faça uma chamada GET através de uma integração com a AWS API Gateway, fornecendo o ticker da ação e, opcionalmente, a data desejada.
   
## Como compilar a imagem Docker e carregá-la no ECR da AWS

1. **Autenticação no AWS ECR**:

aws ecr get-login-password --region <YOUR_REGION> | docker login --username AWS --password-stdin <YOUR_ECR_REPO_URL>

Substitua `<YOUR_REGION>` pela região da AWS em que o ECR foi criado.
Substitua `<YOUR_ECR_REPO_URL>` pela URL do repositório ECR.

2. **Construir a imagem Docker**:

docker build -t get-news .

3. **Taggear a imagem para o ECR**:

docker tag get-news:latest <YOUR_ECR_REPO_URL>:latest

Substitua `<YOUR_ECR_REPO_URL>` pelo URL do repositório ECR.

4. **Enviar a imagem para o ECR**:

docker push <YOUR_ECR_REPO_URL>:latest

## Como criar e implementar a Lambda usando a imagem do ECR

1. Vá para o AWS Lambda e clique em "Criar função".
2. Escolha "Container Image".
3. Forneça o nome da função e selecione a imagem do ECR que acabou de ser enviada.
4. Complete a criação da função.

## Agendamento de Tarefas Cron para Coleta de Notícias

Para automatizar a coleta de notícias, foram configuradas tarefas cron no AWS CloudWatch Events para acionar a função Lambda de hora em hora. Como o tempo máximo de execução da Lambda é de 15 minutos, a coleta foi dividida em 6 tarefas cron, cada uma responsável por um arquivo CSV diferente.

### Configuração das Tarefas Cron

1. **Crie Seis Regras no CloudWatch Events**:
   
   - Configure seis regras cron, cada uma agendada para ser executada uma vez por hora.
   - Cada regra cron deve ser configurada para acionar a função Lambda com um nome de arquivo CSV específico como parâmetro.

2. **Parâmetros para a Função Lambda**:
 
   - Ao configurar cada regra cron, inclua o nome do arquivo CSV correspondente e defina o parâmetro `save_news` como `true`. Além disso, passe o parâmetro `time_filter` como `60m` para recuperar somente as notícias da última hora.

## Integração com AWS API Gateway para Recuperação de Notícias

A função Lambda também está configurada para recuperar notícias via uma API, utilizando a AWS API Gateway. Essa integração permite que um frontend faça chamadas HTTP para recuperar notícias de ações específicas.

### Configuração da API Gateway

1. **Crie um Recurso e Método GET na API Gateway**:

   - Configure um recurso e método GET que aponte para a função Lambda de recuperação de notícias.
   - Defina os parâmetros de consulta necessários, como `ticker` e opcionalmente `date`.

2. **Deploy da API**:

   - Após configurar o método GET, faça o deploy da API para torná-la acessível ao frontend.

3. **Teste e Validação**:

   - Teste a API para garantir que as notícias sejam recuperadas corretamente com base nos parâmetros fornecidos.


