# PyQueue: Lightweight Persistent Message Queue System

A minimal, production-grade asynchronous Message Queue & Background Job Processing System built from scratch in Python using FastAPI, SQLite, and SQLAlchemy ORM.

Designed as a backend engineering exercise to understand how distributed message brokers (like RabbitMQ, Celery, or Kafka) handle decoupled job execution, atomic worker claims, race conditions, and crash recovery.

---

## Why Build This?

When building modern web applications, heavy tasks like image processing, sending emails, or running long mathematical calculations should never run directly inside your API request-response cycle. Doing so blocks the server and leads to slow HTTP responses or timeouts.

This project solves that by decoupling the Producer (FastAPI web server) from the Consumer (Worker processes):
1. Producer accepts HTTP POST requests, assigns a unique `job_id`, saves it to SQLite, and immediately returns a `201 Created` response.
2. Consumers (Workers) run independently in background processes, poll SQLite, claim jobs atomically, execute them, and store results or error tracebacks.

---

## Features

- Asynchronous & Decoupled Architecture: Fast API responses with background processing.
- Persistent Storage: All jobs, payloads, results, and execution errors are safely persisted to SQLite.
- Race-Condition Free (Atomic Job Claiming): Multiple workers can run in parallel without executing the same job twice.
- Automatic Crash Recovery (Stale Job Re-queuing): If a worker crashes mid-execution (e.g., power loss or Ctrl+C), stale jobs stuck in `running` state (> 120s) are automatically detected and re-queued back to `pending`.
- Full Lifecycle Auditing: Explicit status tracking (`pending` -> `running` -> `completed` / `failed`) with automatic UTC timestamps (`created_at`, `updated_at`).
- Error Traceback Storage: Unhandled handler exceptions (e.g., division by zero, invalid payload) don't crash workers; they are logged into the `error` column for inspection.

---

## How it Relates to RabbitMQ & Kafka

If you've ever wondered how real message queues work under the hood, this project implements the fundamental concepts that power enterprise tools:

```
+-------------------------------------------------------------------+
|                        Concept Comparison                         |
+-----------------+-------------------+-----------------------------+
| Component       | PyQueue (This)    | RabbitMQ / Kafka            |
+-----------------+-------------------+-----------------------------+
| Producer        | FastAPI Endpoint  | Publisher / Client          |
| Queue / Broker  | SQLite Table      | AMQP Queue / Log            |
| Consumer        | worker.py         | Consumer Group              |
| Job State       | pending/running   | Unacked / In-flight         |
| Crash Protection| Timeout Re-queue  | NACK / Visibility Timeout   |
+-----------------+-------------------+-----------------------------+
```

### 1. Polling vs. Push Notifications
- RabbitMQ/Redis: Uses socket-based event loops (AMQP / Pub-Sub) to push messages to workers instantly.
- PyQueue: Uses Database Polling (workers poll SQLite with throttling). Simple, highly persistent, zero external server dependencies.

### 2. Visibility Timeout & Leases
- In tools like AWS SQS or Celery, if a worker dies while processing a message, SQS makes the message visible again after a Visibility Timeout.
- In PyQueue, `recover_stale_jobs()` implements this exact pattern by querying `updated_at < threshold` for jobs stuck in `running` status.

### 3. Atomic State Machines
- Enterprise brokers ensure a message is delivered to exactly-one or at-least-one worker.
- PyQueue uses conditional SQL updates (`UPDATE jobs SET status='running' WHERE id=? AND status='pending'`) to guarantee atomic claims across concurrent processes.

---

## Project Structure

```
message_queue/
├── app/
│   ├── main.py             # FastAPI app initialization
│   ├── router.py           # REST endpoints (/api/jobs)
│   └── worker/
│       ├── worker.py       # Background worker (polling loop, handlers, recovery)
│       └── multiprocessing.sh # Helper script to launch 4 parallel workers
├── database/
│   └── database.py         # Dynamic SQLite engine & Session maker
├── models/
│   └── model.py            # SQLAlchemy ORM models & Pydantic request models
├── server.py               # API entry point (uvicorn runner)
├── task_enqueue.sh         # Bash helper script to send POST requests
├── jobs.db                 # SQLite persistent database file
└── pyproject.toml          # UV project configuration & dependencies
```

---

## How to Run

### 1. Prerequisites & Installation
Install dependencies using uv:

```bash
uv sync
```

### 2. Start the API Server (Producer)
Run the server in Terminal 1:

```bash
uv run server.py
```
*API will run at `http://localhost:8000`. Swagger docs available at `http://localhost:8000/docs`.*

### 3. Start Workers (Consumers)
Run a single worker in Terminal 2:

```bash
uv run app/worker/worker.py
```

Or spin up 4 parallel worker processes to test concurrent execution:

```bash
./app/worker/multiprocessing.sh
```

### 4. Enqueue Jobs

- Enqueue a `sleep` job (5 seconds):
  ```bash
  ./task_enqueue.sh 5
  ```

- Enqueue a `calculation` job (via cURL):
  ```bash
  curl -X POST "http://localhost:8000/api/jobs" \
    -H "Content-Type: application/json" \
    -d '{
      "type": "calculation",
      "payload": {"first": 10, "second": 20, "operator": "+"}
    }'
  ```

### 5. Check Job Status

- Get all jobs:
  ```bash
  curl http://localhost:8000/api/jobs
  ```

- Get job by ID:
  ```bash
  curl http://localhost:8000/api/jobs/<job-id>
  ```

---

## Job Handlers Supported

1. `sleep`:
   - Payload: `{"seconds": 5}`
   - Action: Pauses execution for N seconds.
   - Result: `{"result": "Slept for 5s"}`

2. `calculation`:
   - Payload: `{"first": 10, "second": 5, "operator": "*"}`
   - Action: Performs mathematical operations (`+`, `-`, `*`, `/`, `//`, `**`).
   - Result: `{"result": "50"}`