FROM public.ecr.aws/lambda/python:3.11

# Copiar requirements.txt
COPY requirements.txt ${LAMBDA_TASK_ROOT}

# Instalar os pacotes especificados
RUN pip install -r requirements.txt

# Copiar o código da função Lambda
COPY lambda_function.py ${LAMBDA_TASK_ROOT}

# Copiar o arquivo pyESN.py para o diretório de trabalho da Lambda
COPY pyESN.py ${LAMBDA_TASK_ROOT}

# Definir o comando para o manipulador da função Lambda
CMD [ "lambda_function.handler" ]
