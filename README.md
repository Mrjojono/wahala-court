# Wahala Court

Procès tabloïd des petits wahalas — SvelteKit front + FastAPI (Gemma via Ollama + RAG TogoLM).

## Démarrer

### 1. Front

```bash
cd app
cp .env.example .env   # PUBLIC_API_URL=http://127.0.0.1:8000
npm install
npm run dev
```

→ http://localhost:5173

### 2. Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# optionnel: TOGOLM_API_KEY=...
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

→ http://127.0.0.1:8000/health

### 3. Gemma (open-weight)

```bash
# installer Ollama puis:
ollama pull gemma3:1b
# ou gemma2:2b — doit matcher OLLAMA_MODEL dans backend/.env
```

Sans Ollama **ni** clé cloud, débat / rédaction / chambre basculent sur des **mocks** (le jeu reste jouable). TogoLM search fonctionne sans clé (rate-limit public) ; une clé `TOGOLM_API_KEY` augmente les quotas.

### 4. Gemma cloud (Google AI Studio) — si pas d’Ollama

1. Crée une clé sur [Google AI Studio](https://aistudio.google.com/apikey)
2. Dans `backend/.env` :
   ```bash
   GEMINI_API_KEY=ta_cle_ici
   GEMMA_CLOUD_MODEL=gemma-4-26b-a4b-it
   ```
3. Redémarre uvicorn. `GET /health` doit montrer `"gemma_cloud": true`, `"provider": "cloud"`.

**Priorité:** Ollama local si dispo → sinon cloud Gemma → sinon mock.

## Architecture

```
app/                 # SvelteKit UI
  src/lib/api.ts     # HTTP posts + WebSocket débat
  src/routes/        # accueil → role → dossier → debat → vote → verdict → redaction → greffe
backend/             # FastAPI
  app/services/      # togolm (search), ollama (Gemma), engine, prompts
  app/ws/debate.py   # WS /ws/debate
  app/routes/posts.py# POST /v1/posts/generate
design/              # wahala.pen, tokens, SVG
docs/GDD.md
```

**Règle IA:** génération = **Gemma/Ollama** uniquement. TogoLM = **retrieval** (`GET /v1/search`), pas `POST /v1/query` (génération Gemini côté TogoLM).

## Parcours

Accueil → **Dépôt du pote** (optionnel) → Rôle → Dossier → Audience (WS multi-NPC + Objection) → Vote → Verdict (+ lettre au pote) → **Rédaction** → Archives

## Innovation Gemma — Chambre + ADN + Dépôt

1. **Dépôt du pote** (`POST /v1/depot/build`) — wahala brut → dossier tabloïd + ADN.
2. **ADN du pote** (`POST /v1/voice/extract`) — WhatsApp → tone / lexique / excuses.
3. **Chambre du conseil** (`POST /v1/chamber/deliberate`) — Gemma joue procureur + défense + juge ; peut contrer le peuple.
4. **Débat solo** — tu joues un rôle ; Gemma enchaîne les 3 autres.
5. **Lettre au pote** (`POST /v1/letter/write`) — sur `/verdict` après un dépôt.

## Deploy Render

Voir **[docs/DEPLOY_RENDER.md](docs/DEPLOY_RENDER.md)** — Blueprint `render.yaml` (API + Web).

En bref : push GitHub → Render **Blueprint** → secret `GEMINI_API_KEY` → demo = URL `wahala-court-web`.

## Why open (Hacktoberfest)

- **Open-weight:** Gemma tourne en local via Ollama — le wahala d’un pote ne part pas chez un cloud fermé pour la génération.
- **Open corpus:** [TogoLM](https://github.com/omarfarouk228/togolm) nourrit les citations (lois / admin togolais) en open source.
- **Build for a friend:** chaque dossier part d’un vrai wahala partageable ; `/redaction` sort caption / WhatsApp / brouillon DEV (`#hf26challenge`).

## API utile

| Endpoint | Rôle |
|----------|------|
| `GET /health` | Ollama + TogoLM ping |
| `WS /ws/debate` | Stream réplique NPC (token / line / sources) |
| `POST /v1/posts/generate` | Caption + WhatsApp + brouillon DEV |
