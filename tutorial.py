#!/usr/bin/env python
# encoding: utf-8
"""
Author: Amie Settlecowski
Version: 1.0
Date: 4 May 2016
Software project developed during BIOL7800 Programming for Biologists (Brant
Faircloth) at Louisiana State University.

This program executes a tutorial for estimating the mean of a binomial
distribution via Approximate Bayesian Computation. Dependencies include
AbcBin.py and input.csv. The tutorial can be modified by editing fields in
input.csv and can be extended by adding additional lines to
"""
from AbcBin import AbcBin


def get_args(line):
    ''' '''
    line_as_list = line.split(',')
    return float(line_as_list[0]), int(line_as_list[1]), int(line_as_list[2]), int(line_as_list[3]), line_as_list[4], line_as_list[5]


def main():
    with open('input.csv', 'r') as infile:
        infile.readline()
        # Every line of input.csv corresponds to an independent ABC analysis
        for line in infile:
            p, N, sample_size, posterior_size, method, sumstat = get_args(line)
            model = AbcBin(p, N, sample_size, posterior_size, method, sumstat)
            model.run()
            model.tutorial()

if __name__ == '__main__':
    main()
