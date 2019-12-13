import argparse
import json
import os
from collections import namedtuple
from tempfile import NamedTemporaryFile
import weighting
from unittest import TestCase



def run(args):
    Args = namedtuple('Args', ['panelists', 'population', 'output', 'eclipse_bin'])

    tc = TestCase()
    tc.maxDiff = 10 ** 6
    print(args.eclipse_bin)

    base_path = os.path.abspath('test_data')
    for test_path in os.listdir('test_data'):
        with open(os.path.join(base_path, test_path, 'output.json')) as file:
            expected_result = json.load(file)
        with NamedTemporaryFile() as f:
            wargs = Args(
                panelists=os.path.join(base_path, test_path, 'panelists.json'),
                population=os.path.join(base_path, test_path, 'population.json'),
                output=f.name,
                eclipse_bin=args.eclipse_bin
            )
            weighting.run(wargs)

            with open(f.name) as file:
                result = json.load(file)

            tc.assertEqual(result, expected_result)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--eclipse-bin", default="/opt/eclipse/eclipse_clp/bin/x86_64_linux/eclipse")

    args = parser.parse_args()
    run(args)
