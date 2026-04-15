# Week 3 — Waymo Dataset Parsing
# Goal: Extract first frame image and point cloud from Waymo Open Dataset
# (This demo simulates the data structure since Waymo requires registration)
# -----------------------------------------------------------------------
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# ── Waymo Open Dataset structure overview ───────────────────────────────
print("Waymo Open Dataset Structure:")
print("=" * 45)
print("""
TFRecord file (one per segment, ~20s of driving)
└── Frame (repeated, ~10Hz)
    ├── context
    │   ├── name (segment ID)
    │   └── stats (weather, time_of_day, ...)
    ├── timestamp_micros
    ├── images (5 cameras)
    │   ├── FRONT, FRONT_LEFT, FRONT_RIGHT
    │   ├── SIDE_LEFT, SIDE_RIGHT
    │   └── Each: {image bytes, camera_name, pose, ...}
    ├── laser_labels (3D ground truth boxes)
    │   └── Each: {type, box{center_x,y,z, width,length,height,heading}}
    └── lasers (LiDAR point clouds)
        ├── TOP lidar (64-beam, primary)
        └── FRONT, SIDE_LEFT, SIDE_RIGHT, REAR lidars
""")

# ── Simulate a Waymo frame ───────────────────────────────────────────────
np.random.seed(3)

def simulate_waymo_frame():
    """Simulate a single Waymo frame with sensor data."""
    # Camera intrinsics (approximate Waymo FRONT camera)
    fx, fy = 2000, 2000  # focal length pixels
    cx, cy = 960, 640    # principal point
    K = np.array([[fx, 0, cx],
                  [0, fy, cy],
                  [0,  0,  1]])

    # Simulate LiDAR points (TOP lidar: ~120k points per frame)
    N = 2000  # reduced for demo
    r     = np.random.uniform(1, 70, N)       # range [1, 70m]
    theta = np.random.uniform(-np.pi, np.pi, N)  # azimuth
    phi   = np.random.uniform(-0.3, 0.1, N)   # elevation [-17°, +5°]

    x = r * np.cos(phi) * np.cos(theta)
    y = r * np.cos(phi) * np.sin(theta)
    z = r * np.sin(phi)
    intensity = np.random.uniform(0, 1, N)
    points = np.column_stack([x, y, z, intensity])

    # Ground truth 3D boxes (cars in front)
    boxes = [
        {'type': 'VEHICLE', 'cx': 20, 'cy':  3, 'cz': 1.0,
         'l': 4.5, 'w': 2.0, 'h': 1.6, 'heading': 0.1},
        {'type': 'VEHICLE', 'cx': 35, 'cy': -5, 'cz': 1.0,
         'l': 4.5, 'w': 2.0, 'h': 1.6, 'heading': -0.05},
        {'type': 'PEDESTRIAN', 'cx': 15, 'cy': 8, 'cz': 0.9,
         'l': 0.8, 'w': 0.6, 'h': 1.8, 'heading': 0.0},
    ]

    # Extrinsic: LiDAR to camera (approximate)
    T_lidar_to_cam = np.array([
        [ 0, -1,  0,  0.1],
        [ 0,  0, -1,  0.3],
        [ 1,  0,  0,  1.5],
        [ 0,  0,  0,  1.0],
    ])
    return points, boxes, K, T_lidar_to_cam

points, boxes, K, T_ext = simulate_waymo_frame()

# ── Project LiDAR points onto camera image ──────────────────────────────
def project_lidar_to_image(pts, K, T_ext, img_w=1920, img_h=1280):
    ones = np.ones((len(pts), 1))
    pts_h = np.hstack([pts[:, :3], ones])          # (N,4)
    pts_cam = (T_ext @ pts_h.T).T                  # (N,4)

    # Keep points in front of camera (z > 0)
    mask = pts_cam[:, 2] > 0.5
    pts_cam = pts_cam[mask]
    intens  = pts[mask, 3]

    # Project
    uvw = (K @ pts_cam[:, :3].T).T                 # (N,3)
    u = uvw[:, 0] / uvw[:, 2]
    v = uvw[:, 1] / uvw[:, 2]

    # Keep points inside image bounds
    in_bounds = (u >= 0) & (u < img_w) & (v >= 0) & (v < img_h)
    return u[in_bounds], v[in_bounds], intens[in_bounds], pts_cam[in_bounds, 2]

u, v, intens, depth = project_lidar_to_image(points, K, T_ext)
print(f"Simulated frame: {len(points):,} LiDAR points")
print(f"  → {len(u):,} projected onto camera image")
print(f"\nGround truth boxes ({len(boxes)}):")
for b in boxes:
    print(f"  {b['type']:12s} at ({b['cx']:5.1f}, {b['cy']:5.1f}, {b['cz']:4.1f})m  "
          f"size={b['l']}x{b['w']}x{b['h']}m")

# ── Visualize ────────────────────────────────────────────────────────────
fig, axes = plt.subplots(1, 2, figsize=(13, 5))

# BEV with GT boxes
ax1 = axes[0]
fore = points[points[:, 0] > 0]
sc = ax1.scatter(fore[::3, 0], fore[::3, 1],
                 c=fore[::3, 2], cmap='RdYlGn_r',
                 s=1, alpha=0.5, vmin=-3, vmax=3)
plt.colorbar(sc, ax=ax1, label='Height z (m)')
COLORS = {'VEHICLE': '#ef5350', 'PEDESTRIAN': '#ffa726'}
for b in boxes:
    heading = b['heading']
    cos_h, sin_h = np.cos(heading), np.sin(heading)
    l, w = b['l']/2, b['w']/2
    corners_local = np.array([[ l, w],[ l,-w],[-l,-w],[-l, w]])
    cx, cy = b['cx'], b['cy']
    corners = np.array([[cos_h*dx - sin_h*dy + cx,
                          sin_h*dx + cos_h*dy + cy]
                         for dx, dy in corners_local])
    corners = np.vstack([corners, corners[0]])
    ax1.plot(corners[:,0], corners[:,1], '-', lw=2,
             color=COLORS[b['type']], label=b['type'])
    ax1.text(b['cx'], b['cy'], b['type'][0], ha='center', va='center',
             fontsize=7, fontweight='bold', color=COLORS[b['type']])
ax1.set_xlim(-5, 60); ax1.set_ylim(-20, 20)
ax1.set_xlabel('X forward (m)'); ax1.set_ylabel('Y lateral (m)')
ax1.set_title('BEV — LiDAR + GT 3D Boxes', fontsize=10)
handles = [plt.Line2D([0],[0],color=c,lw=2,label=t) for t,c in COLORS.items()]
ax1.legend(handles=handles, fontsize=8)

# Camera projection
ax2 = axes[1]
ax2.set_facecolor('#1a1a2e')
sc2 = ax2.scatter(u, v, c=depth, cmap='plasma',
                  s=1.5, alpha=0.7, vmin=0, vmax=60)
plt.colorbar(sc2, ax=ax2, label='Depth (m)')
ax2.set_xlim(0, 1920); ax2.set_ylim(1280, 0)
ax2.set_title('LiDAR Points Projected on Camera', fontsize=10)
ax2.set_xlabel('u (px)'); ax2.set_ylabel('v (px)')

plt.suptitle('Week 3 — Waymo Dataset: Frame Parsing & Sensor Fusion', fontsize=11, fontweight='bold')
plt.tight_layout()
plt.savefig('/tmp/week03.png', dpi=90, bbox_inches='tight')
print("\nPlot saved!")
