"""
Bird's Eye View (BEV) Projection
==================================
Converts a 3D LiDAR point cloud into a 2D bird's eye view image.
BEV is the standard input representation for AV 3D detection models.
"""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

np.random.seed(1)

def lidar_to_bev(points, x_range=(-30,30), y_range=(-30,30), res=0.2):
    """
    points: (N, 4) array of [x, y, z, intensity]
    Returns: (3, H, W) BEV tensor with channels:
        0: max height, 1: point density (log), 2: max intensity
    """
    W = int((x_range[1]-x_range[0]) / res)
    H = int((y_range[1]-y_range[0]) / res)
    bev = np.zeros((3, H, W))

    xi = ((points[:,0] - x_range[0]) / res).astype(int)
    yi = ((points[:,1] - y_range[0]) / res).astype(int)
    mask = (xi>=0)&(xi<W)&(yi>=0)&(yi<H)
    xi, yi, z, intensity = xi[mask], yi[mask], points[mask,2], points[mask,3]

    np.maximum.at(bev[0], (yi, xi), z)          # max height
    np.add.at(bev[1], (yi, xi), 1)              # count
    np.maximum.at(bev[2], (yi, xi), intensity)  # max intensity

    bev[1] = np.log1p(bev[1]) / np.log1p(bev[1].max() + 1e-6)
    return bev

# Simulate scene: ground + 3 vehicle clusters
def vehicle_cluster(cx, cy, n=300):
    pts = np.random.randn(n, 4) * [1.2, 0.6, 0.3, 0.1]
    pts[:,0]+=cx; pts[:,1]+=cy; pts[:,2]+=1.0; pts[:,3]+=0.7
    return np.clip(pts, None, None)

ground = np.column_stack([np.random.uniform(-30,30,4000), np.random.uniform(-30,30,4000),
                          np.random.uniform(-0.3,0.1,4000), np.random.uniform(0,0.3,4000)])
scene = np.vstack([ground, vehicle_cluster(12,3), vehicle_cluster(22,-6), vehicle_cluster(8,-12)])
bev = lidar_to_bev(scene)

print(f"Point cloud: {len(scene):,} points")
print(f"BEV tensor shape: {bev.shape}  (C x H x W)")
print(f"  Ch0 max height range: [{bev[0].min():.2f}, {bev[0].max():.2f}]")
print(f"  Ch1 density range:    [{bev[1].min():.2f}, {bev[1].max():.2f}]")

fig, axes = plt.subplots(1, 4, figsize=(14, 3.5))
titles = ['Max Height', 'Point Density', 'Max Intensity', 'RGB (H/D/I)']
cmaps  = ['viridis', 'plasma', 'magma']
for i in range(3):
    im = axes[i].imshow(bev[i], cmap=cmaps[i], origin='lower', extent=[-30,30,-30,30])
    axes[i].set_title(titles[i], fontsize=9); plt.colorbar(im, ax=axes[i], fraction=0.05)
bev_rgb = np.stack([bev[0]/bev[0].max(), bev[1], bev[2]/bev[2].max()], axis=-1)
axes[3].imshow(np.clip(bev_rgb,0,1), origin='lower', extent=[-30,30,-30,30])
axes[3].set_title('Pseudo-RGB BEV', fontsize=9)
for ax in axes: ax.set_xlabel('X (m)'); ax.set_ylabel('Y (m)')
plt.suptitle("Bird's Eye View Projection", fontsize=11, fontweight='bold')
plt.tight_layout()
plt.savefig('/tmp/bev_full.png', dpi=90, bbox_inches='tight')
print("Plot saved!")
