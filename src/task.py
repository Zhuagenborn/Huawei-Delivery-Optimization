import csv
from pathlib import Path


class Task:
    def __init__(self, spec: Path, demand: Path, dist: Path) -> None:
        self._customer_num: int = 0
        self._vehicle_num: int = 0
        self._vehicle_cap: int = 0
        self._dist: list[list[float]] = None
        self._demand: list[int] = None

        self._read_spec(spec)
        self._read_demand(demand)
        self._read_dist(dist)

    @property
    def vehicle_cap(self) -> int:
        return self._vehicle_cap

    @property
    def vehicle_num(self) -> int:
        return self._vehicle_num

    @property
    def customer_num(self) -> int:
        return self._customer_num

    @property
    def demands(self) -> list[int]:
        return list(self._demand)

    def demand(self, customer: int) -> int:
        return self._demand[customer - 1]

    def dist(self, src: int, dest: int) -> float:
        return self._dist[src - 1][dest - 1]

    def _read_dist(self, path: Path) -> None:
        self._dist = []
        with path.open(newline="", encoding="utf-8") as file:
            for row in csv.reader(file):
                self._dist.append([float(dist) for dist in row])

    def _read_demand(self, path: Path) -> None:
        assert self._customer_num > 0

        self._demand = [0] * (self._customer_num + 1)
        with path.open(newline="", encoding="utf-8") as file:
            for row in csv.reader(file):
                self._demand[int(row[0]) - 1] = int(row[1])

    def _read_spec(self, path: Path) -> None:
        with path.open(newline="", encoding="utf-8") as file:
            for row in csv.reader(file):
                self._customer_num = int(row[0])
                self._vehicle_num = int(row[1])
                self._vehicle_cap = int(row[2])
                return