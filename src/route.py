from random import shuffle

from task import Task


DEPOT: int = 1


def random_routes(task: Task) -> list[list[int]]:
    """
    Randomly generate a transportation plan for a task.
    Each vehicle has a node list as its route.
    """
    return from_integrated_route(random_integrated_route(task))


def random_integrated_route(task: Task) -> list[int]:
    """
    Randomly generate a transportation plan for a task.
    The routes for all vehicles are integrated into a single node list.
    """
    intgrtd_route = [i for i in range(
        task.customer_num + task.vehicle_num - 1)]
    shuffle(intgrtd_route)
    return intgrtd_route


def valid_routes(task: Task) -> list[list[int]]:
    """
    Generate a valid transportation plan for a task.
    """
    demands = [(task.demand(i + 2), i + 2) for i in range(task.customer_num)]
    demands.sort()

    routes = []
    for _ in range(task.vehicle_num):
        route = []
        cap = 0
        while demands and cap + demands[-1][0] <= task.vehicle_cap:
            next = demands.pop(-1)
            cap += next[0]
            route.append(next[1])
        while demands and cap + demands[0][0] <= task.vehicle_cap:
            next = demands.pop(0)
            cap += next[0]
            route.append(next[1])

        routes.append([DEPOT] + route + [DEPOT])

    assert valid(task, routes)
    return routes


def cost(task: Task, routes: list[list[int]]) -> float:
    """
    Calculate the cost of a transportation plan.
    """
    dist = 0
    for route in routes:
        for i in range(1, len(route)):
            dist += task.dist(route[i - 1], route[i])
    return dist


def valid(task: Task, routes: list[list[int]]) -> bool:
    """
    Check if a transportation plan is not overloaded.
    """
    customers = set()
    for route in routes:
        for customer in route:
            customers.add(customer)

    return len(customers) == task.customer_num + 1 and sum(overload_caps(task, routes)) == 0


def overload_caps(task: Task, routes: list[list[int]]) -> list[int]:
    """
    Calculate the overload weight for each route in a transportation plan.
    """
    overloads = []
    for cap in caps(task, routes):
        overloads.append(max(cap - task.vehicle_cap, 0))
    return overloads


def caps(task: Task, routes: list[list[int]]) -> list[int]:
    """
    Calculate the total demand for each route in a transportation plan.
    """
    caps = []
    for route in routes:
        cap = 0
        for customer in route:
            cap += task.demand(customer)
        caps.append(cap)
    return caps


def from_integrated_route(task: Task, intgrtd_route: list[int]) -> list[list[int]]:
    """
    Convert an integrated node list into a list of routes.
    """
    # The customer number is 2-based.
    intgrtd_route = list(map(lambda x: x + 2, intgrtd_route))
    route, routes = [], []
    for i in range(len(intgrtd_route)):
        customer = intgrtd_route[i]
        if customer <= task.customer_num + 1:
            route.append(customer)

        if (customer > task.customer_num + 1 or i == len(intgrtd_route) - 1) and route:
            routes.append([DEPOT] + route + [DEPOT])
            route = []

    assert len(routes) <= task.vehicle_num
    if len(routes) < task.vehicle_num:
        routes.extend([[DEPOT, DEPOT]
                      for _ in range(task.vehicle_num - len(routes))])
    return routes


def to_integrated_route(routes: list[list[int]]) -> list[int]:
    """
    Convert a list of routes into an integrated node list.
    """
    intgrtd_route = []
    depot_id = max(max(route) for route in routes)
    for route in routes:
        intgrtd_route.extend(
            ([] if not intgrtd_route else [depot_id]) + route[1:-1])
        depot_id += 1
    # The customer number is 2-based.
    return list(map(lambda x: x - 2, intgrtd_route))