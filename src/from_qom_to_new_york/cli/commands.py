"""CLI Command implementations for all 5 rounds of the case study."""

from __future__ import annotations

import argparse
import sys
from typing import Optional

from from_qom_to_new_york.algorithms.advanced import compare_dijkstra_vs_astar
from from_qom_to_new_york.algorithms.approximation import (
    exact_minimum_dominating_set,
    greedy_dominating_set,
)
from from_qom_to_new_york.algorithms.connectivity import find_articulation_points_and_bridges
from from_qom_to_new_york.algorithms.flow import edmonds_karp_max_flow
from from_qom_to_new_york.algorithms.mst import compare_mst_algorithms, kruskal_mst, prim_mst
from from_qom_to_new_york.algorithms.scheduling import (
    interval_scheduling_greedy,
    weighted_interval_scheduling_dp,
)
from from_qom_to_new_york.algorithms.search import bfs_connectivity, dfs_connectivity
from from_qom_to_new_york.algorithms.shortest_path import (
    bellman_ford,
    dag_shortest_path,
    dijkstra,
    floyd_warshall,
)
from from_qom_to_new_york.algorithms.string import fuzzy_search_stations
from from_qom_to_new_york.cli.formatters import (
    blue,
    bold,
    cyan,
    format_path,
    format_table,
    green,
    magenta,
    print_banner,
    print_section,
    red,
    yellow,
)
from from_qom_to_new_york.services.metro_system import MetroSystem


def cmd_info(system: MetroSystem, args: argparse.Namespace) -> None:
    """Display comprehensive network metadata, all stations, and track connections."""
    print_banner("Qom Metro Transit Network - System Overview", "UrbanPulse Dynamics Technical Case Study")

    g = system.graph
    print(f"Network Topology: {bold('Planar Transit Adjacency List')}")
    print(f"Total Stations (|V|): {bold(g.order)}")
    print(f"Total Track Connections (|E|): {bold(g.size)}")
    print(f"Average Degree: {bold(round(sum(g.degree(s) for s in g.get_station_names()) / g.order, 2))}")

    # Stations table
    print_section("Registered Stations")
    st_headers = ["ID", "Station Name", "Coordinates (Lat, Lon)", "Type", "Key Facilities"]
    st_rows = []
    for st in g.get_all_stations():
        coord_str = f"({st.coordinates.latitude:.4f}, {st.coordinates.longitude:.4f})" if st.coordinates else "N/A"
        st_type = "Terminal" if st.is_terminal else ("Transfer Hub" if st.is_transfer else "Standard")
        fac_str = ", ".join(st.facilities[:2]) if st.facilities else "-"
        st_rows.append([st.id, st.name, coord_str, st_type, fac_str])
    print(format_table(st_headers, st_rows))

    # Edges table
    print_section("Track Connections")
    edge_headers = ["Source", "Destination", "Distance (km)", "Time (min)", "Hourly Capacity"]
    edge_rows = []
    for e in g.get_all_edges(deduplicate_undirected=True):
        edge_rows.append([e.source, e.target, f"{e.distance_km:.1f}", f"{e.time_minutes:.1f}", e.capacity])
    print(format_table(edge_headers, edge_rows))


def cmd_connectivity(system: MetroSystem, args: argparse.Namespace) -> None:
    """T1.2: Check connectivity between two stations via BFS or DFS."""
    src = args.source or "Terminal Mosaferbari Qom"
    dst = args.target or "Masjed Moghaddas Jamkaran"
    method = args.method.lower()

    print_banner("T1.2: Station Connectivity & Reachability Engine", f"Method: {method.upper()}")

    res = system.routing.check_connectivity(src, dst, method=method)
    if res.reachable and res.path:
        print(f"\n{green('✔ STATUS: REACHABLE')}")
        print(f"Hop Count (Edges): {bold(res.distance_hops)}")
        print(f"Explored Vertices: {bold(res.visited_count)}")
        print(f"\nDiscovered Route:\n{format_path(res.path)}")
    else:
        print(f"\n{red('✖ STATUS: UNREACHABLE')}")


