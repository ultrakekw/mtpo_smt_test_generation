#!/usr/bin/env python3
import argparse, os, signal, subprocess, sys, threading, time, unittest
import libct.explore
from concurrencytest import ConcurrentTestSuite, fork_for_tests

parser = argparse.ArgumentParser()
parser.add_argument("-n", dest='num', type=int, help="the number of processes", default=1)
args = parser.parse_args()

class TestCodeSnippets(unittest.TestCase):
    dump = False #bool(os.environ.get('dump', False))
    def test_01(self): self._execute("test", "build_in", {'a':0, 'b':0}) # OK
    def test_02(self): self._execute("test", "call_obj", {'a':0, 'b':0}, {11, 26}) # OK with deadcode [11, 26]
    def test_03(self): self._execute("test", "do_abs", {'a':0, 'b':0}) # OK
    def test_04(self): self._execute("test", "do_array", {'a':0, 'b':0}) # OK
    def test_05(self): self._execute("test", "do_numbers", {'a':0, 'b':0}) # OK
    def test_06(self): self._execute("test", "do_range", {'a':0, 'b':0}) # OK
    def test_07(self): self._execute("test", "list_dict", {'a':0, 'b':0}) # OK
    def test_08(self): self._execute("test", "loop", {'a':0, 'b':0}) # OK
    def test_09(self): self._execute("test", "while_loop", {'a':0, 'b':0}) # OK
    def test_10(self): self._execute("test/strings", "string_find", {'a':'', 'b':''}) # OK
    def test_11(self): self._execute("test/strings", "string_in", {'a':'', 'b':''}) # OK
    def test_12(self): self._execute("test/strings", "string_iter", {'a':'', 'b':''}) # OK
    def test_13(self): self._execute("test/strings", "string_others", {'a':'', 'b':''}) # OK
    def test_14(self): self._execute("test/strings", "string_replace", {'a':'', 'b':''}) # OK
    def test_15(self): self._execute("test/strings", "string_slice", {'a':'', 'b':''}) # OK
    def test_16(self): self._execute("test/strings", "string_startswith", {'a':'', 'b':''}) # OK
    def test_17(self): self._execute("test/targets", "count_emma", {'statement':''}) # OK
    def test_18(self): self._execute("test/targets", "multiplication_or_sum", {'num1':0, 'num2':0}, {6}) # TODO: CVC4 cannot solve num1 * num2 >= 1000
    def test_19(self): self._execute("test/targets", "regex", {'string':''}, {8}) # TODO: regex is difficult to implement...
    def test_20(self): self._execute("test/targets/lib", "email__header_value_parser", {'value':''}) # OK
    def test_21(self): self._execute("test/targets/leetcode", "add_digits", {'num':0}) # OK
    def test_22(self): self._execute("test/targets/leetcode", "fraction_to_decimal", {'numerator':0, 'denominator':0}, {24, 25}) # TODO: still cannot handle "dict-contains" yet..
    def test_23(self): self._execute("test/targets/leetcode", "isLongPressedName", {'name':'', 'typed':''}) # OK
    def test_24(self): self._execute("test/targets/leetcode", "numDecodings", {'s':''}) # OK
    def test_25(self): self._execute("test/targets/leetcode", "restoreIpAddresses", {'s':''}) # OK
    def test_26(self): self._execute("test/targets/leetcode", "reverseCheck", {'number':0}) # OK
    def test_27(self): self._execute("test/targets/leetcode", "substring", {'s':''}) # OK
    def test_28(self): self._execute("test/targets/leetcode", "substring2", {'s':''}) # OK
    def test_29(self): self._execute("test/targets/leetcode", "ugly_number", {'num':0}) # OK
    def test_30(self): self._execute("test/target_int/leetcode_int", "add_binary", {'a':'', 'b':''}) # OK
    def test_31(self): self._execute("test/target_int/leetcode_int", "addStrings", {'num1':'', 'num2':''}) # OK
    def test_32(self): self._execute("test/target_int/leetcode_int", "numDecodings", {'s':''}) # OK
    def test_33(self): self._execute("test/target_int/leetcode_int", "restoreIpAddresses", {'s':''}) # OK
    def test_34(self): self._execute("test/target_int/leetcode_int", "validIPAddress", {'IP':''}, {35, 38}) # TODO: 15 minutes is not long enough.
    def test_35(self): self._execute("test/target_int/leetcode_int", "validWordAbbreviation", {'word':'', 'abbr':''}) # OK
    def test_36(self): self._execute("test/target_int/lib_int", "datetime__parse_hh_mm_ss_ff", {'tstr':''}) # OK
    def test_37(self): self._execute("test/target_int/lib_int", "datetime__parse_isoformat_date", {'dtstr':''}) # OK
    def test_38(self): self._execute("test/target_int/lib_int", "distutils_get_build_version", {'version':''}, {26, 30}) # OK with deadcode [26, 30]
    def test_39(self): self._execute("test/target_int/lib_int", "email__parsedate_tz", {'data':''}, {32, 43, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 77, 78, 79, 80, 81, 82, 84, 87, 88, 89, 90, 91, 92, 93, 100, 102, 103, 106, 108}) # TODO: ?/?
    def test_40(self): self._execute("test/target_int/lib_int", "http_parse_request", {'version':''}) # OK
    def test_41(self): self._execute("test/target_int/lib_int", "ipaddress__ip_int_from_string", {'ip_str':''}, {32, 70, 71, 102, 103, 111, 112, 113, 114, 115, 116, 117, 118, 119}) # TODO: 200 iterations is not many enough.
    def test_42(self): self._execute("test/target_int/lib_int", "nntplib__parse_datetime", {'date_str':''}) # OK
    def test_43(self): self._execute("test/target_int/lib_int", "smtpd_parseargs", {'arg1':'', 'arg2':''}, {28, 35, 40}) # OK with deadcode [28, 35, 40]
    def test_44(self): self._execute("test/target_int/lib_int", "wsgiref_check_status", {'status':''}) # OK
    def test_45(self): self._execute("test/feature", "read_str_from_file", {'a':'', 'b':''}) # OK
    def test_46(self): self._executesrv("test/realworld/rpyc", "client", {'x':0}, {34}) # OK with deadcode [34]
    def test_47(self): self._execute("test/realworld", "docxmlrpcserver", {'title':'', 'name':'', 'documentation':''}) # OK

    def _executesrv(self, root, modpath, inputs, _missing_lines):
        libpath = root + '/.venv/lib/python3.8/site-packages'; os.system('kill -KILL $(lsof -t -i:8080)')
        pid = subprocess.Popen(["python3", "test/realworld/rpyc/server.py"], env={**os.environ, 'PYTHONPATH': libpath + ':' + os.environ['PYTHONPATH']}).pid
        time.sleep(1) # this short wait is very important!!! (for the client to connect)
        self._execute(root, modpath, inputs, _missing_lines, lib=libpath)
        os.system(f'kill -KILL {pid}')

    def _execute(self, root, modpath, inputs, _missing_lines=set(), *, lib=None):
        _id = sys._getframe(1).f_code.co_name.split('_')[1]
        if _id == 'executesrv': _id = sys._getframe(2).f_code.co_name.split('_')[1]
        if not self._omit(_id):
            self.iteration_max = 1
            engine = libct.explore.ExplorationEngine()
            iteration = 0
            start = time.time()
            while iteration == 0 or self._check_coverage(iteration, _missing_lines, missing_lines):
                a, b, c, d, e, F, g = engine.explore(modpath, inputs, root=root, deadcode=set(), include_exception=True, lib=lib, file_as_total=True)
                total_lines, executed_lines, missing_lines = engine.coverage_statistics() # missing_lines: dict
                iteration += 1
            finish = time.time()
            # col_3 = str(list(map(lambda x: (list(x[0].values()), x[1]), engine.in_out)))[1:-1]
            # print(modpath + ':', col_3)
        if self.dump: # Logging output section
            if self._omit(_id):
                with open(f'paper_statistics/pyct_run_pyct/{_id}.csv', 'w') as f:
                    f.write(f'{_id}|-|-|-\n')
            else:
                col_1 = "{}/{} ({:.2%})".format(executed_lines, total_lines, (executed_lines/total_lines) if total_lines > 0 else 0)
                # col_2 = str(sorted(list(missing_lines.values())[0]) if missing_lines else '')
                # if col_2 == str(sorted(_missing_lines)):
                #     col_1 += ' >> (100.00%)' #; col_2 += ' (dead code)'
                with open(f'paper_statistics/pyct_run_pyct/{_id}.csv', 'w') as f:
                    cdivb = c / b if b else 0
                    edivd = e / d if d else 0
                    gdivF = g / F if F else 0
                    # f.write(f'{_id}|{root.replace("/", ".") + "." + modpath}|{col_1}|{round(finish-start, 2)}\n')
                    f.write(f'{_id}|{root.replace("/", ".") + "." + modpath}|{col_1}|{round(finish-start, 2)}|{b+d+F}|{b}|{round(cdivb, 2)}|{d}|{round(edivd, 2)}|{F}|{round(gdivF, 2)}\n')

    def _omit(self, _id):
        return False #_id in ('19', '34', '39', '41')

    def _check_coverage(self, iteration, _missing_lines, missing_lines: dict):
        if missing_lines: # we only care about the primary file
            missing_lines = list(missing_lines.values())[0]
        else:
            missing_lines = set()
        status = self.assert_equal(iteration, missing_lines, _missing_lines)
        return not (iteration == self.iteration_max or status) # := not (termination condition)

    def assert_equal(self, iteration, a, b):
        if iteration == self.iteration_max: return True #self.assertEqual(a, b)
        return a == b

