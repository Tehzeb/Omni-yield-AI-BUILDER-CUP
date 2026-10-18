import base64
import logging
import os
import re
from pathlib import Path
from typing import Literal

from dotenv import load_dotenv
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from google import genai
from google.genai import errors
from pydantic import BaseModel, ConfigDict, Field, ValidationError
from starlette.concurrency import run_in_threadpool

load_dotenv(Path(__file__).resolve().with_name(".env"))

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.8-flash").strip()
FRONTEND_ORIGINS = [
    origin.strip()
    for origin in os.getenv(
        "FRONTEND_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000"
    ).split(",")
    if origin.strip()
]
MAX_IMAGE_BYTES = 10 * 1024 * 1024
SUPPORTED_IMAGE_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
    "image/heic",
    "image/heif",
}

app = FastAPI(title="OmniYield API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=FRONTEND_ORIGINS,
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


class Telemetry(BaseModel):
    model_config = ConfigDict(extra="forbid")

    temperature: float | None = Field(default=None, ge=0, allow_inf_nan=False)
    vibration: float | None = Field(default=None, ge=0, allow_inf_nan=False)
    pressure: float | None = Field(default=None, ge=0, allow_inf_nan=False)


class GeminiDiagnosis(BaseModel):
    root_cause: str = Field(min_length=1)
    repair_action: str = Field(min_length=1)
    confidence: Literal["low", "medium", "high"]


class AnalysisResult(GeminiDiagnosis):
    telemetry_flags: list[str]


def gemini_error_detail(status_code: int | None) -> str:
    if status_code in (401, 403):
        return (
            f"Gemini rejected the API key or project access (HTTP {status_code}). "
            "In Google AI Studio, verify the key belongs to a project with the Gemini API enabled "
            "and the required service-account/API permissions."
        )
    if status_code == 404:
        return (
            f"Gemini could not find or use model {GEMINI_MODEL!r} (HTTP 404). "
            "Check GEMINI_MODEL against the models enabled for this API key."
        )
    if status_code == 429:
        return (
            "Gemini quota or rate limit exceeded (HTTP 429). "
            "Check the project's Gemini API quota and billing, then retry later."
        )
    if status_code == 400:
        return (
            "Gemini rejected the request (HTTP 400). Check the uploaded image and request "
            "format; review the backend terminal for Google's error details."
        )
    status = f" (HTTP {status_code})" if status_code is not None else ""
    return (
        f"Gemini API request failed{status}. Check the backend terminal for Google's "
        "error details and verify the API key, project access, and model."
    )


def analyze_telemetry(telemetry: Telemetry) -> list[str]:
    flags = []

    if telemetry.temperature is not None and telemetry.temperature > 85:
        flags.append(
            f"Temperature critical: {telemetry.temperature:g}°C exceeds 85°C threshold"
        )
    if telemetry.vibration is not None and telemetry.vibration > 4.5:
        flags.append(
            f"Vibration critical: {telemetry.vibration:g}mm/s exceeds 4.5mm/s threshold"
        )
    if telemetry.pressure is not None and telemetry.pressure > 150:
        flags.append(
            f"Pressure critical: {telemetry.pressure:g}psi exceeds 150psi threshold"
        )
    if not flags:
        flags.append("All telemetry within nominal range")
    return flags


def build_prompt(
    telemetry: Telemetry, manual_text: str, telemetry_flags: list[str]
) -> str:
    return f"""You are OmniYield, an industrial diagnostic AI agent. You have three inputs:

1. An image of a defective machine part (attached).
2. Live sensor telemetry: {telemetry.model_dump_json(exclude_none=True)}
3. Relevant excerpt from the machine's repair manual:
---
{manual_text}
---

Telemetry analysis flags: {', '.join(telemetry_flags)}

Cross-reference the visual defect in the image with the telemetry readings and the manual excerpt.
Return only a JSON object with root_cause (string), repair_action (string), and confidence (low, medium, or high).
"""


def run_gemini_agent(
    image_bytes: bytes,
    mime_type: str,
    telemetry: Telemetry,
    manual_text: str,
    telemetry_flags: list[str],
) -> GeminiDiagnosis:
    if not GEMINI_API_KEY:
        raise HTTPException(
            status_code=503,
            detail="GEMINI_API_KEY is missing. Set it in backend/.env and restart the server.",
        )
    if not GEMINI_MODEL:
        raise HTTPException(
            status_code=503,
            detail="GEMINI_MODEL is empty. Set it in backend/.env or remove it to use the default model.",
        )

    prompt = build_prompt(telemetry, manual_text, telemetry_flags)

    try:
        with genai.Client(api_key=GEMINI_API_KEY) as client:
            response = client.interactions.create(
                model=GEMINI_MODEL,
                input=[
                    {"type": "text", "text": prompt},
                    {
                        "type": "image",
                        "data": base64.b64encode(image_bytes).decode("utf-8"),
                        "mime_type": mime_type,
                    },
                ],
                response_format={
                    "type": "text",
                    "mime_type": "application/json",
                    "schema": {
                        "type": "object",
                        "properties": {
                            "root_cause": {"type": "string"},
                            "repair_action": {"type": "string"},
                            "confidence": {
                                "type": "string",
                                "enum": ["low", "medium", "high"],
                            },
                        },
                        "required": ["root_cause", "repair_action", "confidence"],
                    },
                },
            )
            raw_text = response.output_text.strip()
    except errors.APIError as exc:
        logging.exception("Gemini API request failed")
        raise HTTPException(
            status_code=502,
            detail=gemini_error_detail(exc.code),
        ) from exc
    except (AttributeError, ValueError) as exc:
        logging.exception("Gemini returned no usable response")
        raise HTTPException(
            status_code=502,
            detail="Gemini returned no usable diagnosis. Try another image or review the backend terminal.",
        ) from exc

    raw_text = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw_text, flags=re.IGNORECASE)
    try:
        return GeminiDiagnosis.model_validate_json(raw_text)
    except ValidationError as exc:
        logging.exception("Gemini response did not match the diagnosis schema")
        raise HTTPException(
            status_code=502,
            detail="Gemini returned a diagnosis in an invalid format. Please retry.",
        ) from exc


