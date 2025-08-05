import logging
from typing import List, Dict, Optional
from langchain.schema import HumanMessage, SystemMessage
from langchain.prompts import ChatPromptTemplate
from config import Config
from vector_store import VectorStore
from gemini_llm import GeminiLLM

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TuyenSinhBot:
    def __init__(self):
        self.vector_store = VectorStore()
        self.llm = None
        self.conversation_history = []
        if getattr(Config, "GEMINI_API_KEY", None):
            self.llm = GeminiLLM()
            self.llm_type = "gemini"
            logger.info("✅ Gemini API key đã được cấu hình thành công!")
        else:
            self.llm_type = None
            logger.warning(
                "Không có Gemini API key. Bot sẽ chỉ sử dụng tìm kiếm vector."
            )
        self.vector_store.build_vector_store()
        self.prompt_template = ChatPromptTemplate.from_messages(
            [
                ("system", Config.SYSTEM_PROMPT),
                (
                    "human",
                    """Dựa trên thông tin sau đây, hãy trả lời câu hỏi của người dùng một cách chính xác và hữu ích:\n\nThông tin tham khảo:\n{context}\n\nCâu hỏi: {question}\n\nLưu ý: Nếu thông tin không đủ để trả lời chính xác, hãy nói rõ rằng bạn không có đủ thông tin và đề xuất người dùng liên hệ trực tiếp với trường để biết thêm chi tiết.""",
                ),
            ]
        )

    def get_relevant_context(self, question: str, k: int = 5, use_query_expansion: bool = True) -> str:
        results = self.vector_store.search(question, k=k, use_query_expansion=use_query_expansion)
        if not results:
            return "Không tìm thấy thông tin liên quan trong cơ sở dữ liệu."
        context_parts = []
        for i, result in enumerate(results, 1):
            context_parts.append(
                f"Thông tin {i} (từ {result['source']}):\n{result['content']}"
            )
        return "\n\n".join(context_parts)

    def generate_response(self, question: str, context: str) -> str:
        if not self.llm:
            return f"Thông tin tìm được:\n\n{context}\n\nLưu ý: Để có câu trả lời chi tiết hơn, vui lòng cung cấp Gemini API key."
        try:
            # Tạo prompt hoàn chỉnh bao gồm system prompt và câu hỏi
            full_prompt = f"""{Config.SYSTEM_PROMPT}

Dựa trên thông tin sau đây, hãy trả lời câu hỏi của người dùng một cách chính xác và hữu ích:

Thông tin tham khảo:
{context}

Câu hỏi: {question}

Lưu ý: Nếu thông tin không đủ để trả lời chính xác, hãy nói rõ rằng bạn không có đủ thông tin và đề xuất người dùng liên hệ trực tiếp với trường để biết thêm chi tiết.

Trả lời bằng tiếng Việt:"""
            
            logger.info(f"📝 Prompt gửi đến Gemini: {full_prompt[:200]}...")
            return self.llm.generate(full_prompt)
        except Exception as e:
            logger.error(f"Lỗi khi tạo câu trả lời: {str(e)}")
            return f"Xin lỗi, có lỗi xảy ra khi xử lý câu hỏi. Thông tin tìm được:\n\n{context}"

    def chat(self, user_message: str, use_query_expansion: bool = True) -> Dict:
        try:
            logger.info(f"👤 User hỏi: {user_message}")
            self.conversation_history.append({"role": "user", "content": user_message})
            if len(self.conversation_history) > Config.MAX_HISTORY * 2:
                self.conversation_history = self.conversation_history[
                    -Config.MAX_HISTORY * 2 :
                ]
            context = self.get_relevant_context(user_message, use_query_expansion=use_query_expansion)
            response = self.generate_response(user_message, context)
            logger.info(f"🤖 Bot trả lời: {response[:200]}...")
            self.conversation_history.append({"role": "assistant", "content": response})
            return {"response": response, "context_used": context, "success": True}
        except Exception as e:
            logger.error(f"❌ Lỗi khi xử lý câu hỏi '{user_message}': {str(e)}")
            logger.error(f"Lỗi trong quá trình chat: {str(e)}")
            return {
                "response": "Xin lỗi, có lỗi xảy ra. Vui lòng thử lại sau.",
                "context_used": "",
                "success": False,
                "error": str(e),
            }

    def get_conversation_history(self) -> List[Dict]:
        return self.conversation_history.copy()

    def clear_history(self):
        self.conversation_history = []

    def get_statistics(self) -> Dict:
        vector_stats = self.vector_store.get_statistics()
        return {
            "vector_store": vector_stats,
            "llm_available": self.llm is not None,
            "conversation_history_length": len(self.conversation_history),
            "model_name": "gemini" if self.llm else "None",
        }

    def suggest_questions(self) -> List[str]:
        return [
            "Chỉ tiêu tuyển sinh năm 2025",
            "Điểm chuẩn các ngành năm 2023-2024 như thế nào?",
            "Quy chế tuyển sinh năm 2025 có gì mới?",
            "Các ngành đào tạo của trường ĐHQN gồm những gì?",
            "Thời gian nộp hồ sơ tuyển sinh năm 2025?",
            "Điều kiện xét tuyển học bạ như thế nào?",
            "Có bao nhiêu phương thức xét tuyển?",
            "Thông tin về học phí và chính sách học bổng?",
        ]


if __name__ == "__main__":
    # Test bot
    bot = TuyenSinhBot()

    test_questions = [
        "Chỉ tiêu tuyển sinh 2025",
        "Điểm chuẩn năm 2023",
        "Quy chế tuyển sinh",
    ]

    for question in test_questions:
        print(f"\n{'='*50}")
        print(f"Câu hỏi: {question}")
        print(f"{'='*50}")

        result = bot.chat(question)
        print(f"Trả lời: {result['response']}")
        print(f"Thành công: {result['success']}")
