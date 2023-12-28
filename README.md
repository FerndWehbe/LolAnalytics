# LolAnalytics

Projeto com finalidade de buscar informações das partidas de League of Legends e montar uma recapitulação do ano. 



Para rodar o ambiente é necessario converter os arquivos sh para o padrão de formatação unix

Steps:

* git clone https://github.com/FerndWehbe/LolAnalytics.git --recursive

* Dentro da pasta docker do projeto, abrir o terminal do git clicando com botão direito na pasta e indo em Open Git Bash here e executar os commandos:

```
    dos2unix.exe app/*.sh
    dos2unix.exe front-end/*.sh
```

* docker-compose up -d --build


Para subir um container sozinho usar o commando

* docker-compose up -d --build --no-deps nome-do-container