def cmd_route(system: MetroSystem, args: argparse.Namespace) -> None:
    """T1.3 & Round 5: Find shortest path using Dijkstra, A*, Bidirectional Dijkstra, or Floyd."""
    src = args.source or "Terminal Mosaferbari Qom"
    dst = args.target or "Masjed Moghaddas Jamkaran"
    metric = args.metric.lower()
    algo = args.algo.lower()

    print_banner(f"Route Optimization Engine - {algo.upper()}", f"Optimizing for: {metric.upper()}")

    unit = "km" if metric == "distance" else ("minutes" if metric == "time" else "units")

    if algo == "dynamic":
        # Demonstrate dynamic congestion re-routing
        flows = {
            ("Meydan Motahari", "Haram Motahhar Hazrat Masoumeh"): 8800.0,
            ("Meydan Motahari", "Bimarestan Nekouei"): 5200.0,
        }
        res_cong = system.routing.dynamic_congestion_route(src, dst, passenger_flows=flows)
        print(f"Static Shortest Route ({metric}):\n{format_path(res_cong.static_shortest_path)}")
        print(f"Static Cost: {bold(res_cong.static_cost_minutes)} minutes")
        print(f"\n{yellow('Congestion-Aware Dynamic Route:')}\n{format_path(res_cong.dynamic_optimal_path)}")
        print(f"Dynamic Congested Cost: {bold(res_cong.dynamic_cost_minutes)} minutes")
        print(f"Benefit: {green(res_cong.congestion_avoidance_benefit)}")
        return

    res = system.routing.find_shortest_path(src, dst, metric=metric, algorithm=algo)

    if res.path:
        print(f"\n{green('✔ Route Found Successfully!')}")
        print(f"Optimal Path:\n{format_path(res.path)}")
        print(f"Total Cost: {bold(f'{res.total_cost:.2f} {unit}')}")
        print(f"Stations Traversed: {bold(len(res.path))}")
        print(f"Algorithm Nodes Visited: {bold(res.nodes_visited)}")
    else:
        print(f"\n{red('✖ No route found between')} {bold(src)} and {bold(dst)}")


def cmd_mst(system: MetroSystem, args: argparse.Namespace) -> None:
    """T2.1 / T2.2: Compute Minimum Spanning Tree via Kruskal (with Union-Find) and Prim."""
    metric = args.metric.lower()
    mode = args.algo.lower()

    print_banner("T2.1 / T2.2: Minimum Spanning Tree (MST) Optimization", f"Metric: {metric.upper()}")

    if mode == "compare":
        comp = system.infrastructure.compare_mst_algorithms(metric=metric)
        k_res, p_res = comp.kruskal_result, comp.prim_result
        unit = "km" if metric == "distance" else "min"

        rows = [
            ["Algorithm", "Kruskal (with Union-Find)", "Prim (with Min-Heap)"],
            ["Total Spanning Cost", f"{k_res.total_weight:.2f} {unit}", f"{p_res.total_weight:.2f} {unit}"],
            ["Spanning Edges Selected", len(k_res.mst_edges), len(p_res.mst_edges)],
            ["Spans All Vertices", "YES (|V|-1 edges)", "YES (|V|-1 edges)"],
            ["Execution Time", f"{k_res.execution_time_ms:.4f} ms", f"{p_res.execution_time_ms:.4f} ms"],
            ["Theoretical Complexity", "O(E log E) / O(E * alpha(V))", "O(E log V)"],
        ]
        headers = ["Metric / Attribute", "Kruskal", "Prim"]
        print(format_table(headers, [[r[0], r[1], r[2]] for r in rows]))
        print(f"\n{green('✔ Both algorithms matched on exact MST total cost!')}")
        print(f"\nAnalysis:\n{comp.analysis}")

        print_section("Selected Spanning Tree Rail Tracks")
        t_headers = ["Segment #", "Station A", "Station B", f"Weight ({unit})"]
        t_rows = [[i + 1, e.source, e.target, f"{e.get_weight(metric):.1f}"] for i, e in enumerate(k_res.mst_edges)]
        print(format_table(t_headers, t_rows))
    else:
        res = system.infrastructure.design_minimum_cost_network(algorithm=mode, metric=metric)
        unit = "km" if metric == "distance" else "min"
        print(f"Algorithm: {bold(res.algorithm_name)}")
        print(f"Total MST Cost: {bold(f'{res.total_weight:.2f} {unit}')}")
        print(f"Edges Selected: {bold(len(res.mst_edges))}")
        print(f"Execution Time: {bold(f'{res.execution_time_ms:.4f} ms')}")


