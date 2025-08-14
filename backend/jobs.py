import os
from rq import Queue
from redis import Redis

REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")
redis_conn = Redis.from_url(REDIS_URL)
q = Queue("ingest", connection=redis_conn)

def enqueue_ingest(doc_id: str):
    # Import by string path so the RQ worker can import it
    # worker.process_document must be importable in the container
    q.enqueue("worker.process_document", doc_id, job_timeout=600)
