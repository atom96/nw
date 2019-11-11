#script (python)

import os
import string

import clingo


def read_file(path, cc):
    with open(path) as f:
        for i, line in enumerate(f):
            if i == 0:
                size = int(line.strip().split(' ')[0])
                board = [[None] * size for _ in range(size)]
            else:
                for j, elem in enumerate(line.strip().split(' ')):
                    if elem != '0':
                        board[i - 1][j] = elem.lower()
                        comm = 'number({i}, {j}, {n}) .'.format(i=i - 1, j=j, n=elem.lower())
                        cc.add('base', [], comm)

    return board, size


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


def print_on_screen(board, sqrt_size):
    for i, row in enumerate(board):
        if i % sqrt_size == 0:
            for _ in range(len(row) + sqrt_size + 1):
                print('-', end=' ')
        print('')
        for j, col in enumerate(row):
            if j % sqrt_size == 0:
                print('|', sep='', end=' ')
            print(col, end=' ')
        print('|')
    for _ in range(sqrt_size * sqrt_size + sqrt_size + 1):
        print('-', end=' ')
    print()


def save_to_file(size, board, output_path):
    if output_path:
        with open(output_path, 'w') as f:
            print(size, file=f)
            for row in board:
                print(*row, sep=' ', end=' ', file=f)
            print(file=f)


def update_solution(model, board):
    for atom in model.symbols(atoms=True):
        if atom.name == 'number':
            args = [str(z) for z in atom.arguments]
            board[int(args[0])][int(args[1])] = args[2]


def run():
    cc = setup_clingo()

    path = os.environ['SUDOKU_PATH']
    output_path = os.environ.get('OUTPUT_PATH')
    board, size = read_file(path, cc)
    sqrt_size = int(size ** 0.5)

    add_main_clingo_program(cc, size)

    cc.ground([("base", [])])

    def on_model(m):
        print('Result: SATISFIABLE')
        update_solution(m, board)
        print_on_screen(board, sqrt_size)
        save_to_file(size, board, output_path)

    res = cc.solve(on_model=on_model)
    if res.unsatisfiable:
        print('Result: UNSATISFIABLE')


if __name__ == '__main__':
    print('\n===== PYTHON RUN STARTS HERE =====\n')
    run()
    print('\n====== PYTHON RUN ENDS HERE ======\n')

#end.