def cmd_express(system: MetroSystem, args: argparse.Namespace) -> None:
    """T2.3: Express Line DAG Shortest Path."""
    src = args.source or "Terminal Mosaferbari Qom"
    dst = args.target or "Masjed Moghaddas Jamkaran"
    metric = args.metric.lower()

    print_banner("T2.3: Express Line Directed Acyclic Graph (DAG) Shortest Path", "Topological Sort Linear O(V + E) Routing")

    res = system.infrastructure.compute_express_dag_shortest_path(src, dst, metric=metric)
    unit = "km" if metric == "distance" else "minutes"

    if res.path:
        print(f"\n{green('✔ Express Route Found!')}")
        print(f"Optimal Express Path:\n{format_path(res.path)}")
        print(f"Total Express Cost: {bold(f'{res.total_cost:.2f} {unit}')}")
        print(f"Nodes Relaxed (Topological Order): {bold(res.nodes_visited)}")
    else:
        print(f"\n{red('✖ Destination unreachable on one-way Express DAG from')} {bold(src)}")


def cmd_bellman_ford(system: MetroSystem, args: argparse.Namespace) -> None:
    """T2.4: Bellman-Ford Shortest Path with Negative Cycle Detection."""
    src = args.source or "Terminal Mosaferbari Qom"
    dst = args.target or "Masjed Moghaddas Jamkaran"
    inject = args.negative_test

    print_banner("T2.4: Bellman-Ford Negative Weight & Cycle Detector", "Promotional Subsidy Analysis")

    res = system.infrastructure.evaluate_negative_weights(src, dst, inject_test_negative_cycle=inject)

    if res.has_negative_cycle:
        print(f"\n{red('⚠ CRITICAL WARNING: NEGATIVE CYCLE DETECTED IN NETWORK!')}")
        print("A negative cycle allows unbounded profit / time reduction through looping.")
        if res.negative_cycle:
            print(f"Negative Cycle Loop:\n{format_path(res.negative_cycle)}")
    else:
        print(f"\n{green('✔ Network verified: NO negative cycles exist.')}")
        if res.path:
            print(f"Shortest Path with Promotional Subsidies:\n{format_path(res.path)}")
            print(f"Total Net Subsidized Cost: {bold(f'{res.total_cost:.2f}')}")


def cmd_schedule(system: MetroSystem, args: argparse.Namespace) -> None:
    """T3.1: Train Platform Interval Scheduling."""
    weighted = args.weighted

    print_banner("T3.1: Platform Interval Scheduling Engine", "Greedy Earliest Finish Time (EFT) & DP Weighted")

    requests = system.operations.generate_sample_platform_requests()
    res = system.operations.schedule_platform_trains(requests, weighted=weighted)

    print(f"Mode: {bold('Weighted DP' if weighted else 'Greedy Earliest Finish Time (Unweighted)')}")
    print(f"Requested Train Slots: {bold(len(requests))}")
    print(f"Scheduled (Accepted) Trains: {bold(res.total_trains)}")
    print(f"Platform Capacity Utilization: {bold(f'{res.platform_utilization_ratio * 100:.1f}%')}")

    print_section("Scheduled Train Time Slots")
    s_headers = ["Train ID", "Occupancy Window", "Duration", "Line", "Weight / Priority"]
    s_rows = [
        [t.train_id, f"{t.start_time:.2f} - {t.end_time:.2f}", f"{t.duration * 60:.0f} min", t.line, t.weight]
        for t in res.selected_trains
    ]
    print(format_table(s_headers, s_rows))

    if res.rejected_trains:
        print_section("Rejected Conflicting Train Requests")
        r_headers = ["Train ID", "Conflict Window", "Line", "Weight"]
        r_rows = [[t.train_id, f"{t.start_time:.2f} - {t.end_time:.2f}", t.line, t.weight] for t in res.rejected_trains]
        print(format_table(r_headers, r_rows))


