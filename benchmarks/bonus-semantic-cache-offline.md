# Bonus C8 — Semantic cache offline regime

Script: `semantic-cache-demo.py --offline --sweep` · 8 prompts · threshold 0.80 ·
synthetic bag-of-words embeddings · fake miss latency 250 ms.

| Metric | Result |
|:--|--:|
| Cache hits | 3 / 8 (38%) |
| LLM calls avoided | 3 |
| Simulated decode avoided | ~750 ms |
| Hit lookup latency | ~0 ms |
| Miss generation latency | ~250 ms |
| Thresholds tested | 0.70, 0.80, 0.85, 0.90, 0.95 |
| Hits at every threshold | 3 / 8 |

True hits là các lexical paraphrase của goodput (#3, #6) và PagedAttention (#8), đều
có cosine 1.00. **False miss:** “What does time to first token mean?” (#4) là
paraphrase của “Explain TTFT and TPOT” (#2) nhưng cosine 0.00, vì bag-of-words không
biết `TTFT` đồng nghĩa với “time to first token”. Không có false hit trong stream
offline này; vì score chỉ nhận gần 0 hoặc 1, mọi threshold cho cùng kết quả 3/8.

Đây là so sánh regime hợp lệ về control flow—cache hit bỏ qua toàn bộ prefill/decode—
nhưng **không** phải đánh giá chất lượng production. Muốn chẩn đoán đồng thời false hit
và false miss cần embedding model chuyên dụng như BGE-M3/Qwen3-Embedding. Cache cũng
phải salt theo tenant để tránh rò rỉ cross-user qua nội dung hoặc timing side channel.
