from typing import List
from models.chat_models import ChatMessage, ChatResponse
from services.translator_service import TranslationService
from services.unified_prompt_service import UnifiedPromptService
from utils.rag_utils import search_similar_documents
from utils.chat_context import get_chat_context, update_chat_history

class ChatService:
    def __init__(self, translation_service: TranslationService, unified_prompt_service: UnifiedPromptService):
        self.translation_service = translation_service
        self.unified_prompt_service = unified_prompt_service
    
    async def process_chat(self, request: ChatMessage) -> ChatResponse:
        """
        챗봇과의 대화 처리 메인 함수
        처리 순서:
        1. 언어 감지 및 번역 (다국어 지원)
        2. 대화 맥락 구성 (이전 대화 기억)
        3. RAG 검색 (관련 문서 찾기)
        4. AI 답변 생성 (Gemini 모델)
        5. 답변 번역 (사용자 언어로)
        6. 대화 히스토리 업데이트
        """
        try:
            print(f"받은 메시지: {request.message}")
            
            # 1단계: 언어 감지 및 번역 (다국어 지원)
            translated_question, detected_lang, needs_translation = self.translation_service.detect_and_translate(request.message)
            
            # 2단계: 대화 맥락 구성 (이전 대화 기억)
            chat_context = get_chat_context(translated_question)
            print(f"대화 맥락 길이: {len(chat_context)} 문자")
            
            # 3단계: LangChain RAG로 유사한 문서 검색 (상위 3개)
            reference_docs = search_similar_documents(translated_question, top_k=3)
            
            # 4단계: 통합된 프롬프트 서비스로 질문 처리 (RAG 결과 포함)
            response = self.unified_prompt_service.process_question(
                question=translated_question,
                reference_docs=reference_docs if reference_docs else None,
                chat_context=chat_context
            )
            
            # 5단계: 답변 번역 (사용자 언어로)
            if needs_translation:
                response = self.translation_service.translate_response(response, detected_lang)
            
            # 6단계: 대화 히스토리 업데이트
            update_chat_history(request.message, response)
            
            return ChatResponse(response=response, success=True)
            
        except Exception as e:
            print(f"오류 발생: {str(e)}")
            return ChatResponse(
                response=f"오류가 발생했습니다: {str(e)}", 
                success=False
            )
