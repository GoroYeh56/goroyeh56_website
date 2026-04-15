# Week 8 — Model Training Pipeline
# Goal: Build complete training loop with IoU Loss on small synthetic dataset
# -----------------------------------------------------------------------
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

np.random.seed(8)

# ── IoU Loss (for bounding box regression) ──────────────────────────────
def compute_iou(pred, gt):
    """pred, gt: [x1, y1, x2, y2] format."""
    xi1 = np.maximum(pred[:,0], gt[:,0]); yi1 = np.maximum(pred[:,1], gt[:,1])
    xi2 = np.minimum(pred[:,2], gt[:,2]); yi2 = np.minimum(pred[:,3], gt[:,3])
    inter = np.maximum(0, xi2-xi1) * np.maximum(0, yi2-yi1)
    area_p = (pred[:,2]-pred[:,0]) * (pred[:,3]-pred[:,1])
    area_g = (gt[:,2]-gt[:,0])   * (gt[:,3]-gt[:,1])
    union = area_p + area_g - inter
    return inter / (union + 1e-6)

def iou_loss(pred, gt):
    return 1.0 - compute_iou(pred, gt).mean()

# ── Synthetic detection data ─────────────────────────────────────────────
# Each sample: 4 BEV features → predict 1 bounding box [cx, cy, w, h]
N = 200
# Features: [dist, angle, height, intensity]
X = np.random.randn(N, 4).astype(float)
X[:, 0] = np.abs(X[:, 0]) * 10 + 5   # distance 5-35m

# Ground truth boxes (simple linear relationship + noise)
gt_cx = X[:,0] * np.cos(X[:,1]*0.3) + np.random.randn(N)*0.5
gt_cy = X[:,0] * np.sin(X[:,1]*0.3) + np.random.randn(N)*0.5
gt_w  = np.clip(2.0 + X[:,2]*0.3 + np.random.randn(N)*0.2, 1.0, 5.0)
gt_h  = np.clip(1.5 + X[:,3]*0.1 + np.random.randn(N)*0.2, 0.8, 4.0)
Y_gt  = np.column_stack([gt_cx, gt_cy, gt_w, gt_h])  # (N, 4)

# ── Simple regression MLP ─────────────────────────────────────────────────
class DetectionHead:
    def __init__(self):
        self.W1 = np.random.randn(32, 4) * 0.1
        self.b1 = np.zeros(32)
        self.W2 = np.random.randn(16, 32) * 0.1
        self.b2 = np.zeros(16)
        self.W3 = np.random.randn(4, 16) * 0.1
        self.b3 = np.zeros(4)

    def forward(self, x):
        h1 = np.maximum(0, x @ self.W1.T + self.b1)
        h2 = np.maximum(0, h1 @ self.W2.T + self.b2)
        return h2 @ self.W3.T + self.b3

    def params(self):
        return [(self.W1,self.b1),(self.W2,self.b2),(self.W3,self.b3)]

def mse_loss(pred, gt): return ((pred - gt)**2).mean()

# Numerical gradient (finite differences)
def numerical_grad(model, X, Y, eps=1e-4):
    loss0 = mse_loss(model.forward(X), Y)
    grads = {}
    for name, (W, b) in [('W1',(model.W1,None)),('W2',(model.W2,None))]:
        grad_W = np.zeros_like(W)
        for i in range(min(3, W.shape[0])):    # only first 3 rows for speed
            for j in range(min(3, W.shape[1])):
                W[i,j] += eps
                loss_p = mse_loss(model.forward(X[:20]), Y[:20])
                W[i,j] -= eps
                grad_W[i,j] = (loss_p - loss0) / eps
        grads[name] = grad_W
    return grads

# ── Training loop (SGD on MSE loss) ─────────────────────────────────────
model = DetectionHead()
lr = 0.005
batch_size = 32
n_epochs = 80
losses_train, losses_val = [], []

