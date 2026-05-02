from collections import defaultdict, deque
from time import monotonic


class InMemoryRateLimiter:
    def __init__(self, limit: int, window_seconds: int = 60) -> None:
        self._limit = limit
        self._window_seconds = window_seconds
        self._events: dict[str, deque[float]] = defaultdict(deque)

    def allow(self, key: str) -> bool:
        now = monotonic()
        queue = self._events[key]
        while queue and now - queue[0] > self._window_seconds:
            queue.popleft()
        if len(queue) >= self._limit:
            return False
        queue.append(now)
        return True
