import asyncio
import base64
import io
import json
import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from fastapi import HTTPException, UploadFile
from google.genai.errors import APIError
from starlette.datastructures import Headers

import main


def make_upload(
    content: bytes = b"image-bytes", content_type: str = "image/png"
) -> UploadFile:
    return UploadFile(
        filename="part.png",
        file=io.BytesIO(content),
        headers=Headers({"content-type": content_type}),
    )


class TelemetryTests(unittest.TestCase):
    def test_flags_each_out_of_range_reading(self):
        telemetry = main.Telemetry(
            temperature=86,
            vibration=4.6,
            pressure=151,
        )

        flags = main.analyze_telemetry(telemetry)

        self.assertEqual(len(flags), 3)
        self.assertIn("Temperature critical", flags[0])
        self.assertIn("Vibration critical", flags[1])
        self.assertIn("Pressure critical", flags[2])

    def test_reports_nominal_values(self):
        telemetry = main.Telemetry(
            temperature=85,
            vibration=4.5,
            pressure=150,
        )

        self.assertEqual(
            main.analyze_telemetry(telemetry),
            ["All telemetry within nominal range"],
        )


class AnalyzeEndpointTests(unittest.TestCase):
    def test_successful_analysis_returns_contract_and_flags(self):
        diagnosis = main.GeminiDiagnosis(
            root_cause="Worn bearing",
            repair_action="Replace the bearing",
            confidence="medium",
        )
        with patch(
            "main.run_in_threadpool",
            new_callable=AsyncMock,
            return_value=diagnosis,
        ) as run_agent:
            response = asyncio.run(
                main.analyze(
                    make_upload(),
                    json.dumps({"temperature": 90, "vibration": 1, "pressure": 100}),
                    "Inspect the bearing.",
                )
            )

        self.assertEqual(response.root_cause, "Worn bearing")
        self.assertEqual(response.repair_action, "Replace the bearing")
        self.assertEqual(response.confidence, "medium")
        self.assertEqual(len(response.telemetry_flags), 1)
        run_agent.assert_awaited_once()

    def test_rejects_invalid_telemetry(self):
        for telemetry in ("not-json", '{"temperature": -1}', "[]"):
            with self.subTest(telemetry=telemetry):
                with self.assertRaises(HTTPException) as raised:
                    asyncio.run(main.analyze(make_upload(), telemetry, ""))
                self.assertEqual(raised.exception.status_code, 400)

    def test_rejects_unsupported_image_type(self):
        with self.assertRaises(HTTPException) as raised:
            asyncio.run(main.analyze(make_upload(content_type="text/plain"), "{}", ""))
        self.assertEqual(raised.exception.status_code, 400)

    def test_rejects_empty_image(self):
        with self.assertRaises(HTTPException) as raised:
            asyncio.run(main.analyze(make_upload(content=b""), "{}", ""))
        self.assertEqual(raised.exception.status_code, 400)

    def test_rejects_oversized_image(self):
        large_upload = make_upload(content=b"x" * (main.MAX_IMAGE_BYTES + 1))
        with self.assertRaises(HTTPException) as raised:
            asyncio.run(main.analyze(large_upload, "{}", ""))
        self.assertEqual(raised.exception.status_code, 413)


class GeminiAgentTests(unittest.TestCase):
    def test_missing_key_returns_actionable_error(self):
        with patch.object(main, "GEMINI_API_KEY", ""):
            with self.assertRaises(HTTPException) as raised:
                main.run_gemini_agent(
                    b"image",
                    "image/png",
                    main.Telemetry(),
                    "",
                    [],
                )
        self.assertEqual(raised.exception.status_code, 503)
        self.assertIn("backend/.env", raised.exception.detail)

    def test_parses_structured_model_response(self):
        expected = {
            "root_cause": "Worn bearing",
            "repair_action": "Replace bearing",
            "confidence": "high",
        }

        class FakeModel:
            def create(self, **kwargs):
                self.request = kwargs
                return SimpleNamespace(output_text=json.dumps(expected))

        class FakeClient:
            def __init__(self, **_kwargs):
                self.interactions = fake_model

            def __enter__(self):
                return self

            def __exit__(self, *_args):
                return False
        fake_model = FakeModel()
        fake_client = FakeClient()
        fake_genai = SimpleNamespace(Client=lambda **_kwargs: fake_client)
        with (
            patch.object(main, "genai", fake_genai),
            patch.object(main, "GEMINI_API_KEY", "test-key"),
        ):
            response = main.run_gemini_agent(
                b"image",
                "image/png",
                main.Telemetry(temperature=90),
                "Manual text",
                ["High temperature"],
            )

        self.assertEqual(response.model_dump(), expected)
        self.assertEqual(fake_model.request["model"], "gemini-3.8-flash")
        self.assertEqual(
            fake_model.request["input"][1]["data"],
            base64.b64encode(b"image").decode("utf-8"),
        )
        self.assertEqual(fake_model.request["input"][1]["mime_type"], "image/png")
        self.assertEqual(
            fake_model.request["response_format"]["mime_type"], "application/json"
        )
        self.assertEqual(
            fake_model.request["response_format"]["schema"]["properties"][
                "confidence"
            ]["enum"],
            ["low", "medium", "high"],
        )

    def test_provider_failures_become_actionable_gateway_errors(self):
        cases = {
            403: "Gemini rejected the API key or project access",
            404: "could not find or use model",
            429: "quota or rate limit exceeded",
            503: "HTTP 503",
        }

        for status_code, message in cases.items():
            with self.subTest(status_code=status_code):

                class FailingModel:
                    def create(self, **_kwargs):
                        raise APIError(
                            status_code,
                            {"error": {"message": "simulated provider failure"}},
                        )

                class FakeClient:
                    def __init__(self, **_kwargs):
                        self.interactions = FailingModel()

                    def __enter__(self):
                        return self

                    def __exit__(self, *_args):
                        return False

                fake_genai = SimpleNamespace(Client=FakeClient)
                with (
                    patch.object(main, "genai", fake_genai),
                    patch.object(main, "GEMINI_API_KEY", "test-key"),
                    self.assertLogs(level="ERROR"),
                ):
                    with self.assertRaises(HTTPException) as raised:
                        main.run_gemini_agent(
                            b"image",
                            "image/png",
                            main.Telemetry(),
                            "",
                            [],
                        )

                self.assertEqual(raised.exception.status_code, 502)
                self.assertIn(message, raised.exception.detail)

    def test_invalid_model_json_is_not_returned_as_success(self):
        class FakeModel:
            def create(self, **_kwargs):
                return SimpleNamespace(output_text="not-json")

        class FakeClient:
            def __init__(self, **_kwargs):
                self.interactions = FakeModel()

            def __enter__(self):
                return self

            def __exit__(self, *_args):
                return False

        fake_genai = SimpleNamespace(Client=FakeClient)
        with (
            patch.object(main, "genai", fake_genai),
            patch.object(main, "GEMINI_API_KEY", "test-key"),
            self.assertLogs(level="ERROR"),
        ):
            with self.assertRaises(HTTPException) as raised:
                main.run_gemini_agent(
                    b"image",
                    "image/png",
                    main.Telemetry(),
                    "",
                    [],
                )

        self.assertEqual(raised.exception.status_code, 502)


if __name__ == "__main__":
    unittest.main()
