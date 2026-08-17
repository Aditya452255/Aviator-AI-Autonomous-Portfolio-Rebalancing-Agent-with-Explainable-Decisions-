# Aviator AI — Autonomous Portfolio Rebalancing Agent

## Enterprise Readiness, Reliability & Observability Service (Phase 9)

**Aviator AI** is an enterprise-grade agentic robo-advisory platform designed to manage, continuously monitor, optimize, and rebalance **50,000 investment portfolios** across five distinct risk categories with explainable decision support, Human-in-the-Loop governance, backtesting, Gradio dashboard, and production-grade reliability & observability.

This repository contains **Phase 1 (Enterprise Foundation & Simulation Layer)**, **Phase 2 (Portfolio Drift Monitoring & Trigger Intelligence Layer)**, **Phase 3 (Portfolio Optimization & Trade Generation Engine)**, **Phase 4 (Multi-Agent Decision Intelligence Layer)**, **Phase 5 (Explainable AI Engine)**, **Phase 6 (Human-in-the-Loop Governance Layer)**, **Phase 7 (Backtesting Engine)**, **Phase 8 (Gradio Enterprise Operations Dashboard)**, and **Phase 9 (Enterprise Readiness, Reliability, Security & Observability Layer)**, built adhering strictly to SOLID design principles, modular architecture, type-safety, and production readiness.

---

## 🏗 System Architecture (Phases 1-9)

```
                                +----------------------------------+
                                |      Central Configuration       |
                                | (YAML + Pydantic Settings + Env) |
                                +----------------------------------+
                                                 |
                                                 v
                                +----------------------------------+
                                | Phase 1: Foundation & Simulation |
                                +----------------------------------+
                                                 |
                                                 v
                                +----------------------------------+
                                |    Phase 2: Drift Monitoring     |
                                +----------------------------------+
                                                 |
                                                 v
                                +----------------------------------+
                                |    Phase 3: Convex Optimization  |
                                +----------------------------------+
                                                 |
                                                 v
                                +----------------------------------+
                                | Phase 4: Multi-Agent Intelligence|
                                +----------------------------------+
                                                 |
                                                 v
                                +----------------------------------+
                                |  Phase 5: Explainable AI Engine  |
                                +----------------------------------+
                                                 |
                                                 v
                                +----------------------------------+
                                |  Phase 6: HITL Governance Layer  |
                                +----------------------------------+
                                                 |
                                                 v
                                +----------------------------------+
                                | Phase 7: Backtesting & Benchmark |
                                +----------------------------------+
                                                 |
                                                 v
                                +----------------------------------+
                                |   Phase 8: Gradio Enterprise     |
                                |       Operations Dashboard       |
                                +----------------------------------+
                                                 |
                                                 v
                                +----------------------------------+
                                | Phase 9: Enterprise Readiness,   |
                                | Reliability, Security & Metrics  |
                                +----------------------------------+
                                                 |
       +-----------------------------------------+-----------------------------------------+
       |                         |               |                         |               |
       v                         v               v                         v               v
+------------------+   +------------------+   +------------------+   +------------------+   +------------------+
| Reliability      |   | Performance      |   | Security & RBAC  |   | Prometheus       |   | Deployment       |
| (CircuitBreaker, |   | (TTL Cache,      |   | (ADMIN, ADVISOR, |   | Observability    |   | (Dockerfile,     |
| Retries, Health) |   | Parallel Pool)   |   | Payload Encryption|  | & Health REST API|   | Docker Compose)  |
+------------------+   +------------------+   +------------------+   +------------------+   +------------------+
```

---

## 🛡 Phase 9 Enterprise Production Components

1. **Reliability & Self-Healing**:
   - `CircuitBreaker`: State machine (`CLOSED`, `OPEN`, `HALF_OPEN`) preventing cascade solver/model failures.
   - `RetryManager` & `FallbackManager`: Exponential backoff retries (`tenacity`) & solver degradation fallbacks.
   - `SystemHealthChecker` & `RecoveryManager`: Self-healing recovery diagnostics monitoring CPU, memory, and disk health.

