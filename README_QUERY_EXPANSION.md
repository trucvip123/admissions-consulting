# Query Expansion Module

## Tổng quan

Mô-đun `QueryExpander` được thiết kế để cải thiện chất lượng tìm kiếm bằng cách mở rộng truy vấn người dùng với từ đồng nghĩa và embedding trung bình.

## Tính năng chính

### 1. Mở rộng từ đồng nghĩa (Synonym Expansion)
- Sử dụng từ điển từ đồng nghĩa tiếng Việt chuyên ngành tuyển sinh
- Tự động thay thế từ gốc bằng từ đồng nghĩa
- Ví dụ: "chỉ tiêu" → "quota", "số lượng", "định mức"

### 2. Mở rộng embedding (Embedding Expansion)
- Tạo embedding cho truy vấn gốc
- Tính embedding trung bình từ context queries
- Kết hợp embedding gốc và context (weighted average)

### 3. Trích xuất từ khóa (Keyword Extraction)
- Nhận diện từ khóa quan trọng trong truy vấn
- Tạo context queries từ các từ khóa
- Tối ưu hóa tìm kiếm

## Cách sử dụng

### Khởi tạo
```python
from query_expander import QueryExpander

expander = QueryExpander()
```

### Mở rộng truy vấn
```python
# Mở rộng bằng từ đồng nghĩa
synonyms = expander.expand_with_synonyms("chỉ tiêu tuyển sinh 2025")

# Mở rộng kết hợp
combined = expander.expand_query("chỉ tiêu tuyển sinh 2025", method="combined")

# Lấy tất cả biến thể
variations = expander.get_query_variations("chỉ tiêu tuyển sinh 2025")
```

### Tích hợp với Vector Store
```python
# Trong vector_store.py
results = self.vector_store.search(query, use_query_expansion=True)
```

### Tích hợp với Chatbot
```python
# Trong chatbot.py
response = bot.chat(user_message, use_query_expansion=True)
```

## Từ điển từ đồng nghĩa

### Tuyển sinh
- `tuyển sinh` → `xét tuyển`, `nhập học`, `đăng ký`, `thi tuyển`
- `chỉ tiêu` → `quota`, `số lượng`, `định mức`, `hạn mức`
- `điểm chuẩn` → `điểm sàn`, `điểm trúng tuyển`, `điểm đầu vào`

### Ngành học
- `ngành` → `chuyên ngành`, `lĩnh vực`, `bộ môn`, `khoa`
- `trường` → `đại học`, `học viện`, `viện`, `cơ sở đào tạo`

### Tài chính
- `học phí` → `phí đào tạo`, `tiền học`, `chi phí học tập`

### Thời gian
- `thời gian` → `thời hạn`, `kỳ hạn`, `deadline`, `hạn chót`

### Hồ sơ
- `hồ sơ` → `giấy tờ`, `tài liệu`, `văn bản`, `chứng từ`

## Từ khóa quan trọng

Các từ khóa được ưu tiên trong tìm kiếm:
- `tuyển sinh`, `chỉ tiêu`, `điểm chuẩn`, `ngành`, `trường`
- `học phí`, `thời gian`, `hồ sơ`, `xét tuyển`, `quota`
- `điểm sàn`, `chuyên ngành`, `đại học`, `phí đào tạo`
- `thời hạn`, `giấy tờ`, `2025`, `2024`, `2023`

## Phương pháp mở rộng

### 1. Synonyms (Từ đồng nghĩa)
- Thay thế từng từ trong truy vấn bằng từ đồng nghĩa
- Tạo nhiều biến thể của truy vấn gốc
- Phù hợp cho tìm kiếm chính xác

### 2. Embeddings (Vector)
- Sử dụng embedding model để tạo vector
- Kết hợp với context queries
- Phù hợp cho tìm kiếm ngữ nghĩa

### 3. Combined (Kết hợp)
- Kết hợp cả hai phương pháp
- Tối ưu hóa kết quả tìm kiếm
- Phương pháp mặc định

## Cấu hình

### Environment Variables
```bash
# Embedding model
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2

# Chunk size và overlap
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
```

### Trong UI
- Checkbox "Mở rộng truy vấn (Query Expansion)" trong sidebar
- Có thể bật/tắt tùy theo nhu cầu

## Lợi ích

### 1. Cải thiện độ chính xác
- Tìm được nhiều kết quả liên quan hơn
- Giảm thiểu kết quả bỏ sót

### 2. Linh hoạt trong tìm kiếm
- Hỗ trợ nhiều cách diễn đạt khác nhau
- Tự động hiểu ý định người dùng

### 3. Tối ưu hóa hiệu suất
- Giảm thời gian tìm kiếm
- Tăng tỷ lệ thành công

## Test

Chạy test để kiểm tra chức năng:
```bash
python test_query_expansion.py
```

## Logging

Mô-đun có logging chi tiết:
- `🔍 Mở rộng truy vấn`
- `🔑 Trích xuất keywords`
- `📝 Tạo context queries`
- `🧠 Kết hợp embedding`

## Troubleshooting

### Lỗi thường gặp
1. **Import error**: Kiểm tra `requirements.txt`
2. **Embedding error**: Kiểm tra kết nối mạng
3. **Memory error**: Giảm số lượng queries mở rộng

### Debug
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Tương lai

### Cải tiến có thể thực hiện
1. Thêm từ điển từ đồng nghĩa động
2. Sử dụng transformer models cho embedding
3. Tích hợp với external APIs
4. Machine learning cho tối ưu hóa

### Mở rộng
1. Hỗ trợ nhiều ngôn ngữ
2. Context-aware expansion
3. Personalized expansion
4. Real-time learning 