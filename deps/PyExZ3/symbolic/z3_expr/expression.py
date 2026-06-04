import utils

from symbolic.symbolic_types.symbolic_int import SymbolicInteger
from symbolic.symbolic_types.symbolic_str import SymbolicStr
from symbolic.symbolic_types.symbolic_type import SymbolicType
from z3 import *

class Z3Expression(object):
	def __init__(self):
		self.z3_vars = {}

	def toZ3(self,solver,asserts,query):
		self.z3_vars = {}
		solver.assert_exprs([self.predToZ3(p,solver) for p in asserts])
		solver.assert_exprs(Not(self.predToZ3(query,solver)))

	def predToZ3(self,pred,solver,env=None):
		sym_expr = self._astToZ3Expr(pred.symtype,solver,env)
		if env == None:
			if not is_bool(sym_expr):
				sym_expr = sym_expr != self._constant(0,solver)
			if not pred.result:
				sym_expr = Not(sym_expr)
		else:
			if not pred.result:
				sym_expr = not sym_expr
		return sym_expr

	def getIntVars(self):
		return [ v[1] for v in self.z3_vars.items() if self._isIntVar(v[1]) ]

	def getStringVars(self):
		return [ v[1] for v in self.z3_vars.items() if is_string(v[1]) ]

	# ----------- private ---------------

	def _isIntVar(self, v):
		raise NotImplementedException

	def _getIntegerVariable(self,name,solver):
		if name not in self.z3_vars:
			self.z3_vars[name] = self._variable(name,solver)
		return self.z3_vars[name]

	def _getStringVariable(self,name,solver):
		if name not in self.z3_vars:
			self.z3_vars[name] = self._stringVariable(name,solver)
		return self.z3_vars[name]

	def _variable(self,name,solver):
		raise NotImplementedException

	def _stringVariable(self,name,solver):
		return String(name,solver.ctx)

	def _constant(self,v,solver):
		raise NotImplementedException

	def _stringConstant(self,v,solver):
		return StringVal(v,solver.ctx)

	def _wrapIf(self,e,solver,env):
		if env == None:
			return If(e,self._constant(1,solver),self._constant(0,solver))
		else:
			return e

	# add concrete evaluation to this, to check
	def _astToZ3Expr(self,expr,solver,env=None):
		if isinstance(expr, list):
			op = expr[0]
			args = [ self._astToZ3Expr(a,solver,env) for a in expr[1:] ]
			z3_l = args[0]
			z3_r = args[1] if len(args) > 1 else None

			# arithmetical operations
			if op == "+":
				return self._add(z3_l, z3_r, solver)
			elif op == "-":
				return self._sub(z3_l, z3_r, solver)
			elif op == "*":
				return self._mul(z3_l, z3_r, solver)
			elif op == "//":
				return self._div(z3_l, z3_r, solver)
			elif op == "%":
				return self._mod(z3_l, z3_r, solver)
			elif op == "str.len":
				return Length(z3_l)

			# bitwise
			elif op == "<<":
				return self._lsh(z3_l, z3_r, solver)
			elif op == ">>":
				return self._rsh(z3_l, z3_r, solver)
			elif op == "^":
				return self._xor(z3_l, z3_r, solver)
			elif op == "|":
				return self._or(z3_l, z3_r, solver)
			elif op == "&":
				return self._and(z3_l, z3_r, solver)

			# string operations
			elif op == "in":
				return self._wrapIf(Contains(z3_l, z3_r),solver,env)
			elif op == "str.startswith":
				return self._wrapIf(PrefixOf(z3_r, z3_l),solver,env)
			elif op == "str.endswith":
				return self._wrapIf(SuffixOf(z3_r, z3_l),solver,env)
			elif op == "str.find":
				return IndexOf(z3_l, z3_r, IntVal(0,solver.ctx))

			# equality gets coerced to integer
			elif op == "==":
				return self._wrapIf(z3_l == z3_r,solver,env)
			elif op == "!=":
				return self._wrapIf(z3_l != z3_r,solver,env)
			elif op == "<":
				return self._wrapIf(z3_l < z3_r,solver,env)
			elif op == ">":
				return self._wrapIf(z3_l > z3_r,solver,env)
			elif op == "<=":
				return self._wrapIf(z3_l <= z3_r,solver,env)
			elif op == ">=":
				return self._wrapIf(z3_l >= z3_r,solver,env)
			else:
				utils.crash("Unknown BinOp during conversion from ast to Z3 (expressions): %s" % op)

		elif isinstance(expr, SymbolicInteger):
			if expr.isVariable():
				if env == None:
					return self._getIntegerVariable(expr.name,solver)
				else:
					return env[expr.name]
			else:
				return self._astToZ3Expr(expr.expr,solver,env)

		elif isinstance(expr, SymbolicStr):
			if expr.isVariable():
				if env == None:
					return self._getStringVariable(expr.name,solver)
				else:
					return env[expr.name]
			else:
				return self._astToZ3Expr(expr.expr,solver,env)

		elif isinstance(expr, SymbolicType):
			utils.crash("{} is an unsupported SymbolicType of {}".
						format(expr, type(expr)))

		elif isinstance(expr, int):
			if env == None:
				return self._constant(expr,solver)
			else:
				return expr
		elif isinstance(expr, str):
			if env == None:
				return self._stringConstant(expr,solver)
			else:
				return expr
		else:
			utils.crash("Unknown node during conversion from ast to Z3 (expressions): %s" % expr)

	def _add(self, l, r, solver):
		if is_string(l) or is_string(r):
			return Concat(l, r)
		return l + r

	def _sub(self, l, r, solver):
		return l - r

	def _mul(self, l, r, solver):
		return l * r

	def _div(self, l, r, solver):
		return l / r

	def _mod(self, l, r, solver):
		return l % r

	def _lsh(self, l, r, solver):
		return l << r

	def _rsh(self, l, r, solver):
		return l >> r

	def _xor(self, l, r, solver):
		return l ^ r

	def _or(self, l, r, solver):
		return l | r

	def _and(self, l, r, solver):
		return l & r
