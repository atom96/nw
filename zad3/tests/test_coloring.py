import os
from typing import List, Tuple, Dict
from unittest import TestCase

from coloring import graph_coloring


class ColoringTest(TestCase):
    TEST_DATA_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'input_data')

    def _read_file(self, filename: str) -> Tuple[List[int], List[Tuple[int, int]]]:
        edges = []
        with open(os.path.join(self.TEST_DATA_PATH, filename)) as f:
            for line in f:
                line = line.rstrip('\n')
                elems = line.split(' ')
                if elems[0] == 'c':
                    continue
                if elems[0] == 'p':
                    number_of_vertices = int(elems[2])
                    number_of_edges = int(elems[3])

                if elems[0] == 'e':
                    edges.append((int(elems[1]), int(elems[2])))
        vertices = list(range(1, number_of_vertices + 1))
        return vertices, edges

    def _test_coloring(self, coloring: Dict[int, int], edges: List[Tuple[int, int]], num_of_colors: int = 3) -> None:
        for (v1, v2) in edges:
            color = coloring[v1]
            neigh_color = coloring[v2]
            self.assertNotEqual(color, neigh_color)
        self.assertLessEqual(len(set(coloring.values())), num_of_colors)

    def _run_on_file(self, filename: str, num_of_colors: int = 3) -> None:
        vertices, edges = self._read_file(filename)
        colors = graph_coloring(
            vertices=vertices,
            edges=edges,
            num_of_colors=num_of_colors
        )
        self.assertTrue(colors is not None)
        self._test_coloring(colors, edges, num_of_colors)

    def test_basic(self):
        edges = [(1, 2), (2, 3), (1, 3)]
        num_of_colors = 3
        res = graph_coloring(
            vertices=[1, 2, 3],
            edges=edges,
            num_of_colors=num_of_colors
        )
        self._test_coloring(res, edges, num_of_colors)

    def test_games(self):
        self._run_on_file('games120.col', 9)

    def test_miles250(self):
        self._run_on_file('miles250.col', 8)

    def test_myciel3(self):
        self._run_on_file('myciel3.col', 4)

    def test_myciel4(self):
        self._run_on_file('myciel4.col', 5)

    def test_queen5_5(self):
        self._run_on_file('queen5_5.col', 5)

    def test_queen8_8(self):
        self._run_on_file('queen5_5.col', 5)

    def test_queen8_12(self):
        self._run_on_file('queen5_5.col', 5)
