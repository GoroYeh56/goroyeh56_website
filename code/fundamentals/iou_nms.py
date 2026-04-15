"""
IoU, GIoU, and Non-Maximum Suppression (NMS)
=============================================
Foundational operations in object detection evaluation.
"""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

def iou(b1, b2):
    """b1, b2: [x1, y1, x2, y2]"""
    xi1 = max(b1[0],b2[0]); yi1 = max(b1[1],b2[1])
    xi2 = min(b1[2],b2[2]); yi2 = min(b1[3],b2[3])
    inter = max(0,xi2-xi1)*max(0,yi2-yi1)
    area1 = (b1[2]-b1[0])*(b1[3]-b1[1])
    area2 = (b2[2]-b2[0])*(b2[3]-b2[1])
    return inter / (area1 + area2 - inter + 1e-6)

def nms(boxes, scores, iou_thresh=0.45):
    """boxes: (N,4) [x1,y1,x2,y2], scores: (N,)"""
    order = scores.argsort()[::-1]
    keep = []
    while len(order):
        i = order[0]; keep.append(i)
        if len(order) == 1: break
        ious = np.array([iou(boxes[i], boxes[j]) for j in order[1:]])
        order = order[1:][ious < iou_thresh]
    return keep

# ── Demo ──────────────────────────────────────────────────────────────────
np.random.seed(5)
gt_box = np.array([2., 2., 6., 5.])

# Generate 8 overlapping predictions around the GT
pred_boxes = gt_box + np.random.randn(8, 4) * 0.8
pred_boxes[:, 2:] = np.maximum(pred_boxes[:, :2] + 1.0, pred_boxes[:, 2:])
pred_scores = np.random.uniform(0.4, 0.95, 8)

ious_raw = [iou(gt_box, b) for b in pred_boxes]
kept = nms(pred_boxes, pred_scores)

print("Raw predictions:")
for i, (b, s, iou_v) in enumerate(zip(pred_boxes, pred_scores, ious_raw)):
    kept_mark = " ✓ KEEP" if i in kept else ""
    print(f"  [{i}] score={s:.2f}  IoU={iou_v:.2f}{kept_mark}")

print(f"\nNMS kept {len(kept)}/{len(pred_boxes)} boxes @ IoU thresh=0.45")

# Visualize
fig, axes = plt.subplots(1, 2, figsize=(11, 4))
for ax, title, show_nms in [(axes[0],'All Predictions',False),(axes[1],'After NMS',True)]:
    ax.set_facecolor('#1a1a2e'); ax.set_xlim(0,9); ax.set_ylim(0,8)
    for i, (b, s) in enumerate(zip(pred_boxes, pred_scores)):
        if show_nms and i not in kept: continue
        color = '#ef5350' if i in kept else '#546e7a'
        rect = Rectangle((b[0],b[1]),b[2]-b[0],b[3]-b[1],fill=False,edgecolor=color,lw=1.5)
        ax.add_patch(rect); ax.text(b[0],b[3]+0.1,f'{s:.2f}',color=color,fontsize=7)
    rect_gt = Rectangle((gt_box[0],gt_box[1]),gt_box[2]-gt_box[0],gt_box[3]-gt_box[1],
                          fill=False,edgecolor='#66bb6a',lw=2.5,label='GT')
    ax.add_patch(rect_gt); ax.set_title(title,fontsize=10); ax.legend(fontsize=8)
plt.suptitle('Non-Maximum Suppression (NMS)', fontsize=11, fontweight='bold')
plt.tight_layout()
plt.savefig('/tmp/nms.png', dpi=90, bbox_inches='tight')
print("Plot saved!")
