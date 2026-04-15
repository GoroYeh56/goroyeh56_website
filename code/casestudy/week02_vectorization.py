# Week 2 — Python for ML (Vectorization)
# Goal: Efficient point cloud ROI filtering with NumPy — no for-loops
# -----------------------------------------------------------------------
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import time

np.random.seed(0)

# ── 1. Simulate a large LiDAR scan (100k points) ────────────────────────
N = 100_000
# x: forward (-40m to 70m), y: lateral (-40m to 40m), z: height (-3m to 5m)
# intensity: 0-255
points = np.column_stack([
    np.random.uniform(-40, 70, N),
    np.random.uniform(-40, 40, N),
    np.random.uniform(-3,   5, N),
    np.random.uniform(  0, 255, N),
])
print(f"Total points: {N:,}")

# ── 2. ROI filter — FOR LOOP (slow) ─────────────────────────────────────
def roi_filter_loop(pts, x_range, y_range, z_range):
    result = []
    for p in pts:
        if (x_range[0] <= p[0] <= x_range[1] and
            y_range[0] <= p[1] <= y_range[1] and
            z_range[0] <= p[2] <= z_range[1]):
            result.append(p)
    return np.array(result)

# ── 3. ROI filter — VECTORIZED (fast) ───────────────────────────────────
def roi_filter_vec(pts, x_range, y_range, z_range):
    mask = (
        (pts[:, 0] >= x_range[0]) & (pts[:, 0] <= x_range[1]) &
        (pts[:, 1] >= y_range[0]) & (pts[:, 1] <= y_range[1]) &
        (pts[:, 2] >= z_range[0]) & (pts[:, 2] <= z_range[1])
    )
    return pts[mask]

ROI = dict(x_range=(0, 50), y_range=(-20, 20), z_range=(-2, 3))

# Benchmark on small subset for loop version
subset = points[:5_000]
t0 = time.perf_counter()
filtered_loop = roi_filter_loop(subset, **ROI)
t_loop = time.perf_counter() - t0

t0 = time.perf_counter()
filtered_loop_ref = roi_filter_vec(subset, **ROI)
t_vec_small = time.perf_counter() - t0

# Full 100k vectorized
t0 = time.perf_counter()
filtered_vec = roi_filter_vec(points, **ROI)
t_vec = time.perf_counter() - t0

print(f"\nROI filter results:")
print(f"  Loop  (5k pts):  {len(filtered_loop):,} pts kept  | {t_loop*1000:.1f} ms")
print(f"  Vec   (5k pts):  {len(filtered_loop_ref):,} pts kept  | {t_vec_small*1000:.2f} ms")
print(f"  Vec (100k pts):  {len(filtered_vec):,} pts kept  | {t_vec*1000:.2f} ms")
print(f"\n  Speedup (5k): {t_loop/max(t_vec_small, 1e-9):.0f}x faster with vectorization!")

# ── 4. Boolean masking demos ─────────────────────────────────────────────
# Remove ground plane (z < -1.5)
no_ground = filtered_vec[filtered_vec[:, 2] > -1.5]
# High intensity returns only
high_intensity = filtered_vec[filtered_vec[:, 3] > 200]
print(f"\n  After ground removal: {len(no_ground):,} pts")
print(f"  High-intensity only:  {len(high_intensity):,} pts")

# ── 5. Visualize ─────────────────────────────────────────────────────────
fig, axes = plt.subplots(1, 2, figsize=(12, 5))

# BEV of full scan vs ROI
ax = axes[0]
ax.scatter(points[::20, 0], points[::20, 1],
           c='#b0bec5', s=0.3, alpha=0.3, label='All points (20x downsample)')
ax.scatter(filtered_vec[::5, 0], filtered_vec[::5, 1],
           c='#ef5350', s=0.8, alpha=0.6, label='ROI points')
roi = plt.Rectangle((0, -20), 50, 40, fill=False, edgecolor='gold', lw=2)
ax.add_patch(roi)
ax.set_xlim(-40, 70); ax.set_ylim(-40, 40)
ax.set_xlabel('X (m)'); ax.set_ylabel('Y (m)')
ax.set_title('Bird\'s Eye View — ROI Filtering', fontsize=10)
ax.legend(fontsize=8, markerscale=5)

# Height distribution
ax2 = axes[1]
ax2.hist(filtered_vec[:, 2], bins=60, color='steelblue', alpha=0.7, label='All ROI pts')
ax2.hist(no_ground[:, 2],    bins=60, color='tomato',    alpha=0.7, label='No ground (z>-1.5)')
ax2.axvline(-1.5, color='black', lw=1.5, ls='--', label='Ground threshold')
ax2.set_xlabel('Height z (m)'); ax2.set_ylabel('Count')
ax2.set_title('Height Distribution', fontsize=10)
ax2.legend(fontsize=8)

plt.suptitle('Week 2 — Vectorized Point Cloud Filtering', fontsize=11, fontweight='bold')
plt.tight_layout()
plt.savefig('/tmp/week02.png', dpi=90, bbox_inches='tight')
print("\nPlot saved!")
