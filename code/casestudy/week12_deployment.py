# Week 12 — Optimization & Deployment
# Goal: Post-Training Quantization (PTQ) demo + inference speed analysis
# -----------------------------------------------------------------------
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import time

np.random.seed(12)
print("Week 12 — Model Quantization (PTQ) & Deployment")

# ── Post-Training Quantization: FP32 → INT8 ─────────────────────────────
def quantize_tensor(tensor, n_bits=8):
    """Symmetric min-max quantization."""
    alpha = np.abs(tensor).max()
    n_levels = 2**(n_bits-1) - 1
    scale = alpha / n_levels
    q = np.clip(np.round(tensor / scale), -n_levels, n_levels)
    return q.astype(np.int8 if n_bits==8 else np.int16), scale

def dequantize(q_tensor, scale):
    return q_tensor.astype(np.float32) * scale

def quantization_error(original, n_bits=8):
    q, scale = quantize_tensor(original, n_bits)
    restored = dequantize(q, scale)
    mse  = ((original - restored)**2).mean()
    psnr = 20 * np.log10(np.abs(original).max() / (np.sqrt(mse) + 1e-12))
    return mse, psnr, restored

# Simulate a layer's weight matrix
W_fp32 = np.random.randn(64, 64).astype(np.float32)  # typical conv weight

print("\nQuantization Analysis:")
for bits in [4, 6, 8, 16]:
    mse, psnr, _ = quantization_error(W_fp32, bits)
    size_ratio = bits / 32
    print(f"  INT{bits:2d}: MSE={mse:.6f}  PSNR={psnr:.1f} dB  "
          f"Size={size_ratio:.2f}x  Memory: {W_fp32.nbytes*size_ratio/1024:.1f} KB")

# ── Inference latency simulation ─────────────────────────────────────────
def simulate_inference(batch_size, model_size_M, quantized=False):
    """Simulate inference time (simplified model)."""
    base_ms_per_M = 0.8 if not quantized else 0.3
    # Larger batches are more efficient (GPU parallelism)
    batch_efficiency = np.log2(batch_size + 1) / np.log2(17)
    latency = model_size_M * base_ms_per_M / batch_efficiency
    latency += np.random.randn() * latency * 0.05  # noise
    return max(1.0, latency)

configs = [
    ('PyTorch FP32',  25, False, '#6b7280'),
    ('PyTorch FP16',  25, False, '#93c5fd'),
    ('ONNX FP32',     25, False, '#86efac'),
    ('ONNX INT8',     25, True,  '#fbbf24'),
    ('TensorRT FP16', 25, False, '#f87171'),
    ('TensorRT INT8', 25, True,  '#34d399'),
]

print("\nInference Latency (simulated, batch=1):")
latencies = {}
for name, size, quant, _ in configs:
    ms = simulate_inference(1, size, quant)
    latencies[name] = ms
    fps = 1000 / ms
    print(f"  {name:20s}: {ms:5.1f} ms ({fps:5.1f} FPS)")

# ── Memory footprint ──────────────────────────────────────────────────────
model_params = 25_000_000  # 25M parameters
print("\nMemory Footprint (25M parameter model):")
for dtype, bits, name in [(np.float32,32,'FP32'),(np.float16,16,'FP16'),(np.int8,8,'INT8'),(np.int8,4,'INT4')]:
    mb = model_params * bits / 8 / 1024**2
    print(f"  {name}: {mb:.0f} MB")

# ── Visualize ─────────────────────────────────────────────────────────────
fig, axes = plt.subplots(2, 2, figsize=(12, 8))

# Quantization error vs bits
bit_widths = range(2, 17)
mse_list, psnr_list = [], []
for b in bit_widths:
    m, p, _ = quantization_error(W_fp32, b)
    mse_list.append(m); psnr_list.append(p)

axes[0,0].semilogy(bit_widths, mse_list, 'b-o', ms=4)
axes[0,0].axvline(8, color='red', ls='--', lw=1.5, label='INT8')
axes[0,0].set_title('Quantization MSE vs Bit Width', fontsize=10)
axes[0,0].set_xlabel('Bits'); axes[0,0].set_ylabel('MSE (log scale)')
axes[0,0].legend(); axes[0,0].grid(True, alpha=0.3)

axes[0,1].plot(bit_widths, psnr_list, 'g-o', ms=4)
axes[0,1].axvline(8, color='red', ls='--', lw=1.5, label='INT8')
axes[0,1].axhline(40, color='orange', ls=':', lw=1, label='40dB threshold')
axes[0,1].set_title('PSNR vs Bit Width', fontsize=10)
axes[0,1].set_xlabel('Bits'); axes[0,1].set_ylabel('PSNR (dB)')
axes[0,1].legend(); axes[0,1].grid(True, alpha=0.3)

# Weight distribution FP32 vs INT8
q8, s8 = quantize_tensor(W_fp32, 8)
W_restored = dequantize(q8, s8)
axes[1,0].hist(W_fp32.flatten(),   bins=60, alpha=0.6, color='steelblue', label='FP32', density=True)
axes[1,0].hist(W_restored.flatten(),bins=60, alpha=0.5, color='tomato',    label='INT8 restored', density=True)
axes[1,0].set_title('Weight Distribution: FP32 vs INT8', fontsize=10)
axes[1,0].legend(); axes[1,0].set_xlabel('Weight value')

# Latency comparison
names  = [n for n,*_ in configs]
lats   = [latencies[n] for n in names]
colors = [c for _,_,_,c in configs]
bars = axes[1,1].barh(names, lats, color=colors, height=0.6)
for bar, lat in zip(bars, lats):
    axes[1,1].text(lat+0.3, bar.get_y()+bar.get_height()/2,
                   f'{lat:.1f} ms', va='center', fontsize=8)
axes[1,1].set_title('Inference Latency (simulated, batch=1)', fontsize=10)
axes[1,1].set_xlabel('Latency (ms)'); axes[1,1].set_xlim(0, max(lats)*1.3)

plt.suptitle('Week 12 — Quantization (PTQ) & Inference Optimization', fontsize=11, fontweight='bold')
plt.tight_layout()
plt.savefig('/tmp/week12.png', dpi=90, bbox_inches='tight')
print("\nPlot saved!")
