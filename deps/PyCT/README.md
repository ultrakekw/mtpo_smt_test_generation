# PyCT

The main objective of PyCT is to produce as a minimum number of different input arguments to achieve as much coverage of the target function as possible by feeding the produced arguments one in an iteration. The currently supported input arguments can only be integers or strings. Other types of arguments may be supported in the future.

---

## Abstract

Concolic testing is a software testing technique for generating concrete inputs of programs to increase code coverage and has been developed for years. For programming languages such as C, JAVA, x86 binary code, and JavaScript, there are already plenty of available concolic testers. However, the concolic testers for Python are relatively less. Since Python is a popular programming language, we believe there is a strong need to develop a good one.

Among the existing testers for Python, PyExZ3 is the most well-known and advanced. However, we found some issues of PyExZ3: (1) it implements only a limited number of base types’ (e.g., integer, string) member functions and(2) it automatically downcasts concolic objects and discards related symbolic information as it encounters built-in types’ constructors.

Based on the concept of PyExZ3, we develop a new tool called PyCT to alleviate these two issues. PyCT supports a more complete set of member functions of data types including integer, string, and range. We also proposes a new method to upcast constants to concolic ones to prevent unnecessary downcasting. Our evaluation shows that with more member functions being supported, the coverage rate is raised to (80.20%) from (71.55%). It continues to go up to (85.68%) as constant upcasting is also implemented.

---

## Prerequisites

