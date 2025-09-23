from flask import Blueprint, request, jsonify, abort, current_app
import os, re, hmac, hashlib

bp_ar = Blueprint("ar_webhook", __name__)

def _extract_phone(payload: dict) -> str | None:
    keys = [
        "phone","sender","sender_number","senderId","sender_id",
        "chat_id","chatId","from","numero","wa_id"
    ]
    for k in keys:
        v = payload.get(k)
        if not v:
            continue
        m = re.search(r"\d{6,}", str(v))
        if m:
            return m.group(0)
    return None

def _check_bearer():
    auth = request.headers.get("Authorization", "")
    if "Bearer " not in auth:
        abort(401)
    token = auth.split("Bearer ", 1)[-1].strip()
    if not token or token != os.environ.get("AR_BEARER", ""):
        abort(401)

def _check_hmac_if_present():
    sig = request.headers.get("X-AR-Signature")
    if not sig:
        return
    raw = request.get_data()
    secret = os.environ.get("AR_SECRET", "")
    calc = hmac.new(secret.encode(), raw, hashlib.sha256).hexdigest()
    if not hmac.compare_digest(calc, sig):
        abort(401)

@bp_ar.post("/v1/wa/autoresponder")
def autoresponder_hook():
    _check_bearer()
    _check_hmac_if_present()

    try:
        data = request.get_json(force=True, silent=False)
    except Exception:
        abort(400)

    phone = _extract_phone(data) or ""
    msg = (data.get("message") or "").strip()

    if not msg:
        return jsonify(["Mensaje vacio."]), 200

    respuesta = f"Recibido {phone}: {msg}"
    return jsonify([respuesta]), 200


