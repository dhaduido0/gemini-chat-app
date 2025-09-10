from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import PGVector
from pdf_importer import CONNECTION_STRING, COLLECTION_NAME

# 벡터 스토어 초기화 (RAG 시스템의 핵심)
vector_store = None

def get_vector_store():
    """벡터 스토어 인스턴스 반환"""
    global vector_store
    if vector_store is None:
        initialize_vector_store()
    return vector_store

def initialize_vector_store():
    """벡터 스토어 초기화"""
    global vector_store
    try:
        # 한국어 특화 임베딩 모델 로드 (KURE-v1)
        embeddings = HuggingFaceEmbeddings(
            model_name='nlpai-lab/KURE-v1',  # 한국어 임베딩 모델
            model_kwargs={'device': 'cpu'}   # CPU 사용 (GPU 있으면 'cuda'로 변경)
        )
        # PostgreSQL + pgvector를 사용한 벡터 데이터베이스 연결
        vector_store = PGVector(
            collection_name=COLLECTION_NAME,     # 컬렉션명: "mjc_homepage"
            connection_string=CONNECTION_STRING, # PostgreSQL 연결 문자열
            embedding_function=embeddings        # 임베딩 함수
        )
        print("✅ LangChain 벡터 스토어 연결 성공")
    except Exception as e:
        print(f"⚠️ 벡터 스토어 연결 실패: {e}")
        print("📝 PDF 데이터를 먼저 import 해주세요: python pdf_importer.py")
        vector_store = None
