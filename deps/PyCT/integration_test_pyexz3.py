#!/usr/bin/env python3
import argparse, os, signal, sys, threading, time, unittest
import libct.explore
from concurrencytest import ConcurrentTestSuite, fork_for_tests

parser = argparse.ArgumentParser()
parser.add_argument("-n", dest='num', type=int, help="the number of processes", default=1)
args = parser.parse_args()

class TestCodeSnippets(unittest.TestCase):
    dump = False #bool(os.environ.get('dump', False))
    def test_01(self): self._execute("test", "abs_test", {'a':0, 'b':0}) # OK
    def test_02(self): self._execute("test", "andor", {'x':0, 'y':0}) # OK
    def test_03(self): self._execute("test", "arrayindex2", {'i':0}) # OK
    def test_04(self): self._execute("test", "bad_eq", {'i':0}) # OK
    def test_05(self): self._execute("test", "bignum", {'a':0}) # OK
    def test_06(self): self._execute("test", "binary_search", {'k':0}, {9, 14}) # OK with deadcode [9, 14]
    def test_07(self): self._execute("test", "bitwidth", {'a':0, 'b':0}, {3}) # OK with deadcode [3]
    def test_08(self): self._execute("test", "complex", {'x':0, 'y':0}, {7}) # TODO: cannot replay mismatch
    def test_09(self): self._execute("test", "cseppento1", {'x':0, 'y':0}, {14, 19}) # OK with deadcode [14, 19]
    def test_10(self): self._execute("test", "cseppento2", {'a':0, 'b':0}, {5}) # OK with deadcode [5]
    def test_11(self): self._execute("test", "cseppento3", {'x':0}) # OK
    def test_12(self): self._execute("test", "decorator_dict", {'d':{}}, {6, 8}) # TODO: dict type is not supported yet
    def test_13(self): self._execute("test", "decorator", {'a':0, 'b':0, 'c':0}) # OK
    def test_14(self): self._execute("test", "diamond", {'x':0, 'y':0, 'z':0}) # OK
    def test_15(self): self._execute("test", "dict", {'x':0}) # OK
    def test_16(self): self._execute("test", "dictionary", {'in1':0}) # OK
    def test_17(self): self._execute("test", "elseif", {'in1':0}, {26}) # OK with deadcode [26]
    def test_18(self): self._execute("test", "expand", {'in1':0, 'in2':0}) # OK
    def test_19(self): self._execute("test", "expressions", {'in1':0, 'in2':0}, {9}) # TODO: CVC4 cannot solve (in1) * (in2 + 47) == 53
    def test_20(self): self._execute20("test", "filesys", {'x':0}, {18, 20}) # OK with deadcode [18, 20]
    def test_21(self): self._execute("test", "fp", {'a':0}) # OK
    def test_22(self): self._execute("test", "gcd", {'x':0, 'y':0}, {69}) # OK with deadcode [69]
    def test_23(self): self._execute("test", "hashval", {'key':0}, {12}) # OK with deadcode [12]
    def test_24(self): self._execute("test", "len_test", {'a':0}) # OK
    def test_25(self): self._execute("test", "list", {'a':0, 'b':0}) # OK
    def test_26(self): self._execute("test", "logical_op", {'in1':0, 'in2':0}, {5,6,8,12}) # TODO: logical operator is not supported yet
    def test_27(self): self._execute("test", "loop", {'in1':0, 'in2':0}, {5}) # OK with deadcode [5]
    def test_28(self): self._execute("test", "many_branches", {'in1':0, 'in2':0, 'in3':0}, {29}) # OK with deadcode [29]
    def test_29(self): self._execute("test", "maxtest", {'a':0, 'b':0, 'c':0, 'd':0}, {16}) # OK with deadcode [16]
    def test_30(self): self._execute("test", "mod", {'x':0, 'y':0}) # OK
    def test_31(self): self._execute("test", "modulo", {'in1':0}) # OK
    def test_32(self): self._execute("test", "modulo2", {'in1':0}) # OK
    def test_33(self): self._execute("test", "mult_assmt", {'in1':0, 'in2':0, 'in3':0}) # OK
    def test_34(self): self._execute("test", "polyspace", {'i':0}, {14}) # OK with deadcode [14]
    def test_35(self): self._execute("test", "power", {'x':0}, {10}) # TODO: CVC4 cannot solve (x+2) ** 2 == 4
    def test_36(self): self._execute("test", "power2", {'x':0}, {9}) # OK with deadcode [9]
    def test_37(self): self._execute("test", "powtest", {'in1':0}, {6}) # OK with deadcode [6]
    def test_38(self): self._execute("test", "reverse", {'x':0}) # OK
    def test_39(self): self._execute("test", "set", {'x':0}) # OK
    def test_40(self): self._execute("test", "shallow_branches", {'in1':0, 'in2':0, 'in3':0, 'in4':0, 'in5':0}) # OK
    def test_41(self): self._execute("test", "simple", {'x':0}) # OK
    def test_42(self): self._execute("test", "swap", {'in1':0, 'in2':0}, {10}) # OK with deadcode [10]
    def test_43(self): self._execute("test", "tuplecmp", {'a0':0, 'a1':0, 'b0':0, 'b1':0}) # OK
    def test_44(self): self._execute("test", "unnecessary_condition", {'in1':0, 'in2':0}, {5}) # OK with deadcode [5]
    def test_45(self): self._execute("test", "unnecessary_condition2", {'in1':0, 'in2':0}, {6}) # OK with deadcode [6]
    def test_46(self): self._execute("test", "unnecessary_condition3", {'in1':0}) # OK
    def test_47(self): self._execute("test", "unnecessary_condition4", {'in1':0}) # OK
    def test_48(self): self._execute("test", "weird", {'x':0, 'y':0}) # OK
    def test_49(self): self._execute("test", "whileloop", {'x':0}) # OK
    def test_50(self): self._execute("test/cvc", "effectivebool", {'string':'', 'num':0}) # OK
    def test_51(self): self._execute("test/cvc", "emptystr", {'s':''}) # OK
    def test_52(self): self._execute("test/cvc", "escape", {'string':''}) # OK
    def test_53(self): self._execute("test/cvc", "none", {'c':0}, {7}) # OK with deadcode [7]
    def test_54(self): self._execute("test/cvc", "strcontains", {'s':''}) # OK
    def test_55(self): self._execute("test/cvc", "strcount", {'s':''}) # OK
    def test_56(self): self._execute("test/cvc", "strfind", {'s':''}) # OK
    def test_57(self): self._execute("test/cvc", "strfindbeg", {'s':''}) # OK
    def test_58(self): self._execute("test/cvc", "strindex", {'s':''}) # OK
    def test_59(self): self._execute("test/cvc", "stringadd", {'s':''}) # OK
    def test_60(self): self._execute("test/cvc", "stringtest", {'s':''}) # OK
    def test_61(self): self._execute("test/cvc", "strmiddle", {'s':''}) # OK
    def test_62(self): self._execute("test/cvc", "strreplace", {'s':''}) # OK
    def test_63(self): self._execute("test/cvc", "strslice", {'s':''}) # OK
    def test_64(self): self._execute("test/cvc", "strsplit", {'s':''}) # OK
    def test_65(self): self._execute("test/cvc", "strstartswith", {'s':''}) # OK
    def test_66(self): self._execute("test/cvc", "strstrip", {'s':''}) # OK
    def test_67(self): self._execute("test/cvc", "strsubstring", {'s':''}) # OK
    def test_68(self): self._execute("fail", "arrayindex", {'i':0}, {13}) # TODO: still not able to pick another list element
    def test_69(self): self._execute("fail", "dictbool", {'d':{}}, {8}) # TODO: dict type is not supported yet
    def test_70(self): self._execute("fail", "divzero", {'in1':0, 'in2':0}, {10}) # OK with deadcode [10]
    def test_71(self): self._execute("fail", "git", {'a':0, 'b':0}) # OK
    def test_72(self): self._execute("fail", "pow", {'x':0}, {7}) # TODO: CVC4 cannot solve 4 == x**2
    def test_73(self): self._execute("fail", "sqrttest", {'in1':0}, {8,9,10}) # TODO: sqrt is still handled concretely

    def _execute20(self, root, modpath, inputs, _missing_lines=set(), *, lib=None):
        os.system('rm ../PyExZ3/test/tmp.txt')
        self._execute(root, modpath, inputs, _missing_lines, lib=lib)

    def _execute(self, root, modpath, inputs, _missing_lines=set(), *, lib=None):
        _id = sys._getframe(1).f_code.co_name.split('_')[1]
        if _id == 'execute20': _id = sys._getframe(2).f_code.co_name.split('_')[1]
        if not self._omit(_id):
            self.iteration_max = 1
            engine = libct.explore.ExplorationEngine()
            iteration = 0
            start = time.time()
            while iteration == 0 or self._check_coverage(iteration, _missing_lines, missing_lines):
                a, b, c, d, e, F, g = engine.explore(modpath, inputs, root='../PyExZ3/' + root, deadcode=set(), include_exception=True, lib='../PyExZ3/', file_as_total=False)
                total_lines, executed_lines, missing_lines = engine.coverage_statistics() # missing_lines: dict
                iteration += 1
                # print(total_lines, executed_lines, missing_lines)
            finish = time.time()
            # col_3 = str(list(map(lambda x: (list(x[0].values()), x[1]), engine.in_out)))[1:-1]
            # print(modpath + ':', col_3)
            # print(modpath + ':', _missing_lines)
        if self.dump: # Logging output section
            if self._omit(_id):
                with open(f'paper_statistics/pyct_run_pyexz3/{_id}.csv', 'w') as f:
                    f.write(f'{_id}|-|-|-\n')
            else:
                col_1 = "{}/{} ({:.2%})".format(executed_lines, total_lines, (executed_lines/total_lines) if total_lines > 0 else 0)
                # col_2 = str(sorted(list(missing_lines.values())[0]) if missing_lines else '')
                # if col_2 == str(sorted(_missing_lines)):
                #     col_1 += ' >> (100.00%)' #; col_2 += ' (dead code)'
                with open(f'paper_statistics/pyct_run_pyexz3/{_id}.csv', 'w') as f:
                    cdivb = c / b if b else 0
                    edivd = e / d if d else 0
                    gdivF = g / F if F else 0
                    # f.write(f'{_id}|{root.replace("/", ".") + "." + modpath}|{col_1}|{round(finish-start, 2)}\n')
                    f.write(f'{_id}|{root.replace("/", ".") + "." + modpath}|{col_1}|{round(finish-start, 2)}|{b+d+F}|{b}|{round(cdivb, 2)}|{d}|{round(edivd, 2)}|{F}|{round(gdivF, 2)}\n')

    def _omit(self, _id):
        return False #_id in ('19', '21', '23', '36', '41', '43')

    def _check_coverage(self, iteration, _missing_lines, missing_lines: dict):
        if missing_lines: # we only care about the primary file
            missing_lines = list(missing_lines.values())[0]
        else:
            missing_lines = set()
        status = self.assert_equal(iteration, missing_lines, _missing_lines)
        return not (iteration == self.iteration_max or status) # := not (termination condition)

    def assert_equal(self, iteration, a, b):
        if iteration == self.iteration_max: return True #self.assertEqual(a, b) # self.assertTrue(a.issubset(b))
        return a == b

