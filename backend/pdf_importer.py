# =============================================================================
# PDF 문서를 벡터 데이터베이스로 변환하는 모듈
# =============================================================================
# 주요 기능:
# 1. PDF 파일을 텍스트로 변환
# 2. 텍스트를 적절한 크기로 분할
# 3. 한국어 임베딩 모델로 벡터화
# 4. PostgreSQL + pgvector에 저장
# =============================================================================
import os
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings 
from langchain_community.vectorstores import PGVector
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

# PostgreSQL 데이터베이스 연결 정보 설정
CONNECTION_STRING = f"postgresql+psycopg2://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@{os.getenv('POSTGRES_HOST')}:{os.getenv('POSTGRES_PORT')}/{os.getenv('POSTGRES_DB')}"
COLLECTION_NAME = "mjc_homepage"  # 벡터 저장소 컬렉션명

def create_vector_store():
    # 독스트링 (함수 설명서)
    """
    PDF 문서를 벡터 데이터베이스로 변환하는 메인 함수
    
    처리 과정:
    1. PDF 파일 로드 및 텍스트 추출
    2. 텍스트를 적절한 크기로 분할 (chunking)
    3. 한국어 임베딩 모델로 벡터화
    4. PostgreSQL + pgvector에 저장
    
    Returns:
        PGVector: 벡터 저장소 객체 (성공 시)
        None: 실패 시
    """
    
    # 1단계: PDF 파일 로드 및 텍스트 추출
    pdf_path = os.path.join("data", "명지전문대학 _ 학부_학과안내 _ 공학ㆍ정보학부 _ AI게임소프트웨어학과 _ 학과소개.pdf")
    if not os.path.exists(pdf_path):
        print(f"Error: PDF file not found at {pdf_path}")
        return None

    # PyPDFLoader로 PDF 파일을 텍스트로 변환
    loader = PyPDFLoader(pdf_path)
    documents = loader.load()
    print("*****PDF 로드 완료.")

    # 2단계: 텍스트 분할 (Chunking)
    # - 너무 긴 텍스트는 AI가 처리하기 어려움
    # - 적절한 크기로 나누되, 맥락을 유지하기 위해 겹치는 부분 포함
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,      # 각 청크의 최대 크기 (1000자)
        chunk_overlap=200,    # 청크 간 겹치는 부분 (200자)
        separators=["\n\n", "\n", " ", ""]  # 분할 기준 (문단 > 줄 > 단어 > 문자)
    )
    docs = text_splitter.split_documents(documents)
    print("*****텍스트 분할 완료.")

    # 3단계: 한국어 임베딩 모델 로드
    # KURE-v1: 한국어 특화 임베딩 모델
    embedding_model_name = 'nlpai-lab/KURE-v1'
    embeddings = HuggingFaceEmbeddings(
        model_name=embedding_model_name,
        model_kwargs={'device': 'cpu'}  # CPU 사용 (GPU 있으면 'cuda'로 변경)
    )
    print("*****임베딩 모델 로드 완료.")

    # 4단계: PGVector를 사용해 벡터 저장소 생성
    # - 텍스트를 벡터로 변환하여 PostgreSQL에 저장
    # - 나중에 유사도 검색으로 관련 문서를 찾을 수 있음
    db = PGVector.from_documents(
        embedding=embeddings,           # 임베딩 함수
        documents=docs,                 # 분할된 문서들
        collection_name=COLLECTION_NAME, # 컬렉션명
        connection_string=CONNECTION_STRING, # DB 연결 문자열
    )

    print("*****Vector store created in PostgreSQL.")
    return db

# =============================================================================
# 스크립트 직접 실행 시
# =============================================================================
if __name__ == "__main__":
    # PDF를 벡터 데이터베이스로 변환
    create_vector_store()