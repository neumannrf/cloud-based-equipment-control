import argparse

from modules.read_tttr import read_T2, read_T3

# Required parameters
parser = argparse.ArgumentParser(description='Read binary OUT file and save it as TXT.')
parser.add_argument('input_file',
                    type=str,
                    action='store',
                    metavar='INPUT_FILE',
                    help='Name of the \'*.out\' input file.')
parser.add_argument('output_file',
                    type=str,
                    action='store',
                    metavar='OUTPUT_FILE',
                    help='Name of the \'*.txt\' output file.')
parser.add_argument('--mode',
                    type=str,
                    default='T2',
                    required=False,
                    action='store',
                    metavar='MODE',
                    choices=['T2', 'T3'],
                    help='TTTR mode of the input file.')
arg = parser.parse_args()

with open(arg.input_file, "rb") as ifile, open(arg.output_file, "w", encoding="utf-8") as ofile:
    if arg.mode == 'T2':
        read_T2(ifile, ofile)
    elif arg.mode == 'T3':
        read_T3(ifile, ofile)