if __name__ == '__main__':
    TestCodeSnippets.dump = True
    os.system('rm -r paper_statistics/pyct_run_pyexz3*')
    os.system('mkdir -p paper_statistics/pyct_run_pyexz3')

    # load the TestSuite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    suite.addTests(loader.loadTestsFromTestCase(TestCodeSnippets))

    # start preparation
    def job():
        while len(next(os.walk('paper_statistics/pyct_run_pyexz3'))[2]) != suite.countTestCases(): pass
        os.system('echo "ID|Function|Line Coverage|Time (sec.)|# of SMT files|# of SAT|Time of SAT|# of UNSAT|Time of UNSAT|# of OTHERWISE|Time of OTHERWISE" > paper_statistics/pyct_run_pyexz3.csv')
        os.system('cat paper_statistics/pyct_run_pyexz3/*.csv >> paper_statistics/pyct_run_pyexz3.csv')
        os.system('rm -r paper_statistics/pyct_run_pyexz3')
        pid = os.getpid()
        os.kill(pid, signal.SIGTERM) #or signal.SIGKILL
    t = threading.Thread(target = job)
    t.start()

    # run the TestSuite
    concurrent_suite = ConcurrentTestSuite(suite, fork_for_tests(args.num))
    result = unittest.TextTestRunner().run(concurrent_suite)
    result.stop()

    print('Finish the integration test!!!')