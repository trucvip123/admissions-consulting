import os
import logging
from typing import List, Dict
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.schema import Document
from config import Config
from document_processor import DocumentProcessor
from query_expander import QueryExpander
from datetime import datetime
import hashlib
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VectorStore:
    def __init__(self):
        self.embeddings = HuggingFaceEmbeddings(
            model_name=Config.EMBEDDING_MODEL,
            model_kwargs={'device': 'cpu'}
        )
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=Config.CHUNK_SIZE,
            chunk_overlap=Config.CHUNK_OVERLAP,
            length_function=len,
        )
        self.vector_db = None
        self.query_expander = QueryExpander()

    def create_documents(self, documents: List[Dict]) -> List[Document]:
        """Tạo danh sách Document từ dữ liệu đã xử lý với metadata nâng cao"""
        langchain_documents = []
        current_time = datetime.now()

        for doc in documents:
            # Chia văn bản thành các đoạn nhỏ
            chunks = self.text_splitter.split_text(doc['content'])

            # Tạo metadata nâng cao
            file_info = self._extract_file_info(doc['filename'])

            for i, chunk in enumerate(chunks):
                # Tạo hash cho chunk để tracking
                chunk_hash = hashlib.md5(chunk.encode()).hexdigest()[:8]

                # Metadata nâng cao
                enhanced_metadata = {
                    'source': doc['filename'],
                    'chunk_id': i,
                    'total_chunks': len(chunks),
                    'chunk_hash': chunk_hash,
                    'load_time': current_time.isoformat(),
                    'file_size': len(doc['content']),
                    'chunk_size': len(chunk),
                    'file_type': file_info['type'],
                    'file_title': file_info['title'],
                    'file_year': file_info['year'],
                    'file_category': file_info['category'],
                    'processing_timestamp': current_time.timestamp()
                }

                langchain_documents.append(
                    Document(
                        page_content=chunk,
                        metadata=enhanced_metadata
                    )
                )

        logger.info(f"Đã tạo {len(langchain_documents)} chunks từ {len(documents)} tài liệu với metadata nâng cao")
        return langchain_documents

    def _extract_file_info(self, filename: str) -> Dict:
        """Trích xuất thông tin từ tên file"""
        info = {
            'type': 'docx',
            'title': filename.replace('.docx', ''),
            'year': 'unknown',
            'category': 'general'
        }

        # Trích xuất năm từ tên file
        year_match = re.search(r'20\d{2}', filename)
        if year_match:
            info['year'] = year_match.group()

        # Phân loại tài liệu dựa trên tên file
        filename_lower = filename.lower()
        if 'chi_tieu' in filename_lower or 'chỉ tiêu' in filename_lower:
            info['category'] = 'quota'
        elif 'quy_che' in filename_lower or 'quy chế' in filename_lower:
            info['category'] = 'regulation'
        elif 'diem_chuan' in filename_lower or 'điểm chuẩn' in filename_lower:
            info['category'] = 'benchmark'
        elif 'thong_tin' in filename_lower or 'thông tin' in filename_lower:
            info['category'] = 'information'

        return info

    def build_vector_store(self, force_rebuild: bool = False):
        """Xây dựng cơ sở dữ liệu vector"""
        if not force_rebuild and os.path.exists(Config.VECTOR_DB_PATH):
            logger.info("Đang tải cơ sở dữ liệu vector hiện có...")
            self.vector_db = FAISS.load_local(
                Config.VECTOR_DB_PATH,
                self.embeddings,
                allow_dangerous_deserialization=True,
            )
            return

        logger.info("Đang xây dựng cơ sở dữ liệu vector mới...")

        # Xử lý tài liệu
        processor = DocumentProcessor()
        documents = processor.process_all_documents()

        if not documents:
            logger.error("Không tìm thấy tài liệu để xử lý!")
            return

        # Tạo documents cho langchain
        langchain_documents = self.create_documents(documents)

        # Tạo vector store
        self.vector_db = FAISS.from_documents(langchain_documents, self.embeddings)

        # Lưu vector store
        os.makedirs(Config.VECTOR_DB_PATH, exist_ok=True)
        self.vector_db.save_local(Config.VECTOR_DB_PATH)

        logger.info(f"Đã lưu cơ sở dữ liệu vector tại: {Config.VECTOR_DB_PATH}")

    def search(self, query: str, k: int = 5, use_query_expansion: bool = True) -> List[Dict]:
        """Tìm kiếm thông tin liên quan đến câu hỏi với tùy chọn mở rộng truy vấn"""
        if not self.vector_db:
            logger.error("Cơ sở dữ liệu vector chưa được khởi tạo!")
            return []

        try:
            logger.info(f"🔍 Tìm kiếm: '{query}' (k={k}, expansion={use_query_expansion})")
            
            # Mở rộng truy vấn nếu được bật
            if use_query_expansion:
                expanded_queries = self.query_expander.expand_query(query, method="combined")
                logger.info(f"📈 Sử dụng {len(expanded_queries)} truy vấn mở rộng")
                
                # Tìm kiếm với tất cả các truy vấn mở rộng
                all_results = []
                for exp_query in expanded_queries:
                    try:
                        exp_results = self.vector_db.similarity_search_with_score(exp_query, k=k//2)
                        all_results.extend(exp_results)
                    except Exception as e:
                        logger.warning(f"Lỗi khi tìm kiếm với query '{exp_query}': {e}")
                
                # Sắp xếp theo score và lấy top k
                all_results.sort(key=lambda x: x[1])  # Sắp xếp theo score (thấp hơn = tốt hơn)
                results = all_results[:k]
            else:
                results = self.vector_db.similarity_search_with_score(query, k=k)

            formatted_results = []
            for doc, score in results:
                formatted_results.append({
                    'content': doc.page_content,
                    'source': doc.metadata.get('source', 'Unknown'),
                    'score': float(score),
                    'chunk_id': doc.metadata.get('chunk_id', 0),
                    'total_chunks': doc.metadata.get('total_chunks', 0),
                    # Metadata nâng cao
                    'chunk_hash': doc.metadata.get('chunk_hash', ''),
                    'load_time': doc.metadata.get('load_time', ''),
                    'file_size': doc.metadata.get('file_size', 0),
                    'chunk_size': doc.metadata.get('chunk_size', 0),
                    'file_type': doc.metadata.get('file_type', 'unknown'),
                    'file_title': doc.metadata.get('file_title', ''),
                    'file_year': doc.metadata.get('file_year', 'unknown'),
                    'file_category': doc.metadata.get('file_category', 'general'),
                    'processing_timestamp': doc.metadata.get('processing_timestamp', 0)
                })

            logger.info(f"✅ Tìm thấy {len(formatted_results)} kết quả từ {len(set(r['source'] for r in formatted_results))} tài liệu")
            for i, result in enumerate(formatted_results[:3], 1):
                logger.info(f"   {i}. {result['file_title']} ({result['file_category']}, {result['file_year']}) - score: {result['score']:.4f}")
                logger.info(f"      Chunk {result['chunk_id']}/{result['total_chunks']} - Hash: {result['chunk_hash']}")

            return formatted_results
        except Exception as e:
            logger.error(f"Lỗi khi tìm kiếm: {str(e)}")
            return []

    def get_statistics(self) -> Dict:
        """Lấy thống kê về cơ sở dữ liệu vector"""
        if not self.vector_db:
            return {'status': 'not_initialized'}
        
        try:
            # Lấy thông tin chi tiết từ vector store
            total_vectors = len(self.vector_db.index_to_docstore_id)
            
            # Thống kê theo category
            categories = {}
            years = {}
            file_sizes = []
            
            # Lấy metadata từ tất cả documents (nếu có thể)
            try:
                # Thử lấy một số documents để phân tích
                sample_docs = self.vector_db.similarity_search("", k=min(100, total_vectors))
                for doc in sample_docs:
                    category = doc.metadata.get('file_category', 'unknown')
                    year = doc.metadata.get('file_year', 'unknown')
                    file_size = doc.metadata.get('file_size', 0)
                    
                    categories[category] = categories.get(category, 0) + 1
                    years[year] = years.get(year, 0) + 1
                    if file_size > 0:
                        file_sizes.append(file_size)
            except:
                pass
            
            return {
                'status': 'initialized',
                'total_vectors': total_vectors,
                'categories': categories,
                'years': years,
                'avg_file_size': sum(file_sizes) // len(file_sizes) if file_sizes else 0,
                'total_files': len(set(years.keys()) - {'unknown'}) if years else 0
            }
        except Exception as e:
            logger.error(f"Lỗi khi lấy thống kê: {str(e)}")
            return {'status': 'error', 'error': str(e)}


if __name__ == "__main__":
    vector_store = VectorStore()
    vector_store.build_vector_store(force_rebuild=True)

    # Test tìm kiếm
    test_query = "chỉ tiêu tuyển sinh 2025"
    results = vector_store.search(test_query)

    print(f"\nKết quả tìm kiếm cho: '{test_query}'")
    for i, result in enumerate(results, 1):
        print(f"\n--- Kết quả {i} ---")
        print(f"Nguồn: {result['source']}")
        print(f"Điểm: {result['score']:.4f}")
        print(f"Nội dung: {result['content'][:200]}...")
