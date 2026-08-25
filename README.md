# Mote & Mer – AI Kundeservice Prototype

En stemmebasert AI-kundeservice prototype for klesbutikk, bygget med [ElevenLabs Conversational AI](https://elevenlabs.io/conversational-ai) og [FastAPI](https://fastapi.tiangolo.com/). Kunder ringer inn via nettleser, snakker med en norsktalende AI-assistent, og blir automatisk satt over til en ekte kundebehandler ved behov.

---

## Kjapp start (4 steg, ingen forkunnskaper nødvendig)

Åpne PowerShell i prosjektmappen og kjør disse fire tingene, i rekkefølge:

```powershell
# 1. Installer det Python-koden trenger
pip install -r requirements.txt

# 2. Lag din egen .env-fil (mal finnes i .env.example)
Copy-Item .env.example .env
# ...åpne .env i notepad og lim inn din ElevenLabs API-nøkkel

# 3. Start alt sammen automatisk
.\start-demo.ps1

# 4. Åpne nettleseren
start http://localhost:8000
```

Trykk **Ring kundeservice**, gi mikrofontilgang, og snakk med assistenten.

Resten av denne filen er teknisk referanse — hva hver del av koden gjør, hvordan
verktøyene henger sammen, og manuelle steg hvis skriptet over ikke skulle virke.
Du trenger den ikke for å bare teste demoen.

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
      │  WebSocket (ElevenLabs JS SDK) — samme forbindelse begge veier
      ▼
ElevenLabs Conversational AI  ──► Claude (LLM)
      │  client-tool-kall (over WebSocket, tilbake til nettleseren)
      ▼
Nettleseren (frontend/index.html)
      │  fetch() til egen backend på localhost
      ▼
FastAPI backend (Python, kun lokalt)
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
5. Ved behov kaller agenten et **client-tool** over den samme WebSocket-forbindelsen; nettleseren tar imot kallet og slår opp data hos egen backend på `localhost` — ingen offentlig URL eller tunnel (f.eks. ngrok) trengs
6. Ved edge cases trigges `escalate_to_human` og kunden overføres

> **Merk:** Fordi alle verktøy er client-tools, virker dette kun så lenge samtalen går via nettleseren.
> Kobles dette senere til ekte telefoni (Twilio e.l., uten nettleser), må verktøyene tilbake til
> `"webhook"`-type med en permanent, offentlig backend-URL — se "Veien videre".

---

## Prosjektstruktur

```
kundeservice-proto/
├── backend/
│   ├── main.py          # FastAPI-server: API-endepunkter, agent-oppsett, token
│   ├── tools.py         # Logikk for alle verktøy-kall fra ElevenLabs
│   ├── agent_config.py  # Norsk systemprompt + verktøy-definisjoner (client-tools)
│   └── mock_data.py     # Testdata: ordre, medlemskap, størrelsesguide, butikkinfo
├── frontend/
│   └── index.html       # Web-UI med mikrofon-knapp, samtalelogg og eskaleringsvisning
├── .env.example         # Mal for miljøvariabler
├── requirements.txt     # Python-avhengigheter
└── README.md
```

---

## Manuelt oppsett (valgfritt)

**Du trenger ikke lese dette for å kjøre demoen** — det er allerede dekket av
"Kjapp start" helt øverst i denne filen. Denne seksjonen forklarer de samme
fire stegene i detalj, ett og ett, med rene kommandoer i stedet for
`start-demo.ps1`. Bruk den kun hvis du vil forstå hva skriptet faktisk gjør,
eller hvis skriptet av en eller annen grunn ikke fungerer hos deg.

### Forutsetninger

- Python 3.11+
- En [ElevenLabs](https://elevenlabs.io)-konto med API-nøkkel

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
```

### 3. Start backend

```bash
cd backend
uvicorn main:app --reload
```

### 4. Opprett ElevenLabs-agenten

```bash
# PowerShell
Invoke-WebRequest -Method POST -Uri http://localhost:8000/api/setup-agent -UseBasicParsing | Select-Object -ExpandProperty Content

# bash / curl
curl -X POST http://localhost:8000/api/setup-agent
```

Svaret inneholder `agent_id` — legg den inn i `.env` som `ELEVENLABS_AGENT_ID=...` og restart serveren.

> Kjør dette på nytt etter enhver endring i `agent_config.py` for å oppdatere agenten.

### 5. Test i nettleseren

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
- [ ] Integrere med telefoni via Twilio for ekte innkommende anrop — merk: da må
      verktøyene i `agent_config.py` gjøres om tilbake fra `"client"` til
      `"webhook"` (siden det ikke finnes noen nettleser i en ekte telefonsamtale),
      og backend må ha en permanent, offentlig URL i stedet for kun `localhost`
- [ ] Legg til autentisering av webhook-kall fra ElevenLabs (relevant igjen den
      dagen verktøyene er webhook-basert)
- [ ] Bytt mock-stemme med en tilpasset norsk stemme i ElevenLabs
- [ ] Logging og analyse av samtaler
