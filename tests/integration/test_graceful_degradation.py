import os
import socket
import subprocess
import sys
import time
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parents[2]


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def _wait(url: str) -> None:
    for _ in range(50):
        try:
            if httpx.get(url, timeout=1.0).status_code == 200:
                return
        except Exception:
            time.sleep(0.2)
    raise RuntimeError(url)


def test_graceful_degradation():
    account_port = _free_port()
    gateway_port = _free_port()
    account_proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "account_service.main:app", "--host", "127.0.0.1", "--port", str(account_port)],
        cwd=ROOT / "account-service",
        env={**os.environ, "DATABASE_URL": f"sqlite:////tmp/acct-{account_port}.db"},
    )
    try:
        _wait(f"http://127.0.0.1:{account_port}/health")
        gateway_proc = subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "gateway_service.main:app", "--host", "127.0.0.1", "--port", str(gateway_port)],
            cwd=ROOT / "gateway-service",
            env={**os.environ, "DATABASE_URL": f"sqlite:////tmp/gw-{gateway_port}.db", "ACCOUNT_SERVICE_URL": f"http://127.0.0.1:{account_port}"},
        )
        try:
            _wait(f"http://127.0.0.1:{gateway_port}/health")
            client = httpx.Client(base_url=f"http://127.0.0.1:{gateway_port}", timeout=10.0)
            payload = {
                "eventId": "evt-degrade",
                "accountId": "acct-degrade",
                "type": "CREDIT",
                "amount": 25,
                "currency": "USD",
                "eventTimestamp": "2026-05-15T14:02:11Z",
            }
            assert client.post("/events", json=payload).status_code == 201

            account_proc.terminate()
            account_proc.wait(timeout=5)

            fail = client.post("/events", json={
                "eventId": "evt-new-fail",
                "accountId": "acct-degrade",
                "type": "CREDIT",
                "amount": 10,
                "currency": "USD",
                "eventTimestamp": "2026-05-15T15:00:00Z",
            })
            assert fail.status_code == 503
            assert client.get("/events/evt-degrade").status_code == 200
            assert client.get("/events", params={"account": "acct-degrade"}).status_code == 200
        finally:
            gateway_proc.terminate()
            gateway_proc.wait(timeout=5)
    finally:
        if account_proc.poll() is None:
            account_proc.terminate()
            account_proc.wait(timeout=5)
