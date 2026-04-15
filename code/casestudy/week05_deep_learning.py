# Week 5 — Deep Learning Fundamentals
# Goal: Implement Linear Layer + Activations + Forward Pass using NumPy only
# -----------------------------------------------------------------------
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

np.random.seed(42)

# ── 1. Building blocks ───────────────────────────────────────────────────
class Linear:
    """y = xW^T + b   (same convention as PyTorch nn.Linear)"""
    def __init__(self, in_features, out_features):
        # He initialization (good for ReLU networks)
        scale = np.sqrt(2.0 / in_features)
        self.W = np.random.randn(out_features, in_features) * scale
        self.b = np.zeros(out_features)

    def forward(self, x):
        return x @ self.W.T + self.b   # (batch, out)

    def __repr__(self):
        return f"Linear({self.W.shape[1]} → {self.W.shape[0]})"


def relu(x):    return np.maximum(0, x)
def sigmoid(x): return 1.0 / (1.0 + np.exp(-np.clip(x, -500, 500)))
def tanh(x):    return np.tanh(x)

def softmax(x):
    e = np.exp(x - x.max(axis=-1, keepdims=True))
    return e / e.sum(axis=-1, keepdims=True)


# ── 2. Build a simple 3-layer MLP ────────────────────────────────────────
class MLP:
    def __init__(self, layer_sizes):
        """layer_sizes: e.g. [4, 64, 32, 3] for input→hidden→output"""
        self.layers = []
        for i in range(len(layer_sizes) - 1):
            self.layers.append(Linear(layer_sizes[i], layer_sizes[i+1]))
        print("MLP architecture:")
        for i, l in enumerate(self.layers):
            print(f"  Layer {i+1}: {l}")
        total = sum(l.W.size + l.b.size for l in self.layers)
        print(f"  Total parameters: {total:,}")

    def forward(self, x):
        """Forward pass: ReLU on hidden layers, softmax on output."""
        activations = [x]
        for i, layer in enumerate(self.layers):
            z = layer.forward(activations[-1])
            if i < len(self.layers) - 1:
                a = relu(z)
            else:
                a = softmax(z)
            activations.append(a)
        return activations


# ── 3. Test on Iris-like data ────────────────────────────────────────────
from sklearn.datasets import load_iris
from sklearn.preprocessing import StandardScaler

iris = load_iris()
X_raw = iris.data[:, :4].astype(float)   # 4 features
y = iris.target                           # 3 classes

scaler = StandardScaler()
X = scaler.fit_transform(X_raw)

model = MLP([4, 16, 8, 3])
activations = model.forward(X)
probs = activations[-1]   # (150, 3)

preds = probs.argmax(axis=1)
acc = (preds == y).mean()
print(f"\nForward pass accuracy (random init, no training): {acc:.2%}")
print(f"Output probabilities for first 5 samples:")
print(np.round(probs[:5], 4))


# ── 4. Visualize activations and weight distributions ───────────────────
fig, axes = plt.subplots(2, 3, figsize=(13, 7))

# Activation functions
x_plot = np.linspace(-4, 4, 300)
ax = axes[0, 0]
ax.plot(x_plot, relu(x_plot),    lw=2, label='ReLU',    color='#ef5350')
ax.plot(x_plot, sigmoid(x_plot), lw=2, label='Sigmoid', color='#42a5f5')
ax.plot(x_plot, tanh(x_plot),    lw=2, label='Tanh',    color='#66bb6a')
ax.axhline(0, color='gray', lw=0.5); ax.axvline(0, color='gray', lw=0.5)
ax.set_title('Activation Functions', fontsize=10)
ax.legend(fontsize=9); ax.grid(True, alpha=0.3)
ax.set_ylim(-1.2, 1.5)

# Weight heatmaps
for i, layer in enumerate(model.layers):
    ax = axes[0, i+1] if i < 2 else axes[1, 0]
    im = ax.imshow(layer.W, cmap='RdBu', aspect='auto',
                   vmin=-2*layer.W.std(), vmax=2*layer.W.std())
    ax.set_title(f'Layer {i+1} Weights {layer.W.shape}', fontsize=9)
    plt.colorbar(im, ax=ax, fraction=0.046)

# Pre-activation distributions per layer
ax = axes[1, 1]
colors = ['#ef5350', '#42a5f5', '#66bb6a']
for i, (act, c) in enumerate(zip(activations[1:], colors)):
    ax.hist(act.flatten(), bins=40, alpha=0.5, color=c,
            label=f'Layer {i+1}', density=True)
ax.set_title('Activation Distributions', fontsize=10)
ax.legend(fontsize=8); ax.set_xlabel('Value')

# Softmax output probabilities
ax = axes[1, 2]
classes = iris.target_names
for ci, (c, name) in enumerate(zip(['#ef5350','#42a5f5','#66bb6a'], classes)):
    mask = y == ci
    ax.scatter(np.where(mask)[0], probs[mask, ci], c=c, s=8, alpha=0.6, label=name)
ax.set_title('Softmax Output (P(correct class))', fontsize=9)
ax.legend(fontsize=8); ax.set_xlabel('Sample index'); ax.set_ylabel('Probability')
ax.set_ylim(0, 1); ax.axhline(1/3, ls='--', color='gray', lw=1, label='Random')

plt.suptitle('Week 5 — Deep Learning Forward Pass from Scratch (NumPy)', fontsize=11, fontweight='bold')
plt.tight_layout()
plt.savefig('/tmp/week05.png', dpi=90, bbox_inches='tight')
print("\nPlot saved!")
