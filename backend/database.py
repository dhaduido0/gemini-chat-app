import os
from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pgvector.sqlalchemy import Vector
from sentence_transformers import SentenceTransformer
import numpy as np

# 환경 변수에서 DB 설정 가져오기 (로컬 PostgreSQL 사용)
DB_HOST = os.getenv('DB_HOST', 'localhost')  # 로컬 PostgreSQL 사용
DB_PORT = os.getenv('DB_PORT', '5432')
DB_NAME = os.getenv('DB_NAME', 'academic_chatbot')
DB_USER = os.getenv('DB_USER', 'academic_chatbot')
DB_PASSWORD = os.getenv('DB_PASSWORD', '1234')

# PostgreSQL 연결 문자열
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class AcademicKnowledge(Base):
    __tablename__ = "academic_knowledge"
    
    id = Column(Integer, primary_key=True, index=True)
    category = Column(String(100), index=True)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    embedding = Column(Vector(384))  # pgvector 사용

# 임베딩 모델
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    Base.metadata.create_all(bind=engine)

def get_text_embedding(text):
    embedding = embedding_model.encode(text)
    return embedding.tolist()

def search_similar_questions(db, query, top_k=3, similarity_threshold=0.7):
    # 벡터 유사도 검색
    query_embedding = get_text_embedding(query)
    
    # 모든 데이터 가져오기
    all_items = db.query(AcademicKnowledge).all()
    
    # 유사도 계산
    similarities = []
    for item in all_items:
        # 코사인 유사도 계산
        import numpy as np
        vec1 = np.array(item.embedding)
        vec2 = np.array(query_embedding)
        
        # 코사인 유사도
        dot_product = np.dot(vec1, vec2)
        norm_a = np.linalg.norm(vec1)
        norm_b = np.linalg.norm(vec2)
        
        if norm_a > 0 and norm_b > 0:
            similarity = dot_product / (norm_a * norm_b)
        else:
            similarity = 0
            
        similarities.append((item, similarity))
    
    # 유사도 기준으로 정렬 (높은 순)
    similarities.sort(key=lambda x: x[1], reverse=True)
    
    # 상위 3개만 출력하고 필터링
    filtered_results = []
    print(f"상위 3개 유사도:")
    for i, (item, similarity) in enumerate(similarities[:3]):
        print(f"{i+1}. 질문: {item.question[:50]}... 유사도: {similarity:.3f}")
        if similarity >= similarity_threshold:
            filtered_results.append(item)
    
    return filtered_results

def add_knowledge(db, category, question, answer):
    embedding = get_text_embedding(question)
    
    knowledge = AcademicKnowledge(
        category=category, 
        question=question, 
        answer=answer,
        embedding=embedding
    )
    
    db.add(knowledge)
    db.commit()
    return knowledge 