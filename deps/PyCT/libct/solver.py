import logging, os, re, subprocess, sys, time
from libct.concolic import Concolic
from libct.predicate import Predicate
from libct.utils import py2smt

log = logging.getLogger("ct.solver")

class Solver:
    # options = {"lan": "smt.string_solver=z3str3", "stdin": "-in"}
    cnt = 1 # for store

    @classmethod # similar to our constructor
    def set_basic_configurations(cls, solver, timeout, safety, store, statsdir):
        cls.safety = safety; cls.statsdir = statsdir
        cls.stats = {'sat_number': 0, 'sat_time': 0, 'unsat_number': 0, 'unsat_time': 0, 'otherwise_number': 0, 'otherwise_time': 0}
        if cls.statsdir: os.system(f"mkdir -p '{cls.statsdir}/formula'")
        if store is not None:
            if not os.path.isdir(store):
                if not re.compile(r"^\d+$").match(store):
                    raise IOError(f"Query folder {store} not found")
        cls.store = store
        ##########################################################################################
        # Build the command from the solver type
        if solver == "cvc4":
            cls.cmd = ["cvc4"] + ["--produce-models", "--lang", "smt", "--quiet", "--strings-exp"]
        # elif solver == "z3seq":
        #     cls.cmd = "z3 -in".split(' ')
        # elif solver == "z3str":
        #     cls.cmd = ["z3"] + self.options.values()
        # elif solver == "trauc":
        #     cls.cmd = ["trauc"] + self.options.values()
        else:
            raise NotImplementedError
        ##########################################################################################
        # Build the command from the timeout parameter
        assert isinstance(timeout, int)
        if "z3" in solver or  "trauc" in solver:
            cls.cmd += ["-T:" + str(timeout)]
        else:
            cls.cmd += ["--tlimit=" + str(1000 * timeout)]

    @classmethod
    def find_model_from_constraint(cls, engine, constraint):
        formulas = Solver._build_formulas_from_constraint(engine, constraint); log.smtlib2(f"Solving To: {constraint}")
        start = time.time()
        try: completed_process = subprocess.run(cls.cmd, input=formulas.encode(), capture_output=True)
        except subprocess.CalledProcessError as e: print(e.output)
        elapsed = time.time() - start
        output = completed_process.stdout.decode()
        model = None
        if output is None or len(output) == 0:
            status = "UNKNOWN"
        else:
            outputs = output.splitlines(); status = outputs[0].lower()
            if "error" in status:
                print('solver error:', status)
                print(f"at SMT-id: {Solver.cnt}")
                print(formulas)
                # sys.exit(1)
            if "sat" == status:
                cls.stats['sat_number'] += 1; cls.stats['sat_time'] += elapsed
                model = Solver._get_model(engine, outputs[1:])
            else:
                if "unsat" == status: cls.stats['unsat_number'] += 1; cls.stats['unsat_time'] += elapsed
                else: status = "UNKNOWN"; cls.stats['otherwise_number'] += 1; cls.stats['otherwise_time'] += elapsed
        ##########################################################################################
        if cls.store is not None:
            if re.compile(r"^\d+$").match(cls.store):
                if int(cls.store) == Solver.cnt:
                    with open(cls.store + f"_{status}.smt2", 'w') as f:
                        f.write(formulas)
            else:
                with open(os.path.join(cls.store, f"{Solver.cnt}_{status}.smt2"), 'w') as f:
                    f.write(formulas)
        if cls.statsdir:
            with open(cls.statsdir + f"/formula/{Solver.cnt}_{status}.smt2", 'w') as f:
                f.write(formulas)
        ##########################################################################################
        log.smtlib2(f"SMT-id: {Solver.cnt}／Status: {status}／Model: {model}")
        Solver.cnt += 1
        return model

    @staticmethod
    def _get_model(engine, models):
        model = {}
        for line in models:
            assert line.startswith('((') and line.endswith('))')
            name, value = line[2:-2].split(" ", 1)
            if engine.var_to_types[name] == "Bool":
                if value == 'true': value = True
                elif value == 'false': value = False
                else: raise NotImplementedError
            elif engine.var_to_types[name] == "Real":
                if "(" in value:
                    value = -float(value.replace("(", "").replace(")", "").split(" ")[1])
                else:
                    value = float(value)
            elif engine.var_to_types[name] == "Int":
                if "(" in value:
                    value = -int(value.replace("(", "").replace(")", "").split(" ")[1])
                else:
                    value = int(value)
            elif engine.var_to_types[name] == "String":
                assert value.startswith('"') and value.endswith('"')
                value = value[1:-1]
                value = value.replace('""', '"').replace("\\t", "\t").replace("\\n", "\n").replace("\\r", "\r").replace("\\\\", "\\")
                # Note the decoding order above must be in reverse with its encoding method (line 41 in libct/utils.py)
            else:
                raise NotImplementedError
            assert name.endswith('_VAR') # '_VAR' is used to avoid name collision
            model[name[:-len('_VAR')]] = value
        return model

    @staticmethod
    def _build_formulas_from_constraint(engine, constraint):
        declare_vars = "\n".join(f"(declare-const {name} {_type})" for (name, _type) in engine.var_to_types.items())
        queries = "\n".join(assertion.get_formula() for assertion in constraint.get_all_asserts())
        get_vars = "\n".join(f"(get-value ({name}))" for name in engine.var_to_types.keys())
        return f"(set-logic ALL)\n{declare_vars}\n{queries}\n(check-sat)\n{get_vars}\n"

    @classmethod
    def _expr_has_engines_and_equals_value(cls, expr, value):
        if e:=Concolic.find_engine_in_expr(expr):
            if cls.safety <= 0: return e # This line is used to disable the value validation feature temporarily.
            if isinstance(value, float): # TODO: Floating point operations may cause subtle errors.
                formulas = f"(assert (and (<= (- (/ 1 1000000000000000)) (- {Predicate.get_formula_shallow(expr)} {py2smt(value)})) (<= (- {Predicate.get_formula_shallow(expr)} {py2smt(value)}) (/ 1 1000000000000000))))\n(check-sat)"
            else:
                formulas = f"(assert (= {Predicate.get_formula_shallow(expr)} {py2smt(value)}))\n(check-sat)"
            try: completed_process = subprocess.run(cls.cmd, input=formulas.encode(), capture_output=True)
            except subprocess.CalledProcessError as e: print(e.output)
            try:
                if completed_process.stdout.decode().splitlines()[0] == 'sat': return e
                raise Exception # move to the following block
            except:
                print(formulas); print(completed_process.stdout.decode().splitlines()); print()
                import traceback; traceback.print_stack()
                if cls.safety >= 2: sys.exit(1)
        return None
