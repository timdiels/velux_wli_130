# Call with python3
import csv
import subprocess
from pathlib import Path


def main():
    # Convert to flipper remote ir file
    # https://github.com/flipperdevices/flipperzero-firmware/blob/dev/documentation/file_formats/InfraredFileFormats.md
    with Path('flipper', 'remote.ir').open('w') as out:
        out.write('Filetype: IR signals file\n')
        out.write('Version: 1\n')
        for command, pulses in sorted(parse_irscrutinizer_csv()):
            out.write('#\n')
            out.write(f'name: {command}\n')
            out.write('type: raw\n')
            out.write('frequency: 32132\n')
            # 0 to 1 fraction for the PWM signal. No idea what the WLI expects, but flipper says it's usually 0.33 but
            # our frequency is unusual so this might be something weird too
            out.write('duty_cycle: 0.33\n')
            out.write(f'data: {" ".join(map(str, pulses))}\n')


def parse_irscrutinizer_csv():
    with Path('irscrutinizer', 'spreadsheet_2023-06-25_22-42-47.csv').open() as csv_in:
        for line in csv.reader(csv_in, delimiter=';'):
            command = line[0].replace('&#134', '').replace(' - ', ' ').replace(' ', '_').lower()
            print(command)

            assert bool(line[9]) != bool(line[10])  # xor
            pulses = parse_formatted_pulses(line[9] or line[10])
            yield command, pulses


def parse_formatted_pulses(formatted_pulses: str):
    # pulses are: on for x time, off for x time, on for ...
    return tuple(abs(int(pulse)) for pulse in formatted_pulses.split())


main()
