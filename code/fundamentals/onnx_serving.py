"""
ONNX Export & Inference Optimization
======================================
Demonstrates model export pipeline and quantization impact.
Simulates PTQ (Post-Training Quantization) without requiring
a full PyTorch installation.
"""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def quantize_weights(W, bits=8):
    alpha   = np.abs(W).max()
    levels  = 2**(bits-1) - 1
    scale   = alpha / levels
    q       = np.clip(np.round(W / scale), -levels, levels)
    W_back  = q * scale
    mse     = ((W - W_back)**2).mean()
    size_mb = W.nbytes * bits / 32 / 1024**2
    return W_back, mse, size_mb

np.random.seed(12)
W_fp32 = np.random.randn(256, 256).astype(np.float32)

print("Model Weight Quantization Analysis")
print("=" * 45)
print(f"{'Format':<12} {'MSE':>12} {'Size (MB)':>10} {'Speedup':>8}")
print("-" * 45)
base_size = W_fp32.nbytes / 1024**2
for bits in [32, 16, 8, 4]:
    if bits == 32:
        mse, size = 0.0, base_size
    else:
        _, mse, size = quantize_weights(W_fp32, bits)
    speedup = base_size / size
    print(f"{'FP32' if bits==32 else f'INT{bits}':<12} {mse:>12.8f} {size:>10.3f} {speedup:>8.1f}x")

# Simulated latency
configs  = ['PyTorch\nFP32','PyTorch\nFP16','ONNX\nFP32','ONNX\nINT8','TensorRT\nFP16','TensorRT\nINT8']
latency  = [45.2, 26.8, 18.4, 9.1, 11.2, 5.8]
colors   = ['#6b7280','#93c5fd','#86efac','#86efac','#f87171','#34d399']

fig, axes = plt.subplots(1, 2, figsize=(12, 4))
bars = axes[0].bar(configs, latency, color=colors, width=0.6, edgecolor='white')
for bar, val in zip(bars, latency):
    axes[0].text(bar.get_x()+bar.get_width()/2, val+0.5, f'{val}ms',
                 ha='center', fontsize=8)
axes[0].set_title('Inference Latency (simulated)', fontsize=10)
axes[0].set_ylabel('Latency (ms)')

bit_widths = range(2, 17)
mses = [quantize_weights(W_fp32, b)[1] if b<32 else 0 for b in bit_widths]
axes[1].semilogy(list(bit_widths), mses, 'b-o', ms=5)
axes[1].axvline(8, color='red', ls='--', lw=1.5, label='INT8')
axes[1].axhline(1e-4, color='orange', ls=':', lw=1, label='Acceptable MSE')
axes[1].set_title('Quantization MSE vs Bit Width', fontsize=10)
axes[1].set_xlabel('Bits'); axes[1].legend(fontsize=8); axes[1].grid(True, alpha=0.3)

plt.suptitle('ONNX Export & Quantization', fontsize=11, fontweight='bold')
plt.tight_layout()
plt.savefig('/tmp/quant.png', dpi=90, bbox_inches='tight')
print("\nPlot saved!")
