"""RabbitMQ publisher utilities for the web app.

Exposes:
- _open_channel() -> (conn, ch)
- publish_task(kind: str, payload: dict | None = None, headers: dict | None = None) -> None
"""

import os
import json
from datetime import datetime
import pika

EXCHANGE = "tasks"
QUEUE = "tasks_q"
ROUTING_KEY = "tasks"

def _open_channel():
    """Connect to RabbitMQ and return (conn, ch) with durable exchange/queue bound."""
    url = os.getenv("RABBITMQ_URL", "amqp://guest:guest@rabbitmq:5672/%2F")
    params = pika.URLParameters(url)
    conn = pika.BlockingConnection(params)
    ch = conn.channel()

    # Durable exchange & queue
    ch.exchange_declare(exchange=EXCHANGE, exchange_type="direct", durable=True)
    ch.queue_declare(queue=QUEUE, durable=True)
    ch.queue_bind(exchange=EXCHANGE, queue=QUEUE, routing_key=ROUTING_KEY)

    # Optional, recommended
    # ch.confirm_delivery()

    return conn, ch


def publish_task(kind: str, payload: dict | None = None, headers: dict | None = None) -> None:
    """Publish a persistent JSON message to the tasks queue."""
    body = json.dumps(
        {"kind": kind, "ts": datetime.utcnow().isoformat(), "payload": payload or {}},
        separators=(",", ":"),
    ).encode("utf-8")

    conn, ch = _open_channel()
    try:
        ch.basic_publish(
            exchange=EXCHANGE,
            routing_key=ROUTING_KEY,
            body=body,
            properties=pika.BasicProperties(
                delivery_mode=2,      # make message persistent
                headers=headers or {},
            ),
            mandatory=False,
        )
        # If using confirms:
        # if not ch.wait_for_confirms():
        #     raise RuntimeError("Publish not confirmed")
    finally:
        conn.close()
