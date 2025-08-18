import os
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings # <--- 수정
from langchain_community.vectorstores import PGVector # <--- 수정
from dotenv import load_dotenv

load_dotenv()

# 데이터베이스 연결 정보 설정
CONNECTION_STRING = f"postgresql+psycopg2://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@{os.getenv('POSTGRES_HOST')}:{os.getenv('POSTGRES_PORT')}/{os.getenv('POSTGRES_DB')}"
COLLECTION_NAME = "hufs_homepage"


def create_vector_store():
    # 1. PDF 파일 로드
    pdf_path = os.path.join("data", "1stMerged.pdf")
    if not os.path.exists(pdf_path):
        print(f"Error: PDF file not found at {pdf_path}")
        return None

    loader = PyPDFLoader(pdf_path)
    documents = loader.load()
    print("*****PDF 로드 완료.")

    # 2. 텍스트 분할
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        separators=["\n\n", "\n", " ", ""]
    )
    docs = text_splitter.split_documents(documents)
    print("*****텍스트 분할 완료.")

    # 3. 임베딩 모델 로드
    embedding_model_name = 'nlpai-lab/KURE-v1'
    embeddings = HuggingFaceEmbeddings(
        model_name=embedding_model_name,
        model_kwargs={'device': 'cpu'} # GPU가 있다면 'cuda'로 변경
    )
    print("*****임베딩 모델 로드 완료.")

    # PGVector를 사용해 벡터 저장소 생성
    db = PGVector.from_documents(
        embedding=embeddings,
        documents=docs,
        collection_name=COLLECTION_NAME,
        connection_string=CONNECTION_STRING,
    )

    print("*****Vector store created in PostgreSQL.")
    return db


if __name__ == "__main__":
    create_vector_store()