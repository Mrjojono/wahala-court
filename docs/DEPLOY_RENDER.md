# Deploy Wahala Court sur Render

Deux services free : **API** (FastAPI) + **Web** (SvelteKit / Node).

## Prérequis

1. Compte [Render](https://render.com) (crédits Hacktoberfest sur [hacktoberfest.com/my](https://hacktoberfest.com/my) si dispo)
2. Repo GitHub poussé (`Mrjojono/wahala-court`)
3. Clé [Google AI Studio](https://aistudio.google.com/apikey) → `GEMINI_API_KEY` (Gemma cloud ; pas d’Ollama sur Render free)

## Option A — Blueprint (recommandé)

1. Push `main` avec `render.yaml` à la racine
2. Render Dashboard → **New** → **Blueprint**
3. Connecte le repo → Apply
4. Quand demandé, colle `GEMINI_API_KEY`
5. Attends les 2 services verts
6. Ouvre l’URL `wahala-court-web` → teste un dépôt / débat
7. (Optionnel) Sur **wahala-court-api** → Environment → `CORS_ORIGINS` = `https://wahala-court-web-….onrender.com` (plus strict que `*`)

## Option B — Manuel

### 1. API

- **New Web Service** → repo → Root Directory: `backend`
- Runtime: Python 3
- Build: `pip install -r requirements.txt`
- Start: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Health: `/health`
- Env:
  - `GEMINI_API_KEY` = ta clé
  - `GEMMA_CLOUD_MODEL` = `gemma-4-26b-a4b-it`
  - `CORS_ORIGINS` = `*` (puis URL du front)
  - `HOST` = `0.0.0.0`

Note l’URL API : `https://wahala-court-api-xxxx.onrender.com`

### 2. Front

- **New Web Service** → même repo → Root Directory: `app`
- Runtime: Node
- Build: `npm ci && npm run build`
- Start: `npm run start` (lance `node build/index.js`)
- Env:
  - `NODE_VERSION` = `22`
  - `PUBLIC_API_URL` = URL API ci-dessus (**sans** slash final)

## Vérifs

```bash
curl https://TON-API.onrender.com/health
# → "gemma_cloud": true, "provider": "cloud"
```

Free tier = cold start ~30–60s. Le WebSocket débat se réveille après le premier hit.

## Submission DEV (#hf26challenge)

Dans le post : lien **demo Render**, lien **GitHub**, explique Gemma + why open + pour quel pote. Catégories naturelles : **Best Use of Gemma** + **Best Use of Render**.
