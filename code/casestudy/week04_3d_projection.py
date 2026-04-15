# Week 4 — Geometric 3D Projection
# Goal: Compute 3D bounding box vertices and project onto camera image
# -----------------------------------------------------------------------
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from itertools import combinations

# ── 1. 3D Bounding Box: 8 corners from (cx, cy, cz, l, w, h, heading) ──
def box3d_corners(cx, cy, cz, l, w, h, heading):
    """Return 8 corners of a 3D box in LiDAR frame.
    
    Convention (KITTI/Waymo):
      length l → X (forward)
      width  w → Y (lateral)
      height h → Z (up)
    """
    # 8 corners in local frame (box centered at origin)
    x = np.array([ l/2,  l/2, -l/2, -l/2,  l/2,  l/2, -l/2, -l/2])
    y = np.array([ w/2, -w/2, -w/2,  w/2,  w/2, -w/2, -w/2,  w/2])
    z = np.array([-h/2, -h/2, -h/2, -h/2,  h/2,  h/2,  h/2,  h/2])

    # Rotate by heading (yaw around Z)
    cos_h, sin_h = np.cos(heading), np.sin(heading)
    x_rot = cos_h * x - sin_h * y
    y_rot = sin_h * x + cos_h * y

    # Translate to world position
    return np.column_stack([x_rot + cx, y_rot + cy, z + cz])  # (8, 3)

# ── 2. Camera projection: P = K @ [R|t] ─────────────────────────────────
def project_to_image(pts_3d, K, R, t):
    """Project 3D points (N,3) into image using K, R, t."""
    pts_cam = (R @ pts_3d.T + t[:, None]).T  # (N, 3) in camera frame
    # Only keep points in front of camera
    valid = pts_cam[:, 2] > 0
    uvw = (K @ pts_cam[valid].T).T            # (N_valid, 3)
    u = uvw[:, 0] / uvw[:, 2]
    v = uvw[:, 1] / uvw[:, 2]
    return u, v, valid

# ── 3. Draw 3D box edges on image ───────────────────────────────────────
EDGES = [
    (0,1),(1,2),(2,3),(3,0),   # bottom face
    (4,5),(5,6),(6,7),(7,4),   # top face
    (0,4),(1,5),(2,6),(3,7),   # vertical edges
]

def draw_box3d(ax, corners_2d, color='lime', lw=1.5):
    """Draw 12 edges of 3D box on a 2D image axes."""
    for i, j in EDGES:
        ax.plot([corners_2d[i,0], corners_2d[j,0]],
                [corners_2d[i,1], corners_2d[j,1]],
                color=color, lw=lw, alpha=0.9)
    # Highlight front face (corners 0,1,5,4)
    front = [0, 1, 5, 4, 0]
    ax.plot([corners_2d[k,0] for k in front],
            [corners_2d[k,1] for k in front],
            color='yellow', lw=lw+0.5, alpha=0.95)

# ── 4. Camera calibration (approximate Waymo FRONT camera) ──────────────
fx, fy = 1900, 1900
cx, cy_px = 960, 640
K = np.array([[fx,  0, cx],
              [ 0, fy, cy_px],
              [ 0,  0,  1]], dtype=float)

# LiDAR → Camera extrinsic (rotation + translation)
R_ext = np.array([[ 0, -1,  0],
                  [ 0,  0, -1],
                  [ 1,  0,  0]], dtype=float)
t_ext = np.array([0.1, 0.8, 1.5])

# ── 5. Define a scene with multiple 3D boxes ─────────────────────────────
scene = [
    # (cx_lidar, cy, cz, l, w, h, heading, label, color)
    (18,  2.5, 1.0, 4.5, 2.0, 1.6,  0.05, 'Car',        '#ef5350'),
    (30, -3.0, 1.0, 4.5, 2.0, 1.6, -0.10, 'Car',        '#ef5350'),
    (12,  8.0, 0.9, 0.8, 0.6, 1.8,  0.00, 'Pedestrian', '#ffa726'),
    (22, -8.0, 0.6, 1.8, 0.8, 1.4,  0.20, 'Cyclist',    '#66bb6a'),
]