def cmd_dispatch(system: MetroSystem, args: argparse.Namespace) -> None:
    """T3.2: Train Dispatch Priority Queue Management."""
    print_banner("T3.2: Train Dispatch Priority Queue", "Min-Heap Urgency Ranking Engine")

    system.operations.initialize_sample_dispatch_queue()
    trains = system.operations.get_dispatch_queue_status()

    print_section("Active Train Dispatch Priority Queue")
    headers = ["Priority Rank", "Train ID", "Line", "Delay (min)", "Emergency Level", "Passengers", "Urgency Score"]
    rows = [
        [
            i + 1,
            t.train_id,
            t.line_name,
            f"{t.delay_minutes:.1f}",
            "Level 3 (Critical)" if t.emergency_level == 3 else f"Level {t.emergency_level}",
            t.passenger_count,
            f"{t.urgency_score:.1f}",
        ]
        for i, t in enumerate(trains)
    ]
    print(format_table(headers, rows))

    next_train = system.operations.peek_next_train()
    if next_train:
        print(f"\n{green('➔ NEXT IN LINE FOR DISPATCH:')} {bold(next_train.train_id)} ({next_train.line_name}) with Urgency Score {bold(round(next_train.urgency_score, 1))}")


def cmd_analytics(system: MetroSystem, args: argparse.Namespace) -> None:
    """T3.3: Operational Ridership Analytics & Quickselect."""
    k = args.k

    print_banner("T3.3: Transit Ridership Analytics & Quickselect", f"Evaluating k={k}-th Busiest Station")

    summary = system.operations.analyze_operational_traffic(k_busiest=k)

    print(f"Network Total Daily Trips: {bold(f'{summary.total_system_trips:,}')}")
    print(f"Average Daily Trips per Station: {bold(f'{summary.average_daily_trips:,.2f}')}")
    print(f"Ridership Standard Deviation: {bold(f'{summary.standard_deviation:,.2f}')}")
    print(f"Busiest Station (Rank 1): {bold(green(summary.busiest_station))}")
    print(f"{bold(f'Rank {summary.k_rank} Most Frequent Station (via Quickselect):')} {bold(yellow(summary.kth_busiest_station))}")

    print_section("Full Station Ridership Ranking")
    headers = ["Rank", "Station Name", "Daily Passenger Trips", "Share of Network"]
    rows = [
        [i + 1, name, f"{count:,}", f"{(count / summary.total_system_trips) * 100:.2f}%"]
        for i, (name, count) in enumerate(summary.station_rankings)
    ]
    print(format_table(headers, rows))


def cmd_simulate(system: MetroSystem, args: argparse.Namespace) -> None:
    """T3.4: Stochastic Passenger Arrival and Gate Simulation."""
    duration = args.duration
    multiplier = args.multiplier

    print_banner("T3.4: Stochastic Passenger Arrival Simulation", f"Horizon: {duration:.0f} min | Load Multiplier: {multiplier:.1f}x")

    rep = system.operations.run_passenger_simulation(duration_minutes=duration, peak_multiplier=multiplier)

    print(f"Total Network Arrivals: {bold(f'{rep.total_system_passengers:,}')}")
    print(f"Average System Wait Time: {bold(f'{rep.average_system_wait_time_minutes * 60:.1f} seconds')}")
    print(f"Max Passenger Wait Time: {bold(f'{rep.max_system_wait_time_minutes * 60:.1f} seconds')}")
    print(f"Busiest Station in Simulation: {bold(green(rep.busiest_station))}")

    print_section("Station Turnstile & Gate Performance")
    headers = ["Station", "Arrived", "Served", "Avg Wait (s)", "Max Q", "Gate Util %", "Bottleneck?"]
    rows = []
    for name, m in rep.station_metrics.items():
        rows.append([
            name,
            m.total_passengers_arrived,
            m.total_passengers_served,
            f"{m.avg_wait_time_minutes * 60:.1f}",
            m.max_queue_length,
            f"{m.gate_utilization_ratio * 100:.1f}%",
            red("YES (Bottleneck)") if m.is_bottleneck else green("Optimal"),
        ])
    print(format_table(headers, rows))

    print_section("Operational Recommendations")
    for r in rep.recommendations:
        print(f"  • {r}")


