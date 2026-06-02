"""Mock data for orders and memberships — replace with real DB/API calls in production."""

ORDERS = {
    "ORD-1001": {
        "id": "ORD-1001",
        "customer_name": "Lise Eriksen",
        "email": "lise@example.com",
        "status": "Pakket – klar for henting",
        "items": ["Sort jakke str. M", "Blå jeans str. 28/32"],
        "created": "2026-05-28",
        "ready_for_pickup": True,
    },
    "ORD-1002": {
        "id": "ORD-1002",
        "customer_name": "Jonas Berg",
        "email": "jonas@example.com",
        "status": "Under behandling",
        "items": ["Rød genser str. L"],
        "created": "2026-06-01",
        "ready_for_pickup": False,
    },
    "ORD-1003": {
        "id": "ORD-1003",
        "customer_name": "Maria Dahl",
        "email": "maria@example.com",
        "status": "Sendt – forventet levering 4. juni",
        "items": ["Hvit kjole str. S", "Beige bukse str. 36"],
        "created": "2026-05-30",
        "ready_for_pickup": False,
    },
}

MEMBERSHIPS = {
    "MED-2001": {
        "id": "MED-2001",
        "name": "Kari Nilsen",
        "email": "kari@example.com",
        "phone": "98765432",
        "points": 340,
        "tier": "Sølv",
        "active": True,
    },
    "MED-2002": {
        "id": "MED-2002",
        "name": "Kari Nilsen",
        "email": "kari.gammel@example.com",
        "phone": "98765432",
        "points": 20,
        "tier": "Basis",
        "active": True,
        "duplicate_of": "MED-2001",
    },
    "MED-2003": {
        "id": "MED-2003",
        "name": "Per Hansen",
        "email": "per@example.com",
        "phone": "91234567",
        "points": 150,
        "tier": "Basis",
        "active": True,
    },
}

STORE_INFO = {
    "name": "Mote & Mer",
    "address": "Storgata 12, 0155 Oslo",
    "phone": "22 11 22 11",
    "hours": {
        "mandag–fredag": "10:00–19:00",
        "lørdag": "10:00–18:00",
        "søndag": "12:00–17:00",
    },
    "return_policy": (
        "Varer kan returneres innen 30 dager med kvittering. "
        "Ubrukte varer med prislapp returnereres for full refusjon. "
        "Salgsvarervarer kan kun byttes, ikke refunderes. "
        "Retur skjer i butikk eller per post (porto dekkes av kunden ved postreturnering)."
    ),
    "complaint_policy": (
        "Reklamasjon følger forbrukerkjøpsloven. Du har 2 års reklamasjonsrett på feil og mangler "
        "som eksisterte ved kjøpstidspunktet. Reklamasjon meldes i butikk med kvittering. "
        "Vi tilbyr reparasjon, ombytting eller refusjon etter avtale. "
        "Vanlig slitasje dekkes ikke av reklamasjonsretten."
    ),
}

SIZE_GUIDE = {
    "dame_overdel": [
        {"størrelse": "XS", "bryst_cm": "80–84", "midje_cm": "62–66"},
        {"størrelse": "S",  "bryst_cm": "84–88", "midje_cm": "66–70"},
        {"størrelse": "M",  "bryst_cm": "88–92", "midje_cm": "70–74"},
        {"størrelse": "L",  "bryst_cm": "92–96", "midje_cm": "74–78"},
        {"størrelse": "XL", "bryst_cm": "96–102","midje_cm": "78–84"},
        {"størrelse": "XXL","bryst_cm": "102–110","midje_cm": "84–92"},
    ],
    "dame_bukse": [
        {"størrelse": "34", "hofte_cm": "88–90",  "midje_cm": "66–68"},
        {"størrelse": "36", "hofte_cm": "90–94",  "midje_cm": "68–72"},
        {"størrelse": "38", "hofte_cm": "94–98",  "midje_cm": "72–76"},
        {"størrelse": "40", "hofte_cm": "98–102", "midje_cm": "76–80"},
        {"størrelse": "42", "hofte_cm": "102–108","midje_cm": "80–86"},
        {"størrelse": "44", "hofte_cm": "108–114","midje_cm": "86–92"},
    ],
    "herre_overdel": [
        {"størrelse": "S",  "bryst_cm": "88–92", "skulder_cm": "43–44"},
        {"størrelse": "M",  "bryst_cm": "92–96", "skulder_cm": "44–46"},
        {"størrelse": "L",  "bryst_cm": "96–100","skulder_cm": "46–48"},
        {"størrelse": "XL", "bryst_cm": "100–106","skulder_cm": "48–50"},
        {"størrelse": "XXL","bryst_cm": "106–114","skulder_cm": "50–52"},
    ],
    "herre_bukse": [
        {"størrelse": "28/30", "midje_cm": "71–73", "hofte_cm": "91–93"},
        {"størrelse": "30/32", "midje_cm": "76–78", "hofte_cm": "96–98"},
        {"størrelse": "32/32", "midje_cm": "81–83", "hofte_cm": "101–103"},
        {"størrelse": "34/32", "midje_cm": "86–88", "hofte_cm": "106–108"},
        {"størrelse": "36/32", "midje_cm": "91–93", "hofte_cm": "111–113"},
    ],
}
