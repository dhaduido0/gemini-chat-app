from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from dotenv import load_dotenv
from translator_service import TranslationService
from unified_prompt_service import UnifiedPromptService
from pdf_importer import create_vector_store, CONNECTION_STRING, COLLECTION_NAME
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import PGVector

# 환경 변수 로드
load_dotenv()

app = FastAPI()

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 서비스 초기화
translation_service = TranslationService()
unified_prompt_service = UnifiedPromptService()

# 벡터 스토어 초기화
vector_store = None
try:
    embeddings = HuggingFaceEmbeddings(
        model_name='nlpai-lab/KURE-v1',
        model_kwargs={'device': 'cpu'}
    )
    vector_store = PGVector(
        collection_name=COLLECTION_NAME,
        connection_string=CONNECTION_STRING,
        embedding_function=embeddings
    )
    print("✅ LangChain 벡터 스토어 연결 성공")
except Exception as e:
    print(f"⚠️ 벡터 스토어 연결 실패: {e}")
    print("📝 PDF 데이터를 먼저 import 해주세요: python pdf_importer.py")

# 대화 히스토리 저장 (메모리 기반)
chat_history = []

# 요청/응답 모델
class ChatMessage(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str
    success: bool

def get_chat_context(current_message: str) -> str:
    """대화 히스토리를 바탕으로 맥락 구성"""
    if not chat_history:
        return current_message
    
    # 최근 3개 대화만 사용 (맥락 유지하면서 메모리 절약)
    recent_history = chat_history[-3:]
    context = ""
    
    for msg in recent_history:
        context += f"사용자: {msg['user']}\n"
        context += f"챗봇: {msg['bot']}\n"
    
    context += f"사용자: {current_message}\n"
    return context

def update_chat_history(user_message: str, bot_response: str):
    """대화 히스토리 업데이트"""
    chat_history.append({
        'user': user_message,
        'bot': bot_response
    })
    
    # 최근 10개 대화만 유지 (메모리 절약)
    if len(chat_history) > 10:
        chat_history[:] = chat_history[-10:]

def search_similar_documents(query: str, top_k: int = 3) -> list:
    """LangChain 벡터 스토어에서 유사한 문서 검색"""
    if not vector_store:
        return []
    
    try:
        print(f"🔍 RAG 검색: '{query}'")
        
        # 단순 유사도 검색 (3개 문서)
        docs = vector_store.similarity_search(query, k=top_k)
        
        # 문서 내용 추출
        reference_docs = []
        for i, doc in enumerate(docs, 1):
            content = doc.page_content[:500] + "..." if len(doc.page_content) > 500 else doc.page_content
            reference_docs.append(f"문서 {i}: {content}")
            print(f"📄 문서 {i}: {content[:100]}...")
        
        print(f"✅ 선택된 문서: {len(reference_docs)}개")
        return reference_docs
        
    except Exception as e:
        print(f"❌ RAG 검색 오류: {e}")
        return []

@app.post("/api/chat", response_model=ChatResponse)
async def chat_with_gemini(request: ChatMessage):
    try:
        print(f"받은 메시지: {request.message}")
        
        # 언어 감지 및 번역
        translated_question, detected_lang, needs_translation = translation_service.detect_and_translate(request.message)
        
        # 대화 맥락 구성
        chat_context = get_chat_context(translated_question)
        print(f"대화 맥락 길이: {len(chat_context)} 문자")
        
        # # LangChain RAG로 유사한 문서 검색 (상위 3개)
        reference_docs = search_similar_documents(translated_question, top_k=3)
        
        # 통합된 프롬프트 서비스로 질문 처리 (RAG 결과 포함)
        response = unified_prompt_service.process_question(
            question=translated_question,
            reference_docs=reference_docs if reference_docs else None,
            chat_context=chat_context
        )
        
        # 번역 처리
        if needs_translation:
            response = translation_service.translate_response(response, detected_lang)
        
        # 대화 히스토리 업데이트
        update_chat_history(request.message, response)
        
        return ChatResponse(response=response, success=True)
        
    except Exception as e:
        print(f"오류 발생: {str(e)}")
        return ChatResponse(
            response=f"오류가 발생했습니다: {str(e)}", 
            success=False
        )

@app.get("/")
async def root():
    return {"message": "명지전문대학 학사 챗봇 API (LangChain RAG + 통합 프롬프트)"}

@app.post("/api/import-pdf")
async def import_pdf():
    """PDF 데이터를 벡터 스토어에 import"""
    try:
        global vector_store
        vector_store = create_vector_store()
        if vector_store:
            return {"message": "PDF import 성공!", "success": True}
        else:
            return {"message": "PDF import 실패", "success": False}
    except Exception as e:
        return {"message": f"PDF import 오류: {str(e)}", "success": False}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)