from typing import TypeVar, List, Tuple, Dict, Optional
import z3


def model(phi):
    s = z3.Solver()
    s.add(phi)
    return s.model() if s.check() == z3.sat else None


def color_var(color_num: int, vertex_num: int) -> z3.Bool:
    return z3.Bool('C_{color}_{vertex}'.format(color=color_num, vertex=vertex_num))


T = TypeVar('T')


def graph_coloring(vertices: List[T], edges: List[Tuple[T, T]], num_of_colors: int) -> Optional[Dict[T, int]]:
    program: List[str] = []
    v_number: Dict[T, int] = {}
    colors: List[int] = list(range(0, num_of_colors))
    for i, v in enumerate(vertices):
        v_number[v] = i
        at_least_one = []
        for color in colors:
            at_least_one.append(
                color_var(color, i)
            )
        program.append(z3.Or(at_least_one))

        pairwise = []
        for (idx, color1) in enumerate(colors):
            for color2 in colors[idx + 1:]:
                pairwise.append(
                    z3.Not(
                        z3.And(
                            color_var(color1, i),
                            color_var(color2, i)
                        )
                    )
                )
        program.append(z3.And(pairwise))

    for (v1, v2) in edges:
        i1 = v_number[v1]
        i2 = v_number[v2]
        for color in colors:
            program.append(
                z3.Not(
                    z3.And(
                        color_var(color, i1),
                        color_var(color, i2)
                    )
                )
            )

    program.append(color_var(0, 0))

    res = model(z3.And(program))

    if res is None:
        return None

    color_map = {}
    for var in map(str, res):
        if var.startswith('C_'):
            if res[z3.Bool(var)]:
                _, color, vertex_idx = var.split('_')
                color_map[vertices[int(vertex_idx)]] = int(color)

    return color_map
