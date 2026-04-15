"""
Gradient Descent & Partial Derivatives
========================================
Demonstrates numerical vs analytical gradients and
gradient descent optimization on a simple function.
"""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# ── Analytical gradient check ────────────────────────────────────────────
def f(x):     return x[0]**2 + 2*x[1]**2
def grad(x):  return np.array([2*x[0], 4*x[1]])

x = np.array([2.0, 3.0])
eps = 1e-5
numeric = np.array([(f(x + eps*np.eye(2)[i]) - f(x)) / eps for i in range(2)])
analytic = grad(x)
print("Analytic gradient:", analytic)
print("Numeric  gradient:", numeric.round(5))
print(f"Max error: {abs(analytic - numeric).max():.2e}")

# ── Gradient descent ─────────────────────────────────────────────────────
for lr in [0.05, 0.1, 0.3]:
    pos = np.array([3.0, 2.0])
    history = [pos.copy()]
    for _ in range(50):
        pos = pos - lr * grad(pos)
        history.append(pos.copy())
    history = np.array(history)
    print(f"lr={lr}: final={history[-1].round(4)}  f={f(history[-1]):.6f}")

# ── Visualize loss surface + GD paths ────────────────────────────────────
x_ = np.linspace(-4, 4, 200)
y_ = np.linspace(-3, 3, 200)
X, Y = np.meshgrid(x_, y_)
Z = X**2 + 2*Y**2

fig, axes = plt.subplots(1, 2, figsize=(11, 4))

ax = axes[0]
ax.contourf(X, Y, Z, levels=25, cmap='Blues', alpha=0.8)
colors = ['#ef5350', '#ffa726', '#66bb6a']
for lr, color in zip([0.05, 0.1, 0.3], colors):
    pos = np.array([3.0, 2.0]); hist = [pos.copy()]
    for _ in range(30): pos = pos - lr*grad(pos); hist.append(pos.copy())
    hist = np.array(hist)
    ax.plot(hist[:,0], hist[:,1], '.-', color=color, ms=4, lw=1.5, label=f'lr={lr}')
    ax.plot(*hist[0], 'ko', ms=6)
ax.set_title('Gradient Descent Paths on f(x,y)=x²+2y²', fontsize=10)
ax.legend(fontsize=8); ax.set_xlabel('x'); ax.set_ylabel('y')

ax2 = axes[1]
for lr, color in zip([0.05, 0.1, 0.3], colors):
    pos = np.array([3.0, 2.0]); losses = [f(pos)]
    for _ in range(40): pos = pos - lr*grad(pos); losses.append(f(pos))
    ax2.semilogy(losses, color=color, lw=2, label=f'lr={lr}')
ax2.set_title('Loss Curve (log scale)', fontsize=10)
ax2.legend(fontsize=8); ax2.set_xlabel('Step'); ax2.set_ylabel('Loss')
ax2.grid(True, alpha=0.3)

plt.suptitle('Gradient Descent Visualization', fontsize=11, fontweight='bold')
plt.tight_layout()
plt.savefig('/tmp/gd.png', dpi=90, bbox_inches='tight')
print("\nPlot saved!")
