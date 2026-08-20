# 01 — Tune: thread-count sweep

Model `gemma-4-E2B-it-UD-Q4_K_XL.gguf` · Windows-AMD64 · llama.cpp `b10488` · Vulkan `ngl=99`
CPU: **4 physical / 8 logical cores** · metric `tg128` · one repetition per point.

| threads (`-t`) | tg128 (tok/s) | vs best |
|--:|--:|--:|
| 1 | 5.09 | 100% |
| 2 | 4.19 | 82% |
| 4 | 1.76 | 35% |
| 8 | 3.84 | 75% |
| 16 | 2.19 | 43% |

**Best:** `-t 1` at 5.09 tok/s. **Physical-core default:** `-t 4` at 1.76 tok/s. Thay đổi này cho speedup **2.89×**. Khoảng biến thiên best/worst là **2.89×**.

## Giải thích

Đường cong không đạt đỉnh ở 4 physical cores như kỳ vọng CPU-only vì phần lớn layer đã offload sang Intel UHD 620 qua Vulkan. Decode của model 4.65B trên iGPU dùng RAM chia sẻ; thêm CPU threads tạo thêm scheduling, synchronization và tranh chấp memory bandwidth mà không bổ sung execution units cho GPU. Điểm `-t 8` hồi phục nhưng vẫn thấp hơn `-t 1`, cho thấy curve có noise/non-monotonicity; vì chỉ chạy một repetition, kết luận nên là “`-t 1` là ứng viên tốt nhất trong run này”, không phải chân lý tuyệt đối.

Với run hiện tại, cấu hình được chọn là `LAB_N_THREADS=1`. Nếu dùng cho production,
nên chạy lại ít nhất 3 repetitions trong cùng power mode để giảm ảnh hưởng của noise.
