import json
import os
from collections import defaultdict

from tests.test_unit import TestBase


class FuzzyTest(TestBase):
    TEST_DATA_PATH = os.path.join(TestBase.BASE_PATH, 'fuzzy_tests')

    @staticmethod
    def population_from_weights(weights, panelists):
        population = defaultdict(lambda: defaultdict(int))
        population['total'] = 0
        for panelist_id, weight in weights.items():
            demo = panelists[panelist_id]["demo"]
            population['total'] += weight
            for demo_name, demo_val in demo.items():
                population[demo_name][demo_val] += weight

        for demo_name, demo_vals in population.items():
            if demo_name == 'total':
                population['total'] = int(round(demo_vals, 0))
            else:
                for demo_val, demo_pop in demo_vals.items():
                    demo_vals[demo_val] = int(round(demo_pop, 0))

        return population

    def _run_fuzzy_test(self, path):
        weights = self._run_eclipse(path)
        with open(self._panelists_path(path)) as f:
            panelists = json.load(f)

        with open(self._population_path(path)) as f:
            expected_population = json.load(f)

        output_population = self.population_from_weights(weights, panelists)
        self.assertDictEqual(output_population, expected_population)

    def test_poland_1(self):
        self._run_fuzzy_test('test_poland_1')

    def test_poland_2(self):
        self._run_fuzzy_test('test_poland_2')

    def test_poland_3(self):
        self._run_fuzzy_test('test_poland_3')

    def test_poland_4(self):
        self._run_fuzzy_test('test_poland_4')

    def test_poland_5(self):
        self._run_fuzzy_test('test_poland_5')

    def test_poland_6(self):
        self._run_fuzzy_test('test_poland_6')

    def test_poland_7(self):
        self._run_fuzzy_test('test_poland_7')

    def test_poland_8(self):
        self._run_fuzzy_test('test_poland_8')

    def test_poland_9(self):
        self._run_fuzzy_test('test_poland_9')

    def test_poland_10(self):
        self._run_fuzzy_test('test_poland_10')
