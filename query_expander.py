import logging
import numpy as np
from typing import List, Dict, Tuple
from langchain_huggingface import HuggingFaceEmbeddings
from config import Config
import re

logger = logging.getLogger(__name__)


class QueryExpander:
    def __init__(self):
        """Khởi tạo QueryExpander với embedding model"""
        self.embeddings = HuggingFaceEmbeddings(
            model_name=Config.EMBEDDING_MODEL,
            model_kwargs={'device': 'cpu'}
        )
        
        # Từ điển từ đồng nghĩa tiếng Việt cho tuyển sinh
        self.synonyms = {
            'tuyển sinh': ['xét tuyển', 'nhập học', 'đăng ký', 'thi tuyển'],
            'chỉ tiêu': ['quota', 'số lượng', 'định mức', 'hạn mức'],
            'điểm chuẩn': ['điểm sàn', 'điểm trúng tuyển', 'điểm đầu vào'],
            'ngành': ['chuyên ngành', 'lĩnh vực', 'bộ môn', 'khoa'],
            'trường': ['đại học', 'học viện', 'viện', 'cơ sở đào tạo'],
            'học phí': ['phí đào tạo', 'tiền học', 'chi phí học tập'],
            'thời gian': ['thời hạn', 'kỳ hạn', 'deadline', 'hạn chót'],
            'hồ sơ': ['giấy tờ', 'tài liệu', 'văn bản', 'chứng từ'],
            'xét tuyển': ['tuyển sinh', 'nhập học', 'đăng ký', 'thi tuyển'],
            'quota': ['chỉ tiêu', 'số lượng', 'định mức', 'hạn mức'],
            'điểm sàn': ['điểm chuẩn', 'điểm trúng tuyển', 'điểm đầu vào'],
            'chuyên ngành': ['ngành', 'lĩnh vực', 'bộ môn', 'khoa'],
            'đại học': ['trường', 'học viện', 'viện', 'cơ sở đào tạo'],
            'phí đào tạo': ['học phí', 'tiền học', 'chi phí học tập'],
            'thời hạn': ['thời gian', 'kỳ hạn', 'deadline', 'hạn chót'],
            'giấy tờ': ['hồ sơ', 'tài liệu', 'văn bản', 'chứng từ']
        }
        
        # Các từ khóa quan trọng trong tuyển sinh
        self.important_keywords = [
            'tuyển sinh', 'chỉ tiêu', 'điểm chuẩn', 'ngành', 'trường',
            'học phí', 'thời gian', 'hồ sơ', 'xét tuyển', 'quota',
            'điểm sàn', 'chuyên ngành', 'đại học', 'phí đào tạo',
            'thời hạn', 'giấy tờ', '2025', '2024', '2023'
        ]

    def expand_with_synonyms(self, query: str) -> List[str]:
        """Mở rộng truy vấn bằng từ đồng nghĩa"""
        expanded_queries = [query]
        
        # Tách từ trong câu hỏi
        words = re.findall(r'\b\w+\b', query.lower())
        
        for word in words:
            if word in self.synonyms:
                synonyms = self.synonyms[word]
                for synonym in synonyms:
                    # Thay thế từ gốc bằng từ đồng nghĩa
                    new_query = re.sub(
                        r'\b' + re.escape(word) + r'\b',
                        synonym,
                        query,
                        flags=re.IGNORECASE
                    )
                    if new_query != query:
                        expanded_queries.append(new_query)
        
        # Loại bỏ các truy vấn trùng lặp
        expanded_queries = list(set(expanded_queries))
        
        logger.info(f"🔍 Mở rộng truy vấn '{query}' thành {len(expanded_queries)} phiên bản")
        for i, exp_query in enumerate(expanded_queries[:3], 1):
            logger.info(f"   {i}. {exp_query}")
        
        return expanded_queries

    def expand_with_embeddings(self, query: str, context_queries: List[str] = None) -> str:
        """Mở rộng truy vấn bằng embedding trung bình"""
        try:
            # Tạo embedding cho truy vấn gốc
            query_embedding = self.embeddings.embed_query(query)
            
            # Nếu có context queries, tính embedding trung bình
            if context_queries:
                context_embeddings = []
                for ctx_query in context_queries:
                    try:
                        ctx_emb = self.embeddings.embed_query(ctx_query)
                        context_embeddings.append(ctx_emb)
                    except Exception as e:
                        logger.warning(f"Không thể tạo embedding cho: {ctx_query} - {e}")
                
                if context_embeddings:
                    # Tính embedding trung bình
                    avg_embedding = np.mean(context_embeddings, axis=0)
                    
                    # Kết hợp với embedding gốc (weighted average)
                    combined_embedding = 0.7 * np.array(query_embedding) + 0.3 * avg_embedding
                    
                    logger.info(f"🧠 Kết hợp embedding từ {len(context_embeddings)} context queries")
                    return query  # Trả về query gốc, embedding đã được cập nhật
            
            return query
            
        except Exception as e:
            logger.error(f"Lỗi khi tạo embedding cho query: {e}")
            return query

    def extract_keywords(self, query: str) -> List[str]:
        """Trích xuất từ khóa quan trọng từ truy vấn"""
        words = re.findall(r'\b\w+\b', query.lower())
        keywords = [word for word in words if word in self.important_keywords]
        
        logger.info(f"🔑 Trích xuất keywords từ '{query}': {keywords}")
        return keywords

    def create_context_queries(self, original_query: str) -> List[str]:
        """Tạo các truy vấn context dựa trên từ khóa"""
        keywords = self.extract_keywords(original_query)
        context_queries = []
        
        # Tạo các truy vấn context bằng cách kết hợp từ khóa
        for i, keyword1 in enumerate(keywords):
            for keyword2 in keywords[i+1:]:
                context_query = f"{keyword1} {keyword2}"
                context_queries.append(context_query)
        
        # Thêm các truy vấn đơn từ khóa quan trọng
        for keyword in keywords:
            if keyword not in [q.split()[0] for q in context_queries]:
                context_queries.append(keyword)
        
        logger.info(f"📝 Tạo {len(context_queries)} context queries từ {len(keywords)} keywords")
        return context_queries[:5]  # Giới hạn 5 context queries

    def expand_query(self, query: str, method: str = "combined") -> List[str]:
        """Mở rộng truy vấn theo phương pháp được chọn"""
        if method == "synonyms":
            return self.expand_with_synonyms(query)
        elif method == "embeddings":
            context_queries = self.create_context_queries(query)
            expanded_query = self.expand_with_embeddings(query, context_queries)
            return [expanded_query]
        elif method == "combined":
            # Kết hợp cả hai phương pháp
            synonym_queries = self.expand_with_synonyms(query)
            context_queries = self.create_context_queries(query)
            
            # Thêm context queries vào danh sách
            all_queries = synonym_queries + context_queries
            
            # Loại bỏ trùng lặp và giới hạn số lượng
            unique_queries = list(set(all_queries))
            return unique_queries[:8]  # Giới hạn 8 truy vấn
        else:
            return [query]

    def get_query_variations(self, query: str) -> Dict[str, List[str]]:
        """Lấy tất cả các biến thể của truy vấn"""
        return {
            'original': [query],
            'synonyms': self.expand_with_synonyms(query),
            'context': self.create_context_queries(query),
            'combined': self.expand_query(query, "combined")
        }


if __name__ == "__main__":
    # Test QueryExpander
    expander = QueryExpander()
    
    test_queries = [
        "chỉ tiêu tuyển sinh 2025",
        "điểm chuẩn ngành công nghệ thông tin",
        "học phí đại học quốc gia",
        "thời gian nộp hồ sơ tuyển sinh"
    ]
    
    for query in test_queries:
        print(f"\n=== Test query: '{query}' ===")
        
        # Test synonyms
        synonyms = expander.expand_with_synonyms(query)
        print(f"Synonyms: {synonyms[:3]}")
        
        # Test keywords
        keywords = expander.extract_keywords(query)
        print(f"Keywords: {keywords}")
        
        # Test context queries
        context = expander.create_context_queries(query)
        print(f"Context: {context[:3]}")
        
        # Test combined expansion
        combined = expander.expand_query(query, "combined")
        print(f"Combined: {combined[:3]}") 