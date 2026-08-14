"""Main CLI Application interface and interactive menu loop."""

from __future__ import annotations

import argparse
import sys
from typing import List, Optional

from from_qom_to_new_york.cli.commands import (
    cmd_analytics,
    cmd_bellman_ford,
    cmd_benchmark,
    cmd_connectivity,
    cmd_critical,
    cmd_dispatch,
    cmd_emergency,
    cmd_express,
    cmd_floyd,
    cmd_info,
    cmd_maxflow,
    cmd_mst,
    cmd_route,
    cmd_schedule,
    cmd_search,
    cmd_simulate,
)
from from_qom_to_new_york.cli.formatters import (
    bold,
    cyan,
    green,
    magenta,
    print_banner,
    red,
    yellow,
)
from from_qom_to_new_york.services.metro_system import MetroSystem


def interactive_menu(system: MetroSystem) -> None:
    """Run interactive CLI menu."""
    while True:
        print_banner("Qom Transit Optimization Platform", "Interactive Engineering Shell")
        print("Select a module to run:")
        print(f"  {bold('1.')} System & Graph Overview (|V|=20, |E|=21)")
        print(f"  {bold('2.')} T1.2: Check Station Connectivity (BFS / DFS)")
        print(f"  {bold('3.')} T1.3 / R5: Shortest Path Routing (Dijkstra, A*, Bi-Dijkstra, Dynamic)")
        print(f"  {bold('4.')} T2.1 / T2.2: Minimum Spanning Tree (Kruskal vs Prim)")
        print(f"  {bold('5.')} T2.3: Express Line DAG Routing (Topological Sort)")
        print(f"  {bold('6.')} T2.4: Negative Cycle & Incentive Detector (Bellman-Ford)")
        print(f"  {bold('7.')} T3.1: Train Platform Interval Scheduling (Greedy EFT & DP)")
        print(f"  {bold('8.')} T3.2: Train Dispatch Priority Queue (Min-Heap)")
        print(f"  {bold('9.')} T3.3: Transit Ridership Analytics & Quickselect")
        print(f"  {bold('10.')} T3.4: Passenger Arrival & Gate Queue Simulation")
        print(f"  {bold('11.')} T4.1: Floyd-Warshall All-Pairs Distance Matrix")
        print(f"  {bold('12.')} T4.2: Maximum Flow & Min-Cut Capacity Analysis (Edmonds-Karp)")
        print(f"  {bold('13.')} T4.3: Critical Infrastructure (Articulation Points & Bridges)")
        print(f"  {bold('14.')} T4.4: Emergency Response Team Deployment (Dominating Set)")
        print(f"  {bold('15.')} T4.5 / T4.6: Fuzzy Station Name Search (Levenshtein)")
        print(f"  {bold('16.')} Round 5: Algorithmic Benchmarks & Exploration Comparison")
        print(f"  {bold('0.')} Exit")

        try:
            choice = input(f"\n{yellow('Enter choice [0-16]: ')}").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nExiting.")
            break

        if choice == "0":
            print("Goodbye!")
            break
        elif choice == "1":
            ns = argparse.Namespace()
            cmd_info(system, ns)
        elif choice == "2":
            src = input("Source station [Terminal Mosaferbari Qom]: ").strip() or "Terminal Mosaferbari Qom"
            dst = input("Destination station [Masjed Moghaddas Jamkaran]: ").strip() or "Masjed Moghaddas Jamkaran"
            method = input("Method [bfs/dfs]: ").strip() or "bfs"
            ns = argparse.Namespace(source=src, target=dst, method=method)
            cmd_connectivity(system, ns)
        elif choice == "3":
            src = input("Source station [Terminal Mosaferbari Qom]: ").strip() or "Terminal Mosaferbari Qom"
            dst = input("Destination station [Masjed Moghaddas Jamkaran]: ").strip() or "Masjed Moghaddas Jamkaran"
            metric = input("Metric [distance/time]: ").strip() or "distance"
            algo = input("Algorithm [dijkstra/astar/bidirectional/dynamic/floyd]: ").strip() or "dijkstra"
            ns = argparse.Namespace(source=src, target=dst, metric=metric, algo=algo)
            cmd_route(system, ns)
        elif choice == "4":
            metric = input("Metric [distance/time]: ").strip() or "distance"
            algo = input("Mode [compare/kruskal/prim]: ").strip() or "compare"
            ns = argparse.Namespace(metric=metric, algo=algo)
            cmd_mst(system, ns)
        elif choice == "5":
            src = input("Source station [Terminal Mosaferbari Qom]: ").strip() or "Terminal Mosaferbari Qom"
            dst = input("Destination station [Masjed Moghaddas Jamkaran]: ").strip() or "Masjed Moghaddas Jamkaran"
            metric = input("Metric [distance/time]: ").strip() or "time"
            ns = argparse.Namespace(source=src, target=dst, metric=metric)
            cmd_express(system, ns)
        elif choice == "6":
            src = input("Source station [Terminal Mosaferbari Qom]: ").strip() or "Terminal Mosaferbari Qom"
            dst = input("Destination station [Masjed Moghaddas Jamkaran]: ").strip() or "Masjed Moghaddas Jamkaran"
            test_neg = input("Inject test negative cycle? [y/N]: ").strip().lower() == "y"
            ns = argparse.Namespace(source=src, target=dst, negative_test=test_neg)
            cmd_bellman_ford(system, ns)
        elif choice == "7":
            weighted = input("Mode [1: Unweighted Greedy EFT, 2: Weighted DP]: ").strip() == "2"
            ns = argparse.Namespace(weighted=weighted)
            cmd_schedule(system, ns)
        elif choice == "8":
            ns = argparse.Namespace()
            cmd_dispatch(system, ns)
        elif choice == "9":
            k_val = input("Rank k for k-th busiest station [5]: ").strip()
            k = int(k_val) if k_val.isdigit() else 5
            ns = argparse.Namespace(k=k)
            cmd_analytics(system, ns)
        elif choice == "10":
            dur_val = input("Simulation duration in minutes [60]: ").strip()
            dur = float(dur_val) if dur_val else 60.0
            peak_val = input("Peak traffic multiplier [1.5]: ").strip()
            peak = float(peak_val) if peak_val else 1.5
            ns = argparse.Namespace(duration=dur, multiplier=peak)
            cmd_simulate(system, ns)
        elif choice == "11":
            metric = input("Metric [distance/time]: ").strip() or "distance"
            ns = argparse.Namespace(metric=metric)
            cmd_floyd(system, ns)
        elif choice == "12":
            src = input("Source station [Terminal Mosaferbari Qom]: ").strip() or "Terminal Mosaferbari Qom"
            dst = input("Sink station [Masjed Moghaddas Jamkaran]: ").strip() or "Masjed Moghaddas Jamkaran"
            ns = argparse.Namespace(source=src, target=dst)
            cmd_maxflow(system, ns)
        elif choice == "13":
            ns = argparse.Namespace()
            cmd_critical(system, ns)
        elif choice == "14":
            exact = input("Solve with exact branch & bound? [y/N]: ").strip().lower() == "y"
            ns = argparse.Namespace(exact=exact)
            cmd_emergency(system, ns)
        elif choice == "15":
            query = input("Search query [e.g. motahari, pardisn, jamkarn]: ").strip() or "motahari"
            ns = argparse.Namespace(query=query, top_k=5)
            cmd_search(system, ns)
        elif choice == "16":
            ns = argparse.Namespace()
            cmd_benchmark(system, ns)
        else:
            print(red("Invalid option. Please choose a valid menu index."))

        input(f"\n{yellow('Press Enter to return to menu...')}")


