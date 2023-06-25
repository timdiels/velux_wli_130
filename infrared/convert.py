# Call with python3
import csv
import subprocess
from pathlib import Path

def main():
    with Path('irscrutinizer', 'spreadsheet_2023-06-25_22-42-47.csv').open() as csv_in:
        for line in csv.reader(csv_in, delimiter=';'):
            #print(line)
            command = line[0].replace('&#134', '').replace(' - ', ' ').replace(' ', '_').lower()
            print(command)
            #pulses = parse_formatted_pulses(line[9])
            #pulses = parse_formatted_pulses(line[10])
            #print(', '.join(map(str, pulses)))
            pronto_hex = line[-2]
            irconvert(command, pronto_hex)


def parse_formatted_pulses(formatted_pulses: str):
    # pulses are: on for x time, off for x time, on for ...
    return tuple(abs(int(pulse)) for pulse in formatted_pulses.split())


def irconvert(command, pronto_hex):
    with Path('flipper', f'{command}.ir').open('w') as out:
        # TODO this is basically the same as the pulses that irscrutinizer gives `+123 -372` but formatted as
        #  `first:\nsecond: 123, 372`
        subprocess.run(('node', 'irconvert.js', pronto_hex), stdout=out)


main()
