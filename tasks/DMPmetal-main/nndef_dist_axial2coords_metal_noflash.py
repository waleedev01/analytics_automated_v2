import torch
from torch import nn, einsum
import torch.nn.functional as F
from torch.utils.checkpoint import checkpoint

from einops import rearrange, repeat

#from flash_attn.flash_attn_interface import flash_attn_unpadded_qkvpacked_func
#from flash_attn.flash_attn_interface import flash_attn_unpadded_kvpacked_func
    
from flash_attn.modules.mha import MHA

from bert_padding import unpad_input, pad_input

from math import sqrt, log, asin, cos, pi, sin, log2

import numpy as np


# Sinusoidal positional embeddings
class FixedPositionalEmbedding(nn.Module):
    def __init__(self, dim, max_seq_len):
        super().__init__()
        inv_freq = 1. / (10000 ** (torch.arange(0, dim, 2).float() / dim))
        position = torch.arange(0, max_seq_len, dtype=torch.float)
        sinusoid_inp = torch.einsum("i,j->ij", position, inv_freq)
        emb = torch.cat((sinusoid_inp.sin(), sinusoid_inp.cos()), dim=-1)
        self.register_buffer('emb', emb)

    def forward(self, residx):
        return self.emb[residx, :]

    
class SwiGLU(nn.Module):
    def forward(self, x):
        x, gates = x.chunk(2, dim = -1)
        return x * F.silu(gates)


# Sequence encoder block
class SeqEncoder(nn.Module):
    def __init__(self, d_model, heads, p_drop=0.1):
        super().__init__()

        # Multihead attention
        self.attn = MHA(d_model, heads, use_flash_attn=False)

        # Feedforward
        self.ff = nn.Sequential(
            nn.Linear(d_model, d_model*8),
            SwiGLU(),
            #nn.Dropout(p_drop),
            nn.Linear(d_model*4, d_model)
        )

        #nn.init.zeros_(self.ff[-1].weight)
        #nn.init.zeros_(self.ff[-1].bias)

        # Normalization and dropout modules
        self.norm1 = nn.LayerNorm(d_model)
        self.norm2 = nn.LayerNorm(d_model)
        #self.dropout = nn.Dropout(p_drop)

    def forward(self, x):
        # Input shape for multihead attention: (BATCH, NSEQ, NRES, EMB)
        # Multihead attention w/ pre-LayerNorm
        x2 = x
        x = self.norm1(x)
        x = self.attn(x)
        x = x2 + x # self.dropout(x)
        
        # feed-forward
        x2 = x
        x = self.norm2(x)
        x = self.ff(x)
        return x2 + x


# Sequence Transformer Module
class SeqTransformer(nn.Module):
    def __init__(self,width,nblocks,nheads):
        super().__init__()

        self.embed = nn.Embedding(22, width)

        self.abs_pos = FixedPositionalEmbedding(width, 3000)

        layers = []

        for i in range(nblocks):
            layers.append(SeqEncoder(d_model=width, heads=nheads, p_drop=0.1))

        self.hv_encoder = nn.ModuleList(layers)

        self.seq_norm = nn.LayerNorm(width)

        self.logits_fc = nn.Linear(width, 29)

        
    def forward(self, x, residx):

        B, L = x.shape[:2]
        att_mask = x <= 20
        x = self.embed(x) + self.abs_pos(residx)

        init_x = x

        #print(x.size(), posbias.size())

        for m in self.hv_encoder:
            x = m(x)

        x = self.seq_norm(x)

        pred_out = self.logits_fc(x)

        return pred_out
