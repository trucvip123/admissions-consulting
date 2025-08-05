import streamlit as st
import time
from datetime import datetime
from chatbot import TuyenSinhBot
from config import Config
import logging

# Cấu hình logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Cấu hình trang
st.set_page_config(
    page_title="Bot Tư Vấn Tuyển Sinh ĐHQN",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# CSS tùy chỉnh
st.markdown(
    """
<style>
    .main-header {
        background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .chat-message {
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        border-left: 4px solid;
    }
    
    .user-message {
        background-color: #e3f2fd;
        border-left-color: #2196f3;
    }
    
    .bot-message {
        background-color: #f3e5f5;
        border-left-color: #9c27b0;
    }
    
    .suggestion-button {
        margin: 0.2rem;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        border: 1px solid #ddd;
        background-color: white;
        cursor: pointer;
        transition: all 0.3s;
    }
    
    .suggestion-button:hover {
        background-color: #f0f0f0;
        transform: translateY(-2px);
    }
    
    .stats-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #28a745;
    }
    
    .sidebar-content {
        padding: 1rem;
    }
</style>
""",
    unsafe_allow_html=True,
)


@st.cache_resource
def initialize_bot():
    """Khởi tạo bot với cache"""
    with st.spinner("Đang khởi tạo bot..."):
        bot = TuyenSinhBot()
        return bot


def display_chat_message(role, content, timestamp=None):
    """Hiển thị tin nhắn chat"""
    formatted_time = timestamp.strftime("%H:%M:%S") if timestamp else ""
    if role == "user":
        st.markdown(
            f"""
        <div class="chat-message user-message">
            <strong>👤 Bạn:</strong><br>
            {content}
            <p style="font-size: 0.8em; color: gray;">🕒 {formatted_time}</p>
        </div>
        """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f"""
        <div class="chat-message bot-message">
            <strong>🤖 Bot:</strong><br>
            {content}
            <p style="font-size: 0.8em; color: gray;">🕒 {formatted_time}</p>
        </div>
        """,
            unsafe_allow_html=True,
        )


def main():
    # Header
    st.markdown(
        """
    <div class="main-header">
        <h1>🎓 Bot Tư Vấn Tuyển Sinh ĐHQN</h1>
        <p>Trợ lý AI thông minh cung cấp thông tin tuyển sinh chính xác và nhanh chóng</p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # Khởi tạo bot
    bot = initialize_bot()

    # Sidebar
    with st.sidebar:
        st.markdown("### ⚙️ Cài đặt")

        # Tùy chọn Query Expansion
        st.markdown("#### 🔍 Tùy chọn tìm kiếm")
        use_query_expansion = st.checkbox(
            "Mở rộng truy vấn (Query Expansion)",
            value=True,
            help="Sử dụng từ đồng nghĩa và context để cải thiện kết quả tìm kiếm"
        )

        # Thống kê
        stats = bot.get_statistics()
        st.markdown("#### 📊 Thống kê")
        st.markdown(
            f"""
        <div class="stats-card">
            <strong>Vector Store:</strong> {stats['vector_store']['status']}<br>
            <strong>LLM:</strong> {'✅ Có sẵn' if stats['llm_available'] else '❌ Chưa cấu hình'}<br>
            <strong>Lịch sử chat:</strong> {stats['conversation_history_length']} tin nhắn<br>
            <strong>Query Expansion:</strong> {'✅ Bật' if use_query_expansion else '❌ Tắt'}
        </div>
        """,
            unsafe_allow_html=True,
        )

        # Câu hỏi gợi ý
        st.markdown("#### 💡 Câu hỏi gợi ý")
        suggestions = bot.suggest_questions()
        for suggestion in suggestions:
            if st.button(suggestion, key=f"suggest_{suggestion[:20]}"):
                st.session_state.user_input = suggestion
                st.rerun()

        # Nút xóa lịch sử
        if st.button("🗑️ Xóa lịch sử chat"):
            bot.clear_history()
            st.session_state.messages = []
            st.success("Đã xóa lịch sử chat!")
            st.rerun()

        # Nút tải lịch sử chat
        import json

        chat_history = st.session_state.get("messages", [])
        st.download_button(
            label="📥 Tải lịch sử chat",
            data=json.dumps(chat_history, ensure_ascii=False, indent=2, default=str),
            file_name="chat_history.json",
            mime="application/json",
        )

    # Khởi tạo session state
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Hiển thị lịch sử chat
    chat_container = st.container()
    with chat_container:
        for message in st.session_state.messages:
            display_chat_message(
                message["role"], message["content"], message.get("timestamp")
            )

    # Input area
    col1, col2 = st.columns([4, 1])

    with col1:
        user_input = st.text_input(
            "Nhập câu hỏi của bạn:",
            key="user_input",
            placeholder="Ví dụ: Chỉ tiêu tuyển sinh năm 2025 là bao nhiêu?",
            label_visibility="collapsed",
        )

    with col2:
        send_button = st.button("🚀 Gửi", use_container_width=True)

    # Xử lý input
    if send_button and user_input and user_input.strip():
        # Thêm tin nhắn người dùng
        st.session_state.messages.append(
            {"role": "user", "content": user_input, "timestamp": datetime.now()}
        )

        # Hiển thị tin nhắn người dùng
        display_chat_message("user", user_input)

        # Xử lý câu trả lời
        with st.spinner("🤖 Bot đang suy nghĩ..."):
            response = bot.chat(user_input, use_query_expansion=use_query_expansion)

            if response["success"]:
                bot_response = response["response"]
            else:
                bot_response = "Xin lỗi, có lỗi xảy ra. Vui lòng thử lại sau."

        # Thêm tin nhắn bot
        st.session_state.messages.append(
            {"role": "assistant", "content": bot_response, "timestamp": datetime.now()}
        )

        # Hiển thị tin nhắn bot
        display_chat_message("assistant", bot_response)

        # Reset input bằng cách rerun
        st.rerun()

    # Footer
    st.markdown("---")
    st.markdown(
        """
    <div style="text-align: center; color: #666; padding: 1rem;">
        <p>🤖 Bot được phát triển với ❤️ để hỗ trợ thí sinh</p>
        <p>📧 Liên hệ: support@dhqn.edu.vn | 📞 Hotline: 1900-xxxx</p>
    </div>
    """,
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
