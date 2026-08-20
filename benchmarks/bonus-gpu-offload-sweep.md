# Bonus - GPU offload sweep

Host `Windows-AMD64` · backend(s) `vulkan` ·
llama.cpp `b10488` · `threads=4` · metric `tg16`

| -ngl | tg16 (tok/s) | vs -ngl 0 | vs best |
|:--|--:|--:|--:|
| 0 | 6.4 | 1.00x | 100% |
| 32 | 3.4 | 0.53x | 53% |
| 99 | 3.7 | 0.57x | 57% |

Best: `-ngl 0` at 6.4 tok/s
-- 1.00x faster than CPU-only.

Where the curve flattens tells you the model ran out of layers to move. Where it
*peaks below* full offload tells you something did not fit and the accelerator
started paying to fetch weights it could not hold.

## Finding

Full offload không tốt nhất trên máy này. CPU-only `-ngl 0` đạt **6.4 tok/s**, cao
hơn partial offload `-ngl 32` (3.4 tok/s) và full offload `-ngl 99` (3.7 tok/s).
Đổi từ full Vulkan sang CPU-only tạo speedup **1.73×** (`6.4 / 3.7`). Intel UHD 620
là iGPU dùng chung RAM với CPU, không có matrix cores và vẫn trả chi phí Vulkan
scheduling/synchronization. Vì vậy offload không đem lại bandwidth độc lập đủ lớn để
bù overhead; partial offload còn chậm nhất do phải chia execution giữa hai backend.

Sweep dùng `tg16`, một repetition mỗi điểm, nên đây là finding cho short decode trên
máy này; production decision cần thêm repetitions và workload dài hơn.