if __name__ == '__main__':
    TestCodeSnippets.dump = True
    os.system('rm -r paper_statistics/pyct_run_pyct*')
    os.system('mkdir -p paper_statistics/pyct_run_pyct')

    # load the TestSuite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    suite.addTests(loader.loadTestsFromTestCase(TestCodeSnippets))

    # start preparation
    def job():
        while len(next(os.walk('paper_statistics/pyct_run_pyct'))[2]) != suite.countTestCases(): pass
        os.system('echo "ID|Function|Line Coverage|Time (sec.)|# of SMT files|# of SAT|Time of SAT|# of UNSAT|Time of UNSAT|# of OTHERWISE|Time of OTHERWISE" > paper_statistics/pyct_run_pyct.csv')
        os.system('cat paper_statistics/pyct_run_pyct/*.csv >> paper_statistics/pyct_run_pyct.csv')
        os.system('rm -r paper_statistics/pyct_run_pyct')
        pid = os.getpid()
        os.kill(pid, signal.SIGTERM) #or signal.SIGKILL
    t = threading.Thread(target = job)
    t.start()

    # run the TestSuite
    concurrent_suite = ConcurrentTestSuite(suite, fork_for_tests(args.num))
    result = unittest.TextTestRunner().run(concurrent_suite)
    result.stop()

    print('Finish the integration test!!!')