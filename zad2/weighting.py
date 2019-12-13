#!/usr/bin/python3

import argparse
import json
import subprocess
from collections import defaultdict
from tempfile import NamedTemporaryFile


def get_all_ids(panelists):
    return ', '.join(map(lambda x: 'X' + x, panelists))


def generate_program_cmd(population, panelists):
    all_ids = get_all_ids(panelists)
    program = [
        ':- lib(eplex).',
        'answer({all_ids}) :-'.format(all_ids=all_ids),
        '  integers([{all_ids}]),'.format(all_ids=all_ids)
    ]

    classes = defaultdict(lambda: defaultdict(list))
    for panelist_id, panelist_data in panelists.items():
        program.append('  {} $>= 1,'.format('X' + panelist_id))
        for demo_id, demo_val in panelist_data['demo'].items():
            classes[demo_id][demo_val].append('X' + panelist_id)

    for demo_name, demo_groups in population.items():
        for demo_group, population in demo_groups.items():
            panelist_ids = classes[demo_name][demo_group]
            program.append(
                '  {weights_sum} $= {population},'.format(
                    weights_sum=' + '.join(panelist_ids),
                    population=population
                )
            )

    pv_sum = []
    for panelist_id, panelist_data in panelists.items():
        pv_sum.append('X' + panelist_id + ' * ' + str(panelist_data['metric']))

    program.append('  Cost $= {pv_sum},'.format(
        pv_sum=' + '.join(pv_sum))
    )
    program.append('  eplex_solver_setup(min(Cost)),')
    program.append('  eplex_solve(Cost).')
    return program


def run_eclipse(eclipse_bin, program_cmd, result_cmd):
    # print(program_cmd)
    with NamedTemporaryFile() as weighting_query_file, \
            NamedTemporaryFile() as result_query_file:
        with open(weighting_query_file.name, 'w') as f:
            f.write(program_cmd)
        with open(result_query_file.name, 'w') as f:
            f.write(result_cmd)
        p = subprocess.run(
            ['{eclipse_bin} -f {weighting_query} < {result_query}'.format(
                eclipse_bin=eclipse_bin,
                weighting_query=weighting_query_file.name,
                result_query=result_query_file.name
            )],
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        if not p.returncode == 0:
            raise Exception(p.stderr.decode('utf-8'))

        return p.stdout.decode('utf-8').split('\n')


def parse_result(result_lines):
    result = {}
    for line in result_lines[11:-4]:
        panelist_id, rest = [x.strip() for x in line.split('=')]
        panelist_id = panelist_id.lstrip('X')
        weight = float(rest.split('@')[1].strip().rstrip('}'))
        assert weight.is_integer()

        result[panelist_id] = int(weight)
    return result


def run(args):
    with open(args.population) as f:
        population = json.load(f)

    with open(args.panelists) as f:
        panelists = json.load(f)

    program = generate_program_cmd(population, panelists)

    eclipse_result = run_eclipse(
        eclipse_bin=args.eclipse_bin,
        program_cmd='\n'.join(program),
        result_cmd='answer({all_ids}).'.format(all_ids=get_all_ids(panelists))
    )
    # print('\n'.join(eclipse_result))
    weights = parse_result(eclipse_result)

    with open(args.output, 'w') as f:
        json.dump(weights, f, indent=4, sort_keys=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--panelists")
    parser.add_argument("--population")
    parser.add_argument("--output")
    parser.add_argument("--eclipse-bin", default="/opt/eclipse/eclipse_clp/bin/x86_64_linux/eclipse")

    args = parser.parse_args()
    run(args)
