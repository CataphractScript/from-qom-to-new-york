# From Qom to New York: Transit Optimization Platform
### UrbanPulse Dynamics — Technical Case Study Track
**Course:** Design and Analysis of Algorithms  
**Target City:** Qom Rail Transit Network ($|V| = 20$ Stations, $|E| = 21$ Track Connections)  
**Implementation:** Python 3.10+ (Standard Library Architecture)  
**Status:** All 5 Rounds + Bonus Innovations Complete (100% Test Pass Rate)

---

## 📖 Table of Contents
1. [Overview & Narrative](#-overview--narrative)
2. [Project Architecture](#-project-architecture)
3. [Installation & Requirements](#-installation--requirements)
4. [How to Run (CLI & Interactive Menu)](#-how-to-run-cli--interactive-menu)
5. [Task Breakdown by Round](#-task-breakdown-by-round)
6. [Algorithmic Complexity Master Table](#-algorithmic-complexity-master-table)
7. [Running Unit & Integration Tests](#-running-unit--integration-tests)
8. [Design Decisions & SOLID Architecture](#-design-decisions--solid-architecture)

---

## 🌆 Overview & Narrative
**UrbanPulse Dynamics** is a smart city transit optimization enterprise based in New York City. Commissioned by the Municipality of Qom, this project implements the algorithmic architecture for Qom's rapid rail transit network.

The platform provides a unified system for:
- **Graph Modeling & Spatial Search** (BFS, DFS, Dijkstra, A*, Bidirectional Dijkstra)
- **Infrastructure Design & Cost Minimization** (Kruskal with Union-Find, Prim, Express DAG, Bellman-Ford)
- **Daily Metro Operations** (Platform Interval Scheduling, Min-Heap Train Dispatch, Quickselect Traffic Analytics, Stochastic Queuing Simulation)
- **Network Resilience & Capacity** (Edmonds-Karp Max-Flow, Min-Cut Bottlenecks, Tarjan Articulation Points & Bridges, Dominating Set Emergency Deployment, Levenshtein Fuzzy Search)
- **Advanced Innovations** (A* Heuristics, Dynamic BPR Congestion Routing)

---

## 🏗 Project Architecture

```
from-qom-to-new-york/
├── README.md                           # Comprehensive documentation and usage guide
├── pyproject.toml                      # Package build configuration and pytest options
├── pytest.ini                          # Test runner configuration
├── requirements.txt                    # Project dependencies (pure stdlib + pytest)
├── main.py                             # CLI executable entry point
├── src/
│   └── from_qom_to_new_york/
│       ├── __init__.py                 # Package root
│       ├── __main__.py                 # python -m entry point
│       ├── core/
│       │   ├── station.py              # Station & GPS Coordinates models (Haversine distance)
│       │   ├── edge.py                 # Edge model with distance, time, capacity, weight
│       │   ├── dsu.py                  # Disjoint Set Union (Path Compression + Union by Rank)
│       │   ├── graph.py                # Adjacency List Graph representation
│       │   └── data.py                 # Official dataset (20 Stations, 21 Edges from PDF)
│       ├── algorithms/
│       │   ├── search.py               # BFS, DFS, Connectivity & Connected Components
│       │   ├── shortest_path.py        # Dijkstra, Bellman-Ford, DAG SP, Floyd-Warshall
│       │   ├── mst.py                  # Kruskal, Prim, and Comparative Benchmarking
│       │   ├── flow.py                 # Edmonds-Karp Max-Flow and Min-Cut Bottlenecks
│       │   ├── connectivity.py         # Tarjan Cut-Vertices (Articulation Points) & Bridges
│       │   ├── scheduling.py           # Interval Scheduling (Greedy EFT & Weighted DP)
│       │   ├── priority.py             # Min-Heap Priority Queue for Train Dispatch
│       │   ├── analytics.py            # Quickselect Rank Statistics & Traffic Analytics
│       │   ├── simulation.py           # Stochastic Passenger Queue & Turnstile Simulation
│       │   ├── string.py               # Levenshtein Distance & Token-Level Fuzzy Search
│       │   ├── approximation.py        # Emergency Placement (Dominating Set: Greedy vs Exact)
│       │   └── advanced.py             # A*, Bidirectional Dijkstra, Dynamic Congestion Routing
│       ├── services/
│       │   ├── routing_service.py      # High-level pathfinding & navigation
│       │   ├── infrastructure_service.py # Network design, MST, DAG, Negative cycles
│       │   ├── operations_service.py   # Daily dispatch, platform scheduling, simulation
│       │   ├── analysis_service.py     # Diagnostics, resilience, max-flow, emergency teams
│       │   └── metro_system.py         # Central Facade unifying all services
│       └── cli/
│           ├── app.py                  # Subcommand parser & interactive menu loop
│           ├── commands.py             # Subcommand handlers
│           └── formatters.py           # ASCII tables, colored output, path visualizer
├── tests/                              # Comprehensive test suite (31 unit/integration tests)
│   ├── test_graph.py
│   ├── test_search.py
│   ├── test_shortest_path.py
│   ├── test_mst.py
│   ├── test_flow.py
│   ├── test_connectivity.py
│   ├── test_scheduling.py
│   ├── test_priority.py
│   ├── test_string.py
│   ├── test_approximation.py
│   ├── test_advanced.py
│   └── test_services.py
└── reports/
    └── TECHNICAL_REPORT.md             # Formal engineering report with mathematical proofs
```

---

## ⚡ Installation & Requirements

### Requirements
- **Python 3.10+** (strictly pure standard library architecture)
- `pytest` (optional, for running the test suite)

### Setup
```bash
# Clone or navigate to the repository
cd /home/parsa/Workspace/Projects/University/Algorithm/from-qom-to-new-york

# Optional: create a virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install test runner
pip install -r requirements.txt
```

---

## 🚀 How to Run (CLI & Interactive Menu)

### 1. Interactive Engineering Shell
Run without arguments to launch the rich terminal menu:
```bash
python3 main.py
```

### 2. Direct Subcommands

| Task | Command | Description |
| :--- | :--- | :--- |
| **System Info** | `python3 main.py info` | Displays all 20 stations, coordinates, and 21 track connections |
| **Connectivity** | `python3 main.py connectivity -s "Qaleh Kamkar" -t "Jamkaran" -m bfs` | Checks reachability via BFS or DFS |
| **Shortest Route** | `python3 main.py route -s "Terminal" -t "Jamkaran" --metric distance --algo astar` | Computes shortest path (Dijkstra, A*, Bidirectional, Dynamic) |
| **MST Optimization** | `python3 main.py mst --algo compare --metric distance` | Compares Kruskal (with Union-Find) vs Prim |
| **Express Line DAG** | `python3 main.py express -s "Terminal" -t "Jamkaran"` | Computes shortest route on one-way DAG in $\mathcal{O}(V + E)$ |
| **Negative Cycles** | `python3 main.py bellman-ford -s "Terminal" -t "Jamkaran" [--negative-test]` | Runs Bellman-Ford and detects negative loops |
| **Platform Schedule** | `python3 main.py schedule [--weighted]` | Schedules non-overlapping platform train slots (Greedy EFT or DP) |
| **Train Dispatch** | `python3 main.py dispatch` | Inspects and pops highest priority train from Min-Heap |
| **Traffic Analytics** | `python3 main.py analytics -k 5` | Finds $k$-th busiest station using Quickselect $\mathcal{O}(N)$ |
| **Queue Simulation** | `python3 main.py simulate -d 60 -m 1.5` | Simulates passenger arrivals at turnstiles |
| **All-Pairs Matrix** | `python3 main.py floyd --metric distance` | Pre-computes Floyd-Warshall $20 \times 20$ distance matrix |
| **Max-Flow / Min-Cut** | `python3 main.py maxflow -s "Terminal" -t "Jamkaran"` | Calculates peak passenger throughput & bottleneck cut |
| **Resilience Analysis**| `python3 main.py critical` | Finds Articulation Points and Bridges via Tarjan's DFS |
| **Emergency Teams** | `python3 main.py emergency [--exact]` | Computes Dominating Set deployment (Greedy vs Exact) |
| **Fuzzy Search** | `python3 main.py search "motahary"` | Typo-tolerant search using Levenshtein distance |
| **Full Benchmark** | `python3 main.py benchmark` | Runs comparative performance benchmarks |

---

## 📊 Algorithmic Complexity Master Table

| Round | Task Code | Algorithm | Time Complexity | Auxiliary Space | Key Data Structure |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **R1** | T1.1 | Graph Modeling | $\mathcal{O}(1)$ insertion | $\mathcal{O}(V + E)$ | Adjacency List (`dict[str, list[Edge]]`) |
| **R1** | T1.2 | Reachability / Path | $\mathcal{O}(V + E)$ | $\mathcal{O}(V)$ | Queue (`deque`) / Recursion Stack |
| **R1** | T1.3 | Shortest Path | $\mathcal{O}((V + E)\log V)$ | $\mathcal{O}(V)$ | Binary Min-Heap (`heapq`) |
| **R2** | T2.1 | Kruskal MST | $\mathcal{O}(E \log E)$ | $\mathcal{O}(V + E)$ | Edge Array + DSU |
| **R2** | T2.1 | Prim MST | $\mathcal{O}(E \log V)$ | $\mathcal{O}(V + E)$ | Min-Heap Priority Queue |
| **R2** | T2.2 | Disjoint Set Union | $\mathcal{O}(\alpha(N))$ amortized | $\mathcal{O}(N)$ | Tree Arrays (`parent`, `rank`) |
| **R2** | T2.3 | Express DAG Shortest Path | $\mathcal{O}(V + E)$ linear | $\mathcal{O}(V)$ | In-degree Queue (Kahn's Topo Sort) |
| **R2** | T2.4 | Bellman-Ford | $\mathcal{O}(V \cdot E)$ | $\mathcal{O}(V)$ | Distance & Predecessor Arrays |
| **R3** | T3.1 | Interval Scheduling (EFT) | $\mathcal{O}(n \log n)$ | $\mathcal{O}(n)$ | Sorted Interval List |
| **R3** | T3.1 | Weighted Interval Sched. | $\mathcal{O}(n \log n)$ | $\mathcal{O}(n)$ | DP Table + Binary Search (`bisect`) |
| **R3** | T3.2 | Train Dispatch Queue | $\mathcal{O}(\log N)$ push/pop | $\mathcal{O}(N)$ | Indexed Binary Min-Heap |
| **R3** | T3.3 | Quickselect Rank Stats | Expected $\mathcal{O}(N)$ | $\mathcal{O}(1)$ | In-place Partitioning |
| **R3** | T3.4 | Passenger Gate Queue | $\mathcal{O}(P \log C)$ | $\mathcal{O}(P)$ | Discrete Event / $M/M/c$ Model |
| **R4** | T4.1 | Floyd-Warshall All-Pairs | $\mathcal{O}(V^3)$ | $\mathcal{O}(V^2)$ | 2D Distance & Next Matrices |
| **R4** | T4.2 | Edmonds-Karp Max-Flow | $\mathcal{O}(V \cdot E^2)$ | $\mathcal{O}(V + E)$ | Residual Adjacency Matrix |
| **R4** | T4.3 | Tarjan's DFS Resilience | $\mathcal{O}(V + E)$ | $\mathcal{O}(V)$ | Discovery Times & Low-Links |
| **R4** | T4.4 | Dominating Set (Greedy) | $\mathcal{O}(V(V + E))$ | $\mathcal{O}(V)$ | Bitmasks / Closed Neighborhoods |
| **R4** | T4.4 | Dominating Set (Exact) | $\mathcal{O}(2^V)$ | $\mathcal{O}(V)$ | Bitmask Branch & Bound |
| **R4** | T4.5 | Levenshtein Search | $\mathcal{O}(M \cdot N)$ | $\mathcal{O}(\min(M, N))$ | 2-Row Dynamic Programming |
| **R5** | Inno 1 | A* Search (Haversine) | $\mathcal{O}(E \log V)$ | $\mathcal{O}(V)$ | Min-Heap + Coordinate Heuristic |
| **R5** | Inno 2 | Bidirectional Dijkstra | $\mathcal{O}((V + E)\log V)$ | $\mathcal{O}(V)$ | Dual Min-Heaps ($Q_F, Q_B$) |
| **R5** | Inno 3 | Dynamic BPR Congestion | $\mathcal{O}((V + E)\log V)$ | $\mathcal{O}(V)$ | Volume-Delay Function |

---

## 🧪 Running Unit & Integration Tests

The test suite contains **31 comprehensive unit and integration tests** verifying correctness, asymptotic constraints, negative cycle handling, and edge cases.

```bash
pytest -v
```

Expected output:
```text
============================== 31 passed in 0.05s ==============================
```

---

## 💎 Design Decisions & SOLID Architecture

1. **Single Responsibility Principle (SRP):**
   - Graph representation (`core/graph.py`) only manages topology.
   - Algorithms (`algorithms/`) are pure functions with zero side-effects.
   - Services (`services/`) orchestrate domain logic.
   - CLI (`cli/`) handles user interaction and formatting.
2. **Open/Closed Principle (OCP):**
   - New routing algorithms (e.g. Contraction Hierarchies, ALT) can be introduced without modifying existing Dijkstra or A* code.
3. **Liskov Substitution & Interface Segregation:**
   - Graph traversal protocols work interchangeably on directed, undirected, and residual subgraphs.
4. **Dependency Inversion Principle (DIP):**
   - Services depend on abstractions and pass callables (`weight_fn`, `heuristic_fn`), decoupling core mechanics from specific metrics.
5. **No Magic Numbers & Strict Typing:**
   - Full Python type hints (`Optional`, `Dict`, `List`, `Tuple`, `Callable`) used across every module.
   - Docstrings follow Google/NumPy conventions, focusing on *why* algorithms were chosen and their mathematical foundations.