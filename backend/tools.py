"""Tool handlers called by the ElevenLabs agent via webhook."""

from __future__ import annotations
from typing import Any
from mock_data import ORDERS, MEMBERSHIPS, STORE_INFO, SIZE_GUIDE


def get_store_info() -> dict[str, Any]:
    info = STORE_INFO
    hours_lines = "\n".join(f"  {day}: {time}" for day, time in info["hours"].items())
    return {
        "butikk": info["name"],
        "adresse": info["address"],
        "telefon": info["phone"],
        "åpningstider": hours_lines,
    }


def get_return_policy() -> dict[str, str]:
    return {"returregler": STORE_INFO["return_policy"]}


def get_complaint_policy() -> dict[str, str]:
    return {"reklamasjonsregler": STORE_INFO["complaint_policy"]}


def check_order(order_id: str) -> dict[str, Any]:
    order_id = order_id.strip().upper()
    order = ORDERS.get(order_id)
    if not order:
        return {"funnet": False, "melding": f"Fant ingen ordre med ID {order_id}."}
    return {
        "funnet": True,
        "ordre_id": order["id"],
        "status": order["status"],
        "varer": ", ".join(order["items"]),
        "klar_for_henting": order["ready_for_pickup"],
    }


def get_size_recommendation(category: str, measurements: dict[str, float]) -> dict[str, Any]:
    """
    category: 'dame_overdel' | 'dame_bukse' | 'herre_overdel' | 'herre_bukse'
    measurements: dict with keys matching the guide columns (e.g. bryst_cm, midje_cm, hofte_cm)
    """
    guide = SIZE_GUIDE.get(category)
    if not guide:
        return {
            "funnet": False,
            "melding": f"Ukjent kategori '{category}'. Gyldige: {', '.join(SIZE_GUIDE.keys())}",
        }

    def in_range(value: float, range_str: str) -> bool:
        try:
            low, high = map(float, range_str.replace(" ", "").split("–"))
            return low <= value <= high
        except Exception:
            return False

    matches = []
    for row in guide:
        score = 0
        total = 0
        for key, val in measurements.items():
            if key in row:
                total += 1
                if in_range(val, row[key]):
                    score += 1
        if total > 0 and score == total:
            matches.append(row["størrelse"])

    if matches:
        return {"anbefalt_størrelse": matches[0], "alle_treff": matches}
    # Partial match fallback
    return {
        "funnet": False,
        "melding": (
            "Målene passer ikke eksakt i noen størrelse. "
            "Prøv gjerne to størrelser eller kontakt oss i butikk."
        ),
    }


def lookup_membership(identifier: str) -> dict[str, Any]:
    """Look up membership by email or phone."""
    identifier = identifier.strip().lower()
    found = [
        m for m in MEMBERSHIPS.values()
        if m["email"].lower() == identifier or m["phone"] == identifier
    ]
    if not found:
        return {"funnet": False, "melding": "Fant ingen medlemskap med denne e-posten eller telefonnummeret."}

    duplicates = [m for m in found if "duplicate_of" in m]
    primary = [m for m in found if "duplicate_of" not in m]

    result: dict[str, Any] = {"funnet": True, "antall_medlemskap": len(found)}
    if primary:
        p = primary[0]
        result["primært_medlemskap"] = {
            "id": p["id"],
            "navn": p["name"],
            "e-post": p["email"],
            "poeng": p["points"],
            "nivå": p["tier"],
        }
    if duplicates:
        result["duplikat_oppdaget"] = True
        result["duplikater"] = [{"id": d["id"], "e-post": d["email"], "poeng": d["points"]} for d in duplicates]

    return result


def update_membership_email(membership_id: str, new_email: str) -> dict[str, Any]:
    membership_id = membership_id.strip().upper()
    if membership_id not in MEMBERSHIPS:
        return {"suksess": False, "melding": f"Fant ikke medlemskap {membership_id}."}
    old_email = MEMBERSHIPS[membership_id]["email"]
    MEMBERSHIPS[membership_id]["email"] = new_email.strip()
    return {
        "suksess": True,
        "melding": f"E-post oppdatert fra {old_email} til {new_email.strip()} for medlemskap {membership_id}.",
    }


def merge_duplicate_memberships(keep_id: str, delete_id: str) -> dict[str, Any]:
    keep_id = keep_id.strip().upper()
    delete_id = delete_id.strip().upper()
    if keep_id not in MEMBERSHIPS or delete_id not in MEMBERSHIPS:
        return {"suksess": False, "melding": "Ett eller begge medlemskaps-IDer ble ikke funnet."}
    points_transferred = MEMBERSHIPS[delete_id]["points"]
    MEMBERSHIPS[keep_id]["points"] += points_transferred
    del MEMBERSHIPS[delete_id]
    return {
        "suksess": True,
        "melding": (
            f"Medlemskap {delete_id} er slettet og {points_transferred} poeng er overført til {keep_id}. "
            f"Totale poeng på {keep_id}: {MEMBERSHIPS[keep_id]['points']}."
        ),
    }


def escalate_to_human(reason: str) -> dict[str, str]:
    """Called when the AI cannot handle the request and must transfer to a human agent."""
    return {
        "handling": "ESKALERT",
        "melding": f"Kunden settes over til en kundebehandler. Årsak: {reason}",
    }


TOOL_HANDLERS: dict[str, Any] = {
    "get_store_info": lambda params: get_store_info(),
    "get_return_policy": lambda params: get_return_policy(),
    "get_complaint_policy": lambda params: get_complaint_policy(),
    "check_order": lambda params: check_order(params.get("order_id", "")),
    "get_size_recommendation": lambda params: get_size_recommendation(
        params.get("category", ""), params.get("measurements", {})
    ),
    "lookup_membership": lambda params: lookup_membership(params.get("identifier", "")),
    "update_membership_email": lambda params: update_membership_email(
        params.get("membership_id", ""), params.get("new_email", "")
    ),
    "merge_duplicate_memberships": lambda params: merge_duplicate_memberships(
        params.get("keep_id", ""), params.get("delete_id", "")
    ),
    "escalate_to_human": lambda params: escalate_to_human(params.get("reason", "")),
}