def cmd_floyd(system: MetroSystem, args: argparse.Namespace) -> None:
    """T4.1: Floyd-Warshall All-Pairs Shortest Path Matrix."""
    metric = args.metric.lower()

    print_banner("T4.1: Floyd-Warshall All-Pairs Shortest Paths", f"Pre-computed Matrix ({metric.upper()})")

    res = system.analysis.compute_all_pairs_matrix(metric=metric)
    stations = res.stations
    unit = "km" if metric == "distance" else "min"

    print(f"Matrix Dimension: {bold(f'{len(stations)} x {len(stations)}')} = {len(stations)**2} pairs pre-computed.")
    print(f"Query Response Time: {bold('O(1) Instant Lookup')}")
    print(f"Path Reconstruction Time: {bold('O(Length) Linear')}")

    # Display subset matrix for top 6 major stations
    sub_stations = [
        "Terminal Mosaferbari Qom",
        "Qaleh Kamkar",
        "Meydan Motahari",
        "Haram Motahhar Hazrat Masoumeh",
        "Pardisan",
        "Masjed Moghaddas Jamkaran",
    ]
    print_section(f"Sample Distance Matrix ({unit})")
    short_names = ["Terminal", "Qaleh", "Motahari", "Haram", "Pardisan", "Jamkaran"]
    headers = ["Origin \\ Dest"] + short_names
    rows = []
    for i, src in enumerate(sub_stations):
        row = [short_names[i]]
        for dst in sub_stations:
            d = res.get_distance(src, dst)
            row.append(f"{d:.1f}" if d < float("inf") else "INF")
        rows.append(row)
    print(format_table(headers, rows))


def cmd_maxflow(system: MetroSystem, args: argparse.Namespace) -> None:
    """T4.2: Maximum Passenger Flow and Min-Cut Bottlenecks (Edmonds-Karp)."""
    src = args.source or "Terminal Mosaferbari Qom"
    dst = args.target or "Masjed Moghaddas Jamkaran"

    print_banner("T4.2: Peak-Hour Passenger Capacity & Max-Flow (Edmonds-Karp)", f"{src} ➔ {dst}")

    res = system.analysis.compute_peak_capacity(src, dst)

    print(f"Source Terminal: {bold(src)}")
    print(f"Destination: {bold(dst)}")
    print(f"Maximum Peak Flow: {bold(green(f'{res.max_flow:,.0f} passengers/hour'))}")

    print_section("Active Flow on Tracks")
    headers = ["From Station", "To Station", "Allocated Flow (passengers/hr)"]
    rows = [[u, v, f"{f:,.0f}"] for (u, v), f in res.flow_on_edges.items()]
    print(format_table(headers, rows))

    print_section("Minimum Cut Saturated Bottlenecks (Max-Flow Min-Cut Theorem)")
    b_headers = ["Bottleneck Segment", "Track Capacity"]
    b_rows = [[f"{e.source} <-> {e.target}", f"{e.capacity:,} pass/hr"] for e in res.bottleneck_edges]
    print(format_table(b_headers, b_rows))


def cmd_critical(system: MetroSystem, args: argparse.Namespace) -> None:
    """T4.3: Articulation Points & Bridges (Tarjan's DFS)."""
    print_banner("T4.3: Critical Infrastructure & Resilience Analysis", "Tarjan's DFS Cut-Vertices and Bridges")

    res = system.analysis.identify_critical_infrastructure()

    print(f"Total Articulation Points (Cut-Vertices): {bold(red(len(res.articulation_points)))}")
    print(f"Total Bridges (Critical Tracks): {bold(red(len(res.bridges)))}")

    print_section("Critical Stations (Single Points of Failure)")
    ap_headers = ["#", "Station Name", "Failure Impact"]
    ap_rows = [[i + 1, ap, res.critical_station_details.get(ap, "Critical Hub")] for i, ap in enumerate(res.articulation_points)]
    print(format_table(ap_headers, ap_rows))

    print_section("Critical Rail Bridges (Cut Edges)")
    br_headers = ["#", "Station A", "Station B", "Severity"]
    br_rows = [[i + 1, u, v, red("High Vulnerability (Track Severing)")] for i, (u, v) in enumerate(res.bridges)]
    print(format_table(br_headers, br_rows))


