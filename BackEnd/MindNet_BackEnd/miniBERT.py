# models.py
import torch
import torch.nn as nn
import torch.nn.functional as F
import math

class SimpleTokenizer:
    """Handles the conversion of English strings to numerical sequences."""
    def __init__(self, vocabulary, max_len=15):
        self.max_len = max_len
        # In production, we pass the saved vocabulary list here
        self.words = vocabulary
        self.word2idx = {word: i for i, word in enumerate(self.words)}
        self.idx2word = {i: word for i, word in enumerate(self.words)}
        self.vocab_size = len(self.words)

    def encode(self, text):
        """Standardizes text and converts to padded IDs."""
        tokens = text.lower().split()
        # Uses index 0 ([PAD]) if a word is unknown
        ids = [self.word2idx.get(w, 0) for w in tokens]
        ids = [self.word2idx["[CLS]"]] + ids # Add start of sentence token

        if len(ids) < self.max_len:
            ids += [self.word2idx["[PAD]"]] * (self.max_len - len(ids))
        else:
            ids = ids[:self.max_len]
        return ids

class MultiHeadAttention(nn.Module):
    """The attention mechanism that finds connections between words."""
    def __init__(self, d_model, num_heads):
        super().__init__()
        self.num_heads = num_heads
        self.d_model = d_model
        self.d_k = d_model // num_heads
        self.w_q = nn.Linear(d_model, d_model)
        self.w_k = nn.Linear(d_model, d_model)
        self.w_v = nn.Linear(d_model, d_model)
        self.w_o = nn.Linear(d_model, d_model)

    def forward(self, q, k, v, mask=None):
        batch_size = q.size(0)
        Q = self.w_q(q).view(batch_size, -1, self.num_heads, self.d_k).transpose(1, 2)
        K = self.w_k(k).view(batch_size, -1, self.num_heads, self.d_k).transpose(1, 2)
        V = self.w_v(v).view(batch_size, -1, self.num_heads, self.d_k).transpose(1, 2)

        scores = torch.matmul(Q, K.transpose(-2, -1)) / math.sqrt(self.d_k)
        if mask is not None:
            scores = scores.masked_fill(mask == 0, -1e9)

        attn = F.softmax(scores, dim=-1)
        context = torch.matmul(attn, V).transpose(1, 2).contiguous().view(batch_size, -1, self.d_model)
        return self.w_o(context)

class EncoderBlock(nn.Module):
    """A single Transformer layer combining Attention and FeedForward logic."""
    def __init__(self, d_model, num_heads, d_ff, dropout=0.1):
        super().__init__()
        self.attention = MultiHeadAttention(d_model, num_heads)
        self.norm1 = nn.LayerNorm(d_model)
        self.ff = nn.Sequential(
            nn.Linear(d_model, d_ff),
            nn.GELU(),
            nn.Linear(d_ff, d_model)
        )
        self.norm2 = nn.LayerNorm(d_model)
        self.dropout = nn.Dropout(dropout)

    def forward(self, x, mask):
        attn_out = self.attention(x, x, x, mask)
        x = self.norm1(x + self.dropout(attn_out))
        ff_out = self.ff(x)
        x = self.norm2(x + self.dropout(ff_out))
        return x

class BERT(nn.Module):
    """The main mini-BERT model container."""
    def __init__(self, vocab_size, d_model=256, n_layers=4, num_heads=8, max_len=15):
        super().__init__()
        self.token_emb = nn.Embedding(vocab_size, d_model)
        self.pos_emb = nn.Embedding(max_len, d_model)
        self.layers = nn.ModuleList([
            EncoderBlock(d_model, num_heads, d_model * 4) for _ in range(n_layers)
        ])

    def forward(self, x, mask=None):
        batch_size, seq_len = x.size()
        pos = torch.arange(seq_len, device=x.device).expand(batch_size, seq_len)
        x = self.token_emb(x) + self.pos_emb(pos)
        for layer in self.layers:
            x = layer(x, mask)
        return x # Return hidden states for embedding extraction