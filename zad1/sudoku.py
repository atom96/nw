#script (python)

import clingo
import string
import os


def read_file(path, cc):
    with open(path) as f:
        for i, line in enumerate(f):
            if i == 0:
                size = int(line.strip().split(' ')[0])
                x = [[None] * size for _ in range(size)]
            else:
                for j, elem in enumerate(line.strip().split(' ')):
                    if elem != '0':
                        x[i - 1][j] = elem.lower()
                        comm = 'number({i}, {j}, {n}) .'.format(i=i - 1, j=j, n=elem.lower())
                        cc.add('base', [], comm)

    return x, size


def setup_clingo():
    clingo_args = []
    cc = clingo.Control(clingo_args)
    return cc


def add_main_clingo_program(cc, size):
    size_sqrt = int(size ** 0.5)

    cc.add('base', [], '''
    #const size = %d.

    %% every cell has unique number
    1 { number(I, J, N) : num(N)} 1 :- row(I), col(J) .
    
    %% every column is filled
    size { number(I, J, N): num(N), row(I) } size :- col(J) .
    
    %% every row is filled
    size { number(I, J, N): num(N), col(J) } size :- row(I) .

    %% numbers are unique in rows
    1 {number(I, J, N) : col(J)} 1 :- row(I), num(N) .
    
    %% numbers are unique in columns
    1 {number(I, J, N) : row(I)} 1 :- col(J), num(N) .
    
    %% numbers are unique in boxes
    :- number(I1, J1, N), 
       number(I2, J2, N),
       I1 / %d == I2 / %d,
       J1 / %d == J2 / %d,
       |I2 - I1| + |J2 - J1| > 0 .
       
    ''' % tuple([size] + [size_sqrt] * 4))

    for i in range(size):
        if i < 9:
            num = i + 1
        else:
            num = string.ascii_lowercase[i - 9]
        cc.add('base', [], 'num({}) .'.format(num))
        cc.add('base', [], 'row({}) .'.format(i))
        cc.add('base', [], 'col({}) .'.format(i))

def run():
    cc = setup_clingo()

    path = os.environ['SUDOKU_PATH']
    x, size = read_file(path, cc)

    add_main_clingo_program(cc, size)

    cc.ground([("base",[])])

    def onmodel(m):
        print('SATISFIABLE')
        for atom in m.symbols(atoms=True):
            if atom.name == 'number':
                args = [str(z) for z in atom.arguments]
                x[int(args[0])][int(args[1])] = args[2]
        for row in x:
            print(*row, sep='', end='')

        print()
        check(x, size, int(size**0.5))

    res = cc.solve(on_model=onmodel)
    if res.unsatisfiable:
        print('UNSATISFIABLE')

def check(solution, size, sqrt_size):
    for row in solution:
        if len(set(row)) != size:
            print("Not valid solution in row", row)
            return
    cols = [[solution[i][j] for i in range(size)] for j in range(size)]

    for col in cols:
        if len(set(col)) != size:
            print("Not valid solution in column", col)
            return

    boxes = [
        [solution[i + i_shift * 3][j + j_shift * 3] for j in range(sqrt_size) for i in range(sqrt_size)]
        for i_shift in range(sqrt_size) for j_shift in range(sqrt_size)
    ]
    for box in boxes:
        if len(set(box)) != size:
            print("Not valid solution in box", box)
            return

    print("Solution is valid")


if __name__ == '__main__':
    print('\n===== PYTHON RUN STARTS HERE =====\n')
    run()
    print('\n====== PYTHON RUN ENDS HERE ======\n')


#end.