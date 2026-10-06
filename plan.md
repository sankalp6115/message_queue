This is a solid project for your weekly backend challenge. I'd recommend building it in Python + FastAPI + SQLite, using a separate worker process rather than background tasks inside FastAPI.

The key is to implement the core queue first, then add retries and priority only after the basic lifecycle works.

Suggested implementation plan

Day 1: API and database

Set up FastAPI and SQLite.

Create a jobs table.

Implement POST /jobs, GET /jobs/{id} and GET /jobs.

Validate job types and payloads using Pydantic.

Day 2: Worker
Create a separate worker process.
Poll SQLite for pending jobs.

Implement sleep and calculate handlers.

Update job statuses and store results.

Day 3: Concurrency and failure handling

Prevent two workers from claiming the same job.

Handle exceptions and mark jobs as failed.

Handle worker interruptions and recover stale running jobs.

Test multiple queued jobs.

Day 4: Docker and persistence

Write a Dockerfile and docker-compose.yml.

Use a persistent volume for SQLite.

Verify that pending jobs survive worker restarts.

Run the API and worker as separate services.

Day 5: Testing

Test job creation and retrieval.

Test successful and failed execution.

Test job recovery and concurrency.

Verify the full lifecycle using curl.

Days 6–7: Stretch goals and documentation

Implement retries with a maximum of three attempts.

Add priority-based scheduling.

Write a README explaining architecture, limitations and setup.

Recommended architecture

FastAPI

Job creation and status API

SQLite

Persistent job storage

Worker

Poll → Claim → Execute

Job handlers

sleep / calculate

Worker writes results and updated statuses back to SQLite.

Database schema

Start with a single table. Avoid adding unnecessary abstractions.

Column

	

Type

	

Purpose




id

	

TEXT

	

UUID




type

	

TEXT

	

Job type




payload

	

TEXT

	

JSON input




status

	

TEXT

	

pending, running, completed, failed




result

	

TEXT

	

JSON result




error

	

TEXT

	

Error details




attempts

	

INTEGER

	

Execution attempts




priority

	

INTEGER

	

Scheduling priority




created_at

	

TEXT

	

Creation timestamp




updated_at

	

TEXT

	

Last status update

Use SQLite transactions when claiming jobs. A simple SELECT followed by an UPDATE without transaction protection can lead to multiple workers executing the same job.

Important design decisions

Polling: Start with a one-second polling interval. No need for Redis or an event-driven system yet.

Concurrency: Use atomic job claiming with transactions. SQLite's write-locking behavior matters here.

Retries: Distinguish between a job's current status and its attempt count. Retry only when the configured limit allows it.

Crash recovery: A worker might crash after marking a job running. You need a recovery mechanism, such as a lease or timeout, to requeue abandoned jobs.

Calculations: Use an explicit allowlist of operations, such as addition, subtraction, multiplication and division. Never use eval().

Sleep jobs: Restrict the allowed duration to prevent unnecessarily long-running jobs.

One particularly important concept: persistent storage does not automatically mean exactly-once execution. If a worker crashes after performing an operation but before saving its result, the operation may run again. Your initial implementation should use at-least-once execution semantics and document this limitation.

Definition of Done checklist

Project progress

0/10

Create and retrieve jobs through the API
Execute sleep and calculate jobs
Observe pending → running → completed
Store and expose execution errors
Run multiple queued jobs
Restart the worker without losing pending jobs
Recover jobs abandoned by a crashed worker
Run API and worker using Docker Compose
Pass tests for core queue behavior
Document setup and known limitations
Reset checklist

My recommendation: Don't start with retries, priority or multiple workers. Get a single worker reliably processing persistent jobs first. Once that works, adding concurrency and recovery will teach you much more about how real job queues behave than building a larger architecture prematurely.