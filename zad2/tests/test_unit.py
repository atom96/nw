import json
import os
from collections import namedtuple
from tempfile import NamedTemporaryFile
import weighting
from unittest import TestCase


class TestBase(TestCase):
    BASE_PATH = os.path.dirname(os.path.abspath(__file__))
    ECLIPSE_BIN = os.environ.get('ECLIPSE_BIN', '/opt/eclipse/eclipse_clp/bin/x86_64_linux/eclipse')
    ARGS_CLS = namedtuple('Args', ['panelists', 'population', 'output', 'eclipse_bin'])
    TEST_DATA_PATH = None  # override in subclass

    def setUp(self) -> None:
        self.maxDiff = 10 ** 6

    def _panelists_path(self, test_path):
        return os.path.join(self.TEST_DATA_PATH, test_path, 'panelists.json')

    def _population_path(self, test_path):
        return os.path.join(self.TEST_DATA_PATH, test_path, 'population.json')

    def _run_eclipse(self, test_path):
        with NamedTemporaryFile() as f:
            weighting.run(
                panelists_path=self._panelists_path(test_path),
                population_path=self._population_path(test_path),
                output_path=f.name,
                eclipse_bin_path=self.ECLIPSE_BIN,
                print_we=False
            )

            with open(f.name) as file:
                result = json.load(file)
        return result


class IntegrationTests(TestBase):
    TEST_DATA_PATH = os.path.join(TestBase.BASE_PATH, 'test_data')

    def _run_test_from_test_data(self, test_path):
        with open(os.path.join(self.TEST_DATA_PATH, test_path, 'output.json')) as file:
            expected_result = json.load(file)
        result = self._run_eclipse(test_path)
        self.assertEqual(result, expected_result)

    def test_basic(self):
        self._run_test_from_test_data('test_basic')

    def test_crosses_division(self):
        self._run_test_from_test_data('test_crosses_division')

    def test_multiple_age_groups(self):
        self._run_test_from_test_data('test_multiple_age_groups')

    def test_optimal_male(self):
        self._run_test_from_test_data('test_optimal_male')

    def test_conflicting_data(self):
        with self.assertRaises(weighting.WeightingError):
            self._run_eclipse('test_conflicting_data')
