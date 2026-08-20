# 03 - Integrate: RAG pipeline run

Host `Windows-AMD64` · llama.cpp `b10488` ·
retrieval backend: **keyword overlap** · 3 queries

| Query | Contexts retrieved | embed (ms) | retrieve (ms) | llm (ms) | total (ms) |
|:--|--:|--:|--:|--:|--:|
| Why is goodput more useful than raw throughp... | goodput, paged, radix | 0.0 | 24.3 | 40763.6 | 40788.0 |
| What problem does PagedAttention actually so... | paged, radix, disagg | 0.0 | 0.1 | 39342.2 | 39342.4 |
| When does splitting prefill and decode help?... | disagg, radix, batching | 0.0 | 0.2 | 36399.1 | 36399.4 |

Mean per stage (ms): embed **0.0** · retrieve **8.2** ·
llm **38835.0** · total **38843.3**
Dominant stage: **llm** (100% of total)

## Answers returned

**Why is goodput more useful than raw throughput?**

> Goodput@SLO counts only the requests per second that met the TTFT and TPOT targets. Throughput at saturation ignores SLOs.

**What problem does PagedAttention actually solve?**

> PagedAttention stores the KV cache in non-contiguous pages, removing the internal fragmentation that wasted most GPU memory.

**When does splitting prefill and decode help?**

> Splitting prefill and decode helps because prefill is compute-bound and decode is memory-bandwidth-bound.


## Which N16-N19 pieces are real

- N16 Cloud/IaC: **stub** — run local Windows, không provision cloud.
- N17 Data pipeline: **stub** — sáu toy documents được nạp tĩnh.
- N18 Lakehouse: **stub** — in-memory list, không có lakehouse thật.
- N19 Vector + features: **stub** — keyword overlap, không dùng vector index.
- N20 Serving: **real** — `llama-server` qua `/v1/chat/completions`.

LLM chiếm 38,835.0 ms, gần 100% total, đúng kỳ vọng vì embed/retrieve là stub nhẹ.
Muốn giảm pipeline latency 2×, tôi sẽ áp dụng `-t 1` đã thắng 2.89× ở tg128 và giảm
prompt/output budget; tối ưu retrieval trung bình 8.2 ms không tạo khác biệt đáng kể.