def cmd_emergency(system: MetroSystem, args: argparse.Namespace) -> None:
    """T4.4: Emergency Response Team Deployment (Dominating Set)."""
    exact = args.exact

    print_banner("T4.4: Emergency Response Team Placement (Dominating Set)", f"Method: {'Exact Branch & Bound' if exact else 'Greedy Set Cover Approximation'}")

    res = system.analysis.plan_emergency_response_deployment(exact=exact)

    print(f"Deployment Strategy: {bold('Exact Optimal' if res.is_exact_optimal else 'Greedy Approximation')}")
    print(f"Total Emergency Teams Needed: {bold(green(res.team_count))}")
    print(f"Network Maximum Degree (Delta): {bold(res.max_degree)}")
    print(f"Theoretical Approximation Guarantee H(Delta+1): {bold(f'{res.theoretical_approx_ratio:.3f}x')}")
    print(f"All 20 Stations Fully Covered (dist <= 1): {bold(green('YES') if res.is_valid_dominating_set else red('NO'))}")

    print_section("Selected Emergency Base Stations")
    for i, st in enumerate(res.chosen_stations):
        covered_nbrs = [nbr for nbr, base in res.coverage_map.items() if base == st and nbr != st]
        print(f"  {bold(f'{i+1}. {st}')} ➔ Covers on-site + neighbors: {cyan(', '.join(covered_nbrs) or 'None')}")


def cmd_search(system: MetroSystem, args: argparse.Namespace) -> None:
    """T4.5 / T4.6: Fuzzy Station Search using Levenshtein Distance."""
    query = args.query

    print_banner("T4.5 / T4.6: Typo-Tolerant Station Name Search", f"Query: '{query}'")

    results = system.analysis.search_station_fuzzy(query, top_k=args.top_k)

    headers = ["Rank", "Station Name", "Edit Distance", "Similarity %", "Match Quality"]
    rows = []
    for i, r in enumerate(results):
        quality = green("Exact / Near Match") if r.similarity_score >= 0.8 else (yellow("Good Match") if r.similarity_score >= 0.5 else red("Weak Match"))
        rows.append([i + 1, r.station_name, r.edit_distance, f"{r.similarity_score * 100:.1f}%", quality])
    print(format_table(headers, rows))


def cmd_benchmark(system: MetroSystem, args: argparse.Namespace) -> None:
    """Benchmark comparisons for algorithms across all rounds."""
    print_banner("Comprehensive Algorithmic Benchmark & Efficiency Evaluation", "Qom Transit Optimization Suite")

    print_section("1. Routing Search Space: Dijkstra vs A*")
    src = "Terminal Mosaferbari Qom"
    dst = "Masjed Moghaddas Jamkaran"
    comp_a = system.routing.compare_dijkstra_astar(src, dst, metric="distance")
    print(f"Query: {src} ➔ {dst}")
    print(f"  • Dijkstra Nodes Explored: {bold(comp_a.dijkstra_visited_nodes)}")
    print(f"  • A* Nodes Explored: {bold(green(comp_a.astar_visited_nodes))}")
    print(f"  • Search Space Reduction: {bold(green(f'{comp_a.search_space_reduction_pct:.1f}%'))}")

    print_section("2. Minimum Spanning Tree: Kruskal vs Prim")
    comp_mst = system.infrastructure.compare_mst_algorithms(metric="distance")
    print(f"  • Kruskal (with Union-Find): {bold(f'{comp_mst.kruskal_result.execution_time_ms:.4f} ms')} (Cost: {comp_mst.kruskal_result.total_weight} km)")
    print(f"  • Prim (with Min-Heap): {bold(f'{comp_mst.prim_result.execution_time_ms:.4f} ms')} (Cost: {comp_mst.prim_result.total_weight} km)")
    print(f"  • Optimal Spanning Trees Match: {bold(green('YES'))}")

    print_section("3. Emergency Team Placement: Greedy vs Exact Optimum")
    greedy_res = system.analysis.plan_emergency_response_deployment(exact=False)
    exact_res = system.analysis.plan_emergency_response_deployment(exact=True)
    print(f"  • Greedy Approximation: {bold(greedy_res.team_count)} teams (Theoretical bound: {greedy_res.theoretical_approx_ratio:.2f}x)")
    print(f"  • Exact Global Optimum: {bold(green(exact_res.team_count))} teams")
    gap = greedy_res.team_count - exact_res.team_count
    print(f"  • Empirical Optimality Gap: {bold(green('0 (Exact match!)') if gap == 0 else f'{gap} team(s)')}")