- [Python](https://www.python.org/downloads/) version == 3.8.5<br>
  Basically, it should also work for other versions not lower than 3.8. Simply follow the usual installation instructions for Python.<br>

- [CVC4](https://github.com/CVC4/CVC4) commit version == [d1f3225e26b9d64f065048885053392b10994e715](https://github.com/cvc5/cvc5/blob/d1f3225e26b9d64f065048885053392b10994e71/INSTALL.md)<br>
  Since our CVC4 version has to cope with that of the base project PyExZ3 when we compare the performance of the two, our designated version above cannot be the latest. Otherwise, the CVC4 Python API bindings used in PyExZ3 cannot work.<br>The installation instructions for CVC4 is almost the same as that in the provided link, except that the configuration command should be modified to `./configure.sh --language-bindings=python --python3` for the use of CVC4 Python API bindings. A user must ensure by himself/herself that the command `cvc4` can be found by an operating system shell. Otherwise the tool may not work.<br>

- [pipenv](https://pypi.org/project/pipenv/)<br>
  This is required for the use of the virtual environment mechanism in our project. Install it as a usual Python package.<br>

- additional settings<br>
  1. For CVC4 to be findable by the Python API, `export PYTHONPATH={path-to-CVC4-build-folder}/src/bindings/python` should be put in `~/.bashrc`.
  2. For pipenv to create a virtual environment in each project folder, `export PIPENV_VENV_IN_PROJECT=1` should be put in `~/.bashrc`, too.

---

## Installation

1. Clone our project to the local repository.<br>
Type `$ git clone git@github.com:alan23273850/PyCT.git` or `$ git clone https://github.com/alan23273850/PyCT.git`<br>
2. Type `$ cd PyCT` and then `$ pipenv shell` for the first time to create a virtual environment.<br>
3. Type `$ pipenv install` to install required packages for this environment.
4. Type `$ exit` or `$ deactivate` to leave this virtual environment.
5. For case #46 of the integration test to work, one must repeat step 2. to 4. in the folder `./test/realworld/rpyc` for its own virtual environment first.

---

## Usage

Keep in mind that always type `$ pipenv shell` or `$ source .venv/bin/activate` in this project directory beforehand when starting an experiment, and always type `$ exit` or `$ deactivate` after the experiment finishes.

For example, to measure the target function `string_find(a, b)` in the target file `./test/strings/string_find.py`, and to let the two initial arguments be `a = ''` and `b = ''`, we can simply type the following command. A user can inspect all options of this script by typing `$ ./pyct.py -h`.
```
 $ ./pyct.py test.strings.string_find "{'a':'','b':''}" -r . -s string_find
```
or
```
 $ ./pyct.py test.strings.string_find "{'a':'','b':''}"
```
Then the output would be:
```
  ct.explore    INFO     Inputs: {'a': '', 'b': ''}
  ct.explore    INFO     Return: 1
  ct.explore    INFO     Not Covered Yet: /root/PyCT/test/strings/string_find.py [9]
  ct.explore    INFO     === Iterations: 1 ===
  ct.explore    INFO     Inputs: {'a': 'ggg', 'b': ''}
  ct.explore    INFO     Return: 1
  ct.explore    INFO     Not Covered Yet: /root/PyCT/test/strings/string_find.py [9]
  ct.explore    INFO     === Iterations: 2 ===
  ct.explore    INFO     Inputs: {'a': 'ADBECggg', 'b': ''}
  ct.explore    INFO     Return: 2
  ct.explore    INFO     Not Covered Yet: /root/PyCT/test/strings/string_find.py {}

Total iterations: 2
```

---

## Evaluation

The following instructions can be used to reproduce Table 3 in the paper #76 of APLAS 2021. For the sake of convenience, we recommend to conduct the experiment in the provided docker image `docker pull alan23273850/pyct`. In this image, all statistics are already prepared except `./root/PyCT/project_statistics`, `./root/PyCT/project_statistics_disable_AST`, `./root/PyExZ3/project_statistics`, `./root/PyExZ3/project_statistics_disable_AST` in order to minimize its size. Please note that these folders contain no csv files, so never mind. To start a new container from the image, type `docker run -it --entrypoint bash [image id]`. To get into an existing container, type `docker start -ai [container id]`. To leave a container simply type `exit`.

* Navigate to `/root/PyExZ3` and run the following three set of experiments with the virtual environment enabled (`pipenv shell` ... `exit`).
    1. Run `./integration_test_pyct.py -n 8`, where `8` can be adjusted to any number of runnable threads.
    2. Run `./integration_test_pyexz3.py -n 8`, where `8` can be adjusted to any number of runnable threads.
    3. Run `./run_project.py 2 ../04_Python` first and then `./measure_coverage.py 2 ../04_Python`.

* Since our tool `/root/PyCT` cannot be switched to disable AST rewriting from input options, one must manually comment out line `180-183` and `202` of `/root/PyCT/libct/wrapper.py` first. Then navigate to `/root/PyCT` and run the following three set of experiments with the virtual environment enabled (`pipenv shell` ... `exit`).

    1. Run `./integration_test_pyct.py -n 8`, where `8` can be adjusted to any number of runnable threads.
    2. Run `./integration_test_pyexz3.py -n 8`, where `8` can be adjusted to any number of runnable threads.
    3. Run `./run_project.py 1 ../04_Python` first and then `./measure_coverage.py 1 ../04_Python`.

  After this series of commands, please `mv paper_statistics paper_statistics_disable_AST`, and `git restore libct/wrapper.py`. If you want to preserve `project_statistics`, also do `mv project_statistics project_statistics_disable_AST`.

* Stay in `/root/PyCT` and run the following three set of experiments with the virtual environment enabled (`pipenv shell` ... `exit`).
    1. Run `./integration_test_pyct.py -n 8`, where `8` can be adjusted to any number of runnable threads.
    2. Run `./integration_test_pyexz3.py -n 8`, where `8` can be adjusted to any number of runnable threads.
    3. Run `./run_project.py 1 ../04_Python` first and then `./measure_coverage.py 1 ../04_Python`.

Finally `./produce_paper_statistics.py` and the output `./paper_total_table.csv` is what we want. The bottleneck of the elapsed time is `/root/04_Python` and it takes almost 2 to 3 days to complete the whole task.

<!-- 
---

## TODO

---

## Known Issues

Although this project aims to provide an error-free concolic testing environment, this goal in fact can be proven almost impossible! The most significant obstacle is "exact type checking." When a program performs this kind of checking, it probably wants to do something that only accepts primitive types. However, whether to unwrap the concolic objects automatically when facing this check solely depends on the purpose of the code, and of course the purpose can not be recognized by softwares nowadays. Besides, we've not come up with a method to unwrap these arguments if they are immutable objects and enclosed in another function. For example, the C source code of socket implementations expects the input arguments to be primitive. In this case we can replace the Python-level socket function with our custom one which unwraps the arguments first. As another example, some network libraries may need to know whether the object to be sent is primitive or not, so that it can decide whether to run the operations designed specifically for non-primitive objects. In this case we should not unwrap the concolic objects automatically. Currently we can only manually adjust the code case by case.

1. To replace an existing function with your custom one, you can refer to the `prepare()` function in `conbyte/explore.py`.

2. To disable wrapping a module when importing it, you can refer to line 144 in `conbyte/wrapper.py`.

---

## How to Contribute

blablabla...

Finally you may want to run the (parallel) integration test (in `integration_test.py`) to ensure the contribution is correct. The command is `pytest integration_test.py --workers [# of processes] -x`, and it takes almost 11 minutes to run.

If you want to create the csv file of the testing result, run `echo "ID|Line Coverage|Missing Lines|Inputs & Outputs" > output.csv2 && dump=True pytest integration_test.py --workers [# of processes] -x && cp /dev/null output.csv && cat *.csv >> output.csv2 && rm -f *.csv && mv output.csv2 output.csv`. Make sure there are no existing *.csv files in the current directory before running the test. Our file content is separated by "|" since "," is already contained in the data. -->
