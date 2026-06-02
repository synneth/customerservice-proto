# Mote & Mer – AI Kundeservice Prototype

En stemmebasert AI-kundeservice prototype for klesbutikk, bygget med [ElevenLabs Conversational AI](https://elevenlabs.io/conversational-ai) og [FastAPI](https://fastapi.tiangolo.com/). Kunder ringer inn via nettleser, snakker med en norsktalende AI-assistent, og blir automatisk satt over til en ekte kundebehandler ved behov.

---

## Funksjonalitet

| Scenario | Beskrivelse |
|---|---|
| Åpningstider og adresse | AI svarer direkte på butikkinfo |
| Retur og bytte | Forklarer returregler og prosess |
| Reklamasjon | Informerer om 2-årsretten etter forbrukerkjøpsloven |
| Ordrestatus | Slår opp ordre basert på ordre-ID (f.eks. `ORD-1001`) |
| Størrelsesguide | Anbefaler størrelse basert på kroppsmål kunden oppgir |
| Medlemskap | Finner konto, endrer e-post, sletter duplikat-medlemskap |
| Eskalering | Setter kunden automatisk over til ekte kundebehandler ved edge cases |

---

## Arkitektur

```
Kunde (nettleser)
      │  WebSocket (ElevenLabs JS SDK)
      ▼
ElevenLabs Conversational AI  ──► Claude (LLM)
      │  Webhook-kall (POST)
      ▼
FastAPI backend (Python)
      │
      ├─ /tools/check_order
      ├─ /tools/lookup_membership
      ├─ /tools/update_membership_email
      ├─ /tools/merge_duplicate_memberships
      ├─ /tools/get_size_recommendation
      ├─ /tools/get_return_policy
      ├─ /tools/get_complaint_policy
      ├─ /tools/get_store_info
      └─ /tools/escalate_to_human
```

**Flyten:**
1. Kunden klikker "Ring kundeservice" i nettleseren
2. Frontend henter et signert samtale-token fra backend
3. ElevenLabs kobler opp en sanntids stemmesamtale
4. Agenten (Claude via ElevenLabs) lytter, forstår og svarer på norsk
5. Ved behov kaller agenten webhook-er i backend for å hente data
6. Ved edge cases trigges `escalate_to_human` og kunden overføres

---

## Prosjektstruktur

```
kundeservice-proto/
├── backend/
│   ├── main.py          # FastAPI-server: API-endepunkter, agent-oppsett, token
│   ├── tools.py         # Logikk for alle verktøy-kall fra ElevenLabs
│   ├── agent_config.py  # Norsk systemprompt + verktøy-definisjoner (api_schema)
│   └── mock_data.py     # Testdata: ordre, medlemskap, størrelsesguide, butikkinfo
├── frontend/
│   └── index.html       # Web-UI med mikrofon-knapp, samtalelogg og eskaleringsvisning
├── .env.example         # Mal for miljøvariabler
├── requirements.txt     # Python-avhengigheter
└── README.md
```

---

## Kom i gang

### Forutsetninger

- Python 3.11+
- En [ElevenLabs](https://elevenlabs.io)-konto med API-nøkkel
- [ngrok](https://ngrok.com/) for lokal testing av webhooks

### 1. Installer avhengigheter

```bash
pip install -r requirements.txt
```

### 2. Konfigurer miljøvariabler

```bash
cp .env.example .env
```

Rediger `.env`:

```env
ELEVENLABS_API_KEY=din_api_nøkkel_her
ELEVENLABS_AGENT_ID=          # Fylles inn etter steg 4
BACKEND_URL=http://localhost:8000   # Byttes med ngrok-URL for webhooks
```

### 3. Eksponer backend med ngrok (nødvendig for webhooks)

ElevenLabs sin sky-agent må kunne nå backend-en din for å kalle verktøyene. Lokalt gjøres dette med ngrok:

```bash
ngrok http 8000
```

Kopier HTTPS-URL-en (f.eks. `https://abc123.ngrok-free.app`) og sett den som `BACKEND_URL` i `.env`.

### 4. Start backend

```bash
cd backend
uvicorn main:app --reload
```

### 5. Opprett ElevenLabs-agenten

```bash
# PowerShell
Invoke-WebRequest -Method POST -Uri http://localhost:8000/api/setup-agent -UseBasicParsing | Select-Object -ExpandProperty Content

# bash / curl
curl -X POST http://localhost:8000/api/setup-agent
```

Svaret inneholder `agent_id` — legg den inn i `.env` som `ELEVENLABS_AGENT_ID=...` og restart serveren.

> Kjør dette på nytt etter enhver endring i `agent_config.py` for å oppdatere agenten.

### 6. Test i nettleseren

Åpne `http://localhost:8000`, klikk **Ring kundeservice** og gi mikrofonilgang.

---

## Mock-testdata

Prototypen inneholder ferdig testdata du kan bruke under utvikling:

### Ordre

| Ordre-ID | Status |
|---|---|
| `ORD-1001` | Pakket – klar for henting |
| `ORD-1002` | Under behandling |
| `ORD-1003` | Sendt – forventet levering 4. juni |

### Medlemskap

| Identifikator | Beskrivelse |
|---|---|
| `kari@example.com` | Har duplikat-medlemskap (MED-2001 + MED-2002) |
| `per@example.com` | Normalt enkelt-medlemskap |
| `98765432` | Telefonnummer for Kari (finner begge kontoer) |

### Størrelsesguide

Støtter fire kategorier: `dame_overdel`, `dame_bukse`, `herre_overdel`, `herre_bukse`.  
Eksempel: *"Jeg er dame, bryst 90 cm og midje 72 cm"* → anbefaler størrelse M.

---

## Eskalering til ekte kundebehandler

AI-agenten kaller verktøyet `escalate_to_human` og informerer kunden høflig om overføring når:

- Kunden ber eksplisitt om å snakke med et menneske
- Saken gjelder skade, tvist eller juridisk vurdering
- Spørsmålet er utenfor agentens kompetanse (B2B, presse, spesialordre)
- Agenten er usikker og gjetting kan gi feil informasjon

I prototypen vises dette som et rødt banner i UI-et. I produksjon kobles dette til telefonsentralen (f.eks. via Twilio).

---

## Veien videre

- [ ] Koble til ekte ordre- og medlemskapsdatabase
- [ ] Integrere med telefoni via Twilio for ekte innkommende anrop
- [ ] Legg til autentisering av webhook-kall fra ElevenLabs
- [ ] Bytt mock-stemme med en tilpasset norsk stemme i ElevenLabs
- [ ] Logging og analyse av samtaler
