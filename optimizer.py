import pandas as pd
import numpy as np
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
from math import radians, cos, sin, asin, sqrt

# -------------------------------
# Distance calculation (Haversine)
# -------------------------------
def haversine(lon1, lat1, lon2, lat2):
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * asin(sqrt(a))
    r = 6371  # km
    return c * r

# -------------------------------
# Create OR-Tools data model
# -------------------------------
def create_data_model(df, num_vehicles, vehicle_capacity):
    data = {}

    coords = df[['lat', 'lon']].to_numpy()
    size = len(coords)

    # Distance matrix (meters, int)
    dist_matrix = np.zeros((size, size), dtype=int)
    for i in range(size):
        for j in range(size):
            dist = haversine(
                coords[i][1], coords[i][0],
                coords[j][1], coords[j][0]
            )
            dist_matrix[i][j] = int(dist * 1000)

    data["distance_matrix"] = dist_matrix

    # Demands (Depot = 0)
    demands = df["pending_mbu"].tolist()
    demands[0] = 0
    data["demands"] = demands

    data["num_vehicles"] = num_vehicles
    data["vehicle_capacities"] = [vehicle_capacity] * num_vehicles
    data["depot"] = 0

    return data

# -------------------------------
# Solve Vehicle Routing Problem
# -------------------------------
def solve_vrp(df, num_vehicles=3, vehicle_capacity=200):
    # Add depot row (first row)
    depot = {
        "school_name": "DEPOT",
        "lat": df.iloc[0]["lat"],
        "lon": df.iloc[0]["lon"],
        "pending_mbu": 0,
        "risk_level": "Depot"
    }

    # High‑risk schools only
    critical_df = df[df["risk_level"] == "High"].copy()

    if critical_df.empty:
        return []

    critical_df = pd.concat(
        [pd.DataFrame([depot]), critical_df],
        ignore_index=True
    )

    data = create_data_model(critical_df, num_vehicles, vehicle_capacity)

    manager = pywrapcp.RoutingIndexManager(
        len(data["distance_matrix"]),
        data["num_vehicles"],
        data["depot"]
    )

    routing = pywrapcp.RoutingModel(manager)

    # Distance callback
    def distance_callback(from_index, to_index):
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return data["distance_matrix"][from_node][to_node]

    transit_cb = routing.RegisterTransitCallback(distance_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(transit_cb)

    # Capacity constraint
    def demand_callback(from_index):
        from_node = manager.IndexToNode(from_index)
        return data["demands"][from_node]

    demand_cb = routing.RegisterUnaryTransitCallback(demand_callback)

    routing.AddDimensionWithVehicleCapacity(
        demand_cb,
        0,
        data["vehicle_capacities"],
        True,
        "Capacity"
    )

    # Solver parameters
    search_params = pywrapcp.DefaultRoutingSearchParameters()
    search_params.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
    )

    solution = routing.SolveWithParameters(search_params)

    if not solution:
        return []

    # -------------------------------
    # Extract routes
    # -------------------------------
    routes = []

    for vehicle_id in range(data["num_vehicles"]):
        index = routing.Start(vehicle_id)
        route = []

        while not routing.IsEnd(index):
            node = manager.IndexToNode(index)
            route.append(critical_df.iloc[node].to_dict())
            index = solution.Value(routing.NextVar(index))

        # End at depot
        node = manager.IndexToNode(index)
        route.append(critical_df.iloc[node].to_dict())

        if len(route) > 1:
            routes.append(route)

    return routes
