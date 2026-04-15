"""
Self-Attention Mechanism
=========================
From scratch implementation of scaled dot-product attention,
the core building block of Transformers.
"""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

np.random.seed(0)

def softmax(x):
    e = np.exp(x - x.max(axis=-1, keepdims=True))
    return e / e.sum(axis=-1, keepdims=True)

def attention(Q, K, V, mask=None):
    """Scaled dot-product attention."""
    d_k = Q.shape[-1]
    scores = Q @ K.T / np.sqrt(d_k)          # (seq, seq)
    if mask is not None:
        scores = scores.masked_fill(mask == 0, -1e9)
    weights = softmax(scores)                  # (seq, seq)
    output  = weights @ V                      # (seq, d_v)
    return output, weights

# ── Demo on a short sentence ──────────────────────────────────────────────
tokens = ["the", "cat", "sat", "on", "mat"]
seq_len, d_model = len(tokens), 16
d_k = 8

# Random projections (in practice, learned)
Wq = np.random.randn(d_model, d_k) * 0.1
Wk = np.random.randn(d_model, d_k) * 0.1
Wv = np.random.randn(d_model, d_k) * 0.1

# Random input embeddings
X = np.random.randn(seq_len, d_model)
Q = X @ Wq; K = X @ Wk; V = X @ Wv

out, weights = attention(Q, K, V)

print("Input shape:", X.shape)
print("Q,K,V shape:", Q.shape)
print("Output shape:", out.shape)
print("\nAttention weights (each row sums to 1):")
for i, tok in enumerate(tokens):
    row = " ".join(f"{w:.2f}" for w in weights[i])
    print(f"  {tok:5s} → [{row}]")

# ── Visualize ─────────────────────────────────────────────────────────────
fig, axes = plt.subplots(1, 2, figsize=(10, 4))

im = axes[0].imshow(weights, cmap='Blues', vmin=0)
axes[0].set_xticks(range(seq_len)); axes[0].set_xticklabels(tokens, fontsize=9)
axes[0].set_yticks(range(seq_len)); axes[0].set_yticklabels(tokens, fontsize=9)
axes[0].set_title('Self-Attention Weight Matrix', fontsize=10)
plt.colorbar(im, ax=axes[0], fraction=0.046)
for i in range(seq_len):
    for j in range(seq_len):
        axes[0].text(j, i, f'{weights[i,j]:.2f}', ha='center', va='center', fontsize=7)

# Attention scores (pre-softmax) vs post
scores_raw = Q @ K.T / np.sqrt(d_k)
axes[1].plot(scores_raw[0], 'b.-', ms=8, label='Scores (pre-softmax)')
axes[1].plot(weights[0],    'r.-', ms=8, label='Weights (post-softmax)')
axes[1].set_xticks(range(seq_len)); axes[1].set_xticklabels(tokens)
axes[1].set_title(f'Attention from "{tokens[0]}"', fontsize=10)
axes[1].legend(fontsize=8); axes[1].grid(True, alpha=0.3)

plt.suptitle('Scaled Dot-Product Attention', fontsize=11, fontweight='bold')
plt.tight_layout()
plt.savefig('/tmp/attn.png', dpi=90, bbox_inches='tight')
print("\nPlot saved!")
