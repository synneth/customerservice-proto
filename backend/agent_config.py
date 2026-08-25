"""ElevenLabs Conversational AI agent definition — tools and system prompt."""

SYSTEM_PROMPT = """Du er en vennlig og profesjonell kundeserviceassistent for klesbutikken Mote & Mer.
Du hjelper kunder som ringer inn med vanlige henvendelser.

## Hva du kan hjelpe med
- Informasjon om butikken (åpningstider, adresse, telefon)
- Retur- og bytteregler
- Reklamasjonsregler
- Ordrestatus (kunden oppgir ordre-ID, f.eks. ORD-1001)
- Størrelsesanbefaling basert på mål kunden har tatt
- Medlemskap: finne medlemskap, endre e-post, slette duplikat

## Viktige retningslinjer
- Snakk alltid norsk, vær vennlig og klar.
- Spør etter nødvendig informasjon steg for steg – ikke still flere spørsmål samtidig.
- Hvis kunden spør om noe du kan svare på direkte (åpningstider, returregler), bruk riktig verktøy.
- For størrelsesguide: spør kunden om kategori (dame overdel, dame bukse, herre overdel, herre bukse) og relevante mål i cm.
- For ordrestatus: be kunden oppgi ordre-ID (format ORD-XXXX).
- For medlemskap: be om e-post eller telefonnummer for å slå opp kontoen.

## Eskalering til ekte kundebehandler
Bruk verktøyet `escalate_to_human` når:
- Kunden er misfornøyd og vil snakke med en leder
- Saken gjelder en spesifikk skade eller tvist som krever manuell vurdering
- Spørsmålet er utenfor din kompetanse (f.eks. spesielle B2B-ordrer, pressesaker)
- Kunden ber eksplisitt om å snakke med et menneske
- Du er usikker på svaret og gjetting kan gi feil informasjon

Når du eskalerer: informer kunden høflig om at du setter dem over til en kundebehandler,
og at de ikke trenger å forklare saken på nytt.

## Tone
Vær som en dyktig, rolig og løsningsorientert butikkansatt. Ikke vær overdrevent entusiastisk.
Hold svarene konsise – kunden ringer, de vil ha raskt svar.
"""

# Alle verktøy under er "client"-tools: de kjøres av frontend/index.html over
# WebSocket-forbindelsen som uansett er åpen for stemmesamtalen, og trenger
# derfor IKKE at backend er nåbar fra internett. Det er grunnen til at
# ngrok ikke lenger trengs for å kjøre demoen lokalt.
#
# Frontend sin generiske proxy-handler kaller backend sin egen /tools/<navn>
# på localhost (samme maskin, samme nettleser — ingen tunnel nødvendig) og
# sender svaret tilbake til agenten.
#
# NB: dette fungerer fordi demoen kjører i nettleseren. Hvis dette senere
# kobles til ekte telefoni (Twilio e.l. uten nettleser), må disse tilbake
# til "webhook"-type med en permanent, offentlig backend-URL — se README.

TOOLS = [
    {
        "type": "client",
        "name": "get_store_info",
        "description": "Henter butikkens adresse, telefon og åpningstider.",
        "expects_response": True,
        "parameters": {"type": "object", "properties": {}, "required": []},
    },
    {
        "type": "client",
        "name": "get_return_policy",
        "description": "Henter informasjon om butikkens retur- og bytteregler.",
        "expects_response": True,
        "parameters": {"type": "object", "properties": {}, "required": []},
    },
    {
        "type": "client",
        "name": "get_complaint_policy",
        "description": "Henter reklamasjonsreglene (forbrukerkjøpsloven, 2-årsrett osv.).",
        "expects_response": True,
        "parameters": {"type": "object", "properties": {}, "required": []},
    },
    {
        "type": "client",
        "name": "check_order",
        "description": "Slår opp status på en kundeordre basert på ordre-ID.",
        "expects_response": True,
        "parameters": {
            "type": "object",
            "properties": {
                "order_id": {"type": "string", "description": "Ordre-ID, f.eks. ORD-1001"}
            },
            "required": ["order_id"],
        },
    },
    {
        "type": "client",
        "name": "get_size_recommendation",
        "description": "Anbefaler riktig klesstr. basert på kroppsmål kunden har tatt.",
        "expects_response": True,
        "parameters": {
            "type": "object",
            "properties": {
                "category": {
                    "type": "string",
                    "description": "Kategori: dame_overdel, dame_bukse, herre_overdel, herre_bukse",
                    "enum": ["dame_overdel", "dame_bukse", "herre_overdel", "herre_bukse"],
                },
                "measurements": {
                    "type": "object",
                    "description": "Mål i cm, f.eks. {\"bryst_cm\": 90, \"midje_cm\": 72}",
                },
            },
            "required": ["category", "measurements"],
        },
    },
    {
        "type": "client",
        "name": "lookup_membership",
        "description": "Slår opp kundens medlemskap basert på e-post eller telefonnummer.",
        "expects_response": True,
        "parameters": {
            "type": "object",
            "properties": {
                "identifier": {"type": "string", "description": "E-post eller telefonnummer"}
            },
            "required": ["identifier"],
        },
    },
    {
        "type": "client",
        "name": "update_membership_email",
        "description": "Oppdaterer e-postadressen knyttet til et medlemskap.",
        "expects_response": True,
        "parameters": {
            "type": "object",
            "properties": {
                "membership_id": {"type": "string", "description": "Medlemskaps-ID, f.eks. MED-2001"},
                "new_email": {"type": "string", "description": "Ny e-postadresse"},
            },
            "required": ["membership_id", "new_email"],
        },
    },
    {
        "type": "client",
        "name": "merge_duplicate_memberships",
        "description": "Sletter et duplikat-medlemskap og overfører poeng til det primære.",
        "expects_response": True,
        "parameters": {
            "type": "object",
            "properties": {
                "keep_id": {"type": "string", "description": "Medlemskaps-ID som skal beholdes"},
                "delete_id": {"type": "string", "description": "Medlemskaps-ID som skal slettes"},
            },
            "required": ["keep_id", "delete_id"],
        },
    },
    {
        # Egen kommentar bevart: dette var det første verktøyet som ble gjort om
        # til "client" fordi frontend viser et eget rødt banner for denne — se
        # clientTools.escalate_to_human i frontend/index.html.
        "type": "client",
        "name": "escalate_to_human",
        "description": "Setter kunden over til en ekte kundebehandler når AI ikke kan hjelpe. Viser en eskaleringsvisning i kundens nettleser.",
        "expects_response": True,
        "parameters": {
            "type": "object",
            "properties": {
                "reason": {"type": "string", "description": "Kort forklaring på hvorfor saken eskaleres"}
            },
            "required": ["reason"],
        },
    },
]
