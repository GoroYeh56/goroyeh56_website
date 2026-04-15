# Week 9 — Sensor Fusion: Camera-LiDAR Geometric Alignment
# Goal: Implement geometric alignment fusion
# -----------------------------------------------------------------------
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

np.random.seed(9)

print("Week 9 — Camera-LiDAR Sensor Fusion")
print("=" * 45)

# ── Fusion strategies overview ───────────────────────────────────────────
print("""
Fusion Strategies:
  Early Fusion  : Concatenate raw sensor data → single model
  Late Fusion   : Separate models → merge predictions
  Middle Fusion : BEVFusion — align features in BEV space ← SOTA

Geometric Alignment Steps:
  1. Calibration: K (camera intrinsic), R,t (extrinsic LiDAR→Cam)
  2. LiDAR → Camera frame: P_cam = R @ P_lidar + t
  3. Camera → Pixel: [u,v] = K @ P_cam / P_cam[2]
  4. Depth-aware coloring: paint pixel with LiDAR depth/intensity
""")

# ── Simulate calibrated sensors ─────────────────────────────────────────
# Camera intrinsics
K = np.array([[1900, 0, 960],
              [0, 1900, 640],
              [0, 0, 1]], dtype=float)

# LiDAR → Camera extrinsic (rotation + translation)
R = np.array([[0,-1,0],[0,0,-1],[1,0,0]], dtype=float)
t = np.array([0.1, 0.8, 1.5])

def project(pts_lidar, K, R, t):
    pts_cam = (R @ pts_lidar[:,:3].T).T + t
    valid = pts_cam[:,2] > 0.5
    uvw = (K @ pts_cam[valid].T).T
    u = uvw[:,0]/uvw[:,2]; v = uvw[:,1]/uvw[:,2]
    depth = pts_cam[valid,2]
    in_img = (u>0)&(u<1920)&(v>0)&(v<1280)
    return u[in_img], v[in_img], depth[in_img], pts_lidar[valid][in_img]

# Simulate LiDAR + two overlapping detections (camera box + lidar cluster)
N = 2000
angles  = np.random.uniform(-np.pi/3, np.pi/3, N)
ranges  = np.random.uniform(3, 50, N)
x = ranges * np.cos(angles)
y = ranges * np.sin(angles) * 0.5
z = np.random.uniform(-2, 3, N)
intens  = np.random.uniform(0,1,N)
lidar_pts = np.column_stack([x, y, z, intens])

# Camera 2D detections (bounding boxes)
cam_dets = [
    {'box2d': [800,500,1100,750], 'class':'Car',   'conf':0.92, 'color':'#ef5350'},
    {'box2d': [400,520,600,720],  'class':'Car',   'conf':0.85, 'color':'#ef5350'},
    {'box2d': [1100,550,1200,700],'class':'Cyclist','conf':0.78,'color':'#66bb6a'},
]

u, v, depth, orig_pts = project(lidar_pts, K, R, t)

# Early Fusion: for each camera box, find LiDAR points inside and compute 3D center
print("Early Fusion — LiDAR points inside camera boxes:")
for det in cam_dets:
    x1,y1,x2,y2 = det['box2d']
    mask = (u>=x1)&(u<=x2)&(v>=y1)&(v<=y2)
    n_pts = mask.sum()
    if n_pts > 5:
        median_depth = np.median(depth[mask])
        cx_3d = (x1+x2)/2; cy_3d = (y1+y2)/2
        # Back-project to 3D
        X3d = (cx_3d - K[0,2]) * median_depth / K[0,0]
        Y3d = (cy_3d - K[1,2]) * median_depth / K[1,1]
        print(f"  {det['class']:8s}: {n_pts:4d} pts  depth={median_depth:.1f}m  "
              f"3D=({X3d:.1f},{Y3d:.1f},{median_depth:.1f})m")
    else:
        print(f"  {det['class']:8s}: {n_pts:4d} pts  (insufficient LiDAR coverage)")

# ── Visualize ─────────────────────────────────────────────────────────────
fig, axes = plt.subplots(1, 2, figsize=(13, 5))

# Camera view with projected LiDAR + 2D boxes
ax1 = axes[0]
ax1.set_facecolor('#1c1c2e')
sc = ax1.scatter(u[::3], v[::3], c=depth[::3], cmap='plasma',
                 s=1.5, alpha=0.6, vmin=0, vmax=50)
plt.colorbar(sc, ax=ax1, label='LiDAR depth (m)')
for det in cam_dets:
    x1,y1,x2,y2 = det['box2d']
    rect = plt.Rectangle((x1,y1), x2-x1, y2-y1,
                          fill=False, edgecolor=det['color'], lw=2)
    ax1.add_patch(rect)
    ax1.text(x1, y1-8, f"{det['class']} {det['conf']:.2f}",
             color=det['color'], fontsize=8, fontweight='bold')
ax1.set_xlim(0,1920); ax1.set_ylim(1280,0)
ax1.set_title('Camera View + LiDAR Projection', fontsize=10)

# BEV with camera frustum
ax2 = axes[1]
fore = lidar_pts[lidar_pts[:,0]>0]
ax2.scatter(fore[::3,0], fore[::3,1], c=fore[::3,2],
            cmap='RdYlGn_r', s=1, alpha=0.3, vmin=-2, vmax=3)
# Camera FOV cone
fov_half = np.radians(30)
for angle in [-fov_half, fov_half]:
    ax2.plot([0, 50*np.cos(angle)], [0, 50*np.sin(angle)],
             'y--', lw=1, alpha=0.6)
ax2.scatter([0],[0], c='cyan', s=80, zorder=5, label='Ego')
ax2.set_xlim(-5,55); ax2.set_ylim(-25,25)
ax2.set_title("BEV + Camera FOV", fontsize=10)
ax2.legend(fontsize=8)

plt.suptitle('Week 9 — Camera-LiDAR Fusion', fontsize=11, fontweight='bold')
plt.tight_layout()
plt.savefig('/tmp/week09.png', dpi=90, bbox_inches='tight')
print("\nPlot saved!")
