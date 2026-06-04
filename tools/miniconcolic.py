from __future__ import annotations

import inspect
from dataclasses import dataclass
from typing import Any, Callable, Sequence

import z3

from benchmarks.catalog import ParameterSpec


_ACTIVE_TRACE: "ExecutionTrace | None" = None


def _as_symscalar(value: Any) -> "SymInt | SymBool | SymStr":
    if isinstance(value, (SymInt, SymBool, SymStr)):
        return value
    if isinstance(value, bool):
        return SymBool(bool(value), z3.BoolVal(bool(value)))
    if isinstance(value, int):
        return SymInt(int(value), z3.IntVal(int(value)))
    if isinstance(value, str):
        return SymStr(str(value), z3.StringVal(str(value)))
    raise TypeError(f"Unsupported symbolic operand type: {type(value)!r}")


def _as_symbool(value: Any) -> "SymBool":
    symbolic = _as_symscalar(value)
    if isinstance(symbolic, SymBool):
        return symbolic
    raise TypeError(f"Expected symbolic bool, got {type(symbolic)!r}")


def _as_symint(value: Any) -> "SymInt":
    symbolic = _as_symscalar(value)
    if isinstance(symbolic, SymInt):
        return symbolic
    raise TypeError(f"Expected symbolic int, got {type(symbolic)!r}")


def _as_symstr(value: Any) -> "SymStr":
    symbolic = _as_symscalar(value)
    if isinstance(symbolic, SymStr):
        return symbolic
    raise TypeError(f"Expected symbolic str, got {type(symbolic)!r}")


@dataclass
class Decision:
    expr: z3.BoolRef
    taken: bool


class ExecutionTrace:
    def __init__(self) -> None:
        self.decisions: list[Decision] = []

    def record(self, condition: "SymBool") -> bool:
        self.decisions.append(Decision(condition.expr, condition.concrete))
        return condition.concrete


class SymBool:
    def __init__(self, concrete: bool, expr: z3.BoolRef):
        self.concrete = bool(concrete)
        self.expr = expr

    def __bool__(self) -> bool:
        if _ACTIVE_TRACE is None:
            return self.concrete
        return _ACTIVE_TRACE.record(self)

    def __invert__(self) -> "SymBool":
        return SymBool(not self.concrete, z3.Not(self.expr))

    def __and__(self, other: Any) -> "SymBool":
        other = _as_symbool(other)
        return SymBool(self.concrete and other.concrete, z3.And(self.expr, other.expr))

    def __rand__(self, other: Any) -> "SymBool":
        return _as_symbool(other).__and__(self)

    def __or__(self, other: Any) -> "SymBool":
        other = _as_symbool(other)
        return SymBool(self.concrete or other.concrete, z3.Or(self.expr, other.expr))

    def __ror__(self, other: Any) -> "SymBool":
        return _as_symbool(other).__or__(self)

    def __eq__(self, other: Any) -> "SymBool":  # type: ignore[override]
        other = _as_symbool(other)
        return SymBool(self.concrete == other.concrete, self.expr == other.expr)

    def __ne__(self, other: Any) -> "SymBool":  # type: ignore[override]
        other = _as_symbool(other)
        return SymBool(self.concrete != other.concrete, self.expr != other.expr)

    def __repr__(self) -> str:
        return f"SymBool(concrete={self.concrete}, expr={self.expr})"


