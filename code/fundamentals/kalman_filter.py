"""
Kalman Filter for Object Tracking
===================================
State: [x, y, vx, vy]  — position + velocity in BEV space.
Used in AV for tracking vehicles across frames.
"""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

np.random.seed(42)

class KalmanTracker2D:
    def __init__(self, x0, y0, dt=0.1):
        self.x = np.array([x0, y0, 0., 0.])
        self.F = np.array([[1,0,dt,0],[0,1,0,dt],[0,0,1,0],[0,0,0,1]])
        self.H = np.array([[1,0,0,0],[0,1,0,0]])
        self.P = np.eye(4) * 5.
        self.Q = np.diag([0.05, 0.05, 0.5, 0.5])
        self.R = np.diag([0.4, 0.4])

    def predict(self):
        self.x = self.F @ self.x
        self.P = self.F @ self.P @ self.F.T + self.Q
        return self.x[:2].copy()

    def update(self, z):
        z = np.array(z)
        S = self.H @ self.P @ self.H.T + self.R
        K = self.P @ self.H.T @ np.linalg.inv(S)
        self.x = self.x + K @ (z - self.H @ self.x)
        self.P = (np.eye(4) - K @ self.H) @ self.P
        return self.x[:2].copy()

# Simulate: vehicle drives forward + slight curve, occluded frames 12-20
T = 35
true_x = 2 + np.arange(T) * 0.7
true_y = 1 + np.sin(np.arange(T) * 0.18) * 2.5
meas   = np.column_stack([true_x, true_y]) + np.random.randn(T,2)*0.5
OCCLUDED = set(range(12, 21))

tracker = KalmanTracker2D(meas[0,0], meas[0,1])
tracked = []
for t in range(T):
    pred = tracker.predict()
    if t in OCCLUDED:
        tracked.append(pred)
    else:
        tracked.append(tracker.update(meas[t]))
tracked = np.array(tracked)

print(f"Tracked {T} frames, occluded frames: {min(OCCLUDED)}–{max(OCCLUDED)}")
pos_err = np.linalg.norm(tracked - np.column_stack([true_x,true_y]), axis=1)
print(f"Mean position error: {pos_err.mean():.3f} m")
print(f"Error during occlusion: {pos_err[list(OCCLUDED)].mean():.3f} m")

fig, ax = plt.subplots(figsize=(9, 5))
ax.plot(true_x, true_y, 'g-', lw=2.5, label='True path', zorder=4)
ax.scatter(meas[:,0], meas[:,1], c='steelblue', s=15, alpha=0.4, label='Measurements')
ax.plot(tracked[:,0], tracked[:,1], 'r-', lw=2, label='KF estimate', zorder=3)
occ = sorted(OCCLUDED)
ax.scatter(tracked[occ,0], tracked[occ,1], c='orange', s=35, zorder=5, label='During occlusion')
ax.axvspan(true_x[min(OCCLUDED)]-0.3, true_x[max(OCCLUDED)]+0.3,
           alpha=0.1, color='orange', label='Occluded region')
ax.set_title('Kalman Filter: 2D Object Tracking with Occlusion', fontsize=10)
ax.set_xlabel('X (m)'); ax.set_ylabel('Y (m)')
ax.legend(fontsize=8); ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('/tmp/kf2d.png', dpi=90, bbox_inches='tight')
print("Plot saved!")
