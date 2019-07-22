# Detector de edificações

Programa para identificar edificações através de imagens utilizando um modelo treinado de Deep Learning. Essa identificação gera um arquivo Geopackage com os boxes da identificação.

## Como Usar

Essa programa funciona no Linux e no Windows.

### Pré-requisitos

Para utilizar esse programa é preciso ter instalado no seu sistema operacional apenas o
[Docker](https://docs.docker.com/install/).

### Instalação

A primeira coisa é obter esse repositório.

No Linux pelo terminal execute:
```
$ git clone https://github.com/1cgeo/detect_build.git
```
No Windows faça o Download desse repositório:

![](doc_img/download.png)

e extraia os arquivos.

Com o [Docker](https://docs.docker.com/install/) instalado e os arquivos, salvos em um local de sua preferência, dentro da pasta "detect_build" execute o seguinte comando pelo terminal (No Linux ou Windows):

```
docker build . -t detectbuild
```

## Executando

Após executar o comando anterior com sucesso. Coloque suas imagens dentro da pasta "input_images" e inicie o programa.

No linux pelo terminal execute:

```
docker run -v $PWD:/app -it detectbuild
```

No windows pelo terminal execute:

```
docker run -v %cd%:/app -it detectbuild
```

No final do processo será gerado um arquivo Geopackage na pasta "output_gpkg" contendo os boxes da identificação.