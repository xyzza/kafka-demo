from __future__ import annotations

import asyncio
import inspect
import json
import os
from dataclasses import dataclass, field
from typing import Any, Mapping, Optional

from confluent_kafka.aio import AIOProducer


@dataclass(frozen=True)
class ConfluentProducerConfig:
    bootstrap_servers: str = field(
        default_factory=lambda: os.environ.get("KAFKA_BOOTSTRAP_SERVERS", "localhost:29092")
    )

    acks: str = "1"
    linger_ms: int = 20
    batch_num_messages: int = 10_000
    batch_size: int = 256 * 1024
    compression_type: str = "gzip"
    queue_buffering_max_kbytes: int = 256 * 1024
    queue_buffering_max_messages: int = 1_000_000

    def as_dict(self) -> dict:
        return {
            "bootstrap.servers": self.bootstrap_servers,
            "acks": self.acks,
            "linger.ms": self.linger_ms,
            "batch.num.messages": self.batch_num_messages,
            "batch.size": self.batch_size,
            "compression.type": self.compression_type,
            "queue.buffering.max.kbytes": self.queue_buffering_max_kbytes,
            "queue.buffering.max.messages": self.queue_buffering_max_messages,
        }


class AsyncConfluentKafkaProducer:
    def __init__(self, config: ConfluentProducerConfig | None = None, *, in_flight_limit: int = 10_000) -> None:
        self._config = config or ConfluentProducerConfig()
        self._producer: AIOProducer | None = None
        self._sem = asyncio.Semaphore(in_flight_limit)
        self._pending: set[asyncio.Task] = set()
        self._dumps = lambda v: json.dumps(v, ensure_ascii=False, separators=(",", ":")).encode("utf-8")

    async def __aenter__(self) -> "AsyncConfluentKafkaProducer":
        self._producer = AIOProducer(self._config.as_dict())
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        try:
            await self.drain()
            if self._producer is not None:
                await self._producer.flush()
        finally:
            if self._producer is not None:
                await self._producer.close()
                self._producer = None

    async def _await_message(self, produced: Any) -> Any:
        """
        Normalize across different AIOProducer versions:
        - produce() may return Message
        - produce() may return Future[Message]
        - produce() may return coroutine -> Future[Message] -> Message
        """
        x = produced
        # up to two layers of await is enough for all known return variants
        for _ in range(2):
            if inspect.isawaitable(x) or asyncio.isfuture(x):
                x = await x
            else:
                break
        return x

    async def send_json(
        self,
        topic: str,
        value: Mapping[str, Any],
        *,
        key: str | bytes | None = None,
        wait_delivery: bool = False,
    ) -> Optional[tuple[int, int]]:
        if self._producer is None:
            raise RuntimeError("Producer is not started. Use async with.")

        await self._sem.acquire()

        key_b: bytes | None = key.encode("utf-8") if isinstance(key, str) else key
        payload = self._dumps(value)

        async def _produce_and_return_meta() -> tuple[int, int]:
            produced = self._producer.produce(topic=topic, value=payload, key=key_b)
            msg = await self._await_message(produced)
            return msg.partition(), msg.offset()

        task = asyncio.create_task(_produce_and_return_meta())
        self._pending.add(task)

        def _done_cb(t: asyncio.Task) -> None:
            self._pending.discard(t)
            self._sem.release()
            # retrieve exception to suppress "Task exception was never retrieved"
            _ = t.exception()

        task.add_done_callback(_done_cb)

        if wait_delivery:
            return await task
        return None

    async def drain(self) -> None:
        while self._pending:
            done, _ = await asyncio.wait(self._pending, return_when=asyncio.FIRST_COMPLETED)
            for t in done:
                _ = t.result()  # re-raises delivery errors if any