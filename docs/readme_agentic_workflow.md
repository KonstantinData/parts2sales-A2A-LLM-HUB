# ToDo: Agentic Workflow Refactoring at Expert Level

**Goal:**
Transform the entire prompt quality & improvement workflow into a professional, scalable, and extensible Agentic AI architecture.
All components must be versioned, testable, and maximally flexible.

---

---

## 1. Structure and Standardization

### 1.1 Unified Event and Result Schemas (pydantic, e.g. PromptQualityResult, AgentEvent)

- [X] Create `agents/utils/schemas.py`
- [X] Define base schemas:
  - [X] `PromptQualityResult`
  - [X] `AgentEvent`
  - [X] `ImprovementResult`
  - [X] `FeatureResult`
  - [X] `ControllerResult` (for ControllerAgent decisions)
- [X] Ensure all meta fields are present in every schema:
  - [X] agent_name
  - [X] agent_version
  - [X] timestamp
  - [X] step_id
  - [X] prompt_version
  - [X] meta (generic dict for workflow context)
- [X] Ensure all schemas and fields have full docstrings and descriptions
- [X] Schema versioning system (add `schema_version` field, prepare for backward-compatibility checks)

---

### 1.2 All agents only return structured events/results

- [X] Refactor `PromptQualityAgent` to return `AgentEvent` with `PromptQualityResult`
- [X] Refactor `PromptImprovementAgent` to return `AgentEvent` with `ImprovementResult`
- [X] Refactor `ControllerAgent` to return `AgentEvent` with `ControllerResult`
- [X] Refactor all additional/utility agents as needed
- [X] Adapt all controller/workflow functions to handle only event/result objects, not dicts/tuples

---

### 1.3 Logging/Tracking exclusively as JSON Events

- [ ] Refactor `write_log()` to always write validated JSON event objects
- [ ] Standardize naming and log paths:
  - [ ] by event type
  - [ ] by agent name
  - [ ] by workflow step
- [ ] Validate every event object before logging (schema validation)
- [ ] Ensure log output is always machine-readable and consistent

---

### 1.4 Every event contains meta-information

- [ ] Implement automatic inclusion of all required meta fields in event creation
- [ ] Helper to populate common meta fields (timestamp, agent name, version, prompt version, step id)
- [ ] Double-check all agent event creation for completeness of meta information

## 2. Main Workflow Refactoring

- [ ] Refactor main workflow (batch or single)

  - [ ] Create function `evaluate_and_improve_prompt(...)`
    - [ ] Use agents as function arguments (dependency injection)
    - [ ] Allow flexible configuration (threshold, max iterations, paths, agent method)
    - [ ] Return all key results as a list of AgentEvents
    - [ ] Implement robust exception handling and generate error events
    - [ ] Make the function compatible with unit/integration testing (no hard-coded globals)
  - [ ] Refactor main CLI runner to use new workflow logic
  - [ ] Add batch support (process all templates in a directory)
  - [ ] Document function and workflow with in-code #Notes
- [ ] Implement Helper functions/utilities

  - [ ] YAML versioning:
    - [ ] Read version from YAML
    - [ ] Bump version (semantic)
    - [ ] Replace version in YAML file content
  - [ ] Unified writing/validation of event logs
    - [ ] Write event logs as JSON
    - [ ] Validate event against schema before logging (try/except)
    - [ ] Write error log if validation fails
  - [ ] Add utility for path and filename management (by event type, agent, version)
- [ ] Agent calls & decision flow

  - [ ] QualityAgent evaluates prompt → produces event
  - [ ] If score < threshold: ImprovementAgent suggests change → new event & prompt version
  - [ ] ControllerAgent checks alignment/abort → event
  - [ ] Version and log every iteration/change (prompt, event, result)
  - [ ] Exception handling:
    - [ ] If no improvement is possible, log event and abort
    - [ ] Catch/handle unexpected errors in agent execution

---

## 3. Extensibility & Flexibility

- [ ] All parameters configurable via Config/ENV

  - [ ] Store all settings in `.env` or `config/` directory
  - [ ] Read config via `os.getenv` or helper functions
  - [ ] Document all environment variables/settings
- [ ] Agents and methods (matrix, llm, hybrid) easy to swap/extend

  - [ ] Agent structure allows easy plug-and-play of methods/strategies
  - [ ] Include agent method/mode in event and result versioning
  - [ ] Document how to register/add new methods
- [ ] Add more agents (feature extraction, usecase, CRM sync) via plug-and-play

  - [ ] Define template event/result schema for new agent types (naming, meta, version, fields)
  - [ ] Extend main workflow logic to support additional agents/steps as needed
  - [ ] Example agent skeleton in codebase for rapid onboarding
- [ ] Unit and integration tests for every component (including new agents)

  - [ ] Write/extend tests for all agent event/result objects
  - [ ] Write/extend tests for workflow/decision logic
  - [ ] Include mock agents and test datasets
- [ ] Optional: CLI/API interface for agent selection, mode, log level, etc.

  - [ ] CLI parameters for agent, method, threshold, log-level, etc.
  - [ ] (Optional) REST API endpoint for running workflow or managing agents
  - [ ] Document all CLI/API interfaces

---

## 4. Testing & Quality Assurance

- [ ] Unit tests for event/result schemas

  - [ ] Test for required/default fields, error handling
  - [ ] Test for backward compatibility when changing schema
- [ ] Unit tests for all agents

  - [ ] Test all agent methods and returned events
  - [ ] Test all decision flows (score logic, exceptions, boundary cases)
- [ ] Integration tests for the full process

  - [ ] End-to-end workflow run with dummy prompts/templates
  - [ ] Validate logfile/event output and prompt versioning after workflow run
- [ ] Example data & dummy prompts for testing

  - [ ] Create and document example prompts for each agent
  - [ ] Provide example input files for tests and demos

---

## 5. Documentation & Extension-Readiness

- [ ] In-code #Notes for all core logic (clear, concise, English)

  - [ ] Document every agent class/function with docstring and #Notes
  - [ ] Follow a consistent in-code documentation style (reference template)
- [ ] Update/create README.md for the overall process

  - [ ] Overview diagram of agent workflow/interplay
  - [ ] Document event flow and logging approach
  - [ ] Notes on extensibility and parameterization
  - [ ] Add FAQ and Troubleshooting section
- [ ] Example: how to add a new agent (skeleton + quick guide)

  - [ ] Step-by-step checklist for onboarding a new agent (code + config)
  - [ ] Example agent skeleton in the repo
- [ ] Best practices for adaptability/extensibility

  - [ ] Guidelines for updating schemas, versioning, breaking changes
  - [ ] Patterns for robust, future-proof pipeline design

---

## 6. (Optional) Monitoring & Analytics

- [ ] Extend logs for later analysis (prompt quality, improvement rate, agent costs)

  - [ ] Add structured log fields (e.g., process time, cost, feedback class)
  - [ ] Prepare log/event output for analytics tools (e.g., JSONL, CSV export)
  - [ ] (Optional) Integrate with external monitoring/analytics/dashboard
- [ ] Push logs to dashboard/tool

  - [ ] Export or push interface for logs (local or remote)
  - [ ] Provide an example/dashboard notebook for log analytics

---

**Result:**
A workflow that is 100% transparent, versioned, auditable, and always extensible – with professional quality/error handling and complete event logging.