2. **Performance & Concurrency**:
   - `CacheManager`: In-memory TTL caching (`cachetools`).
   - `ParallelExecutor` & `BatchProcessor`: ThreadPool processing for 50k portfolio batches.
   - `ResourceMonitor`: Real-time hardware monitoring via `psutil`.

3. **Security & Governance**:
   - `Role` RBAC (`ADMIN`, `ADVISOR`, `COMPLIANCE_OFFICER`, `READ_ONLY`).
   - `AuthenticationManager` & `AuthorizationManager`: Token authentication and permission enforcement.
   - `PayloadEncryption`: AES/Fernet payload encryption and input sanitization.

4. **Observability & REST Health APIs**:
   - `PrometheusMetricsManager`: Counter, Gauge, and Histogram metrics for Prometheus scraping.
   - FastAPI REST Server exposing:
     - GET `/health` — Subsystem health metrics.
     - GET `/metrics` — Prometheus metrics text payload.
     - GET `/status` — High-level operational status.
     - GET `/system` — System hardware stats (`psutil`).

5. **Deployment & CI/CD**:
   - `Dockerfile`: Multi-stage Python 3.11 container.
   - `docker-compose.yml`: Multi-container orchestrator (App + Prometheus).
   - `.github/workflows/ci.yml`: GitHub Actions pipeline running linting, pytest, coverage, and Docker build.

---

## 📁 Directory Structure

```
project_root/
├── README.md                          # Technical documentation
├── Dockerfile                         # Production multi-stage Docker image
├── docker-compose.yml                 # Multi-container Compose config
├── main.py                            # CLI entry point runner (Phases 1-9)
├── requirements.txt                   # Production dependencies
├── .github/workflows/ci.yml           # GitHub Actions CI workflow
├── config/                            # YAML configurations
├── src/
│   ├── core/                          # Config, logger, constants, exceptions, utils
│   ├── models/                        # Pydantic domain models
│   ├── data/                          # Generators & market simulator
│   ├── monitoring/                    # Drift calculator, trigger & priority engines
│   ├── optimization/                  # Optimizer, constraints, tax loss harvester, execution planner
│   ├── memory/                        # Decision memory & shared workflow state
│   ├── agents/                        # Orchestrator, Analyst, Risk, Tax, Compliance, Explanation agents
│   ├── workflows/                     # TaskFactory, HandoffManager, CrewBuilder, MultiAgentWorkflowEngine
│   ├── validators/                    # Consensus & conflict validators
│   ├── explainability/                # SurrogateModel, SHAPEngine, LIMEEngine, CounterfactualEngine, Explainers
│   ├── governance/                    # ApprovalEngine, OverrideManager, EscalationManager, KillSwitch, AuditTrail
│   ├── backtesting/                   # HistoricalReplayEngine, StrategyRunner, BenchmarkEngine, ScenarioEngine, StressTestEngine
│   ├── analytics/                     # Performance, Benchmark, Scenario, Override, Audit analytics
│   ├── ui/                            # Gradio UI (theme, layout, 10 tabs, components)
│   ├── reliability/                   # CircuitBreaker, RetryManager, FallbackManager, HealthChecker, RecoveryManager
│   ├── performance/                   # CacheManager, BatchProcessor, ParallelExecutor, ResourceMonitor
│   ├── security/                      # RBAC, Authentication, Authorization, PayloadEncryption, InputValidator
│   ├── observability/                 # PrometheusMetricsManager, Monitoring, StructuredLogger, AlertEngine
│   └── services/                      # SimulationService, MonitoringService, OptimizationService, AgentService, ExplainabilityService, GovernanceService, BacktestingService, DashboardService, ProductionService
└── tests/                             # Enterprise Pytest test suite (58 unit tests)
```

---

## 🏃 Running Phase 9 Production Service

Run Phase 9 health evaluation and export reports:

```bash
python main.py --phase 9
```

Launch production Docker container:

```bash
docker-compose up --build
```

---

## 🧪 Testing & Verification

Execute full test suite across all 9 phases:

```bash
pytest tests/ --cov=src --cov-report=term-missing
```
