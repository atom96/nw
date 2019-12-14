#!/usr/bin/python3

import argparse
import itertools
import json
import subprocess
from collections import defaultdict, OrderedDict
from tempfile import NamedTemporaryFile


class WeightingError(Exception):
    pass


def get_all_ids(panelists):
    return ', '.join(map(lambda x: 'X' + x, panelists))


def get_cross_name(cross):
    name = 'C'
    for (demo_name, demo_val) in cross:
        name += demo_name
        name += demo_val.replace('-', '')
    return name


def get_crosses_names(crosses):
    return [get_cross_name(cross) for cross in crosses]


def get_cross_mapping(crosses):
    return {
        get_cross_name(cross): cross
        for cross in crosses
    }


def product(lists):
    return list(itertools.product(*lists))


def _rename_population(population):
    new_population = {}
    for demo_name, demo_vals in population.items():
        flatten_vals = []
        if demo_name == "total":
            continue
        for demo_val in demo_vals:
            flatten_vals.append((demo_name, demo_val))
        new_population[demo_name] = flatten_vals
    return new_population


def get_crosses_population(panelists, renamed_population, all_crosses):
    crosses_population = defaultdict(list)

    demo_to_crosses_map = {
        cls: []
        for cls in itertools.chain(*renamed_population.values())
    }

    for cross in all_crosses:
        for part in cross:
            demo_to_crosses_map[part].append(cross)

    for panelist_id, panelist_data in panelists.items():
        demo_vals = []
        for demo_id, demo_val in sorted(panelist_data['demo'].items()):
            demo_vals.append((demo_id, demo_val))
        crosses_population[tuple(demo_vals)].append(panelist_id)
    return crosses_population, demo_to_crosses_map


def generate_program_cmd(population, panelists):
    renamed_population = _rename_population(population)
    all_crosses = product(value for key, value in sorted(renamed_population.items()))
    all_cross_names = get_crosses_names(all_crosses)
    cross_mapping = get_cross_mapping(all_crosses)

    program = [
        ':- lib(eplex).',
        'answer({all_ids}) :-'.format(all_ids=', '.join(all_cross_names)),
        '  integers([{all_ids}]),'.format(all_ids=', '.join(all_cross_names))
    ]

    crosses_population, demo_to_crosses_map = get_crosses_population(panelists, renamed_population, all_crosses)

    for (demo_name, demo_val), crosses in demo_to_crosses_map.items():
        program.append('  {crosses_sum} $= {population},'.format(
            population=population[demo_name][demo_val],
            crosses_sum=' + '.join(get_crosses_names(crosses))
        ))

    costs_abs = []
    panelists_len = len(panelists)
    for i, (cross, input_cross_population) in enumerate(crosses_population.items()):
        name = get_cross_name(cross)
        cross_cost = '{cross} * {rev_output_population} - {input_cross_perc}'.format(
            cross=name,
            rev_output_population=1 / population['total'],
            input_cross_perc=len(input_cross_population) / panelists_len
        )
        cost_abs = 'A{}'.format(i)
        costs_abs.append(cost_abs)
        program.extend([
            '  {cross} $>= {input_pop},'.format(cross=name, input_pop=len(input_cross_population)),
            '  {cross_cost} $=< {cost_abs},'.format(cross_cost=cross_cost, cost_abs=cost_abs),
            '  {cross_cost} $>= -1 * {cost_abs},'.format(cross_cost=cross_cost, cost_abs=cost_abs),
            '  {cost_abs} $>= 0,'.format(cost_abs=cost_abs)
        ])

    program.append(
        '  Cost $= {all_abs},'.format(
            all_abs=' + '.join(costs_abs)
        )
    )

    program.append('  eplex_solver_setup(min(Cost)),')
    program.append('  eplex_solve(Cost).')
    return program, all_cross_names, crosses_population, cross_mapping


def run_eclipse(eclipse_bin, program_cmd, result_cmd):
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
            raise Exception('Out:\n' + p.stdout.decode('utf-8') + 'Err:\n' + p.stderr.decode('utf-8'))

        return p.stdout.decode('utf-8').split('\n')


def parse_result(result_lines):
    result = {}
    start = None
    end = None
    not_found = None
    for i, line in enumerate(result_lines):
        if line.startswith('[eclipse 1]:'):
            start = i + 1
            break

    for i, line in enumerate(result_lines):
        if line.startswith('Yes'):
            end = i
            break

    for i, line in enumerate(result_lines):
        if line.startswith('No'):
            not_found = i
            break

    if not_found is not None:
        raise WeightingError('Weighting failed. Eclipse output: {}'.format('\n'.join(result_lines)))

    if start is None or end is None:
        raise ValueError('Parsing error.-  start: {}, end: {}, eclipse output: {}'.format(
            start, end, '\n'.join(result_lines)
        ))

    for line in result_lines[start:-4]:
        if line == '':
            continue
        panelist_id, rest = [x.strip() for x in line.split('=')]
        weight = float(rest.split('@')[1].strip().rstrip('}'))

        result[panelist_id] = int(round(weight, 0))
    return result


def get_weights(crosses, cross_mapping, crosses_panelists):
    weights = {}
    for cross_name, population in crosses.items():
        panelists = crosses_panelists[cross_mapping[cross_name]]
        for panelist_id in panelists:
            weights[panelist_id] = population / len(panelists)
    weights = OrderedDict(sorted(weights.items(), key=lambda x: int(x[0])))
    return weights


def calc_weighting_efficiency(weights):
    w_square_sum = 0
    w_sum = 0
    w_len = 0
    for weight in weights.values():
        w_len += 1
        w_sum += weight
        w_square_sum += weight ** 2
    return 100 * (w_sum ** 2 / w_len) / w_square_sum


def run(population_path, panelists_path, output_path, eclipse_bin_path, print_we):
    with open(population_path) as f:
        population = json.load(f)

    with open(panelists_path) as f:
        panelists = json.load(f)

    program, all_cross_ids, crosses_population, cross_mapping = generate_program_cmd(population, panelists)
    eclipse_result = run_eclipse(
        eclipse_bin=eclipse_bin_path,
        program_cmd='\n'.join(program),
        result_cmd='answer({all_ids}).'.format(all_ids=', '.join(all_cross_ids))
    )
    crosses = parse_result(eclipse_result)
    weights = get_weights(crosses, cross_mapping, crosses_population)

    with open(output_path, 'w') as f:
        json.dump(weights, f, indent=4)

    if print_we:
        we = calc_weighting_efficiency(weights)
        print('Weighting efficiency', we)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--panelists")
    parser.add_argument("--population")
    parser.add_argument("--output")
    parser.add_argument("--print-we", action='store_true', default=False)
    parser.add_argument("--eclipse-bin", default="/opt/eclipse/eclipse_clp/bin/x86_64_linux/eclipse")

    args = parser.parse_args()
    run(
        panelists_path=args.panelists,
        population_path=args.population,
        output_path=args.output,
        eclipse_bin_path=args.eclipse_bin,
        print_we=args.print_we
    )
