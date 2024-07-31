# DMPmetal

DMPmetal is a deep learning-based method for predicting metal binding sites from amino acid sequences. This uses a pretrained protein language model (pLM) to embed the target sequences and to provide the features for simple feed-forward classifier. From a user perspective, the input to the model is a single amino acid sequence, and the output probabilities relate to each of the 29 CHEBI metal codes. This model was ranked 1st in the UniProt Metal Binding Site Machine Learning Challenge held in 2022, and was trained on the organizers’ provided NEG_TRAIN and POS_TRAIN_FULL datasets, based on curated UniProt annotations (http://insideuniprot.blogspot.com/2022/02/the-uniprot-metal-binding-site-machine.html).

## Installation

DMPmetal requires pytorch and the flash-attn packages. At the time of writing flash-attn most easily installs with pytorch 2.0.1 and cuda 11.8. Though you should be able to compile it against later versions of both. Python dependencies can be installed with

```
pip install -r requirements.txt
```

The weights file should be downloaded and unpackaged from:

```
http://bioinfadmin.cs.ucl.ac.uk/downloads/DMPmetal/metalpred.pt.gz
```

## Usage

The standard usage is:

``` 
python pytorch_dmp2e2e_pred.py -i /path/to/file.fasta
```

### Example

```
python pytorch_dmp2e2e_pred.py -i 5pcy.fasta
```

### Options
```
  -i INPUT   Specify path to fasta file input. 
  -d DEVICE  Hardware to run on. Options: 'cpu', 'cuda'. default is 'cpu'
```

## Outputs

### String output to stdout
 
By default, DMPmetal returns output to stdout. You can capture this to a file with a typical redirection. A typical output might be:

```
FASTA HEADER ID, CHEBI CODE, RESIUDE NUMBER, PROBABILITY
PDB|5PCY	CHEBI:25213	11	0.01
PDB|5PCY	CHEBI:23378	37	0.99
PDB|5PCY	CHEBI:29036	37	0.02
PDB|5PCY	CHEBI:60240	37	0.03
PDB|5PCY	CHEBI:24875	37	0.02
```

Only binding residues that pass a 0.01 cutoff are returned. Metal binding residues are predicted for the following CHEBI codes:

```
CHEBI:48775   : Cd2+
CHEBI:29108   : Ca2+
CHEBI:48828   : Co2+
CHEBI:49415   : Co3+
CHEBI:23378   : Cu cation
CHEBI:49552   : Cu+
CHEBI:29036   : Cu2+
CHEBI:60240   : divalent metal cation
CHEBI:190135  : di-μ-sulfido-diiron
CHEBI:24875   : iron cation
CHEBI:29033   : Fe2+
CHEBI:29034   : Fe3+
CHEBI:30408   : iron-sulfur cluster
CHEBI:49713   : Li+
CHEBI:18420   : Mg2+
CHEBI:29035   : Mn2+
CHEBI:16793   : Hg2+
CHEBI:49786   : Ni2+
CHEBI:60400   : nickel-iron-sulfur cluster
CHEBI:47739   : NiFe4S4 cluster
CHEBI:29103   : K+
CHEBI:29101   : Na+
CHEBI:49883   : tetra-μ3-sulfido-tetrairon
CHEBI:21137   : tri-μ-sulfido-μ3-sulfido-triiron
CHEBI:29105   : Zn2+
CHEBI:177874  : NiFe4S5 cluster
CHEBI:21143   : Fe8S7 iron-sulfur cluster
CHEBI:60504   : iron-sulfur-iron cofactor
CHEBI:25213   : metal cation
```
