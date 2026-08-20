# 02 - Serve: load test + saturation reading

Host `Windows-AMD64` · llama.cpp `b10488` ·
`--parallel 4` · `ctx=2048` · `threads=1` ·
`ngl=99`

| Users | Reqs | RPS | P50 (ms) | P95 (ms) | P99 (ms) | Eff. concurrency | Failures |
|:--|--:|--:|--:|--:|--:|--:|--:|
| 10 | 10 | 0.08 | 122000 | 122000 | 122000 | 9.1 | 60.0% |
| 50 | 50 | 0.41 | 122000 | 122000 | 122000 | 48.8 | 94.0% |

*Effective concurrency = RPS x average latency (Little's Law) -- how many requests were
really in flight, regardless of how many users locust simulated. It counts queued requests
too, so the occupancy/slot ratio can legitimately exceed 1.0; it is occupancy, not
utilisation. For true slot utilisation use the server's own gauges (`make metrics`).*

## What these two runs say

| Going from 10 to 50 users | |
|:--|--:|
| Offered load | 5x |
| Total completion/timeout rate | **5.00x** |
| Successful goodput | **0.75x** (0.0325 → 0.0244 req/s) |
| P95 latency | **1.00x** |
| Effective concurrency at 50 users | 48.8 vs `--parallel 4` slots (occupancy/slot ratio 12.19) |

**Saturated.** `Requests/s` của Locust gồm cả request timeout, nên mức 5.00x không phải
throughput hữu ích. Số request thành công giảm từ 4/10 xuống 3/50; successful goodput
giảm 25%, failure tăng 60% → 94%, và effective concurrency 48.8 vượt xa 4 slots.
P95 cùng chạm timeout khoảng 122 giây nên không còn phản ánh compute latency thuần.

> **Small sample.** Only 10 requests completed in the
> shorter run, so these percentiles are indicative rather than solid. Note also that
> locust averages only *completed* requests: when the run ends with requests still
> queued, effective concurrency is an **under**-estimate. Trust the throughput-scaling
> row over the concurrency row here, and run longer (`-t 3m`) if you want firmer numbers.

## My reading

Server đã bão hòa từ run 10 users. Bằng chứng thuyết phục nhất là failure 60% ở 10
users và 94% ở 50 users; metric nội bộ đồng thời ghi 4/4 processing slots và 46
deferred requests. Latency tăng thêm chủ yếu là queue time. Để nâng goodput@SLO, tôi
sẽ cap admission concurrency gần 4 và giảm output budget trước, thay vì tăng
`--parallel`: UHD 620 dùng RAM chia sẻ, thêm slot sẽ tăng tranh chấp bandwidth.
