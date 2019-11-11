# Sudoku solver created using Answer Set Programming

### How to test
Make sure you have `clingo` command available in your shell. If not, you can install it f.e. by conda `conda install clingo`

Run tests by executing `./sudoku_tester.py` in project directory

### How to run manually
``` shell script
export SUDOKU_PATH=/path/to/input/file &&
export OUTPUT_PATH=/path/to/result/file &&
clingo sudoku_solver.py
```

### Input file format
First line is number of rows/columns. Only square (3x3, 4x4 etc.) puzzles are supported. Next lines are respresentation of sudoku puzzle separated by `' '`. No value is represented by `0`. Values greater than 10 are represented by consequitive letters: 10=`a`, 11=`b`, 12=`c` etc.
```text
9
0 5 0 0 0 4 8 1 0 
0 0 0 0 0 6 0 5 0 
0 0 0 2 0 0 0 0 4 
0 0 7 3 0 0 1 0 0 
0 4 9 0 6 0 0 0 7 
0 6 0 0 0 0 3 0 0 
0 0 0 0 0 0 0 0 0 
0 0 0 0 8 0 9 0 2 
6 0 1 0 3 0 0 7 0 
```

### Output file format

Corresponds to input file format, but there is no newline after row ending
```text
9
7 6 4 5 1 9 2 8 3 5 1 9 2 8 3 7 6 4 2 8 3 7 6 4 5 1 9 6 7 5 4 9 1 8 3 2 4 9 1 8 3 2 6 7 5 8 3 2 6 7 5 4 9 1 1 4 7 9 5 6 3 2 8 9 5 6 3 2 8 1 4 7 3 2 8 1 4 7 9 5 6
```


### Shell output format

- For satisfiable Sudoku

```text
===== PYTHON RUN STARTS HERE =====

Result: SATISFIABLE
- - - - - - - - - - - - - 
| 7 6 4 | 5 1 9 | 2 8 3 |

| 5 1 9 | 2 8 3 | 7 6 4 |

| 2 8 3 | 7 6 4 | 5 1 9 |
- - - - - - - - - - - - - 
| 6 7 5 | 4 9 1 | 8 3 2 |

| 4 9 1 | 8 3 2 | 6 7 5 |

| 8 3 2 | 6 7 5 | 4 9 1 |
- - - - - - - - - - - - - 
| 1 4 7 | 9 5 6 | 3 2 8 |

| 9 5 6 | 3 2 8 | 1 4 7 |

| 3 2 8 | 1 4 7 | 9 5 6 |
- - - - - - - - - - - - - 

====== PYTHON RUN ENDS HERE ======
```

- For unsatisfiable Sudoku

```text
===== PYTHON RUN STARTS HERE =====

Result: UNSATISFIABLE

====== PYTHON RUN ENDS HERE ======
```