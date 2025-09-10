# =============================================================================
# 명지전문대학 학사 챗봇 API 서버 (FastAPI + LangChain RAG)
# =============================================================================
# 주요 기능:
# 1. 다국어 번역 지원 (한국어, 미얀마어, 영어, 베트남어)
# 2. LangChain RAG를 통한 PDF 문서 기반 답변
# 3. 대화 히스토리 관리
# 4. Gemini 2.5 Flash Lite 모델 활용
# =============================================================================

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv

# 모듈화된 컴포넌트들 import
from api.chat_routes import router as chat_router
from api.pdf_routes import router as pdf_router
from config.vector_store import initialize_vector_store

# 환경 변수 로드 (.env 파일에서 API 키, DB 설정 등)
load_dotenv()

# FastAPI 애플리케이션 초기화
app = FastAPI()

# CORS 설정 - 프론트엔드에서 API 호출 허용
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],        # 모든 도메인에서 접근 허용
    allow_credentials=True,     # 쿠키/인증 정보 허용
    allow_methods=["*"],        # 모든 HTTP 메서드 허용
    allow_headers=["*"],        # 모든 헤더 허용
)

# 벡터 스토어 초기화
initialize_vector_store()

# 라우터 등록
app.include_router(chat_router)
app.include_router(pdf_router)

@app.get("/")
async def root():
    """API 서버 상태 확인"""
    return {"message": "명지전문대학 학사 챗봇 API (LangChain RAG + 통합 프롬프트)"}

# =============================================================================
# 서버 실행
# =============================================================================
if __name__ == "__main__":
    import uvicorn
    # FastAPI 서버 실행 (모든 IP에서 접근 가능, 포트 8000)
    uvicorn.run(app, host="0.0.0.0", port=8000)