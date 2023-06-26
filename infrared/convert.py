# python3.10, pip install more-itertools
import csv
from more_itertools import chunked
from pathlib import Path


MIDPOINT = 96 // 2 - 1
REPEAT_START = MIDPOINT + 1


def main():
    analyse_cmds()
    convert_to_flipper_remote()


def analyse_cmds():
    cmd_groups = {
        key: [] for key in ('m1', 'm2', 'm3', 'stop', 'up_auto', 'up_manual', 'down_auto', 'down_manual', 'all')
    }

    print('It sends the same signal twice')
    print("Except for the 2nd pulse, if it's -1214, then it's repeated as -1183, else it's the same")
    print("And except for the last pulse of the signal")
    print()
    for command, pulses in sorted(parse_irscrutinizer_csv()):
        first_pulses = pulses[:MIDPOINT]
        second_pulses = pulses[MIDPOINT + 1:-1]
        assert first_pulses[1] == second_pulses[1] or (first_pulses[1] == -1214 and second_pulses[1] == -1183)
        for i, (x, y) in enumerate(zip(first_pulses, second_pulses)):
            assert i == 1 or x == y

        # Group commands
        if 'manual' not in command and 'auto' not in command:
            cmd_groups['stop'].append(first_pulses)
        for key, values in cmd_groups.items():
            if key in command:
                if key == 'down':
                    print('-' * 80)
                    print(command)
                    print(first_pulses[:12])
                cmd_groups[key].append(first_pulses)
        cmd_groups['all'].append(first_pulses)

    all_pulses = set.union(*(
        set(cmd)
        for cmds in cmd_groups.values()
        for cmd in cmds
    ))
    print('All possible pulses', all_pulses)
    print()

    print('Bits are short/long pairs')
    print()
    pairs = {
        (1245, -373): '1',
        (1245, 'MIDPOINT'): '1',
        (436, -1183): '0',
        (436, -1214): '0',
        (436, 'MIDPOINT'): '0',
    }
    cmd_groups = {
        key: [
            ''.join(pairs[tuple(pair)] for pair in chunked(cmd + ('MIDPOINT',), 2)) for cmd in cmds
        ]
        for key, cmds in cmd_groups.items()
    }

    # pulses 0-5 are the same within an action group => maybe the action
    # pulses 6-11 are only the same within the m1, m2, m3 group => maybe which motor; hopefully motor == velux
    # pulses 12-39 is the same across all cmds => maybe the 10-bit security code
    # pulses 40-46 are different within any group => junk?
    print('Indices of pulses which remain constant per group')
    for key, cmds in cmd_groups.items():
        first_cmd = cmds[0]
        differences = [False] * len(first_cmd)
        for cmd in cmds[1:]:
            for i, (pulse1, pulse2) in enumerate(zip(first_cmd, cmd)):
                if pulse1 != pulse2:
                    differences[i] = True
        same_indices = [i for i, different in enumerate(differences) if not different]
        print(key, same_indices)
    print()

    print('Bits 0-2 are the action:')
    for key in ('up_auto', 'up_manual', 'down_auto', 'down_manual', 'stop'):
        print(cmd_groups[key][0][:3], key)
    print()

    print('Bits 3-6 are motor 1, 2 or 3')
    for key in ('m1', 'm2', 'm3'):
        print(cmd_groups[key][0][3:6], key)
    print()

    print('Bits 6-20 are constant, probably contains the security key')
    print(cmd_groups['all'][0][6:20])


def convert_to_flipper_remote():
    # https://github.com/flipperdevices/flipperzero-firmware/blob/dev/documentation/file_formats/InfraredFileFormats.md
    with Path('flipper', 'remote.ir').open('w') as out:
        out.write('Filetype: IR signals file\n')
        out.write('Version: 1\n')
        for command, pulses in sorted(parse_irscrutinizer_csv()):
            out.write('#\n')
            out.write(f'name: {command}\n')
            out.write('type: raw\n')
            out.write('frequency: 32132\n')
            # 0 to 1 fraction for the PWM signal, flipper says it's usually 0.33, it's just a power saving thing. The
            # LED of the WLI responds to the IR with this setting, so it seems fine.
            out.write('duty_cycle: 0.33\n')
            out.write(f'data: {" ".join(str(abs(pulse)) for pulse in pulses)}\n')


def parse_irscrutinizer_csv():
    with Path('irscrutinizer', 'spreadsheet_2023-06-25_22-42-47.csv').open() as csv_in:
        for line in sorted(csv.reader(csv_in, delimiter=';')):
            command = line[0].replace('&#134', '').replace(' - ', ' ').replace(' ', '_').lower()
            assert bool(line[9]) != bool(line[10])  # xor
            pulses = parse_formatted_pulses(line[9] or line[10])
            yield command, pulses


def parse_formatted_pulses(formatted_pulses: str):
    # pulses are: on for x time, off for x time, on for ...
    return tuple(int(pulse) for pulse in formatted_pulses.split())


main()
