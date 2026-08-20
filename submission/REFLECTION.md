# Reflection — Day 20 Lab

**Họ tên:** Đào Chí Hiển

**MSSV:** 2A202601066

**Cohort:** A20-K3

**Ngày submit:** 2026-08-20

> Số liệu dưới đây là before/after trên cùng máy và được đối chiếu với các artifact
> JSON/CSV trong thư mục `benchmarks/`.

## 1. Hardware & runtime

- **OS:** Windows 10, AMD64; Python runtime dùng khi probe: 3.11.9.
- **CPU:** Intel Core i5-8265U @ 1.60 GHz.
- **Cores:** 4 physical / 8 logical.
- **CPU extensions:** backend llama.cpp chọn `ggml-cpu-haswell` (AVX2-class).
- **RAM:** 15.9 GB.
- **Accelerator:** Intel UHD Graphics 620 qua Vulkan, unified/shared memory.
- **llama.cpp:** `llama-b10488-bin-win-vulkan-x64.zip`, build `b10488`.
- **Model:** Gemma 4 E2B (`LAB_MODEL=gemma4-e2b`).
- **Quantization:** UD-Q4_K_XL primary + UD-Q2_K_XL compare.
- **Chạy ở đâu:** laptop cá nhân, local; không dùng Colab/Kaggle.

Setup ban đầu tải đủ hai GGUF nhưng Python gốc của `.venv` bị gỡ/di chuyển. Tôi cài
Python 3.11.15 portable, tái tạo `.venv`, cài lại requirements và chạy các target bằng
script chuẩn của lab. Do máy yếu không hoàn tất request trong 60 giây, hai run Locust
dùng 3 phút theo mục Troubleshooting của GUIDE, với output budget 8/12 tokens.

## 2. Đo lường

| Quantization | Size (GB) | Load (ms) | TTFT P50/P95 (ms) | TPOT P50/P95 (ms) | E2E P50/P95/P99 (ms) | Decode (tok/s) |
|---|---:|---:|---:|---:|---:|---:|
| UD-Q4_K_XL | 2.97 | 86,565 | 7,209 / 32,294 | 400.6 / 890.8 | 37,026 / 70,981 / 70,981 | 2.5 |
| UD-Q2_K_XL | 2.24 | 94,380 | 9,156 / 58,574 | 3,468.0 / 4,307.7 | 218,224 / 329,959 / 329,959 | 0.3 |

Q2 decode chậm hơn khoảng 8.33× dù nhỏ hơn 0.73 GB. Cùng prompt goodput@SLO, Q4 trả lời đúng về request đạt SLO; Q2 nhầm sang hiệu quả triển khai phần mềm. Trên iGPU compute-limited, overhead dequantization lấn át lợi ích giảm bytes, nên Q2 không đáng dùng ở đây.

## 3. Serving under load

| Users | RPS | P50 (ms) | P95 (ms) | P99 (ms) | Eff. concurrency | Failures |
|---:|---:|---:|---:|---:|---:|---:|
| 10 | 0.08 | 122,000 | 122,000 | 122,000 | 9.1 | 60% |
| 50 | 0.41 | 122,000 | 122,000 | 122,000 | 48.8 | 94% |

- **Offered users tăng:** 5×; total completion/timeout rate tăng 5×, nhưng successful
  goodput giảm **0.75×** (0.0325 → 0.0244 req/s).
- **P95:** **1.00×** vì cả hai run đều chạm timeout khoảng 122 giây.
- **Effective concurrency ở 50 users:** 48.8 so với `--parallel=4`; phần vượt slots là queue.
- **Peak `n_busy_slots_per_decode`:** 3.88/4; `requests_processing=4`, `requests_deferred=46`.

Server bão hòa từ 10 users: failure đã là 60%, lên 94% ở 50 users và deferred đạt
46. RPS Locust gồm cả timeout nên không phải goodput; goodput thành công thực tế giảm
25%. Queue time là nguyên nhân chính. Tôi sẽ cap admission concurrency gần 4 trước;
tăng slots trên UHD 620 có thể làm từng sequence chậm hơn do tranh chấp RAM.

## 4. Integration

