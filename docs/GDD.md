# WAHALA COURT — Game Design Doc

## 1. Concept

Un vrai wahala raconté par un pote devient un procès généré en live par IA locale (Ollama + gemma3:1b, RAG sur corpus légal togolais). Avant le verdict officiel, le public vote. Le contraste **peuple vs tribunal** est le cœur du partage.

## 2. Structure narrative (3 actes, 2–3 min)

### Acte 1 — Mise en accusation
- Greffier (texte scripté, zéro IA)
- Stamp « LE TRIBUNAL DE WAHALA EST EN SESSION »
- Dossier : n°, charge, pièce à conviction

### Acte 2 — Le débat
- 2–3 échanges Procureur ↔ Défense (citations loi via RAG)
- Intervention Accusé (ton réel de l’ami)
- Spectateur par défaut ; objection front-only

### Acte 3 — Le verdict
1. Vote GUILTY / NOT GUILTY
2. Verdict juge + sentence comique + article en dur
3. Carte partageable peuple vs tribunal

## 3. Format dossier

```
CHARGE / PIÈCE À CONVICTION / CONTEXTE / CATÉGORIE
```

Catégories : Dating · Amitié · Famille · WhatsApp · Transport · Argent · Travail

## 4. Extras low-cost

- Wahala Meter live pendant le débat
- Mode Chaos / Sérieux (toggle prompt)
- Bouton OBJECTION ! (procureur / défense seulement ; stamp + réplique + ruling juge ; front-only)
- Max 3 objections / audience, cooldown 12s
- Archives / 15 dossiers
- Carte verdict partageable (share/clipboard)
- Chambre du conseil Gemma (peuple vs tribunal)
- ADN du pote (WhatsApp → style)

Implémentation code : `app/src/lib/data/model.ts`, `cases.ts`, `trial.ts`, `stores/session.svelte.ts`, `backend/`.
