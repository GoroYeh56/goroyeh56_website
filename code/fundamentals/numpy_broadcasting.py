"""
NumPy Arrays & Broadcasting
============================
Broadcasting lets NumPy apply operations across arrays of different shapes
without copying data — essential for efficient ML computations.
"""
import numpy as np

np.random.seed(42)

# ── 1. Basic broadcasting ────────────────────────────────────────────────
A = np.array([[1, 2, 3],
              [4, 5, 6],
              [7, 8, 9]])   # shape (3, 3)
b = np.array([10, 20, 30])  # shape (3,) — broadcast to each row

result = A + b
print("A + b (broadcast b to each row):")
print(result)

# ── 2. Matrix multiplication with @ ─────────────────────────────────────
W = np.random.randn(3, 4)   # weight matrix
out = A @ W                  # (3,3) @ (3,4) → (3,4)
print(f"\nA @ W:  {A.shape} @ {W.shape} → {out.shape}")

# ── 3. Broadcasting rules ────────────────────────────────────────────────
# Rule: dimensions are compatible if they are equal OR one of them is 1
X = np.random.randn(5, 1, 4)  # (5, 1, 4)
Y = np.random.randn(1, 3, 4)  # (1, 3, 4)
Z = X + Y                      # (5, 3, 4)  ← broadcast
print(f"\nX{X.shape} + Y{Y.shape} → Z{Z.shape}")

# ── 4. Vectorized batch normalization (no loops) ─────────────────────────
batch = np.random.randn(32, 10)  # 32 samples, 10 features
mean  = batch.mean(axis=0)       # (10,)
std   = batch.std(axis=0) + 1e-8
normalized = (batch - mean) / std  # broadcasting (32,10) - (10,)
print(f"\nBatch norm: mean≈{normalized.mean():.4f}  std≈{normalized.std():.4f}")

# ── 5. Pairwise Euclidean distance matrix (no loops) ────────────────────
def pairwise_dist(A, B):
    """Compute all pairwise distances: result[i,j] = ||A[i] - B[j]||"""
    # ||a - b||^2 = ||a||^2 + ||b||^2 - 2*a·b
    aa = (A**2).sum(axis=1, keepdims=True)  # (N,1)
    bb = (B**2).sum(axis=1, keepdims=True)  # (M,1)
    ab = A @ B.T                             # (N,M)
    return np.sqrt(np.maximum(aa + bb.T - 2*ab, 0))

pts_a = np.random.randn(5, 3)
pts_b = np.random.randn(4, 3)
D = pairwise_dist(pts_a, pts_b)
print(f"\nPairwise distance matrix: {D.shape}")
print(D.round(3))
