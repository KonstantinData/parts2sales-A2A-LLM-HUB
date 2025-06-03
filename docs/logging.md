# parts2sales-A2A-LLM-HUB

## Developer Onboarding & Logging Policy

### Logging & Output Policy (IMPORTANT)

**All logging and output are now handled exclusively via the workflow-centric JSONL log structure.
Do not use local log files, scattered per-agent logs, or any kind of legacy output files.**

#### How does logging work now?

- Every workflow/session gets a single log file:
  - Location: `logs/workflows/`
  - Pattern: `{timestamp}_workflow_{workflow_id}.jsonl`
- All agent events (success and error) are recorded as structured `AgentEvent` objects, one per line, in the workflow log.
- No more legacy logs in `logs/quality_check/`, `logs/prompt_improvement/`, `logs/controller_decision/`, or any `data/outputs/` directory.

#### What must developers do?

- Always use `JsonlEventLogger` (`from utils.jsonl_event_logger import JsonlEventLogger`) to log agent or workflow events.
- Always pass a `workflow_id` through the agent stack for consistent session-based logging.
- Never write output or logs directly to files from agents, controllers, or scripts.

#### Why this change?

- Ensures **traceability, auditability, and compliance** for all runs and workflows.
- Makes debugging and monitoring much easier—one log file per run, all events chronologically ordered.
- Keeps the repository and local workspace clean, secure, and production-ready.

---

For details, see [docs/logging.md](docs/logging.md) or the comments in `utils/jsonl_event_logger.py`.

If you have questions about integrating the logger into your agent or workflow, contact the maintainers or check the example agent scripts.
