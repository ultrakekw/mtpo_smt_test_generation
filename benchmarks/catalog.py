from __future__ import annotations

from dataclasses import dataclass
from importlib import import_module
from typing import Any, Callable, Literal, Sequence


ParameterKind = Literal["int", "bool", "str"]


@dataclass(frozen=True)
class ParameterSpec:
    name: str
    kind: ParameterKind
    initial: Any
    lower_bound: int = -50
    upper_bound: int = 50
    alphabet: str = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789/_-."
    max_length: int = 16

    def coerce(self, value: Any) -> Any:
        if self.kind == "int":
            return int(value)
        if self.kind == "bool":
            if isinstance(value, str):
                normalized = value.strip().lower()
                if normalized in {"true", "1", "yes"}:
                    return True
                if normalized in {"false", "0", "no", ""}:
                    return False
            return bool(value)
        if self.kind == "str":
            return str(value)
        raise TypeError(f"Unsupported parameter kind: {self.kind}")

    @property
    def initial_value(self) -> Any:
        return self.coerce(self.initial)

    @property
    def pyexz3_symbolic_value(self) -> Any:
        if self.kind == "bool":
            return int(bool(self.initial))
        return self.initial_value


@dataclass(frozen=True)
class Benchmark:
    name: str
    module_name: str
    function_name: str
    parameters: Sequence[ParameterSpec]
    total_branches: int
    family: Literal["micro", "industrial"] = "micro"
    scenario: str = ""
    supported_tools: Sequence[str] = ("mini", "pyexz3", "crosshair")

    @property
    def file_name(self) -> str:
        return f"{self.name}.py"

    @property
    def argument_names(self) -> tuple[str, ...]:
        return tuple(parameter.name for parameter in self.parameters)

    def parameter_map(self) -> dict[str, ParameterSpec]:
        return {parameter.name: parameter for parameter in self.parameters}

    def load_function(self) -> Callable:
        return getattr(import_module(self.module_name), self.function_name)

    def load_branch_collector(self) -> Callable:
        return getattr(import_module(self.module_name), "collect_branches")

    def seed_inputs(self) -> dict[str, Any]:
        return {parameter.name: parameter.initial_value for parameter in self.parameters}


BENCHMARKS = [
    Benchmark(
        name="threshold",
        module_name="benchmarks.threshold",
        function_name="threshold",
        parameters=(ParameterSpec("x", "int", 0, lower_bound=-50, upper_bound=50),),
        total_branches=6,
        family="micro",
        scenario="Линейная цепочка арифметических условий",
    ),
    Benchmark(
        name="pair_relation",
        module_name="benchmarks.pair_relation",
        function_name="pair_relation",
        parameters=(
            ParameterSpec("x", "int", 0, lower_bound=-20, upper_bound=20),
            ParameterSpec("y", "int", 0, lower_bound=-20, upper_bound=20),
        ),
        total_branches=8,
        family="micro",
        scenario="Вложенные ветви и нелинейное целочисленное ограничение",
    ),
    Benchmark(
        name="loop_bucket",
        module_name="benchmarks.loop_bucket",
        function_name="loop_bucket",
        parameters=(
            ParameterSpec("x", "int", 0, lower_bound=-10, upper_bound=10),
            ParameterSpec("y", "int", 0, lower_bound=-10, upper_bound=10),
        ),
        total_branches=12,
        family="micro",
        scenario="Ограниченный цикл и постусловие после итераций",
    ),
    Benchmark(
        name="fastapi_status_body",
        module_name="benchmarks.fastapi_status_body",
        function_name="fastapi_status_body",
        parameters=(
            ParameterSpec("status_code", "int", 200, lower_bound=100, upper_bound=399),
        ),
        total_branches=8,
        family="industrial",
        scenario="FastAPI: допустимость тела ответа для HTTP status code",
        supported_tools=("mini", "pyexz3", "crosshair"),
    ),
    Benchmark(
        name="flask_load_dotenv",
        module_name="benchmarks.flask_load_dotenv",
        function_name="flask_load_dotenv",
        parameters=(
            ParameterSpec(
                "val",
                "str",
                "",
                alphabet="abcdefghijklmnopqrstuvwxyz0123456789",
                max_length=5,
            ),
            ParameterSpec("default", "bool", False),
        ),
        total_branches=6,
        family="industrial",
        scenario="Flask: интерпретация флага FLASK_SKIP_DOTENV",
        supported_tools=("mini", "pyexz3", "crosshair"),
    ),
    Benchmark(
        name="pip_archive_suffix",
        module_name="benchmarks.pip_archive_suffix",
        function_name="pip_archive_suffix",
        parameters=(
            ParameterSpec(
                "name",
                "str",
                "",
                alphabet="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789._-",
                max_length=16,
            ),
        ),
        total_branches=10,
        family="industrial",
        scenario="pip: распознавание архивного имени дистрибутива по суффиксу",
        supported_tools=("mini", "pyexz3", "crosshair"),
    ),
    Benchmark(
        name="werkzeug_server_name",
        module_name="benchmarks.werkzeug_server_name",
        function_name="werkzeug_server_name",
        parameters=(
            ParameterSpec(
                "scheme",
                "str",
                "",
                alphabet="abcdefghijklmnopqrstuvwxyz",
                max_length=5,
            ),
            ParameterSpec(
                "server_name",
                "str",
                "",
                alphabet="abcdefghijklmnopqrstuvwxyz0123456789.:-",
                max_length=18,
            ),
        ),
        total_branches=8,
        family="industrial",
        scenario="Werkzeug: stripping standard ports from server names",
        supported_tools=("mini", "pyexz3", "crosshair"),
    ),
    Benchmark(
        name="black_numeric_string",
        module_name="benchmarks.black_numeric_string",
        function_name="black_numeric_string",
        parameters=(
            ParameterSpec(
                "text",
                "str",
                "",
                alphabet="0123456789.",
                max_length=5,
            ),
        ),
        total_branches=6,
        family="industrial",
        scenario="Black: различение случаев нормализации числовой строки",
        supported_tools=("mini", "pyexz3", "crosshair"),
    ),
]
