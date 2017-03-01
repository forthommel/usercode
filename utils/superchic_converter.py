#!/usr/bin/python
import argparse
from math import sqrt

def main():
    parser = argparse.ArgumentParser(description='Convert a LHE file from SuperCHIC.')
    parser.add_argument('input', help='input LHE file')
    parser.add_argument('--output', help='output LHE file', type=str)
    parser.add_argument('--xsect', help='process cross section', type=float)
    parser.add_argument('--xsect_err', help='error on the process cross section', type=float)
    args = parser.parse_args()

    output_file = args.output
    if not args.output:
        output_file = args.input.replace('.lhe', '_converted.lhe')
    xsect = args.xsect
    if not args.xsect:
        xsect = 0.0
    xsect_err = args.xsect_err
    if not args.xsect_err:
        xsect_err = 0.0

    out = open(output_file, 'w')

    block = ''
    in_init = False
    in_event = False
    ini_info = {}
    for l in open(args.input):
        if '<event>' in l:
            in_event = True
            block += l
        elif '</event>' in l:
            in_event = False
            block += l
            block = convert_event_block(block, ini_info)
            out.write(block)
            block = ''
        elif in_init:
            l = l.split()
            if len(l)>4: #incoming particles' block
                in1_pdg, in2_pdg, in1_pz, in2_pz = l[0:4]
                ini_info = {'in1_pdg': in1_pdg, 'in1_pz': in1_pz,
                            'in2_pdg': in2_pdg, 'in2_pz': in2_pz}
            elif (xsect>0. or xsect_err>0.) and len(l)==4: #xsection/QCD/QED constants
                l[0] = '%.9E' % (xsect)
                l[1] = '%.9E' % (xsect_err)
            out.write('\t'.join(l)+'\n')
        elif in_event:
            block += l
        else:
            out.write(l)

        if '<init>' in l:
            in_init = True
        elif '</init>' in l:
            in_init = False


def convert_event_block(block, ini_info):
    out = ''
    npart = 0
    for l in block.split('\n'):
        l = l.split()
        if len(l)==0: continue
        if len(l)>1 and len(l)<10: #in header
            l[0] = str(int(l[0])+2)
            out += '  '.join(l)+'\n'
            part_mass = '0.000000000E+00'
            if int(ini_info['in1_pdg'])==2212: part1_mass = '0.938272046E+00'
            if int(ini_info['in2_pdg'])==2212: part2_mass = '0.938272046E+00'
            part1_ene = sqrt(float(ini_info['in1_pz'])**2+float(part1_mass)**2)
            part2_ene = sqrt(float(ini_info['in2_pz'])**2+float(part2_mass)**2)
            out += '\t'.join([
                    ini_info['in1_pdg'], '-1', '0', '0', '0', '0',
                    '0.000000000E+00', '0.000000000E+00', ini_info['in1_pz'],
                    '%.9E' % (part1_ene), part1_mass,
                    '0.', '9.'])+'\n'
            out += '\t'.join([
                    ini_info['in2_pdg'], '-1', '0', '0', '0', '0',
                    '0.000000000E+00', '0.000000000E+00', '-'+ini_info['in2_pz'],
                    '%.9E' % (part2_ene), part2_mass,
                    '0.', '9.'])+'\n'
        elif len(l)>2:
            if npart==0: #first outgoing proton
                l[2] = '1'
            elif npart==1: #second outgoing proton
                l[2] = '2'
            else:
                l[2] = str(int(l[2])+2)
            out += '\t'.join(l)+'\n'
            npart += 1
        else:
            out += '\t'.join(l)+'\n'
    return out

if __name__=='__main__':
    main()
