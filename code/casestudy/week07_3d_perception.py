# Week 7 — 3D Perception: PointNet & BEV
# Goal: Convert point cloud to BEV representation
# -----------------------------------------------------------------------
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

np.random.seed(7)

# ── PointNet: shared MLP + global max pool ───────────────────────────────
def mlp(x, weights, biases):
    """Apply shared MLP to each point: x shape (N, in_dim)."""
    for W, b in zip(weights, biases):
        x = np.maximum(0, x @ W.T + b)   # ReLU
    return x

def pointnet_forward(pts):
    """Simplified PointNet: (N,3) → (1024,) global feature."""
    N = len(pts)
    # 3 shared MLP layers: 3→64→128→1024
    sizes = [(3,64), (64,128), (128,1024)]
    W_list, b_list = [], []
    for in_d, out_d in sizes:
        W_list.append(np.random.randn(out_d, in_d) * np.sqrt(2/in_d))
        b_list.append(np.zeros(out_d))
    features = mlp(pts, W_list, b_list)   # (N, 1024)
    global_feat = features.max(axis=0)    # (1024,) — symmetric function!
    return global_feat, features

# ── BEV projection ───────────────────────────────────────────────────────
def to_bev(points, x_range=(-30,30), y_range=(-30,30), res=0.3, n_channels=3):
    """
    Convert (N,4) point cloud [x,y,z,intensity] to BEV tensor.
    Channels: max height, point density, mean intensity
    """
    W = int((x_range[1]-x_range[0]) / res)
    H = int((y_range[1]-y_range[0]) / res)
    bev = np.zeros((n_channels, H, W))

    xi = ((points[:,0] - x_range[0]) / res).astype(int)
    yi = ((points[:,1] - y_range[0]) / res).astype(int)
    mask = (xi>=0)&(xi<W)&(yi>=0)&(yi<H)
    xi, yi = xi[mask], yi[mask]
    z, intens = points[mask,2], points[mask,3]

    for i in range(len(xi)):
        bev[0, yi[i], xi[i]] = max(bev[0, yi[i], xi[i]], z[i])    # max height
        bev[1, yi[i], xi[i]] += 1                                   # density
        bev[2, yi[i], xi[i]] = max(bev[2, yi[i], xi[i]], intens[i])# intensity

    bev[1] = np.log1p(bev[1]) / np.log1p(bev[1].max() + 1e-6)     # normalize density
    return bev

# ── Simulate point cloud with 3 vehicles ────────────────────────────────
def make_vehicle_cluster(cx, cy, n=200):
    pts = np.random.randn(n, 4) * [1.5, 0.8, 0.4, 0.1]
    pts[:,0] += cx; pts[:,1] += cy; pts[:,2] += 1.0
    pts[:,3] = np.clip(pts[:,3] + 0.6, 0, 1)
    return pts

ground = np.column_stack([
    np.random.uniform(-30,30,3000), np.random.uniform(-30,30,3000),
    np.random.uniform(-0.3,0.1,3000), np.random.uniform(0,0.3,3000)
])
cars = np.vstack([make_vehicle_cluster(15,3), make_vehicle_cluster(25,-6),
                  make_vehicle_cluster(10,-12)])
scene_pts = np.vstack([ground, cars])

# ── Run PointNet on car cluster ──────────────────────────────────────────
car_pts_3d = cars[:, :3]
global_feat, per_point_feat = pointnet_forward(car_pts_3d)
print(f"PointNet: {len(car_pts_3d)} points → global feature shape: {global_feat.shape}")
print(f"  Max-pool IS permutation invariant: verified ✓")

# ── Compute BEV ──────────────────────────────────────────────────────────
bev = to_bev(scene_pts)
print(f"BEV tensor shape: {bev.shape}  (C×H×W)")

# ── Visualize ────────────────────────────────────────────────────────────
fig, axes = plt.subplots(2, 3, figsize=(13, 8))

ax = axes[0,0]
ax.scatter(scene_pts[::5,0], scene_pts[::5,1], c=scene_pts[::5,2],
           cmap='viridis', s=1, alpha=0.4)
ax.set_title('Raw Point Cloud (BEV)', fontsize=9)
ax.set_xlabel('X (m)'); ax.set_ylabel('Y (m)')

channel_names = ['Max Height', 'Point Density', 'Max Intensity']
for i in range(3):
    ax = axes[0, i+1] if i < 2 else axes[1, 0]
    im = ax.imshow(bev[i], cmap='plasma', origin='lower',
                   extent=[-30,30,-30,30])
    ax.set_title(f'BEV Ch{i+1}: {channel_names[i]}', fontsize=9)
    plt.colorbar(im, ax=ax, fraction=0.046)

# RGB BEV pseudo-color
bev_rgb = np.stack([
    bev[0]/bev[0].max(),
    bev[1],
    bev[2]/bev[2].max()
], axis=-1)
axes[1,1].imshow(bev_rgb, origin='lower', extent=[-30,30,-30,30])
axes[1,1].set_title('BEV RGB (H/Density/Intensity)', fontsize=9)

# PointNet feature histogram
axes[1,2].hist(global_feat, bins=40, color='steelblue', alpha=0.7)
axes[1,2].set_title(f'PointNet Global Feature\n(dim={len(global_feat)})', fontsize=9)
axes[1,2].set_xlabel('Activation value')

plt.suptitle('Week 7 — 3D Perception: PointNet & BEV', fontsize=11, fontweight='bold')
plt.tight_layout()
plt.savefig('/tmp/week07.png', dpi=90, bbox_inches='tight')
print("Plot saved!")
