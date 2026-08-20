# Bonus C4 - Best-of-N with reranking

Host `Windows-AMD64` · llama.cpp `b10488` · N=4 parallel
candidates · temperature 0.8 · output budget 24 tokens

Prompt: *Explain why goodput@SLO is more useful than raw throughput for an LLM serving team. Answer in exactly two concise sentences.*

| Mode | Seed | Latency (ms) | Sentences | Words | Heuristic score |
|:--|--:|--:|--:|--:|--:|
| single | 100 | 30902.7 | 0 | 19 | 4.0 |
| candidate 1 | 101 | 236556.7 | 0 | 19 | 4.0 |
| candidate 2 | 102 | 244581.4 | 0 | 19 | 4.0 |
| candidate 3 | 103 | 244577.3 | 0 | 18 | 4.0 |
| candidate 4 | 104 | 244580.5 | 1 | 19 | 4.0 |

Single-shot wall latency: **30902.7 ms**
Best-of-4 wall latency: **244720.8 ms** (7.92x single-shot)
Chosen candidate: seed **101**, heuristic score **4.00**

## Single-shot answer

> Goodput@SLO measures the actual volume of requests successfully served within agreed-upon service level objectives, reflecting user experience

## Selected Best-of-4 answer

> Goodput@SLO measures the actual delivered, usable output rate within service level agreements, reflecting the quality of the user

## Finding

Best-of-4 **không cải thiện** heuristic score: single và cả bốn candidate đều đạt
4.0; không output nào hoàn thành đúng hai câu vì budget 24 token làm câu bị cắt. Trong
khi đó wall latency tăng từ 30.9 giây lên 244.7 giây (**7.92×**). Bốn slots trên UHD
620 tranh chấp cùng memory bandwidth nên parallel generation không mang lại latency
gần single-shot. Với cấu hình này, Best-of-N là quyết định tệ: tốn compute và latency
mà reranker không có candidate tốt hơn để chọn.

Heuristic chỉ kiểm tra cấu trúc/từ khóa, không chứng minh factual correctness. Muốn C4
hữu ích cần model nhanh hơn, budget đủ hoàn thành câu và reranker semantic/factual;
trên máy hiện tại nên dùng single-shot và dành slots cho người dùng khác.