| Day | Piece | Real hay stub? |
|---|---|---|
| N16 Cloud/IaC | Local Windows path | stub |
| N17 Data pipeline | Static toy documents | stub |
| N18 Lakehouse | In-memory document list | stub |
| N19 Vector + features | Keyword-overlap retrieval | stub |
| N20 Serving | `llama-server` OpenAI-compatible API | real |

Mean trên 3 query: embed **0.0 ms**, retrieve **8.2 ms**, LLM **38,835.0 ms**,
total **38,843.3 ms**. LLM chiếm xấp xỉ **100%** total. Bottleneck đúng như kỳ vọng
vì N16–N19 đều là stub nhẹ. Muốn giảm 2×, tôi ưu tiên `-t 1` đã chứng minh 2.89×
trên tg128 và giảm prompt/output; tối ưu retrieval 8.2 ms gần như vô nghĩa.

## 5. The single change that mattered most

**Change:** giảm decode threads từ physical-core default `-t 4` xuống `-t 1`, giữ nguyên model, `ngl=99` và workload tg128.

```text
before:  1.76 tok/s  (-t 4)
after:   5.09 tok/s  (-t 1)
speedup: 2.89×
```

Kết quả ngược trực giác CPU-only vì workload này offload sang Intel UHD 620. GPU tích hợp dùng RAM chung; thêm CPU threads không tăng execution units của GPU nhưng tăng scheduling/synchronization và cạnh tranh memory bandwidth. Vì vậy một thread host đủ feed GPU lại thắng bốn thread. Curve không đơn điệu (`-t 8` hồi lên 3.84 tok/s), cảnh báo rằng thermal state và noise có ảnh hưởng.

Finding hiện dựa trên một repetition mỗi điểm do Python venv hỏng và direct sweep rất
chậm. Đây là bằng chứng hợp lệ cho run lab, nhưng nếu dùng cho production cần chạy lại
ít nhất 3 repetitions trong cùng power mode để xác nhận độ ổn định.

## 6. Bonus

**Đã làm:** B2 GPU-offload sweep, B3 before/after từ sweep, B4 challenge C4 Best-of-N,
và B5/C8 semantic cache offline.

```text
before:  3.7 tok/s  (full Vulkan offload, -ngl 99)
after:   6.4 tok/s  (CPU-only, -ngl 0)
speedup: 1.73×
```

UHD 620 dùng RAM chung, không có matrix cores, nhưng offload vẫn phát sinh Vulkan
scheduling và synchronization. Do không có bandwidth VRAM độc lập để bù overhead,
CPU-only thắng; partial `-ngl 32` còn thấp nhất ở 3.4 tok/s vì chia execution giữa hai
backend. Kết quả trái heuristic “có GPU thì offload tối đa”, nhưng phù hợp với iGPU cũ.

C4 cho kết quả âm nhưng hữu ích: Best-of-4 tăng wall latency từ 30.9 lên 244.7 giây
(7.92×) mà score không tăng (4.0 → 4.0), do bốn slots tranh chấp bandwidth và output
24 token bị cắt trước khi đủ hai câu. C8 offline đạt 3/8 cache hit, tránh ba lần fake
decode (~750 ms); threshold curve phẳng và có false miss TTFT (cosine 0.00), chứng minh
bag-of-words stub không thể thay embedding model chuyên dụng.

## 7. Điều làm tôi ngạc nhiên nhất

Quantization nhỏ hơn không những chậm hơn mà còn trả lời sai nghĩa, và cấu hình một
thread lại thắng physical-core default gần 3× khi offload qua iGPU. Hai kết quả cho
thấy không thể chọn cấu hình chỉ theo heuristic; phải đo trên đúng workload và hardware.

## 8. Self-check trước khi push

- [ x] Số trong reflection khớp `benchmarks/*.md` và raw JSON/CSV.
- [ x] Đã thêm 5 screenshot thật vào `submission/screenshots/`.
- [x ] Đã commit `hardware.json`, `models/active.json`, reports, raw evidence và screenshots.
- [ x] Chạy `python scripts/verify.py` hoặc `./lab.ps1 verify` → exit 0 sau khi phục hồi Python.
- [x ] Repo GitHub ở chế độ public và URL đã paste vào LMS.
- [x ] Không commit model GGUF, runtime binaries hay server logs.