class SymInt:
    def __init__(self, concrete: int, expr: z3.ArithRef):
        self.concrete = int(concrete)
        self.expr = expr

    def _binary(self, other: Any, concrete_fn: Callable[[int, int], int], expr_fn: Callable[[Any, Any], Any]) -> "SymInt":
        other = _as_symint(other)
        return SymInt(concrete_fn(self.concrete, other.concrete), expr_fn(self.expr, other.expr))

    def _compare(self, other: Any, concrete_fn: Callable[[int, int], bool], expr_fn: Callable[[Any, Any], Any]) -> SymBool:
        other = _as_symint(other)
        return SymBool(concrete_fn(self.concrete, other.concrete), expr_fn(self.expr, other.expr))

    def __add__(self, other: Any) -> "SymInt":
        return self._binary(other, lambda a, b: a + b, lambda a, b: a + b)

    def __radd__(self, other: Any) -> "SymInt":
        return _as_symint(other).__add__(self)

    def __sub__(self, other: Any) -> "SymInt":
        return self._binary(other, lambda a, b: a - b, lambda a, b: a - b)

    def __rsub__(self, other: Any) -> "SymInt":
        return _as_symint(other).__sub__(self)

    def __mul__(self, other: Any) -> "SymInt":
        return self._binary(other, lambda a, b: a * b, lambda a, b: a * b)

    def __rmul__(self, other: Any) -> "SymInt":
        return _as_symint(other).__mul__(self)

    def __neg__(self) -> "SymInt":
        return SymInt(-self.concrete, -self.expr)

    def __lt__(self, other: Any) -> SymBool:
        return self._compare(other, lambda a, b: a < b, lambda a, b: a < b)

    def __le__(self, other: Any) -> SymBool:
        return self._compare(other, lambda a, b: a <= b, lambda a, b: a <= b)

    def __gt__(self, other: Any) -> SymBool:
        return self._compare(other, lambda a, b: a > b, lambda a, b: a > b)

    def __ge__(self, other: Any) -> SymBool:
        return self._compare(other, lambda a, b: a >= b, lambda a, b: a >= b)

    def __eq__(self, other: Any) -> SymBool:  # type: ignore[override]
        return self._compare(other, lambda a, b: a == b, lambda a, b: a == b)

    def __ne__(self, other: Any) -> SymBool:  # type: ignore[override]
        return self._compare(other, lambda a, b: a != b, lambda a, b: a != b)

    def __int__(self) -> int:
        return self.concrete

    def __repr__(self) -> str:
        return f"SymInt(concrete={self.concrete}, expr={self.expr})"


class SymStr:
    def __init__(self, concrete: str, expr: z3.SeqRef):
        self.concrete = str(concrete)
        self.expr = expr

    def __bool__(self) -> bool:
        concrete = bool(self.concrete)
        expr = z3.Length(self.expr) != 0
        condition = SymBool(concrete, expr)
        if _ACTIVE_TRACE is None:
            return concrete
        return _ACTIVE_TRACE.record(condition)

    def __add__(self, other: Any) -> "SymStr":
        other = _as_symstr(other)
        return SymStr(self.concrete + other.concrete, z3.Concat(self.expr, other.expr))

    def __radd__(self, other: Any) -> "SymStr":
        return _as_symstr(other).__add__(self)

    def __eq__(self, other: Any) -> SymBool:  # type: ignore[override]
        other = _as_symstr(other)
        return SymBool(self.concrete == other.concrete, self.expr == other.expr)

    def __ne__(self, other: Any) -> SymBool:  # type: ignore[override]
        other = _as_symstr(other)
        return SymBool(self.concrete != other.concrete, self.expr != other.expr)

    def startswith(self, prefix: Any) -> SymBool:
        prefix = _as_symstr(prefix)
        return SymBool(self.concrete.startswith(prefix.concrete), z3.PrefixOf(prefix.expr, self.expr))

    def endswith(self, suffix: Any) -> SymBool:
        suffix = _as_symstr(suffix)
        return SymBool(self.concrete.endswith(suffix.concrete), z3.SuffixOf(suffix.expr, self.expr))

    def __contains__(self, item: Any) -> SymBool:
        item = _as_symstr(item)
        return SymBool(item.concrete in self.concrete, z3.Contains(self.expr, item.expr))

    def __repr__(self) -> str:
        return f"SymStr(concrete={self.concrete!r}, expr={self.expr})"


def _concretize(value: Any) -> Any:
    if isinstance(value, SymInt):
        return value.concrete
    if isinstance(value, SymBool):
        return value.concrete
    if isinstance(value, SymStr):
        return value.concrete
    return value


def _symbolize_value(name: str, value: Any) -> SymInt | SymBool | SymStr:
    if isinstance(value, bool):
        return SymBool(value, z3.Bool(name))
    if isinstance(value, int):
        return SymInt(value, z3.Int(name))
    if isinstance(value, str):
        return SymStr(value, z3.String(name))
    raise TypeError(f"Unsupported input type for symbolic execution: {type(value)!r}")


