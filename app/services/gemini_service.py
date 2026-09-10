"""
Gemini AI service — tenant screening, maintenance triage, lease summaries.

Every call is logged to MongoDB (`ai_logs` collection) with the raw prompt,
raw response, parsed JSON, and metadata (model name, timestamp, latency).

If GEMINI_API_KEY is not set in .env, all functions raise a clear HTTPException
so the UI can show "AI not configured" instead of crashing.
"""
import json
import time
from datetime import datetime, timezone
from typing import Dict, Any

from fastapi import HTTPException

from app.core.config import settings
from app.core.database import mongodb_db


# ---------- Client init (lazy, optional) ----------
_client = None


def _get_client():
    global _client
    if not settings.gemini_api_key:
        raise HTTPException(
            status_code=503,
            detail="Gemini API key not configured. Add GEMINI_API_KEY to .env",
        )
    if _client is None:
        try:
            from google import genai
        except ImportError:
            raise HTTPException(
                status_code=500,
                detail="google-genai not installed. Run: pip install google-genai",
            )
        _client = genai.Client(api_key=settings.gemini_api_key)
    return _client


# ---------- Mongo logging ----------
async def _log(kind: str, payload: Dict[str, Any], raw_prompt: str,
               raw_response: str, parsed: Dict, latency_ms: int) -> None:
    try:
        await mongodb_db["ai_logs"].insert_one({
            "kind": kind,
            "input": payload,
            "raw_prompt": raw_prompt,
            "raw_response": raw_response,
            "parsed": parsed,
            "model": settings.gemini_model,
            "latency_ms": latency_ms,
            "timestamp": datetime.now(timezone.utc),
        })
    except Exception as e:
        # Don't let a logging failure break the response
        print(f"[gemini] mongo log failed: {e}")


# ---------- Core call helper ----------
def _generate_json(prompt: str):
    """Call Gemini with JSON response mode. Returns (raw_text, parsed_dict)."""
    from google.genai import types

    client = _get_client()
    response = client.models.generate_content(
        model=settings.gemini_model,
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.2,
            response_mime_type="application/json",
        ),
    )
    raw = response.text

    # Strip markdown fences if Gemini ignores the mime hint
    text = raw.strip()
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
        text = text.strip()

    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        parsed = {"error": "invalid_json", "raw": raw}

    return raw, parsed


# ---------- 1. Tenant screening ----------
async def screen_tenant(application: Dict, room: Dict) -> Dict:
    """
    Score a rental applicant against a room listing.
    Returns:
      {
        "score": 0-100,
        "verdict": "approve" | "review" | "reject",
        "strengths": [...],
        "concerns": [...],
        "summary": "..."
      }
    """
    prompt = f"""You are a rental tenant screening assistant. Evaluate the applicant against the room listing and return ONLY valid JSON matching this schema:

{{
  "score": <integer 0-100>,
  "verdict": "approve" | "review" | "reject",
  "strengths": [<string>, ...],
  "concerns": [<string>, ...],
  "summary": <string, max 3 sentences, no markdown>
}}

Rule of thumb:
- score >= 75 -> approve
- 50-74 -> review
- < 50 -> reject

APPLICANT:
- Full name: {application.get('full_name', 'N/A')}
- Monthly income: {application.get('monthly_income', 'N/A')}
- Employment: {application.get('employment', 'N/A')}
- References: {application.get('references', [])}
- Notes: {application.get('notes', '')}

ROOM:
- Room number: {room.get('room_number', 'N/A')}
- Monthly rent: {room.get('monthly_rent', 'N/A')}
- Room type: {room.get('room_type', 'N/A')}
- Deposit: {room.get('deposit_amount', 'N/A')}
"""

    t0 = time.time()
    raw, parsed = _generate_json(prompt)
    latency = int((time.time() - t0) * 1000)

    await _log("tenant_screening",
               {"application": application, "room": room},
               prompt, raw, parsed, latency)
    return parsed


# ---------- 2. Maintenance triage ----------
async def classify_maintenance(title: str, description: str) -> Dict:
    """
    Classify a maintenance ticket.
    Returns:
      {
        "priority": "low" | "normal" | "high" | "urgent",
        "category": "plumbing" | "electrical" | "structural" | "appliance" | "other",
        "suggested_action": "..."
      }
    """
    prompt = f"""Classify this maintenance request and return ONLY valid JSON matching this schema:

{{
  "priority": "low" | "normal" | "high" | "urgent",
  "category": "plumbing" | "electrical" | "structural" | "appliance" | "other",
  "suggested_action": <string, one sentence>
}}

Guidance:
- urgent: safety hazard, flooding, no power, no water
- high: major malfunction affecting daily life
- normal: standard repairs
- low: cosmetic or minor

Title: {title}
Description: {description}
"""

    t0 = time.time()
    raw, parsed = _generate_json(prompt)
    latency = int((time.time() - t0) * 1000)

    await _log("maintenance_classify",
               {"title": title, "description": description},
               prompt, raw, parsed, latency)
    return parsed


# ---------- 3. Lease summary ----------
async def draft_lease_summary(lease: Dict, tenant: Dict, room: Dict) -> Dict:
    """
    Plain-English summary of a lease.
    Returns:
      {
        "headline": "...",
        "plain_english_summary": "...",
        "key_obligations": [...],
        "risks": [...]
      }
    """
    prompt = f"""Draft a plain-English lease summary for the tenant. Return ONLY valid JSON matching this schema:

{{
  "headline": <string, max 8 words>,
  "plain_english_summary": <string, max 4 sentences, no legal jargon>,
  "key_obligations": [<string>, ...],
  "risks": [<string>, ...]
}}

LEASE:
{json.dumps({k: str(v) for k, v in lease.items() if not k.startswith('_')}, indent=2)}

TENANT:
{json.dumps({k: str(v) for k, v in tenant.items() if not k.startswith('_')}, indent=2)}

ROOM:
{json.dumps({k: str(v) for k, v in room.items() if not k.startswith('_')}, indent=2)}
"""

    t0 = time.time()
    raw, parsed = _generate_json(prompt)
    latency = int((time.time() - t0) * 1000)

    await _log("lease_summary",
               {"lease_id": lease.get("id"), "tenant_id": tenant.get("id"),
                "room_id": room.get("id")},
               prompt, raw, parsed, latency)
    return parsed