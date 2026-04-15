# Week 11 — Capstone: End-to-End 3D Perception
# Goal: Integrate all modules, evaluate on Waymo-like synthetic data
# -----------------------------------------------------------------------
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

np.random.seed(11)
print("Week 11 — Capstone: End-to-End 3D Detector")

# ── Pipeline: BEV features → Detection Head → NMS ───────────────────────

def make_scene(n_vehicles=5):
    """Simulate a driving scene with ground truth."""
    vehicles = []
    for i in range(n_vehicles):
        angle = np.random.uniform(-0.5, 0.5)
        dist  = np.random.uniform(8, 45)
        cx = dist * np.cos(angle) + np.random.randn() * 0.5
        cy = dist * np.sin(angle) * 2 + np.random.randn() * 0.5
        vehicles.append({
            'cx': cx, 'cy': cy,
            'l': np.random.uniform(3.5, 5.0),
            'w': np.random.uniform(1.6, 2.2),
            'heading': angle + np.random.randn() * 0.1,
        })
    return vehicles

def extract_bev_features(vehicles, noise=0.3):
    """Simulate BEV feature extraction for each vehicle cluster."""
    feats = []
    for v in vehicles:
        feats.append([
            v['cx'] + np.random.randn() * noise,
            v['cy'] + np.random.randn() * noise,
            v['l']  + np.random.randn() * 0.2,
            v['w']  + np.random.randn() * 0.1,
        ])
    return np.array(feats)

def nms(boxes, scores, iou_thresh=0.4):
    """Non-Maximum Suppression."""
    order = scores.argsort()[::-1]
    keep  = []
    while len(order) > 0:
        i = order[0]; keep.append(i)
        if len(order) == 1: break
        rest = order[1:]
        # Compute IoU between box i and rest
        cx1,cy1,l1,w1 = boxes[i]
        ious = []
        for j in rest:
            cx2,cy2,l2,w2 = boxes[j]
            # Simple overlap check (axis-aligned)
            x_overlap = max(0, min(cx1+l1/2,cx2+l2/2) - max(cx1-l1/2,cx2-l2/2))
            y_overlap = max(0, min(cy1+w1/2,cy2+w2/2) - max(cy1-w1/2,cy2-w2/2))
            inter = x_overlap * y_overlap
            union = l1*w1 + l2*w2 - inter
            ious.append(inter/(union+1e-6))
        ious = np.array(ious)
        order = rest[ious < iou_thresh]
    return keep

def compute_ap(ious, iou_thresh=0.5):
    """Simple AP from sorted IoU matches."""
    tp = (ious >= iou_thresh).astype(float)
    fp = 1 - tp
    tp_cum = np.cumsum(tp); fp_cum = np.cumsum(fp)
    precision = tp_cum / (tp_cum + fp_cum + 1e-6)
    recall    = tp_cum / (len(ious) + 1e-6)
    return np.trapz(precision, recall)

# ── Evaluate across multiple scenes ──────────────────────────────────────
all_ious = []; all_scores = []
n_scenes = 20

for scene_id in range(n_scenes):
    gt_vehicles = make_scene(np.random.randint(3, 8))
    pred_boxes  = extract_bev_features(gt_vehicles, noise=1.5)
    scores      = np.random.uniform(0.5, 0.99, len(pred_boxes))
    keep        = nms(pred_boxes, scores)
    pred_final  = pred_boxes[keep]; scores_final = scores[keep]

    # Match predictions to GT by proximity
    for pred in pred_final:
        best_iou = 0
        for gt in gt_vehicles:
            dx = pred[0] - gt['cx']; dy = pred[1] - gt['cy']
            dist = np.sqrt(dx**2 + dy**2)
            # Approximate IoU from distance
            iou_approx = max(0, 1.0 - dist/3.0) * 0.9
            best_iou = max(best_iou, iou_approx)
        all_ious.append(best_iou)
        all_scores.append(scores_final[0] if len(scores_final) else 0)

all_ious   = np.array(all_ious)
all_scores = np.array(all_scores)

# mAP calculation
thresholds = [0.3, 0.5, 0.7]
for t in thresholds:
    ap = (all_ious >= t).mean()
    print(f"  AP@{t:.1f} (proxy): {ap:.3f}")

map_50 = (all_ious >= 0.5).mean()
print(f"\n  Proxy mAP@0.5: {map_50:.3f}")
print(f"  Total detections evaluated: {len(all_ious)}")

# ── Visualize a final scene ───────────────────────────────────────────────
scene = make_scene(6)
preds = extract_bev_features(scene, noise=1.0)
scores_viz = np.random.uniform(0.6, 0.98, len(preds))
keep = nms(preds, scores_viz)

fig, axes = plt.subplots(1, 2, figsize=(13, 5))
ax1, ax2 = axes

# Scene visualization
ax1.set_facecolor('#1a1a2e')
ax1.scatter([0],[0], c='cyan', s=80, zorder=5, label='Ego')
# GT boxes (green)
for v in scene:
    rect = plt.Rectangle((v['cx']-v['l']/2, v['cy']-v['w']/2),
                          v['l'], v['w'], fill=False,
                          edgecolor='#66bb6a', lw=2, label='GT')
    ax1.add_patch(rect)
# Predictions (red)
for i, p in enumerate(preds[keep]):
    rect = plt.Rectangle((p[0]-p[2]/2, p[1]-p[3]/2),
                          p[2], p[3], fill=False,
                          edgecolor='#ef5350', lw=1.5,
                          linestyle='--', label='Pred')
    ax1.add_patch(rect)
    ax1.text(p[0], p[1], f'{scores_viz[keep[i]]:.2f}',
             color='#ef5350', fontsize=7, ha='center')
# Legend (avoid duplicates)
handles = [
    plt.Line2D([0],[0], color='#66bb6a', lw=2, label='GT'),
    plt.Line2D([0],[0], color='#ef5350', lw=2, ls='--', label='Pred'),
    plt.scatter([],[],c='cyan',s=60),
]
ax1.legend(handles=handles, labels=['GT box','Pred box','Ego'], fontsize=8)
ax1.set_xlim(-5, 55); ax1.set_ylim(-20, 20)
ax1.set_title('Scene: GT vs Predictions', fontsize=10)
ax1.set_xlabel('X (m)'); ax1.set_ylabel('Y (m)')

# mAP curve
ax2.hist(all_ious, bins=25, color='#42a5f5', edgecolor='white', alpha=0.8)
for t in thresholds:
    ax2.axvline(t, ls='--', lw=1.5, label=f'@{t} ({(all_ious>=t).mean():.2f})')
ax2.set_title(f'IoU Distribution (proxy mAP@0.5={map_50:.2f})', fontsize=10)
ax2.set_xlabel('IoU score'); ax2.set_ylabel('Count'); ax2.legend(fontsize=8)

plt.suptitle('Week 11 — Capstone: End-to-End 3D Perception Pipeline', fontsize=11, fontweight='bold')
plt.tight_layout()
plt.savefig('/tmp/week11.png', dpi=90, bbox_inches='tight')
print("Plot saved!")
