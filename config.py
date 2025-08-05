import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    # Google Gemini API Key
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

    # Model Configuration
    EMBEDDING_MODEL = os.getenv(
        "EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2"
    )
    EMBEDDING_DEVICE = os.getenv("EMBEDDING_DEVICE", "cpu")
    LLM_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5")

    # Vector Database Configuration
    VECTOR_DB_PATH = os.getenv("VECTOR_DB_PATH", "./vector_db")
    CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", 1000))
    CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", 200))
    
    # Chat Configuration
    MAX_HISTORY = 10
    TEMPERATURE = 0.7
    DATA_DIR = "./data"
    SYSTEM_PROMPT = """Bạn là một trợ lý AI chuyên về tư vấn tuyển sinh cho trường Đại học Quy Nhơn (ĐHQN).\nBạn có kiến thức sâu rộng về:\n- Quy chế tuyển sinh\n- Chỉ tiêu tuyển sinh các ngành\n- Điểm chuẩn các năm trước\n- Thông tin chi tiết về các ngành đào tạo\n\nHãy trả lời các câu hỏi một cách chính xác, rõ ràng và hữu ích.\nNếu không có thông tin trong dữ liệu, hãy nói rõ rằng bạn không có thông tin đó.\nLuôn trả lời bằng tiếng Việt."""
