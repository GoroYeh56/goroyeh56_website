# Week 10 — Temporal Modeling
# Goal: Use previous frame info to handle object occlusion
# -----------------------------------------------------------------------
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch

np.random.seed(10)

print("Week 10 — Temporal Modeling & Kalman Filter Tracking")

# ── Kalman Filter for 2D object tracking ────────────────────────────────
class KalmanTracker:
    """
    State: [x, y, vx, vy]  (position + velocity in BEV)
    Observation: [x, y]    (measured position)
    """
    def __init__(self, x0, y0):
        dt = 0.1  # 10 Hz
        self.x = np.array([x0, y0, 0.0, 0.0])  # initial state
        # State transition: x(t+1) = F @ x(t)
        self.F = np.array([[1,0,dt,0],
                           [0,1,0,dt],
                           [0,0,1, 0],
                           [0,0,0, 1]])
        self.H = np.array([[1,0,0,0],
                           [0,1,0,0]])       # observation model
        self.P = np.eye(4) * 10.0            # initial covariance
        self.Q = np.diag([0.1,0.1,1.0,1.0]) # process noise
        self.R = np.diag([0.5,0.5])          # measurement noise
        self.history = [self.x.copy()]
        self.missed = 0

    def predict(self):
        self.x = self.F @ self.x
        self.P = self.F @ self.P @ self.F.T + self.Q
        return self.x[:2]

    def update(self, z=None):
        if z is None:  # occlusion: use prediction only
            self.missed += 1
            self.history.append(self.x.copy())
            return self.x[:2]
        z = np.array(z)
        S = self.H @ self.P @ self.H.T + self.R
        K = self.P @ self.H.T @ np.linalg.inv(S)
        self.x = self.x + K @ (z - self.H @ self.x)
        self.P = (np.eye(4) - K @ self.H) @ self.P
        self.history.append(self.x.copy())
        self.missed = 0
        return self.x[:2]

# ── Simulate a vehicle trajectory with occlusion ─────────────────────────
T = 40  # 40 frames = 4 seconds at 10Hz
t = np.arange(T)

# True trajectory: vehicle moves forward + slight curve
true_x = 5 + t * 0.8
true_y = 2 + np.sin(t * 0.15) * 3

# Noisy measurements (with occlusion from frame 15-25)
noise = np.random.randn(T, 2) * 0.5
measurements = np.column_stack([true_x, true_y]) + noise
OCCLUDED_FRAMES = set(range(15, 25))

tracker = KalmanTracker(measurements[0,0], measurements[0,1])
tracked = [tracker.x[:2].copy()]
predicted = [tracker.predict().copy()]

print(f"\nSimulating {T} frames with occlusion at frames 15-24:")
for frame in range(1, T):
    pred = tracker.predict()
    if frame in OCCLUDED_FRAMES:
        est = tracker.update(z=None)  # no measurement available!
        if frame == 15: print(f"  Frame {frame}: OCCLUSION START — using prediction only")
        if frame == 24: print(f"  Frame {frame}: OCCLUSION END")
    else:
        est = tracker.update(measurements[frame])
    tracked.append(est.copy())

tracked = np.array(tracked)
history = np.array(tracker.history)

# ── Velocity estimation from temporal features ───────────────────────────
velocities = np.diff(history[:, :2], axis=0) / 0.1   # m/s
speeds = np.linalg.norm(velocities, axis=1)
print(f"\nEstimated mean speed: {speeds.mean():.2f} m/s  ({speeds.mean()*3.6:.1f} km/h)")
print(f"True mean speed: {np.sqrt(0.8**2 + np.diff(true_y).mean()**2):.2f} m/s")
print(f"Missed frames: {tracker.missed} (during occlusion, velocity helped predict!)")

# ── Visualize ─────────────────────────────────────────────────────────────
fig, axes = plt.subplots(1, 3, figsize=(14, 5))

ax1 = axes[0]
ax1.plot(true_x, true_y, 'g-', lw=2.5, label='True trajectory', zorder=3)
ax1.scatter(measurements[:,0], measurements[:,1],
            c='steelblue', s=15, alpha=0.4, label='Noisy measurements')
# Occluded region
occ_frames = sorted(OCCLUDED_FRAMES)
ax1.scatter(measurements[occ_frames,0], measurements[occ_frames,1],
            c='gray', s=15, alpha=0.2, label='Occluded (no meas.)')
ax1.plot(tracked[:,0], tracked[:,1], 'r-', lw=2, label='KF estimate', zorder=4)
# Mark occlusion period
occ_mask = [f in OCCLUDED_FRAMES for f in range(T)]
ax1.scatter(tracked[occ_mask,0], tracked[occ_mask,1],
            c='orange', s=30, zorder=5, label='KF during occlusion')
ax1.set_title('Kalman Filter Tracking\nwith Occlusion Handling', fontsize=10)
ax1.set_xlabel('X (m)'); ax1.set_ylabel('Y (m)')
ax1.legend(fontsize=7); ax1.grid(True, alpha=0.3)

ax2 = axes[1]
frame_axis = range(T)
ax2.plot(true_x, 'g-', lw=2, label='True X')
ax2.plot(tracked[:,0], 'r-', lw=1.5, label='KF X')
ax2.plot(measurements[:,0], 'b.', ms=4, alpha=0.5, label='Measured X')
for f in OCCLUDED_FRAMES:
    ax2.axvspan(f-0.5, f+0.5, alpha=0.08, color='orange')
ax2.axvspan(min(OCCLUDED_FRAMES)-0.5, max(OCCLUDED_FRAMES)+0.5,
            alpha=0.15, color='orange', label='Occlusion')
ax2.set_title('X Position over Time', fontsize=10)
ax2.set_xlabel('Frame'); ax2.set_ylabel('X (m)')
ax2.legend(fontsize=7); ax2.grid(True, alpha=0.3)

ax3 = axes[2]
ax3.plot(speeds, color='#7e57c2', lw=2)
for f in OCCLUDED_FRAMES:
    if f < len(speeds):
        ax3.axvspan(f-0.5, f+0.5, alpha=0.08, color='orange')
ax3.axvspan(min(OCCLUDED_FRAMES)-0.5, min(len(speeds)-1,max(OCCLUDED_FRAMES)+0.5),
            alpha=0.15, color='orange', label='Occlusion')
ax3.axhline(speeds[list(set(range(T))-OCCLUDED_FRAMES)].mean(),
            ls='--', color='gray', lw=1, label='Mean speed (visible)')
ax3.set_title('Estimated Speed (from KF velocity)', fontsize=10)
ax3.set_xlabel('Frame'); ax3.set_ylabel('Speed (m/s)')
ax3.legend(fontsize=7); ax3.grid(True, alpha=0.3)

plt.suptitle('Week 10 — Temporal Modeling: Tracking through Occlusion', fontsize=11, fontweight='bold')
plt.tight_layout()
plt.savefig('/tmp/week10.png', dpi=90, bbox_inches='tight')
print("Plot saved!")
