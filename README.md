# Penumbra

Um índice de dados abertos que revela os municípios da Bahia mais esquecidos ao
mesmo tempo pela renda, pelo serviço público, pelo orçamento e pela atenção. O
foco é o interior, e em especial a zona cacaueira, com o gancho das eleições de
2026.

## De onde vem o nome

Penumbra é a faixa de meia-luz entre a sombra total e a claridade plena. Não é o
breu, onde nada se vê, nem a luz cheia do holofote, onde tudo aparece. É o
entremeio, o lugar onde alguma coisa existe mas quase ninguém repara. Foi esse
estado que o projeto quis nomear. Os municípios que o índice ilumina não são
invisíveis por decreto, estão ali, com nome, código e gente, mas vivem numa zona
cinzenta de atenção pública, longe da manchete e da agenda de campanha. Há ainda
o sentido astronômico, a penumbra é a borda de um eclipse, onde a luz é apenas
parcialmente bloqueada. É essa borda que o projeto tenta mapear.

## A zona cacaueira

O coração do projeto é o sul da Bahia. A região do cacau já foi das mais ricas do
país e afundou no esquecimento a partir do fim dos anos 1980, quando a praga da
vassoura-de-bruxa arrasou a lavoura. Existe até hoje uma controvérsia, defendida
por parte dos produtores e pesquisadores e alvo de investigação, de que o fungo
teria sido introduzido de propósito. O projeto não toma partido nessa disputa. O
que ele faz é medir, com dados, o tamanho da sombra em que a região acabou.

## Como o índice funciona

Cada município recebe uma nota de 0 a 100. Quanto maior, mais fundo na penumbra.
A nota vem de seis sinais, agrupados em três ideias.

A carência da necessidade, medida pela renda por habitante e pela combinação de
IDHM, IDEB e mortalidade infantil. A falta de orçamento próprio, medida pela
autonomia fiscal, o quanto a cidade arrecada por conta própria em vez de depender
de repasse. E a invisibilidade, medida pela distância até a capital, pela baixa
densidade e pela população pequena.

Cada sinal vira um percentil dentro do conjunto dos municípios, o que torna o
índice resistente a casos extremos como Salvador. Um dado que falta recebe o
valor mediano, nunca o pior. Já um município que não prestou contas ao Tesouro
recebe nota alta no sinal de orçamento, porque a falta de transparência é, ela
mesma, um sinal de penumbra. Os pesos ficam versionados em
`pipeline/config/pesos.json` e o site também mostra uma versão com todos os
sinais valendo o mesmo, como teste de sensibilidade.

## Fontes

Todos os dados são públicos e por município, chaveados pelo código IBGE.

- IBGE, lista de municípios, malha territorial, Censo 2022 e PIB dos municípios
- IPEA, Atlas do Desenvolvimento Humano, IDHM e mortalidade infantil
- INEP, IDEB dos anos iniciais
- Tesouro Nacional, SICONFI, receitas, despesas e investimento

## Estrutura

```
pipeline/   coleta os dados abertos e gera o índice (Python)
  src/      um coletor por fonte, além de normalização e cálculo
  config/   fontes e pesos, versionados
app/        site que mostra o mapa, o ranking e a ficha (Next.js)
  public/data/  índice.json e municipios.geojson, consumidos pelo site
```

## Como rodar

O pipeline gera os dados. Testado com Python 3.12.

```bash
cd pipeline
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python run.py
```

O site mostra os dados. Testado com Node 20.

```bash
cd app
npm install
npm run dev
```

## Deploy

O site sobe na Vercel apontando o diretório raiz para `app`. Os dados já vão
versionados em `app/public/data`, então o deploy não depende de rodar o pipeline.

## Aviso

Projeto independente e sem vínculo partidário. Não diz em quem votar. Reúne dados
públicos para ampliar o campo de visão às vésperas das eleições de 2026, quando o
interior costuma ficar fora do roteiro. O índice não substitui o conhecimento de
quem vive no lugar, apenas devolve contorno a quem estava na meia-luz.

## Autor

Feito por Cauã Moraes. Conheça outros projetos em [mowaveone.com](https://mowaveone.com).