# Train/val split
split = int(N * 0.8)
X_tr, Y_tr = X[:split], Y_gt[:split]
X_val, Y_val = X[split:], Y_gt[split:]

for epoch in range(n_epochs):
    # Shuffle
    idx = np.random.permutation(len(X_tr))
    epoch_loss = 0
    for start in range(0, len(X_tr), batch_size):
        batch_idx = idx[start:start+batch_size]
        xb, yb = X_tr[batch_idx], Y_tr[batch_idx]
        pred = model.forward(xb)
        loss = mse_loss(pred, yb)
        epoch_loss += loss

        # Backprop (simplified analytical gradient for MSE)
        dL = 2 * (pred - yb) / len(xb)
        # Layer 3 gradient
        h1 = np.maximum(0, xb @ model.W1.T + model.b1)
        h2 = np.maximum(0, h1 @ model.W2.T + model.b2)
        model.W3 -= lr * dL.T @ h2
        model.b3 -= lr * dL.sum(axis=0)
        # Layer 2
        dh2 = dL @ model.W3 * (h2 > 0)
        model.W2 -= lr * dh2.T @ h1
        model.b2 -= lr * dh2.sum(axis=0)
        # Layer 1
        dh1 = dh2 @ model.W2 * (h1 > 0)
        model.W1 -= lr * dh1.T @ xb
        model.b1 -= lr * dh1.sum(axis=0)

    val_pred = model.forward(X_val)
    val_loss = mse_loss(val_pred, Y_val)
    losses_train.append(epoch_loss / (len(X_tr) / batch_size))
    losses_val.append(val_loss)

    if epoch % 20 == 0:
        print(f"Epoch {epoch:3d} | Train Loss: {losses_train[-1]:.4f} | Val Loss: {val_loss:.4f}")

# ── IoU evaluation ───────────────────────────────────────────────────────
final_pred = model.forward(X_val)
# Convert cx,cy,w,h → x1,y1,x2,y2
def to_xyxy(boxes):
    cx,cy,w,h = boxes[:,0],boxes[:,1],boxes[:,2],boxes[:,3]
    return np.column_stack([cx-w/2, cy-h/2, cx+w/2, cy+h/2])

iou_scores = compute_iou(to_xyxy(np.clip(final_pred, 0, 100)),
                         to_xyxy(np.clip(Y_val, 0, 100)))
print(f"\nValidation IoU — mean: {iou_scores.mean():.3f}  median: {np.median(iou_scores):.3f}")

# ── Visualize ─────────────────────────────────────────────────────────────
fig, axes = plt.subplots(1, 3, figsize=(13, 4))

axes[0].plot(losses_train, label='Train', color='#42a5f5')
axes[0].plot(losses_val,   label='Val',   color='#ef5350')
axes[0].set_title('Training Curve (MSE Loss)', fontsize=10)
axes[0].set_xlabel('Epoch'); axes[0].legend(); axes[0].grid(True, alpha=0.3)

axes[1].scatter(Y_val[:,0], final_pred[:,0], alpha=0.5, s=20, color='#66bb6a')
lim = [Y_val[:,0].min()-1, Y_val[:,0].max()+1]
axes[1].plot(lim, lim, 'r--', lw=1); axes[1].set_title('GT vs Pred cx', fontsize=10)
axes[1].set_xlabel('GT cx (m)'); axes[1].set_ylabel('Pred cx (m)')

axes[2].hist(iou_scores, bins=20, color='#ffa726', edgecolor='white', alpha=0.8)
axes[2].axvline(iou_scores.mean(), color='red', lw=2, ls='--', label=f'Mean={iou_scores.mean():.2f}')
axes[2].set_title('IoU Score Distribution', fontsize=10)
axes[2].set_xlabel('IoU'); axes[2].legend()

plt.suptitle('Week 8 — Detection Training Pipeline with IoU Loss', fontsize=11, fontweight='bold')
plt.tight_layout()
plt.savefig('/tmp/week08.png', dpi=90, bbox_inches='tight')
print("Plot saved!")