def run_once(function: Callable, concrete_inputs: dict[str, Any]) -> tuple[Any, list[Decision]]:
    global _ACTIVE_TRACE
    trace = ExecutionTrace()
    inspect.signature(function)
    symbolic_inputs = {
        name: _symbolize_value(name, concrete_inputs[name])
        for name in concrete_inputs
    }
    previous_trace = _ACTIVE_TRACE
    _ACTIVE_TRACE = trace
    try:
        result = function(**symbolic_inputs)
    finally:
        _ACTIVE_TRACE = previous_trace
    return _concretize(result), trace.decisions


def _decision_constraints(decisions: list[Decision], negate_index: int) -> list[z3.BoolRef]:
    constraints: list[z3.BoolRef] = []
    for index, decision in enumerate(decisions):
        expr = decision.expr if decision.taken else z3.Not(decision.expr)
        if index == negate_index:
            expr = z3.Not(expr)
        constraints.append(expr)
    return constraints


def _string_domain_constraints(symbol: z3.SeqRef, spec: ParameterSpec) -> list[z3.BoolRef]:
    constraints: list[z3.BoolRef] = [z3.Length(symbol) >= 0, z3.Length(symbol) <= spec.max_length]
    alphabet = sorted(set(spec.alphabet))
    if not alphabet:
        return constraints
    for index in range(spec.max_length):
        allowed = [z3.SubString(symbol, index, 1) == z3.StringVal(char) for char in alphabet]
        constraints.append(z3.Or(z3.Length(symbol) <= index, z3.Or(*allowed)))
    return constraints


def _decode_model_value(spec: ParameterSpec, value: z3.ExprRef) -> Any:
    if spec.kind == "int":
        return value.as_long()
    if spec.kind == "bool":
        return z3.is_true(value)
    if spec.kind == "str":
        return value.as_string()
    raise TypeError(f"Unsupported parameter kind: {spec.kind}")


def solve_path(
    parameter_specs: Sequence[ParameterSpec],
    decisions: list[Decision],
    negate_index: int,
) -> dict[str, Any] | None:
    solver = z3.Solver()
    symbols: dict[str, z3.ExprRef] = {}

    for spec in parameter_specs:
        if spec.kind == "int":
            symbol = z3.Int(spec.name)
            solver.add(symbol >= spec.lower_bound)
            solver.add(symbol <= spec.upper_bound)
        elif spec.kind == "bool":
            symbol = z3.Bool(spec.name)
        elif spec.kind == "str":
            symbol = z3.String(spec.name)
            solver.add(*_string_domain_constraints(symbol, spec))
        else:
            raise TypeError(f"Unsupported parameter kind: {spec.kind}")
        symbols[spec.name] = symbol

    for constraint in _decision_constraints(decisions[: negate_index + 1], negate_index):
        solver.add(constraint)
    if solver.check() != z3.sat:
        return None

    model = solver.model()
    result: dict[str, Any] = {}
    for spec in parameter_specs:
        value = model.eval(symbols[spec.name], model_completion=True)
        result[spec.name] = _decode_model_value(spec, value)
    return result


def explore(function: Callable, parameter_specs: Sequence[ParameterSpec], max_iterations: int = 20) -> list[dict[str, Any]]:
    pending_inputs: list[dict[str, Any]] = [{spec.name: spec.initial_value for spec in parameter_specs}]
    seen_inputs: set[tuple[tuple[str, Any], ...]] = set()
    seen_prefixes: set[str] = set()
    collected: list[dict[str, Any]] = []

    while pending_inputs and len(collected) < max_iterations:
        concrete_inputs = pending_inputs.pop(0)
        frozen_input = tuple(sorted(concrete_inputs.items()))
        if frozen_input in seen_inputs:
            continue
        seen_inputs.add(frozen_input)
        result, decisions = run_once(function, concrete_inputs)
        collected.append({"inputs": concrete_inputs, "result": result, "path_length": len(decisions)})
        for index in range(len(decisions)):
            constraints = _decision_constraints(decisions[: index + 1], index)
            prefix_key = " && ".join(str(z3.simplify(constraint)) for constraint in constraints)
            if prefix_key in seen_prefixes:
                continue
            seen_prefixes.add(prefix_key)
            candidate = solve_path(parameter_specs, decisions, index)
            if candidate is None:
                continue
            candidate_key = tuple(sorted(candidate.items()))
            if candidate_key not in seen_inputs:
                pending_inputs.append(candidate)
    return collected
