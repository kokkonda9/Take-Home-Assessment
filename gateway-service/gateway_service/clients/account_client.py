import httpx
import structlog
from httpx import HTTPStatusError, RequestError, TimeoutException
from tenacity import (
    retry,
    retry_if_exception,
    stop_after_attempt,
    wait_exponential,
    wait_random,
)

from gateway_service.config import settings
from gateway_service.metrics import metrics
from gateway_service.middleware.trace import TRACE_HEADER

logger = structlog.get_logger()


def _should_retry(exc: BaseException) -> bool:
    if isinstance(exc, (TimeoutException, RequestError)):
        return True
    if isinstance(exc, HTTPStatusError) and exc.response.status_code >= 500:
        return True
    return False


class AccountServiceUnavailable(Exception):
    pass


class AccountClient:
    def __init__(self, base_url: str | None = None, timeout: float | None = None) -> None:
        self.base_url = (base_url or settings.account_service_url).rstrip("/")
        self.timeout = timeout or settings.http_timeout_seconds

    async def apply_transaction(self, account_id: str, payload: dict, trace_id: str) -> None:
        url = f"{self.base_url}/accounts/{account_id}/transactions"

        @retry(
            stop=stop_after_attempt(settings.retry_attempts),
            wait=wait_exponential(multiplier=0.5, min=0.5, max=4) + wait_random(0, 0.5),
            retry=retry_if_exception(_should_retry),
            reraise=True,
        )
        async def _call() -> None:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                logger.info("account_service_call", url=url, event_id=payload.get("eventId"))
                response = await client.post(
                    url,
                    json=payload,
                    headers={TRACE_HEADER: trace_id},
                )
                if response.status_code >= 500:
                    response.raise_for_status()
                if response.status_code >= 400:
                    response.raise_for_status()
                metrics.record_account_call("success")

        try:
            await _call()
        except Exception as exc:
            metrics.record_account_call("failure")
            logger.warning("account_service_unavailable", error=str(exc))
            raise AccountServiceUnavailable("Account Service unavailable") from exc
