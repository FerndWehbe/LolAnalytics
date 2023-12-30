# LolAnalytics

Projeto com finalidade de buscar informações das partidas de League of Legends e montar uma recapitulação do ano. 


## Steps
Siga os passos abaixo para configurar e executar o ambiente:


### Clonar o repositório

Clone o repositório do LolAnalytics, incluindo os submódulos, utilizando o seguinte comando:

```
git clone https://github.com/FerndWehbe/LolAnalytics.git --recursive
```

### Crie arquivo .env
Criar um arquivo .env dentro do modulo app/tasks, esse arquivo permite que você personalize suas variáveis de ambiente de trabalho individual, e dentro do arquivo adicione a chave:

```
riot_api_key=<pegar a chave na parte de dashboard no site da [riot](https://developer.riotgames.com/)>
```

### Converta para o formato Unix

Para rodar o ambiente é necessario converter os arquivos sh para o padrão de formatação unix.

Dentro da pasta docker do projeto, abrir o terminal do git clicando com botão direito na pasta e indo em Open Git Bash here e executar os commandos:

```
    dos2unix.exe app/*.sh
    dos2unix.exe front-end/*.sh
```

### Executando docker

No seu editor de código-fonte execute o seguinte comando no terminal:

```
    docker-compose up -d --build
```

Para subir um container sozinho usar o commando:

```
    docker-compose up -d --build --no-deps nome-do-container
```