# Natação

Acompanhamento das minhas natações com dados do Garmin: ritmo, SWOLF, braçadas, volume e sugestões de treino.

**Site:** https://fernandalpcosta.github.io/natacao/

- **Painel**: evolução de ritmo, SWOLF, braçadas, volume e mistura de nados.
- **Detalhe de cada natação** (`sessao.html?id=...`): tempo por piscina, colorido por nado, e a tabela de séries.
- **Calendário** (`calendario.html`): treinos agendados no Garmin Connect e natações feitas; dá para agendar, mudar o dia ou tirar um treino (com um token do GitHub de permissão mínima, salvo só no navegador). O calendário da Garmin é a referência e é lido na sincronização diária.
- **Treinos** (`treinos.html`): os treinos passo a passo, com tempo estimado e download do .fit.

## Como funciona

- `sync/` baixa as natações pela [Garmin Connect Personal API](https://developer.garmin.com/gc-developer-program/personal/personal-api) e grava métricas em `docs/data/`. Não são gravados GPS, frequência cardíaca nem arquivos .FIT originais.
- `.github/workflows/sync.yml` roda a sincronização todo dia de manhã (e pode ser disparada à mão em **Actions → Sincronizar Garmin → Run workflow**).
- `docs/` é o site publicado pelo GitHub Pages (`estilo.css` e `comum.js` são compartilhados pelas páginas).
- `treinos/` tem os treinos em JSON; `python treinos/gerar.py` cria os `.fit` e o índice em `docs/treinos/`, que aparecem na página Treinos.

## Chave da Garmin

A chave pessoal vale 30 dias. Ao renovar em connect.garmin.com → Settings → Personal API Key, atualize o segredo
`GARMIN_PERSONAL_API_KEY` em **Settings → Secrets and variables → Actions** deste repositório.

## Enviar um treino ao relógio pelo celular (Bluetooth)

1. Uma única vez: crie os segredos `GARMIN_EMAIL` e `GARMIN_PASSWORD` em **Settings → Secrets and variables → Actions**.
2. Em **Actions → Enviar treino ao Garmin → Run workflow**, escolha o treino e o dia (AAAA-MM-DD).
3. O treino entra na sua conta e no calendário do Garmin Connect; o app do celular passa para o relógio na próxima sincronização.

Usa a biblioteca não oficial `garminconnect`. Se a conta tiver verificação em duas etapas, o envio automático não funciona.
Ao criar um treino novo em `treinos/`, acrescente o nome dele na lista `options` de `.github/workflows/enviar-treino.yml`.

## Levar um treino para o relógio pelo cabo USB

1. Conecte o relógio ao computador pelo cabo USB.
2. Baixe o .fit na página Treinos e copie para a pasta `GARMIN/NewFiles` do relógio.
3. Desconecte: o treino aparece em **Treinos** na natação em piscina.

## Rodar localmente

```bash
pip install -r requirements.txt
GARMIN_PERSONAL_API_KEY=... python sync/sync.py
```
