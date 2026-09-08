# Aviator AI — Autonomous Portfolio Rebalancing Agent

## Final Year Project | Complete 12-Phase System

**Aviator AI** is an autonomous portfolio rebalancing platform engineered to manage, continuously monitor, optimize, govern, and explain investment decisions across **50,000 investment portfolios** across five distinct risk profiles with Explainable AI (XAI), Human-in-the-Loop governance, backtesting, interactive Gradio dashboards, and production-grade reliability & observability.

This repository contains the complete **Phases 1–12 Architecture**:
- **Phase 1**: Simulation & Data Generation Layer
- **Phase 2**: Portfolio Drift Monitoring & Trigger Intelligence Layer
- **Phase 3**: Portfolio Convex Optimization & Tax-Aware Rebalancing Engine
- **Phase 4**: Multi-Agent Decision Intelligence Layer (6 Specialized AI Agents)
- **Phase 5**: Explainable AI (XAI) Engine (SHAP, LIME, Counterfactuals)
- **Phase 6**: Human-in-the-Loop Governance & Compliance Layer (SHA-256 Audit Trail)
- **Phase 7**: Backtesting, Benchmarks & Macro Stress Testing Engine
- **Phase 8**: Gradio Operations Dashboard
- **Phase 9**: Enterprise Readiness, Reliability, Security & Observability Layer
- **Phase 10**: User-Centric UI & Guided Demonstration (`🚀 RUN DEMO PORTFOLIO` Workflow)
- **Phase 11**: Validation & Evidence (62/62 Pytest Tests Passing, 100% Pass Rate)
- **Phase 12**: Final Integration & Academic Release

---

## 🏗 Complete 12-Phase System Architecture

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
                                | Phase 8 & 10: Gradio Operations  |
                                |   & Story-Driven Demo Dashboard  |
                                +----------------------------------+
                                                 |
                                                 v
                                +----------------------------------+
                                | Phase 9: Enterprise Reliability, |
                                | Security, RBAC & Health REST API |
                                +----------------------------------+
                                                 |
                                                 v
                                +----------------------------------+
                                | Phase 11 & 12: Academic Release  |
                                |   & Empirical Test Validation    |
                                +----------------------------------+
```

---

## 🏛 8 Presentation Story Tabs

The UI dashboard tells a clear 8-step presentation story:

1. **`1. Executive Dashboard`**: Portfolio status (`🚨 REBALANCING REQUIRED` | Current Drift: `6.8%` vs Allowed Drift: `5.0%`), plain-English explanation, allocation chart, and recommended trade action.
2. **`2. Portfolio Analysis`**: Current vs Target vs Proposed allocation chart, asset class drift table (`OVERWEIGHT` / `UNDERWEIGHT`), overweight/underweight asset cards, and risk findings.
3. **`3. Rebalancing & Optimization`**: Recommended trade execution order table (`Asset Class`, `Action`, `Quantity`, `Est. Price (₹)`, `Strategy`), optimization objective, constraints, and collapsible `Technical Details ▼` accordion (`CVXPY` / `SciPy SLSQP`).
4. **`4. AI Financial Council`**: `96% Consensus` visual badge, voting breakdown across 6 specialized AI agents (Ops Orchestrator, Portfolio Analyst, Risk Officer, Tax Specialist, Compliance Officer, Comms Specialist), and final verdict (`RECOMMEND EXECUTION`).
5. **`5. Explainable AI (XAI)`**: Plain-English narrative *"Why did Aviator make this decision?"*, SHAP global feature impact scores, LIME weights table, and Counterfactual scenario (*"What would have changed the decision?"*).
6. **`6. Governance & Approval`**: Human-in-the-Loop advisor action center (`Advisor Approval Required`), policy check status (`PASS`), interactive `Approve Trade`, `Reject Trade`, `Override` controls, portfolio-filtered audit log, and SHA-256 cryptographic ledger.
7. **`7. Backtesting & Results`**: 252-day historical backtesting CAGR % comparison chart matching exact table values (Aviator AI 15.7% vs Calendar 13.8% vs Buy & Hold 12.5%) and risk-adjusted performance matrix.
8. **`8. Validation & Evidence`**: Empirical validation display showing **62/62 Pytest tests passed (100%)**, end-to-end multi-phase execution checklist, and Phase 9 system health status (`HEALTHY`, CPU/Memory, `/health` & `/metrics` endpoints).

---

## 📁 Repository Structure

```
project_root/
├── README.md                          # Technical documentation
├── PROJECT_OVERVIEW.md                # Comprehensive problem-solving guide
├── Dockerfile                         # Production multi-stage Docker image
├── docker-compose.yml                 # Multi-container Compose config
├── main.py                            # CLI entry point runner (Phases 1-12)
├── requirements.txt                   # Production dependencies
├── .github/workflows/ci.yml           # GitHub Actions CI workflow
├── config/                            # YAML configurations
├── src/
│   ├── core/                          # Config, logger, constants, exceptions, utils
│   ├── models/                        # Pydantic domain models
│   ├── data/                          # Generators & market simulator
│   ├── monitoring/                    # Drift calculator, trigger & priority engines
│   ├── optimization/                  # Optimizer, constraints, tax harvester, execution planner
│   ├── memory/                        # Decision memory & shared workflow state
│   ├── agents/                        # Orchestrator, Analyst, Risk, Tax, Compliance, Explanation agents
│   ├── workflows/                     # TaskFactory, HandoffManager, CrewBuilder, MultiAgentWorkflowEngine
│   ├── validators/                    # Consensus & conflict validators
│   ├── explainability/                # SurrogateModel, SHAPEngine, LIMEEngine, CounterfactualEngine, Explainers
│   ├── governance/                    # ApprovalEngine, OverrideManager, EscalationManager, KillSwitch, AuditTrail
│   ├── backtesting/                   # HistoricalReplayEngine, StrategyRunner, BenchmarkEngine, ScenarioEngine, StressTestEngine
│   ├── analytics/                     # Performance, Benchmark, Scenario, Override, Audit analytics
│   ├── ui/                            # Gradio UI (theme, layout, 8 story tabs, components)
│   ├── reliability/                   # CircuitBreaker, RetryManager, FallbackManager, HealthChecker, RecoveryManager
│   ├── performance/                   # CacheManager, BatchProcessor, ParallelExecutor, ResourceMonitor
│   ├── security/                      # RBAC, Authentication, Authorization, PayloadEncryption, InputValidator
│   ├── observability/                 # PrometheusMetricsManager, Monitoring, StructuredLogger, AlertEngine
│   └── services/                      # SimulationService, MonitoringService, OptimizationService, AgentService, ExplainabilityService, GovernanceService, BacktestingService, DashboardService, ProductionService
└── tests/                             # Enterprise Pytest test suite (62 unit & integration tests)
```

---

## 🏃 Operational Commands

### 1. Launch Guided Presentation Dashboard (Port 7860)
```bash
python main.py --phase 8
```
*Access via browser*: **`http://localhost:7860`**

### 2. Run Production Health & Observability Service (Port 8000)
```bash
python main.py --phase 9
```
- Health API: `http://localhost:8000/health`
- Prometheus Metrics: `http://localhost:8000/metrics`

### 3. Run End-to-End Simulation
```bash
python main.py --phase 7 --clients 100 --portfolios 100 --days 252
```

### 4. Execute Full Pytest Test Suite
```bash
pytest tests/ -v
```
*(62/62 tests passing, 100% pass rate)*
