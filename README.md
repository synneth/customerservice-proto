# Mote & Mer – AI Kundeservice Prototype

Stemmebasert kundeservice-prototype bygget med ElevenLabs Conversational AI og FastAPI.

## Hva den gjør

- Svarer på kundehenvendelser på norsk via mikrofon i nettleseren
- Håndterer: åpningstider, retur/bytte, reklamasjon, ordrestatus, størrelsesguide og medlemskap
- Eskalerer automatisk til ekte kundebehandler ved edge cases

## Oppsett

### 1. Klon og installer avhengigheter

```bash
cd kundeservice-proto
pip install -r requirements.txt
```

### 2. Konfigurer miljøvariabler

```bash
cp .env.example .env
```

Rediger `.env` og legg inn din ElevenLabs API-nøkkel.

### 3. Start backenden

```bash
cd backend
uvicorn main:app --reload
```

Backenden kjører nå på `http://localhost:8000`.

### 4. Opprett ElevenLabs-agenten

Gjør et POST-kall for å opprette/oppdatere agenten automatisk:

```bash
curl -X POST http://localhost:8000/api/setup-agent
```

Svaret inneholder en `agent_id` — legg den inn i `.env` som `ELEVENLABS_AGENT_ID=...`.

Start deretter backenden på nytt.

### 5. Åpne frontend

Gå til `http://localhost:8000` i nettleseren, klikk **Ring kundeservice** og gi mikrofonilgang.

> **Merk om webhooks lokalt:** ElevenLabs sin sky-agent kaller `BACKEND_URL` for å kjøre verktøy.
> Lokalt må du eksponere backenden via f.eks. [ngrok](https://ngrok.com/):
> ```bash
> ngrok http 8000
> ```
> Oppdater `BACKEND_URL` i `.env` med ngrok-URLen og kjør `POST /api/setup-agent` på nytt.

## Prosjektstruktur

```
kundeservice-proto/
├── backend/
│   ├── main.py          # FastAPI-server, API-endepunkter
│   ├── tools.py         # Verktøy-handlere kalt av ElevenLabs-agenten
│   ├── agent_config.py  # Systemprompt og verktøy-definisjoner
│   └── mock_data.py     # Mockdata for ordre og medlemskap
├── frontend/
│   └── index.html       # Web-grensesnitt med ElevenLabs JS SDK
├── .env.example
├── requirements.txt
└── README.md
```

## Mock-data

Prototype inneholder testdata du kan bruke under testing:

| Type | ID / Identifikator | Beskrivelse |
|------|-------------------|-------------|
| Ordre | `ORD-1001` | Klar for henting |
| Ordre | `ORD-1002` | Under behandling |
| Ordre | `ORD-1003` | Sendt |
| Medlemskap | `kari@example.com` | Har duplikat-medlemskap |
| Medlemskap | `per@example.com` | Normalt medlemskap |

## Eskalering

AI-agenten eskalerer til menneskelig behandler når:
- Kunden ber om å snakke med en person
- Saken krever skjønnsmessig vurdering (skader, tvister)
- Spørsmålet er utenfor agentens kompetanse

I prototypen vises dette som et rødt banner. I produksjon kobles dette til telefonsentralen.
