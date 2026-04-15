# Week 1 — Linear Algebra & Calculus
# Goal: Write a 3D rotation matrix and visualize point cloud displacement
# -----------------------------------------------------------------------
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# ── 1. Rotation matrices ────────────────────────────────────────────────
def Rx(theta):
    """Rotation around X-axis by theta radians."""
    c, s = np.cos(theta), np.sin(theta)
    return np.array([[1, 0, 0],
                     [0, c,-s],
                     [0, s, c]])

def Ry(theta):
    """Rotation around Y-axis by theta radians."""
    c, s = np.cos(theta), np.sin(theta)
    return np.array([[ c, 0, s],
                     [ 0, 1, 0],
                     [-s, 0, c]])

def Rz(theta):
    """Rotation around Z-axis by theta radians."""
    c, s = np.cos(theta), np.sin(theta)
    return np.array([[c,-s, 0],
                     [s, c, 0],
                     [0, 0, 1]])

# ── 2. Compose rotation: R = Rz * Ry * Rx ──────────────────────────────
roll, pitch, yaw = np.radians(30), np.radians(20), np.radians(45)
R = Rz(yaw) @ Ry(pitch) @ Rx(roll)
print("Rotation matrix R (roll=30°, pitch=20°, yaw=45°):")
print(np.round(R, 4))
print(f"\nDet(R) = {np.linalg.det(R):.6f}  (should be 1.0 for valid rotation)")

# ── 3. Simulate a mini point cloud (a cube) ─────────────────────────────
np.random.seed(42)
pts = np.random.uniform(-1, 1, (50, 3))   # 50 points in [-1,1]^3

# Apply rotation
pts_rotated = (R @ pts.T).T               # shape (50, 3)

# ── 4. Gradient descent demo: minimize f(x,y) = x^2 + 2y^2 ─────────────
def f(x, y):    return x**2 + 2*y**2
def grad(x, y): return np.array([2*x, 4*y])

pos = np.array([3.0, 2.0])
lr, history = 0.1, [pos.copy()]
for _ in range(30):
    pos = pos - lr * grad(*pos)
    history.append(pos.copy())
history = np.array(history)

# ── 5. Visualize ────────────────────────────────────────────────────────
fig = plt.figure(figsize=(12, 4))

# Plot 1: point cloud rotation
ax1 = fig.add_subplot(131, projection='3d')
ax1.scatter(*pts.T,         c='steelblue', s=12, alpha=0.6, label='Original')
ax1.scatter(*pts_rotated.T, c='tomato',    s=12, alpha=0.6, label='Rotated')
ax1.set_title('3D Point Cloud\nRotation', fontsize=9)
ax1.legend(fontsize=7)

# Plot 2: rotation matrix heatmap
ax2 = fig.add_subplot(132)
im = ax2.imshow(R, cmap='RdBu', vmin=-1, vmax=1)
for i in range(3):
    for j in range(3):
        ax2.text(j, i, f'{R[i,j]:.2f}', ha='center', va='center', fontsize=9)
ax2.set_title('Rotation Matrix R', fontsize=9)
ax2.set_xticks([]); ax2.set_yticks([])
plt.colorbar(im, ax=ax2, fraction=0.046)

# Plot 3: gradient descent trajectory
ax3 = fig.add_subplot(133)
x_ = np.linspace(-4, 4, 100)
y_ = np.linspace(-3, 3, 100)
X, Y = np.meshgrid(x_, y_)
ax3.contourf(X, Y, f(X, Y), levels=20, cmap='Blues', alpha=0.7)
ax3.plot(history[:,0], history[:,1], 'r.-', ms=4, lw=1.5, label='GD path')
ax3.plot(*history[0],  'go', ms=8, label='Start')
ax3.plot(*history[-1], 'r*', ms=10, label='End')
ax3.set_title('Gradient Descent\non f(x,y)=x²+2y²', fontsize=9)
ax3.legend(fontsize=7)

plt.suptitle('Week 1 — Linear Algebra & Calculus', fontsize=11, fontweight='bold')
plt.tight_layout()
plt.savefig('/tmp/week01.png', dpi=90, bbox_inches='tight')
print("\nFinal position after GD:", np.round(history[-1], 4), " (should be near [0,0])")
print("Plot saved!")
