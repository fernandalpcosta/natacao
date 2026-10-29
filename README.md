# Natação

Acompanhamento das minhas natações com dados do Garmin: ritmo, SWOLF, braçadas, volume e sugestões de treino.

**Site:** https://fernandalpcosta.github.io/natacao/

- **Painel**: evolução de ritmo, SWOLF, braçadas, volume e mistura de nados.
- **Detalhe de cada natação** (`sessao.html?id=...`): tempo por piscina, colorido por nado, e a tabela de séries.
- **Treinos** (`treinos.html`): os treinos passo a passo, com tempo estimado e download do .fit.

## Como funciona

- `sync/` baixa as natações pela [Garmin Connect Personal API](https://developer.garmin.com/gc-developer-program/personal/personal-api) e grava métricas em `docs/data/`. Não são gravados GPS, frequência cardíaca nem arquivos .FIT originais.
- `.github/workflows/sync.yml` roda a sincronização todo dia de manhã (e pode ser disparada à mão em **Actions → Sincronizar Garmin → Run workflow**).
- `docs/` é o site publicado pelo GitHub Pages (`estilo.css` e `comum.js` são compartilhados pelas páginas).
- `treinos/` tem os treinos em JSON; `python treinos/gerar.py` cria os `.fit` e o índice em `docs/treinos/`, que aparecem na página Treinos.

## Chave da Garmin

A chave pessoal vale 30 dias. Ao renovar em connect.garmin.com → Settings → Personal API Key, atualize o segredo
`GARMIN_PERSONAL_API_KEY` em **Settings → Secrets and variables → Actions** deste repositório.

## Levar um treino para o relógio

1. Conecte o relógio ao computador pelo cabo USB.
2. Baixe o .fit na página Treinos e copie para a pasta `GARMIN/NewFiles` do relógio.
3. Desconecte: o treino aparece em **Treinos** na natação em piscina.

## Rodar localmente

```bash
pip install -r requirements.txt
GARMIN_PERSONAL_API_KEY=... python sync/sync.py
```
