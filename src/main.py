from pathlib import Path
import argparse
import json

from deap import base, creator, tools, algorithms

from task import Task
import route


def load_config(path: Path) -> dict:
    """
    Load the configuration.
    """
    with path.open(encoding="utf-8") as file:
        cfg = json.load(file)
    if cfg["populationSize"] <= 0:
        raise ValueError("The population size must be greater than 0")
    if cfg["generationNum"] <= 0:
        raise ValueError("The number of generation must be greater than 0")

    cfg["rate"]["cross"] = min(1, max(0, cfg["rate"]["cross"]))
    cfg["rate"]["mutate"] = min(1, max(0, cfg["rate"]["mutate"]))
    cfg["tournProportion"] = min(1, max(0, cfg["tournProportion"]))
    return cfg


parser = argparse.ArgumentParser()
parser.add_argument('--task', '-t', help="The task number", type=int, default=1)
args = parser.parse_args()

cfg = load_config(Path(__file__).parent.joinpath("config.json"))
data_dir = Path(__file__).parent.parent.joinpath("tasks", str(args.task))
task = Task(data_dir.joinpath("spec.txt"), data_dir.joinpath(
    "demand.txt"), data_dir.joinpath("distance.txt"))


creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
creator.create("Individual", list, fitness=creator.FitnessMin, task=task)


def to_individual(integrated_route: list[int]) -> creator.Individual:
    """
    Convert an integrated route into a genetic individual.
    """
    return creator.Individual(integrated_route)


def from_individual(ind: creator.Individual) -> list[list[int]]:
    """
    Convert a genetic individual into an integrated route.
    """
    return route.from_integrated_route(ind.task, ind)


def evaluation(ind: creator.Individual) -> float:
    """
    Evaluate a genetic individual's fitness.
    """
    routes = from_individual(ind)
    return (route.cost(ind.task, routes),)


def valid(ind: creator.Individual) -> float:
    """
    Check if a genetic individual is overloaded.
    """
    routes = from_individual(ind)
    return route.valid(ind.task, routes)


def penalty_base(task: Task) -> float:
    """
    If a genetic individual is overloaded, this penalty is added to its fitness as a penalty base.
    """
    dist = 0
    for i in range(1, task.customer_num + 1):
        for j in range(1, task.customer_num + 1):
            dist += task.dist(i, j)
    return dist


def overload_penalty(ind: creator.Individual) -> float:
    """
    Apart from the penalty base, this value is also added to a genetic individual's fitness if it is overloaded.
    It increases as overload weight increases.
    """
    routes = from_individual(ind)
    return sum(route.overload_caps(ind.task, routes)) ** 2


toolbox = base.Toolbox()
toolbox.register("individual", lambda: to_individual(
    route.random_integrated_route(task)))
toolbox.register("population", tools.initRepeat, list, toolbox.individual)
toolbox.register("evaluate", evaluation)
toolbox.decorate("evaluate", tools.DeltaPenalty(
    valid, penalty_base(task), overload_penalty))
toolbox.register("mate", tools.cxOrdered)
toolbox.register("mutate", tools.mutShuffleIndexes, indpb=0.05)
toolbox.register("select", tools.selTournament,
                 tournsize=max(int(cfg["populationSize"] * cfg["tournProportion"]), 2))


pop = toolbox.population(n=cfg["populationSize"])
fame = tools.HallOfFame(1)
final_pop, log = algorithms.eaSimple(pop, toolbox,
                                     cxpb=cfg["rate"]["cross"], mutpb=cfg["rate"]["mutate"],
                                     ngen=cfg["generationNum"], halloffame=fame, verbose=False)


res_dir = Path(__file__).parent.parent.joinpath("results")
if not res_dir.exists():
    res_dir.mkdir(parents=True)

with res_dir.joinpath(f"{args.task}.txt").open(encoding="utf-8", mode="a") as file:
    file.write(
        f"Task: {args.task}\nPopulation Size: {cfg['populationSize']}\nGeneration Number: {cfg['generationNum']}\n")
    for ind in fame:
        routes = from_individual(ind)
        if not route.valid(task, routes):
            file.write("[Overload]\n")
        file.write(f"Cost: {route.cost(task, routes)}\n")
        file.write("Routes:\n")
        for route in routes:
            file.write(f"{route}\n")
        file.write("\n\n")