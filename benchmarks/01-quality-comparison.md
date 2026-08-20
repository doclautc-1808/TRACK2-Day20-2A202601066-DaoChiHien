# 01 — Human quality comparison: Q4 vs Q2

Same prompt, system message, temperature 0.3 and local `llama-server` build `b10488`:

> Define goodput@SLO in one sentence.

## UD-Q4_K_XL

> Goodput@SLO measures the amount of work actually completed within the defined service level objective.

- Prompt: 35 tokens / 17,277 ms / 2.03 tok/s.
- Decode: 20 tokens / 6,175 ms / 3.08 tok/s.
- Human assessment proposed by experimenter: **correct and relevant**.

## UD-Q2_K_XL

> Goodput@SLO measures the efficiency of software deployment and operational processes, focusing on the speed and effectiveness of delivering software solutions within a Service Level Objective (SLO).

- Prompt: 35 tokens / 53,531 ms / 0.65 tok/s.
- Decode: 35 tokens / 144,872 ms / 0.23 tok/s.
- Human assessment proposed by experimenter: **incorrect meaning**; it shifts from request goodput under latency SLO to software delivery efficiency.

## Kết luận

Latency không đủ để chọn quantization. Theo ba tiêu chí — định nghĩa đúng, liên quan
model serving và không tự thêm phạm vi — Q4 đạt còn Q2 không đạt. Vì Q4 đồng thời nhanh
hơn trong run này, Q4 được giữ làm primary.