def build_cli_parser() -> argparse.ArgumentParser:
    """Build the command-line argument parser."""
    parser = argparse.ArgumentParser(
        prog="from-qom-to-new-york",
        description="Qom Metro Transit Optimization Platform - Technical Case Study",
    )
    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    # info
    subparsers.add_parser("info", help="Display network overview, stations, and track topology")

    # connectivity
    p_conn = subparsers.add_parser("connectivity", help="Check reachability between two stations (BFS/DFS)")
    p_conn.add_argument("--source", "-s", type=str, default="Terminal Mosaferbari Qom")
    p_conn.add_argument("--target", "-t", type=str, default="Masjed Moghaddas Jamkaran")
    p_conn.add_argument("--method", "-m", choices=["bfs", "dfs"], default="bfs")

    # route
    p_route = subparsers.add_parser("route", help="Find shortest path between stations")
    p_route.add_argument("--source", "-s", type=str, default="Terminal Mosaferbari Qom")
    p_route.add_argument("--target", "-t", type=str, default="Masjed Moghaddas Jamkaran")
    p_route.add_argument("--metric", choices=["distance", "time"], default="distance")
    p_route.add_argument("--algo", choices=["dijkstra", "astar", "bidirectional", "dynamic", "floyd"], default="dijkstra")

    # mst
    p_mst = subparsers.add_parser("mst", help="Compute Minimum Spanning Tree (Kruskal/Prim)")
    p_mst.add_argument("--metric", choices=["distance", "time"], default="distance")
    p_mst.add_argument("--algo", choices=["compare", "kruskal", "prim"], default="compare")

    # express
    p_exp = subparsers.add_parser("express", help="One-way Express Line DAG shortest path")
    p_exp.add_argument("--source", "-s", type=str, default="Terminal Mosaferbari Qom")
    p_exp.add_argument("--target", "-t", type=str, default="Masjed Moghaddas Jamkaran")
    p_exp.add_argument("--metric", choices=["distance", "time"], default="time")

    # bellman-ford
    p_bf = subparsers.add_parser("bellman-ford", help="Bellman-Ford with negative cycle detection")
    p_bf.add_argument("--source", "-s", type=str, default="Terminal Mosaferbari Qom")
    p_bf.add_argument("--target", "-t", type=str, default="Masjed Moghaddas Jamkaran")
    p_bf.add_argument("--negative-test", action="store_true", help="Inject an artificial negative cycle to test detection")

    # schedule
    p_sched = subparsers.add_parser("schedule", help="Train platform interval scheduling")
    p_sched.add_argument("--weighted", action="store_true", help="Use weighted dynamic programming")

    # dispatch
    subparsers.add_parser("dispatch", help="Inspect train dispatch priority queue")

    # analytics
    p_an = subparsers.add_parser("analytics", help="Operational ridership analytics & Quickselect")
    p_an.add_argument("-k", type=int, default=5, help="Query rank for k-th busiest station")

    # simulate
    p_sim = subparsers.add_parser("simulate", help="Stochastic passenger arrival simulation")
    p_sim.add_argument("--duration", "-d", type=float, default=60.0, help="Simulation duration in minutes")
    p_sim.add_argument("--multiplier", "-m", type=float, default=1.0, help="Traffic load multiplier")

    # floyd
    p_fl = subparsers.add_parser("floyd", help="Floyd-Warshall all-pairs distance matrix")
    p_fl.add_argument("--metric", choices=["distance", "time"], default="distance")

    # maxflow
    p_mf = subparsers.add_parser("maxflow", help="Maximum passenger flow & min-cut (Edmonds-Karp)")
    p_mf.add_argument("--source", "-s", type=str, default="Terminal Mosaferbari Qom")
    p_mf.add_argument("--target", "-t", type=str, default="Masjed Moghaddas Jamkaran")

    # critical
    subparsers.add_parser("critical", help="Identify articulation points and bridge tracks")

    # emergency
    p_emg = subparsers.add_parser("emergency", help="Emergency response team placement (Dominating Set)")
    p_emg.add_argument("--exact", action="store_true", help="Compute exact global optimum via branch-and-bound")

    # search
    p_srch = subparsers.add_parser("search", help="Fuzzy station name search (Levenshtein)")
    p_srch.add_argument("query", type=str, help="Station search query string")
    p_srch.add_argument("--top-k", "-k", type=int, default=5, help="Max candidate matches")

    # benchmark
    subparsers.add_parser("benchmark", help="Run algorithmic benchmarks and comparisons")

    # interactive
    subparsers.add_parser("interactive", help="Start interactive shell menu")

    return parser


def main(argv: Optional[List[str]] = None) -> int:
    """CLI application entry point."""
    system = MetroSystem.create_default()
    parser = build_cli_parser()
    args = parser.parse_args(argv)

    if args.command is None or args.command == "interactive":
        interactive_menu(system)
        return 0

    command_handlers = {
        "info": cmd_info,
        "connectivity": cmd_connectivity,
        "route": cmd_route,
        "mst": cmd_mst,
        "express": cmd_express,
        "bellman-ford": cmd_bellman_ford,
        "schedule": cmd_schedule,
        "dispatch": cmd_dispatch,
        "analytics": cmd_analytics,
        "simulate": cmd_simulate,
        "floyd": cmd_floyd,
        "maxflow": cmd_maxflow,
        "critical": cmd_critical,
        "emergency": cmd_emergency,
        "search": cmd_search,
        "benchmark": cmd_benchmark,
    }

    handler = command_handlers.get(args.command)
    if handler:
        handler(system, args)
        return 0
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())
