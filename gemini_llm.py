import google.generativeai as genai
from config import Config
import logging

logger = logging.getLogger(__name__)


class GeminiLLM:
    def __init__(self, api_key=None):
        self.api_key = api_key or getattr(Config, "GEMINI_API_KEY", None)
        if not self.api_key:
            raise ValueError("Chưa cấu hình GEMINI_API_KEY!")
        genai.configure(api_key=self.api_key)
        try:
            self.model = genai.GenerativeModel(Config.LLM_MODEL)
        except:
            raise Exception("Không thể khởi tạo Gemini model. Vui lòng kiểm tra API key và kết nối mạng.")

    def generate(self, prompt: str) -> str:
        try:
            logger.info("🧠 Đang gọi Gemini API...")
            response = self.model.generate_content(prompt)
            result_text = response.text if hasattr(response, 'text') else str(response)
            logger.info(f"✅ Gemini trả về: {result_text[:100]}...")
            return result_text
        except Exception as e:
            error_msg = str(e)
            if "429" in error_msg or "quota" in error_msg.lower():
                logger.error("❌ Lỗi quota Gemini API")
                raise Exception("Đã vượt quá giới hạn quota Gemini API. Vui lòng thử lại sau hoặc nâng cấp tài khoản.")
            else:
                logger.error(f"❌ Lỗi Gemini API: {error_msg}")
                raise e
