# 01 — Latency baseline

Model `Gemma 4 E2B` · host `Windows-AMD64` · llama.cpp `b10488` (Vulkan)
Settings: `threads=4`, `ngl=99`, `ctx=2048`, `max_tokens=64`; warm-up discarded; 10/10 requests completed per quantization.

| Quantization | Size (GB) | Load (ms) | TTFT P50/P95 (ms) | TPOT P50/P95 (ms) | E2E P50/P95/P99 (ms) | Decode (tok/s) |
|:--|--:|--:|--:|--:|--:|--:|
| UD-Q4_K_XL | 2.97 | 86,565 | 7,209 / 32,294 | 400.6 / 890.8 | 37,026 / 70,981 / 70,981 | 2.5 |
| UD-Q2_K_XL | 2.24 | 94,380 | 9,156 / 58,574 | 3,468.0 / 4,307.7 | 218,224 / 329,959 / 329,959 | 0.3 |

TTFT và TPOT được báo riêng: TTFT phản ánh prefill; TPOT phản ánh chi phí mỗi token decode. `decode tok/s = 1000 / TPOT P50`.

## Nhận xét cá nhân

Q2 nhỏ hơn 0.73 GB nhưng decode chậm hơn khoảng **8.33×** và E2E P50 cao hơn **5.89×**. Với cùng prompt về goodput@SLO, Q4 trả lời đúng trọng tâm SLO; Q2 diễn giải sai sang hiệu quả quy trình triển khai phần mềm. Vì vậy Q2 **không đáng dùng trên máy này**: tiết kiệm 24.6% dung lượng nhưng thua cả tốc độ lẫn độ hữu ích. Cơ chế hợp lý là iGPU cũ bị giới hạn compute/dequantization; giảm số bit không tự động thắng khi memory bandwidth không phải nút thắt duy nhất.
