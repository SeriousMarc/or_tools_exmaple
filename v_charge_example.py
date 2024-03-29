from dataclasses import dataclass
from typing import List
from random import randint
from pprint import pprint
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp


"""CONSTRAINTS"""
charge_spot_capacity = 3
max_vehicle_on_charge_spot = charge_spot_capacity
vehicle_charge_time = 2
vehicle_energy_stock = vehicle_charge_time * 2

@dataclass
class Point:
    x: int
    y: int


def rectilinear_distance(p1: Point, p2: Point) -> int:
    return abs(p1.x - p2.x) + abs(p1.y - p2.y)


def location_generator(length: int = 10, a: int = 0, b: int = 1000) -> List[Point]:
    return [Point(randint(a, b), randint(a, b)) for _ in range(length)]


def distance_matrix_generator(points: List[Point]) -> List[List[int]]:
    matrix = list()

    for point_i in points:
        matrix.append([rectilinear_distance(point_i, point_j) for point_j in points])

    print('Distance matrix:')
    pprint(matrix)

    return matrix


def create_data_model() -> dict:
    """Stores the data for the problem."""
    # Definitions
    return dict(
        # TSP
        distance_matrix=distance_matrix_generator(location_generator()),
        depot=0,
        # VRP
        num_vehicles=2,
        # VRPTW
        # Resource Constraints
    )


def print_solution(data, manager, routing, solution):
    """Prints solution on console."""
    max_route_distance = 0

    for vehicle_id in range(data['num_vehicles']):
        index = routing.Start(vehicle_id)
        plan_output = 'Route for vehicle {}:\n'.format(vehicle_id)
        route_distance = 0

        while not routing.IsEnd(index):
            plan_output += ' {} -> '.format(manager.IndexToNode(index))
            previous_index = index
            index = solution.Value(routing.NextVar(index))
            route_distance += routing.GetArcCostForVehicle(previous_index, index, vehicle_id)

        plan_output += '{}\n'.format(manager.IndexToNode(index))
        plan_output += 'Distance of the route: {}m\n'.format(route_distance)

        print(plan_output)

        max_route_distance = max(route_distance, max_route_distance)

    print('Maximum of the route distances: {}m'.format(max_route_distance))


def main():
    """Entry point of the program."""
    # Instantiate the data problem.
    data = create_data_model()

    # Create the routing index manager.
    manager = pywrapcp.RoutingIndexManager(len(data['distance_matrix']), data['num_vehicles'], data['depot'])

    # Create Routing Model.
    routing = pywrapcp.RoutingModel(manager)

    def distance_callback(from_index, to_index):
        """Returns the distance between the two nodes."""
        # Convert from routing variable Index to distance matrix NodeIndex.
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)

        return data['distance_matrix'][from_node][to_node]

    transit_callback_index = routing.RegisterTransitCallback(distance_callback)

    # Define cost of each arc.
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    # Add Distance constraint.
    dimension_name = 'Distance'
    routing.AddDimension(
        transit_callback_index,
        0,  # no slack
        3000,  # vehicle maximum travel distance
        True,  # start cumul to zero
        dimension_name)
    distance_dimension = routing.GetDimensionOrDie(dimension_name)
    distance_dimension.SetGlobalSpanCostCoefficient(100)

    # Add Load Time constraint
    dimension_name = 'LoadTime'  # in hours
    routing.AddDimension(transit_callback_index, 0, 8, False, dimension_name)
    
    # Setting first solution heuristic.
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC

    # Solve the problem.
    assignment = routing.SolveWithParameters(search_parameters)

    # Print solution on console.
    if assignment:
        print_solution(data, manager, routing, assignment)


if __name__ == '__main__':
    main()
