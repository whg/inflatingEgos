"""This takes the TSV copied from Google Docs and creates a Python dict"""

import sys
from pprintpp import pprint

def transpose(matrix):
    t = [[None for _ in matrix] for _ in matrix[0]]
    rows = len(matrix)
    cols = len(matrix[0])
    for i in range(rows):
        for j in range(cols):
            t[j][i] = matrix[i][j]
    return t


def getstdin():
    inputs = []
    while True:
        inp = input()

        if inp == "":
            break
        else:
            inputs.append(inp)

    return '\n'.join(inputs)


if __name__ == "__main__":

    table = getstdin()

    lines = table.split('\n')
    matrix = [line.split('\t') for line in lines]
    # print(table)
    tmatrix = transpose(matrix)

    # now each element has the candidnate name at 0 and the tags in the rest

    d = dict()
    for line in tmatrix:
        name = line[0]
        d[name] = [e for e in line[1:] if e != '']

    out = sys.argv[1] if len(sys.argv) > 1 else 'terms.py'

    with open(out, 'w') as f:
        pprint(d, stream=f)



    
