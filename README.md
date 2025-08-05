# 🤖 Bot Tư Vấn Tuyển Sinh ĐHQN

Bot AI thông minh được phát triển để cung cấp thông tin tuyển sinh chính xác và nhanh chóng cho trường Đại học Quốc gia (ĐHQN).

## ✨ Tính năng chính

- 📚 **Xử lý tài liệu DOCX**: Tự động trích xuất thông tin từ các file tài liệu tuyển sinh
- 🔍 **Tìm kiếm thông minh**: Sử dụng vector database để tìm kiếm thông tin liên quan
- 💬 **Chatbot thân thiện**: Giao diện chat đẹp mắt và dễ sử dụng
- 🧠 **AI thông minh**: Tích hợp OpenAI GPT để trả lời câu hỏi tự nhiên
- 📊 **Thống kê chi tiết**: Theo dõi hiệu suất và sử dụng bot

## 🚀 Cài đặt và chạy

### 1. Cài đặt dependencies

```bash
pip install -r requirements.txt
```

### 2. Cấu hình API Key (tùy chọn)

Để sử dụng tính năng AI nâng cao, bạn cần:

1. Tạo file `.env` từ `env_example.txt`
2. Thêm OpenAI API key vào file `.env`:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   ```

**Lưu ý**: Bot vẫn hoạt động tốt mà không cần API key, chỉ sử dụng tìm kiếm vector.

### 3. Chạy ứng dụng

```bash
streamlit run app.py
```

Ứng dụng sẽ mở tại: http://localhost:8501

## 📁 Cấu trúc dự án

```
bot_tuyen_sinh/
├── data/                          # Thư mục chứa tài liệu DOCX
│   ├── Chi_tieu_tuyen_sinh_2025.docx
│   ├── Quy_che_tuyen_sinh_Truong_DHQN_2025_V3.docx
│   ├── Thong tin Tuyen_sinh_2025_QNU_V6-7.docx
│   └── Thong tin chi tieu diem trung tuyen 2023 2024.docx
├── vector_db/                     # Cơ sở dữ liệu vector (tự động tạo)
├── app.py                         # Ứng dụng Streamlit chính
├── chatbot.py                     # Module chatbot
├── config.py                      # Cấu hình hệ thống
├── document_processor.py          # Xử lý tài liệu DOCX
├── vector_store.py                # Quản lý vector database
├── requirements.txt               # Dependencies
├── env_example.txt                # Mẫu file cấu hình
└── README.md                      # Hướng dẫn sử dụng
```

## 🎯 Cách sử dụng

### 1. Khởi động bot
- Chạy lệnh `streamlit run app.py`
- Bot sẽ tự động xử lý các tài liệu trong thư mục `data/`

### 2. Đặt câu hỏi
Bạn có thể hỏi về:
- Chỉ tiêu tuyển sinh các ngành
- Điểm chuẩn các năm trước
- Quy chế tuyển sinh
- Thời gian nộp hồ sơ
- Điều kiện xét tuyển
- Và nhiều thông tin khác...

### 3. Sử dụng câu hỏi gợi ý
Bot cung cấp sẵn các câu hỏi mẫu trong sidebar để bạn dễ dàng bắt đầu.

## 🔧 Tùy chỉnh

### Thêm tài liệu mới
1. Đặt file DOCX vào thư mục `data/`
2. Khởi động lại bot
3. Bot sẽ tự động xử lý tài liệu mới

### Cấu hình hệ thống
Chỉnh sửa file `config.py` để thay đổi:
- Model AI sử dụng
- Kích thước chunk văn bản
- Số lượng kết quả tìm kiếm
- Prompt hệ thống

## 📊 Hiệu suất

Bot được tối ưu hóa để:
- Xử lý nhanh các tài liệu lớn
- Tìm kiếm chính xác thông tin
- Trả lời nhanh chóng
- Sử dụng ít tài nguyên

## 🛠️ Công nghệ sử dụng

- **Streamlit**: Giao diện web
- **LangChain**: Framework AI
- **OpenAI GPT**: Model ngôn ngữ
- **FAISS**: Vector database
- **Sentence Transformers**: Embedding model
- **python-docx**: Xử lý file DOCX

## 🤝 Đóng góp

Mọi đóng góp đều được chào đón! Vui lòng:
1. Fork dự án
2. Tạo branch mới
3. Commit thay đổi
4. Push và tạo Pull Request

## 📞 Hỗ trợ

- 📧 Email: support@dhqn.edu.vn
- 📞 Hotline: 1900-xxxx
- 🐛 Báo lỗi: Tạo issue trên GitHub

## 📄 Giấy phép

Dự án này được phát hành dưới giấy phép MIT.

---

**Lưu ý**: Bot được phát triển để hỗ trợ thí sinh và không thay thế tư vấn chính thức từ trường. Vui lòng liên hệ trường để có thông tin chính xác nhất. 