# ── 6. Visualize: BEV and camera projection ──────────────────────────────
fig, axes = plt.subplots(1, 2, figsize=(14, 6))
ax_bev = axes[0]
ax_cam = axes[1]

# Camera image background (fake road texture)
img_w, img_h = 1920, 1280
ax_cam.set_facecolor('#1c1c1e')
# Draw horizon line and lane markings
ax_cam.axhline(y=640, color='#555', lw=0.5, alpha=0.5)
for lane_x in [760, 960, 1160]:
    ax_cam.plot([lane_x]*2, [640, 1280], '--', color='#f5a623', lw=1, alpha=0.4)

# Simulated LiDAR point cloud (background scatter)
np.random.seed(4)
N = 1500
bev_pts = np.column_stack([
    np.random.uniform(0, 50, N),
    np.random.uniform(-15, 15, N),
    np.random.uniform(-2, 0.2, N),
])
ax_bev.scatter(bev_pts[:, 0], bev_pts[:, 1], c='#546e7a', s=1, alpha=0.3)

COLORS = {'Car': '#ef5350', 'Pedestrian': '#ffa726', 'Cyclist': '#66bb6a'}

for cx_l, cy_l, cz_l, l, w, h, heading, label, color in scene:
    # 3D corners in LiDAR frame
    corners_lidar = box3d_corners(cx_l, cy_l, cz_l, l, w, h, heading)

    # BEV: draw box footprint (bottom 4 corners)
    foot = corners_lidar[:4, :2]  # (4,2)
    foot_c = np.vstack([foot, foot[0]])
    ax_bev.plot(foot_c[:, 0], foot_c[:, 1], '-', color=color, lw=2)
    ax_bev.text(cx_l, cy_l, label[0], ha='center', va='center',
                fontsize=8, fontweight='bold', color=color)

    # Camera projection
    u_pts, v_pts, valid = project_to_image(corners_lidar, K, R_ext, t_ext)
    if valid.sum() >= 6:
        corners_2d = np.zeros((8, 2))
        corners_2d[valid] = np.column_stack([u_pts, v_pts])
        # Fill invalid (behind camera) with visible points
        if not valid.all():
            mean_u, mean_v = u_pts.mean(), v_pts.mean()
            corners_2d[~valid] = [mean_u, mean_v]
        draw_box3d(ax_cam, corners_2d, color=color, lw=2)
        ax_cam.text(corners_2d[4,0], corners_2d[4,1]-15, label,
                    color=color, fontsize=8, fontweight='bold')

# Axis formatting
ax_bev.set_xlim(-2, 55); ax_bev.set_ylim(-20, 20)
ax_bev.set_xlabel('X forward (m)'); ax_bev.set_ylabel('Y lateral (m)')
ax_bev.set_title("Bird's Eye View", fontsize=10)
ax_bev.set_facecolor('#1a1a2e')
ax_bev.scatter([0],[0], c='cyan', s=60, zorder=5, label='Ego vehicle')
ax_bev.legend(fontsize=8)

handles = [mpatches.Patch(color=c, label=l) for l,c in COLORS.items()]
ax_bev.legend(handles=handles + [plt.scatter([],[],c='cyan',s=60)],
              labels=list(COLORS.keys()) + ['Ego'], fontsize=8)

ax_cam.set_xlim(0, img_w); ax_cam.set_ylim(img_h, 0)
ax_cam.set_title('Camera View — 3D Box Projection', fontsize=10)
ax_cam.set_xlabel('u (px)'); ax_cam.set_ylabel('v (px)')

plt.suptitle('Week 4 — 3D Bounding Box Projection', fontsize=11, fontweight='bold')
plt.tight_layout()
plt.savefig('/tmp/week04.png', dpi=90, bbox_inches='tight')

print("3D Box corner computation:")
demo = box3d_corners(18, 2.5, 1.0, 4.5, 2.0, 1.6, 0.05)
print(f"  8 corners (x,y,z):\n{np.round(demo, 2)}")
print("\nPlot saved!")
