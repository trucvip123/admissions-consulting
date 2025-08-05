#!/usr/bin/env python3
"""
Test script cho QueryExpander
"""

import logging
from query_expander import QueryExpander

# Cấu hình logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_query_expansion():
    """Test các chức năng của QueryExpander"""
    print("🧪 Bắt đầu test QueryExpander...")
    
    expander = QueryExpander()
    
    # Test queries
    test_queries = [
        "chỉ tiêu tuyển sinh 2025",
        "điểm chuẩn ngành công nghệ thông tin",
        "học phí đại học quốc gia",
        "thời gian nộp hồ sơ tuyển sinh",
        "quy chế xét tuyển học bạ",
        "điều kiện nhập học ngành y"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{'='*60}")
        print(f"Test {i}: '{query}'")
        print(f"{'='*60}")
        
        # Test synonyms
        print("\n🔍 Test Synonyms:")
        synonyms = expander.expand_with_synonyms(query)
        for j, syn in enumerate(synonyms[:3], 1):
            print(f"   {j}. {syn}")
        
        # Test keywords
        print("\n🔑 Test Keywords:")
        keywords = expander.extract_keywords(query)
        print(f"   Keywords: {keywords}")
        
        # Test context queries
        print("\n📝 Test Context Queries:")
        context = expander.create_context_queries(query)
        for j, ctx in enumerate(context[:3], 1):
            print(f"   {j}. {ctx}")
        
        # Test combined expansion
        print("\n🚀 Test Combined Expansion:")
        combined = expander.expand_query(query, "combined")
        for j, comb in enumerate(combined[:3], 1):
            print(f"   {j}. {comb}")
        
        # Test all variations
        print("\n📊 Test All Variations:")
        variations = expander.get_query_variations(query)
        for method, queries in variations.items():
            print(f"   {method}: {len(queries)} queries")
            for j, q in enumerate(queries[:2], 1):
                print(f"     {j}. {q}")


def test_embedding_expansion():
    """Test embedding expansion"""
    print("\n🧠 Test Embedding Expansion...")
    
    expander = QueryExpander()
    query = "chỉ tiêu tuyển sinh 2025"
    
    # Test embedding expansion
    context_queries = expander.create_context_queries(query)
    expanded_query = expander.expand_with_embeddings(query, context_queries)
    
    print(f"Original query: {query}")
    print(f"Context queries: {context_queries[:3]}")
    print(f"Expanded query: {expanded_query}")


if __name__ == "__main__":
    try:
        test_query_expansion()
        test_embedding_expansion()
        print("\n✅ Tất cả tests hoàn thành!")
    except Exception as e:
        print(f"\n❌ Lỗi trong quá trình test: {e}")
        import traceback
        traceback.print_exc() 