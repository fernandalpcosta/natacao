# Natação

Acompanhamento das minhas natações com dados do Garmin: ritmo, SWOLF, braçadas, volume e sugestões de treino.

**Painel:** https://fernandalpcosta.github.io/natacao/

## Como funciona

- `sync/` baixa as natações pela [Garmin Connect Personal API](https://developer.garmin.com/gc-developer-program/personal/personal-api) e grava métricas em `docs/data/`. Não são gravados GPS, frequência cardíaca nem arquivos .FIT originais.
- `.github/workflows/sync.yml` roda a sincronização todo dia de manhã (e pode ser disparada à mão em **Actions → Sincronizar Garmin → Run workflow**).
- `docs/` é o painel, publicado pelo GitHub Pages.
- `treinos/` tem treinos em JSON; `python treinos/gerar.py` cria os `.fit` em `treinos/fit/`.

## Chave da Garmin

A chave pessoal vale 30 dias. Ao renovar em connect.garmin.com → Settings → Personal API Key, atualize o segredo
`GARMIN_PERSONAL_API_KEY` em **Settings → Secrets and variables → Actions** deste repositório.

## Levar um treino para o relógio

1. Conecte o relógio ao computador pelo cabo USB.
2. Copie o arquivo de `treinos/fit/` para a pasta `GARMIN/NewFiles` do relógio.
3. Desconecte: o treino aparece em **Treinos** na natação em piscina.

## Rodar localmente

```bash
pip install -r requirements.txt
GARMIN_PERSONAL_API_KEY=... python sync/sync.py
```
