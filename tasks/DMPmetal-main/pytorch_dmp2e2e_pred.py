#!/usr/bin/env python

# ############################## DMPmetal Main program ################################
# By David T. Jones, Jan 2023


from __future__ import print_function

import sys
import os
import time
import random
import argparse
from collections import OrderedDict

import numpy as np

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.nn.functional import normalize

from nndef_dist_axial2coords_metal_noflash import SeqTransformer

def parse_fasta(file):
    fasta_dict = OrderedDict()
    with open(file, "r") as f:
        current_header = ""
        current_seq = ""
        for line in f:
            line = line.strip()
            if line.startswith(">"):
                if current_header:
                    accession = current_header.split(" ")[0]
                    fasta_dict[accession] = current_seq
                current_header = line[1:]
                current_seq = ""
            else:
                current_seq += line
        accession = current_header.split(" ")[0]
        fasta_dict[accession] = current_seq
    return fasta_dict


def main():

    torch.set_float32_matmul_precision('high')

    #torch.backends.cudnn.benchmark = True

    # Create the parser
    parser = argparse.ArgumentParser()
    # Add arguments
    parser.add_argument('-i', '--input_file', type=str, required=True)
    parser.add_argument('-d', '--device', type=str, default='cpu', required=False)
    # Parse the argument
    args = parser.parse_args()

    device = torch.device(args.device)

    # Create neural network model (depending on first command line parameter)
    network = SeqTransformer(1536,32,32).to(device).eval()

    #print("Trainable parameters: ", sum(p.numel() for p in network.parameters() if p.requires_grad))

    #network = AxialTransformer(512,48,16).to(device).eval()

    scriptdir = os.path.dirname(os.path.realpath(__file__))

    network.load_state_dict(torch.load(scriptdir + '/metalpred.pt', map_location=lambda storage, loc: storage), strict=True)

    seqdict = parse_fasta(args.input_file)

    aa_trans = str.maketrans('ARNDCQEGHILKMFPSTWYVBJOUXZ-.', 'ABCDEFGHIJKLMNOPQRSTUUUUUUVV')

    network.eval()

    cmdict = { 0 : 'CHEBI:48775', 1 : 'CHEBI:29108', 2 : 'CHEBI:48828', 3 : 'CHEBI:49415', 4 : 'CHEBI:23378', 5 : 'CHEBI:49552',
               6 : 'CHEBI:29036', 7 : 'CHEBI:60240', 8 : 'CHEBI:190135', 9 : 'CHEBI:24875', 10 : 'CHEBI:29033', 11 : 'CHEBI:29034',
               12 : 'CHEBI:30408', 13 : 'CHEBI:49713', 14 : 'CHEBI:18420', 15 : 'CHEBI:29035', 16 : 'CHEBI:16793',
               17 : 'CHEBI:49786', 18 : 'CHEBI:60400', 19 : 'CHEBI:47739', 20 : 'CHEBI:29103', 21 : 'CHEBI:29101', 
               22 : 'CHEBI:49883', 23 : 'CHEBI:21137', 24 : 'CHEBI:29105', 25 : 'CHEBI:177874', 26 : 'CHEBI:21143',
               27 : 'CHEBI:60504', 28 : 'CHEBI:25213' }

    for ac in seqdict:
        seq = seqdict[ac]
        naa = len(seq)
        aacodes = (np.frombuffer(seq.translate(aa_trans).encode('latin-1'), dtype=np.uint8) - ord('A')).reshape(1,naa)
        inputs = torch.from_numpy(aacodes).type(torch.LongTensor).to(device)
        rtxidx = torch.arange(naa, dtype=torch.long, device=inputs.device).unsqueeze(0)

        chunked_inputs = torch.split(inputs, 1024, dim=1)
        chunked_idx = torch.split(rtxidx, 1024, dim=1)

        with torch.no_grad():
            for nc in range(len(chunked_inputs)):
                inp_chunk = chunked_inputs[nc]
                idx_chunk = chunked_idx[nc]
                chunk_len = inp_chunk.size(1)
                #with torch.cuda.amp.autocast(enabled=True, dtype=torch.bfloat16):
                probs = torch.sigmoid(network(inp_chunk, idx_chunk-idx_chunk[0,0]))
                for ri in range(chunk_len):
                    for m in range(29):
                        prob = probs[0,ri,m].item()
                        if prob >= 0.01:
                            print(ac, cmdict[m], ri+1+idx_chunk[0,0].item(), "{:.2f}".format(prob), sep='\t')

if __name__=="__main__":
    main()
