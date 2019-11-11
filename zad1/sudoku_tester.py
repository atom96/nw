#!/usr/bin/python3
import os
import subprocess
from tempfile import NamedTemporaryFile


def read_file(path):
    with open(path) as f:
        for k, line in enumerate(f):
            if k == 0:
                size = int(line.strip().split(' ')[0])
                board = [[None] * size for _ in range(size)]
            else:
                gen = iter(line.strip().split(' '))

                for i in range(size):
                    for j in range(size):
                        board[i][j] = next(gen)
    return board, size


def check(solution, size, sqrt_size):
    for row in solution:
        if len(set(row)) != size:
            print("Not valid solution in row", row)
            raise AssertionError
    cols = [[solution[i][j] for i in range(size)] for j in range(size)]

    for col in cols:
        if len(set(col)) != size:
            print("Not valid solution in column", col)
            raise AssertionError

    boxes = [
        [solution[i + i_shift * sqrt_size][j + j_shift * sqrt_size] for j in range(sqrt_size) for i in range(sqrt_size)]
        for i_shift in range(sqrt_size) for j_shift in range(sqrt_size)
    ]
    for box in boxes:
        if len(set(box)) != size:
            print("Not valid solution in box", box)
            raise AssertionError


if __name__ == '__main__':
    for file in os.listdir('examples/good'):
        with NamedTemporaryFile() as temp_file:
            try:
                command = ('export SUDOKU_PATH="examples/good/{}" &&'
                           'export OUTPUT_PATH={} &&'
                           'clingo sudoku_solver.py > /dev/null').format(file, temp_file.name)
                p = subprocess.run(command, shell=True)
                """
                enum ExitCode {
                    E_UNKNOWN   = 0,  /*!< Satisfiablity of problem not knwon; search not started.    */
                    E_INTERRUPT = 1,  /*!< Run was interrupted.                                       */
                    E_SAT       = 10, /*!< At least one model was found.                              */
                    E_EXHAUST   = 20, /*!< Search-space was completely examined.                      */
                    E_MEMORY    = 33, /*!< Run was interrupted by out of memory exception.            */
                    E_ERROR     = 65, /*!< Run was interrupted by internal error.                     */
                    E_NO_RUN    = 128 /*!< Search not started because of syntax or command line error.*/
                };       
                30 =  E_SAT + E_EXHAUST
                """
                if p.returncode != 30:
                    print("Command", command, "returned status", p.returncode)
            except subprocess.CalledProcessError as e:
                print(command)
                raise
            board, size = read_file(temp_file.name)
            sqrt_size = int(size ** 0.5)
            try:
                check(board, size, sqrt_size)
            except AssertionError:
                print('Error in', file)
                print(size, board)

    for file in os.listdir('examples/bad'):
        with NamedTemporaryFile() as temp_file:
            command = ('export SUDOKU_PATH="examples/bad/{}" &&'
                       'clingo sudoku_solver.py > {}').format(file, temp_file.name)
            p = subprocess.run(command, shell=True)
            if p.returncode != 30:
                print("Command", command, "returned status", p.returncode)
            with open(temp_file.name) as f:
                output_lines = f.readlines()
                if 'Result: UNSATISFIABLE\n' not in output_lines:
                    print('Error in', file)
                    print(output_lines)
