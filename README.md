# API Tweeter :octocat:

## Script de captura de dados do tweeter e armezenamento no blob storage account

# :pushpin: Pré-requisitos:
- Biblioteca para o projeto: <img src='https://img.shields.io/badge/azure--storage--blob-12.0.0-informational'> <img src='https://img.shields.io/badge/python--decouple-3.3-informational'> <img src='https://img.shields.io/badge/tweepy-3.9.0-informational'><br>
- Linguagem de programação: <img src='https://camo.githubusercontent.com/2857442965ab9a51229c075102012bdbd340abc3/68747470733a2f2f696d672e736869656c64732e696f2f707970692f707976657273696f6e732f72657175657374733f6c6162656c3d507974686f6e266c6f676f3d505954484f4e266c6f676f436f6c6f723d79656c6c6f77267374796c653d706c6173746963'>
- Plataforma utilizada: **Azure**
- Arquivo **.env**: É necessário criar um arquivo .env para inserir as credenciais da API do Tweeter e do Azure.
  - API Tweeter: **consumer_key, consumer_secret, access_token e access_secret**
  - Plataforma Azure: **connect_string e container**
# :pushpin: Modo de instalação:
- MakeFile: ```$ make requirements ``` 

# :rocket: Executar os scripts:

   - Pegar tweets de **30 minutos** atrás:  ``` $ make run_hour```
   - Pegar tweets de **hoje**: ``` $ make run_day```
    
     
# :cloud: Ambiente de armezenamento:
- Os dados capturados do tweeter são armazenados no ambiente do Azure (**blob storage account**)
