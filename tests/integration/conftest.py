import os
import socket
import subprocess
import sys
import time
from pathlib import Path

import httpx
import pytest

ROOT = Path(__file__).resolve().parents[2]
ACCOUNT_DIR = ROOT / "account-service"
GATEWAY_DIR = ROOT / "gateway-service"


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def _wait_for_url(url: str, timeout: float = 15.0) -> None:
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            r = httpx.get(url, timeout=1.0)
            if r.status_code == 200:
                return
        except Exception:
            time.sleep(0.2)
    raise RuntimeError(f"Service not ready: {url}")


@pytest.fixture(scope="session")
def running_services():
    account_port = _free_port()
    gateway_port = _free_port()
    account_db = f"/tmp/account-e2e-{account_port}.db"
    gateway_db = f"/tmp/gateway-e2e-{gateway_port}.db"

    account_env = os.environ.copy()
    account_env.update({
        "DATABASE_URL": f"sqlite:///{account_db}",
        "PORT": str(account_port),
    })
    gateway_env = os.environ.copy()
    gateway_env.update({
        "DATABASE_URL": f"sqlite:///{gateway_db}",
        "ACCOUNT_SERVICE_URL": f"http://127.0.0.1:{account_port}",
        "PORT": str(gateway_port),
    })

    account_proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "account_service.main:app", "--host", "127.0.0.1", "--port", str(account_port)],
        cwd=ACCOUNT_DIR,
        env=account_env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    gateway_proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "gateway_service.main:app", "--host", "127.0.0.1", "--port", str(gateway_port)],
        cwd=GATEWAY_DIR,
        env=gateway_env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    try:
        _wait_for_url(f"http://127.0.0.1:{account_port}/health")
        _wait_for_url(f"http://127.0.0.1:{gateway_port}/health")
        yield {
            "account_port": account_port,
            "gateway_port": gateway_port,
            "gateway_url": f"http://127.0.0.1:{gateway_port}",
            "account_url": f"http://127.0.0.1:{account_port}",
            "account_proc": account_proc,
            "gateway_proc": gateway_proc,
        }
    finally:
        gateway_proc.terminate()
        account_proc.terminate()
        gateway_proc.wait(timeout=5)
        account_proc.wait(timeout=5)


@pytest.fixture()
def gateway_client(running_services):
    with httpx.Client(base_url=running_services["gateway_url"], timeout=10.0) as client:
        yield client


@pytest.fixture()
def account_client(running_services):
    with httpx.Client(base_url=running_services["account_url"], timeout=10.0) as client:
        yield client
