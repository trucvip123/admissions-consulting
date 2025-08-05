#!/usr/bin/env python3
"""
Script test để kiểm tra bot tuyển sinh hoạt động
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from chatbot import TuyenSinhBot
from document_processor import DocumentProcessor
from vector_store import VectorStore
import time


def test_document_processing():
    """Test xử lý tài liệu"""
    print("🔍 Testing document processing...")

    processor = DocumentProcessor()
    summary = processor.get_document_summary()

    print(f"✅ Đã xử lý {summary['total_documents']} tài liệu")
    print(f"📊 Tổng số ký tự: {summary['total_characters']}")

    for doc in summary["documents"]:
        print(f"   - {doc['filename']}: {doc['characters']} ký tự")

    return summary["total_documents"] > 0


def test_vector_store():
    """Test vector store"""
    print("\n🔍 Testing vector store...")

    vector_store = VectorStore()
    vector_store.build_vector_store(force_rebuild=True)

    stats = vector_store.get_statistics()
    print(f"✅ Vector store status: {stats['status']}")

    if stats["status"] == "initialized":
        print(f"📊 Total vectors: {stats['total_vectors']}")

    # Test tìm kiếm
    test_query = "chỉ tiêu tuyển sinh"
    results = vector_store.search(test_query, k=3)

    print(f"🔍 Tìm kiếm '{test_query}': {len(results)} kết quả")
    for i, result in enumerate(results, 1):
        print(f"   {i}. {result['source']} (score: {result['score']:.4f})")

    return len(results) > 0


def test_chatbot():
    """Test chatbot"""
    print("\n🔍 Testing chatbot...")

    bot = TuyenSinhBot()

    # Test câu hỏi
    test_questions = [
        "Chỉ tiêu tuyển sinh năm 2025",
        "Điểm chuẩn các ngành",
        "Quy chế tuyển sinh",
    ]

    for question in test_questions:
        print(f"\n❓ Câu hỏi: {question}")

        start_time = time.time()
        response = bot.chat(question)
        end_time = time.time()

        print(f"⏱️  Thời gian phản hồi: {end_time - start_time:.2f}s")
        print(f"✅ Thành công: {response['success']}")

        if response["success"]:
            print(f"🤖 Trả lời: {response['response'][:200]}...")
        else:
            print(f"❌ Lỗi: {response.get('error', 'Unknown error')}")

    # Test thống kê
    stats = bot.get_statistics()
    print(f"\n📊 Bot statistics:")
    print(f"   - LLM available: {stats['llm_available']}")
    print(f"   - Conversation history: {stats['conversation_history_length']}")
    print(f"   - Model: {stats['model_name']}")

    return True


def main():
    """Chạy tất cả test"""
    print("🚀 Bắt đầu test bot tuyển sinh...\n")

    tests = [
        ("Document Processing", test_document_processing),
        ("Vector Store", test_vector_store),
        ("Chatbot", test_chatbot),
    ]

    results = []

    for test_name, test_func in tests:
        try:
            print(f"🧪 Running {test_name} test...")
            result = test_func()
            results.append((test_name, result, None))
            print(f"✅ {test_name} test completed successfully!")
        except Exception as e:
            print(f"❌ {test_name} test failed: {str(e)}")
            results.append((test_name, False, str(e)))

    # Tổng kết
    print("\n" + "=" * 50)
    print("📋 TEST SUMMARY")
    print("=" * 50)

    passed = 0
    total = len(results)

    for test_name, success, error in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if error:
            print(f"   Error: {error}")
        if success:
            passed += 1

    print(f"\n🎯 Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 Tất cả test đều thành công! Bot sẵn sàng sử dụng.")
        print("\n🚀 Để chạy bot, sử dụng lệnh:")
        print("   streamlit run app.py")
    else:
        print("⚠️  Một số test thất bại. Vui lòng kiểm tra lại cấu hình.")


if __name__ == "__main__":
    main()
