# Week 6 — CV Foundations: CNN & ViT
# Goal: Implement a simple image backbone for feature extraction
# -----------------------------------------------------------------------
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.signal import convolve2d

np.random.seed(6)

# ── 1. Manual Conv2D operation ───────────────────────────────────────────
def conv2d(img, kernel, stride=1, padding=0):
    """2D convolution (single channel, no batch)."""
    if padding:
        img = np.pad(img, padding, mode='constant')
    kH, kW = kernel.shape
    H_out = (img.shape[0] - kH) // stride + 1
    W_out = (img.shape[1] - kW) // stride + 1
    out = np.zeros((H_out, W_out))
    for i in range(0, H_out * stride, stride):
        for j in range(0, W_out * stride, stride):
            out[i//stride, j//stride] = (img[i:i+kH, j:j+kW] * kernel).sum()
    return out

def relu(x): return np.maximum(0, x)

def max_pool2d(x, size=2):
    H, W = x.shape
    H2, W2 = H // size, W // size
    out = np.zeros((H2, W2))
    for i in range(H2):
        for j in range(W2):
            out[i, j] = x[i*size:(i+1)*size, j*size:(j+1)*size].max()
    return out

# ── 2. Classic edge-detection kernels ────────────────────────────────────
kernels = {
    'Sobel X':   np.array([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]]) / 4,
    'Sobel Y':   np.array([[-1,-2,-1], [ 0, 0, 0], [ 1, 2, 1]]) / 4,
    'Laplacian': np.array([[ 0,-1, 0], [-1, 4,-1], [ 0,-1, 0]]) / 4,
    'Sharpen':   np.array([[ 0,-1, 0], [-1, 5,-1], [ 0,-1, 0]]) / 4,
}

# Create a synthetic "road scene" image (64x64)
img = np.zeros((64, 64))
img[20:45, 20:45] = 0.8   # vehicle
img[10:15, :] = 0.6        # sky/horizon
img[50:, 15:50] = 0.3      # road
img[30:35, 5:10] = 0.9     # sign
img += np.random.randn(64, 64) * 0.05  # noise
img = np.clip(img, 0, 1)

# ── 3. Self-attention (simplified ViT patch attention) ───────────────────
def self_attention(X, d_k=8):
    """X: (N_patches, d_model) — returns attended output."""
    Wq = np.random.randn(X.shape[1], d_k) * 0.1
    Wk = np.random.randn(X.shape[1], d_k) * 0.1
    Wv = np.random.randn(X.shape[1], d_k) * 0.1
    Q = X @ Wq; K = X @ Wk; V = X @ Wv
    scores = Q @ K.T / np.sqrt(d_k)
    scores -= scores.max(axis=-1, keepdims=True)
    weights = np.exp(scores) / np.exp(scores).sum(axis=-1, keepdims=True)
    return weights @ V, weights

# Treat 8x8 image patches as tokens
patch_size = 8
patches = []
for i in range(0, 64, patch_size):
    for j in range(0, 64, patch_size):
        patches.append(img[i:i+patch_size, j:j+patch_size].flatten())
X_patches = np.array(patches)   # (64 patches, 64 dims)
out_attn, attn_weights = self_attention(X_patches)

# ── 4. Apply convolutions ────────────────────────────────────────────────
feature_maps = {}
for name, kernel in kernels.items():
    fm = conv2d(img, kernel, padding=1)
    feature_maps[name] = relu(fm)

pooled = {k: max_pool2d(v, 2) for k, v in feature_maps.items()}

# ── 5. Visualize ─────────────────────────────────────────────────────────
fig, axes = plt.subplots(3, 5, figsize=(15, 9))

axes[0, 0].imshow(img, cmap='gray'); axes[0, 0].set_title('Input Image', fontsize=9)
axes[0, 0].axis('off')

for i, (name, fm) in enumerate(feature_maps.items()):
    axes[0, i+1].imshow(fm, cmap='hot'); axes[0, i+1].set_title(name, fontsize=9)
    axes[0, i+1].axis('off')
    axes[1, i].imshow(kernels[name], cmap='RdBu')
    axes[1, i].set_title(f'{name}\nKernel', fontsize=8)
    axes[1, i+1].imshow(pooled[name], cmap='hot')
    axes[1, i+1].set_title(f'MaxPool\n{pooled[name].shape}', fontsize=8)

axes[1, 0].imshow(img[16:32, 16:32], cmap='gray')
axes[1, 0].set_title('Zoomed patch', fontsize=9)

# Attention map (reshaped 8x8 grid of patches)
axes[2, 0].imshow(attn_weights, cmap='Blues')
axes[2, 0].set_title(f'Self-Attention\n{attn_weights.shape}', fontsize=9)

# Attention weights for the first patch
attn_map = attn_weights[0].reshape(8, 8)
axes[2, 1].imshow(attn_map, cmap='Reds')
axes[2, 1].set_title('Attn from Patch 0', fontsize=9)

# Feature vector comparison
axes[2, 2].bar(range(8), X_patches[:8].mean(axis=1), color='steelblue', alpha=0.7)
axes[2, 2].set_title('Mean patch values', fontsize=9)
axes[2, 2].set_xlabel('Patch index')

axes[2, 3].bar(range(8), out_attn[:8, 0], color='tomato', alpha=0.7)
axes[2, 3].set_title('Post-attention features', fontsize=9)

axes[2, 4].plot(np.sort(attn_weights[0])[::-1], 'o-', ms=4, color='purple')
axes[2, 4].set_title('Attention weight dist.', fontsize=9)
axes[2, 4].set_xlabel('Sorted rank')

for ax in axes.flat: ax.axis('off') if ax.get_title() else None
for row in axes:
    for ax in row:
        if not ax.images and not ax.lines and not ax.patches and not ax.collections:
            ax.axis('off')

plt.suptitle('Week 6 — CNN Convolutions & ViT Self-Attention', fontsize=11, fontweight='bold')
plt.tight_layout()
plt.savefig('/tmp/week06.png', dpi=90, bbox_inches='tight')
print("Week 6 — CNN & ViT demo complete!")
print(f"  Input: {img.shape}, Feature map: {list(feature_maps.values())[0].shape}")
print(f"  Patches: {X_patches.shape}, Attention: {attn_weights.shape}")
print("Plot saved!")
