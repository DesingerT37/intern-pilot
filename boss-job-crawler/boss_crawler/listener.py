"""API listener for job-list responses."""

from __future__ import annotations

import json
import queue
import re
import time
from typing import Any

from .exceptions import ListenerError


class APIListener:
    """Wrap browser-side network listening behind a stable interface."""

    def __init__(self, page: Any | None = None):
        self.page = page
        self.pattern: str | None = None
        self._compiled_pattern: re.Pattern[str] | None = None
        self._response_queue: queue.Queue[dict[str, Any]] = queue.Queue()
        self._backend_listener: Any | None = None
        self._running = False

    def bind_page(self, page: Any) -> None:
        self.page = page

    def start(self, pattern: str) -> None:
        if not pattern.strip():
            raise ListenerError("pattern cannot be empty")

        self.pattern = pattern
        self._compiled_pattern = re.compile(pattern)
        self._running = True
        self._clear_queue()

        if self.page is None:
            return

        listen_obj = getattr(self.page, "listen", None)
        if listen_obj is None:
            return

        self._backend_listener = listen_obj
        try:
            if hasattr(listen_obj, "start"):
                listen_obj.start(pattern)
            elif callable(listen_obj):
                listen_obj(pattern)
        except Exception as exc:
            raise ListenerError(f"failed to start network listener: {exc}") from exc

    def get_job_response(self, timeout: int | float) -> dict[str, Any]:
        if timeout <= 0:
            raise ListenerError("timeout must be greater than 0")
        if not self._running:
            raise ListenerError("listener has not been started")

        deadline = time.monotonic() + float(timeout)
        while time.monotonic() < deadline:
            queued = self._poll_queue()
            if queued is not None:
                return queued

            captured = self._poll_backend_listener()
            if captured is not None:
                return captured

            time.sleep(0.1)

        raise ListenerError(f"timed out after {timeout}s waiting for job response")

    def stop(self) -> None:
        self._running = False
        backend = self._backend_listener
        self._backend_listener = None
        if backend is not None:
            try:
                if hasattr(backend, "stop"):
                    backend.stop()
            except Exception:
                pass

    def push_response(self, response: Any) -> None:
        """Inject a captured response, mainly for tests and adapters."""
        normalized = self._normalize_response(response)
        self._response_queue.put(normalized)

    def _poll_queue(self) -> dict[str, Any] | None:
        try:
            return self._response_queue.get_nowait()
        except queue.Empty:
            return None

    def _poll_backend_listener(self) -> dict[str, Any] | None:
        backend = self._backend_listener
        if backend is None:
            return None

        for method_name in ("wait", "steps", "next"):
            method = getattr(backend, method_name, None)
            if not callable(method):
                continue
            try:
                if method_name == "wait":
                    payload = method(timeout=0.1)
                else:
                    payload = method()
            except TypeError:
                try:
                    payload = method(0.1)
                except Exception:
                    continue
            except StopIteration:
                return None
            except Exception:
                continue

            if payload is None:
                return None
            try:
                return self._normalize_response(payload)
            except ListenerError:
                continue

        return None

    def _normalize_response(self, response: Any) -> dict[str, Any]:
        if isinstance(response, dict):
            return response

        body_candidates = [
            response,
            getattr(response, "body", None),
            getattr(response, "response", None),
        ]

        nested_response = getattr(response, "response", None)
        if nested_response is not None:
            body_candidates.extend(
                [
                    getattr(nested_response, "body", None),
                    getattr(nested_response, "json", None),
                    getattr(nested_response, "text", None),
                ]
            )

        for candidate in body_candidates:
            normalized = self._coerce_candidate(candidate)
            if normalized is not None:
                return normalized

        raise ListenerError("unable to normalize captured response into JSON data")

    def _coerce_candidate(self, candidate: Any) -> dict[str, Any] | None:
        if candidate is None:
            return None
        if isinstance(candidate, dict):
            return candidate
        if callable(candidate):
            try:
                result = candidate()
            except Exception:
                return None
            return self._coerce_candidate(result)
        if isinstance(candidate, (bytes, bytearray)):
            try:
                return json.loads(candidate.decode("utf-8"))
            except Exception:
                return None
        if isinstance(candidate, str):
            try:
                data = json.loads(candidate)
            except json.JSONDecodeError:
                return None
            return data if isinstance(data, dict) else None
        return None

    def _clear_queue(self) -> None:
        while not self._response_queue.empty():
            try:
                self._response_queue.get_nowait()
            except queue.Empty:
                break