@app.get("/")
def health_check() -> dict[str, str]:
    return {"status": "ok", "service": "OmniYield backend"}


@app.post("/analyze", response_model=AnalysisResult)
async def analyze(
    image: UploadFile = File(...),
    telemetry: str = Form(...),
    manual_text: str = Form(""),
) -> AnalysisResult:
    try:
        telemetry_data = Telemetry.model_validate_json(telemetry)
    except (ValidationError, ValueError) as exc:
        raise HTTPException(
            status_code=400,
            detail="telemetry must be a JSON object containing non-negative numeric temperature, vibration, and pressure values.",
        ) from exc

    mime_type = (image.content_type or "").lower()
    if mime_type not in SUPPORTED_IMAGE_TYPES:
        raise HTTPException(
            status_code=400,
            detail="Upload a JPEG, PNG, WebP, HEIC, or HEIF image.",
        )

    image_bytes = await image.read(MAX_IMAGE_BYTES + 1)
    if not image_bytes:
        raise HTTPException(status_code=400, detail="Uploaded image is empty.")
    if len(image_bytes) > MAX_IMAGE_BYTES:
        raise HTTPException(
            status_code=413,
            detail="Image is too large. The maximum supported size is 10 MB.",
        )

    telemetry_flags = analyze_telemetry(telemetry_data)
    diagnosis = await run_in_threadpool(
        run_gemini_agent,
        image_bytes=image_bytes,
        mime_type=mime_type,
        telemetry=telemetry_data,
        manual_text=manual_text.strip() or "No manual excerpt provided.",
        telemetry_flags=telemetry_flags,
    )

    return AnalysisResult(
        **diagnosis.model_dump(),
        telemetry_flags=telemetry_flags,
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)
