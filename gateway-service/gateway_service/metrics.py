from collections import defaultdict
from threading import Lock


class MetricsRegistry:
    def __init__(self) -> None:
        self._lock = Lock()
        self._events_received: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
        self._account_calls: dict[str, int] = defaultdict(int)

    def record_event(self, endpoint: str, status: str) -> None:
        with self._lock:
            self._events_received[endpoint][status] += 1

    def record_account_call(self, result: str) -> None:
        with self._lock:
            self._account_calls[result] += 1

    def snapshot(self) -> dict:
        with self._lock:
            return {
                "gateway.events.received": {k: dict(v) for k, v in self._events_received.items()},
                "gateway.account.calls": dict(self._account_calls),
            }


metrics = MetricsRegistry()
