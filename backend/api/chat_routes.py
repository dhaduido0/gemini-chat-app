from fastapi import APIRouter
from models.chat_models import ChatMessage, ChatResponse
from services.chat_service import ChatService
from services.translator_service import TranslationService
from services.unified_prompt_service import UnifiedPromptService

# 라우터 생성
router = APIRouter()

# 서비스 초기화
translation_service = TranslationService()
unified_prompt_service = UnifiedPromptService()
chat_service = ChatService(translation_service, unified_prompt_service)

@router.post("/api/chat", response_model=ChatResponse)
async def chat_with_gemini(request: ChatMessage):
    """챗봇과의 대화 처리 메인 함수"""
    return await chat_service.process_chat(request)
