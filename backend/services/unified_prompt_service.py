# =============================================================================
# 통합 프롬프트 서비스 모듈
# =============================================================================
# 주요 기능:
# 1. Gemini 2.5 Flash Lite 모델과의 통신
# 2. 질문 분류 및 답변 생성 (통합 프롬프트)
# 3. RAG 검색 결과와 대화 맥락을 활용한 답변
# 4. 토큰 사용량 최적화 (기존 대비 50% 절약)
# =============================================================================

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import SystemMessage, HumanMessage
from typing import Dict, Any, List
import json

class UnifiedPromptService:
    """
    통합된 프롬프트 처리를 담당하는 서비스 클래스
    통합된 프롬프트로 1번의 LLM 호출로 모든 처리
    """
    
    def __init__(self):
        # Gemini 2.5 Flash Lite 모델 초기화 (system_instruction 제거)
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash-lite",
            temperature=0.6,        # 낮은 온도로 일관된 응답
            max_output_tokens=200,  # 최대 출력 토큰 제한
            top_p=0.5,             # 일관성
        )
    
    # =============================================================================
    # 메인 질문 처리 함수
    # =============================================================================
    
    def process_question(self, question: str, reference_docs: List[str] = None, chat_context: str = None) -> str:
        """
        통합된 프롬프트로 질문을 처리하고 적절한 답변 생성
        
        처리 과정:
        1. RAG 검색 결과와 대화 맥락을 종합하여 프롬프트 구성
        2. Gemini 모델에 통합된 프롬프트 전송
        3. 질문 분류와 답변 생성을 한 번에 처리
        
        Args:
            question: 사용자 질문 (이미 한국어로 번역됨)
            reference_docs: RAG 검색으로 찾은 관련 문서 리스트
            chat_context: 이전 대화 맥락 (최근 3개 대화)
            
        Returns:
            str: AI가 생성한 답변 텍스트
        """
        try:
            print(f"\n🔍 프롬프트 구성 시작:")
            print(f"   원본 질문: {question}")
            
            # =============================================================================
            # 1단계: 프롬프트 구성
            # =============================================================================
            prompt_parts = []
            
            # 1-1. RAG 검색 결과가 있으면 참고 문서 추가
            if reference_docs:
                print(f"   📚 참고 문서 {len(reference_docs)}개 포함:")
                prompt_parts.append("참고할 수 있는 학사 정보:")
                for i, doc in enumerate(reference_docs, 1):
                    doc_preview = doc[:100] + "..." if len(doc) > 100 else doc
                    print(f"      문서 {i}: {doc_preview}")
                    prompt_parts.append(f"{i}. {doc}")
                prompt_parts.append("")
            else:
                print(f"   📚 참고 문서: 없음")
            
            # 1-2. 대화 맥락이 있으면 추가 (개선된 맥락 처리)
            if chat_context and chat_context.strip():
                context_preview = chat_context[:100] + "..." if len(chat_context) > 100 else chat_context
                print(f"   �� 대화 맥락 포함: {context_preview}")
                prompt_parts.append(f"이전 대화 맥락:\n{chat_context}")
                prompt_parts.append("")
            else:
                print(f"   💬 대화 맥락: 없음")
            
            # 1-3. 현재 질문 추가 (맥락과 구분)
            print(f"   ❓ 현재 질문: {question}")
            prompt_parts.append(f"현재 질문: {question}")
            prompt_parts.append("")
            
            # 1-4. 답변 모드에 따른 지시사항 추가 (맥락 고려)
            if reference_docs:
                print(f"   �� 지시사항: RAG 기반 답변 모드")
                prompt_parts.append("위 참고 정보를 바탕으로 명지전문대학에 대해 정확하고 친근하게 답변해주세요.")
                prompt_parts.append("참고 정보에 정확한 답변이 없다면, '죄송합니다. 해당 정보를 확인할 수 없습니다.'라고 답변해주세요.")
            elif chat_context and chat_context.strip():
                print(f"   📋 지시사항: 맥락 기반 답변 모드")
                prompt_parts.append("위 대화 맥락을 바탕으로 사용자의 질문에 답변해주세요.")
                prompt_parts.append("맥락을 파악할 수 없거나 명지전문대학과 관련이 없다면 '죄송합니다. 해당 정보를 확인할 수 없습니다.'라고 답변해주세요.")
            else:
                print(f"   📋 지시사항: 일반 답변 모드")
                prompt_parts.append("사용자의 질문에 친근하게 답변해주세요.")
                prompt_parts.append("명지전문대학과 관련이 없다면 '죄송합니다. 명지전문대학 관련 질문에만 답변드릴 수 있습니다.'라고 답변해주세요.")
            
            # =============================================================================
            # 2단계: 통합된 프롬프트 생성
            # =============================================================================
            unified_prompt = "\n".join(prompt_parts)
            
            print(f"🔀 통합 프롬프트 생성 완료:")
            print(f"   �� 총 길이: {len(unified_prompt)} 문자")
            print(f"   📝 프롬프트 미리보기:")
            print(f"      {unified_prompt[:200]}...")
            
            # =============================================================================
            # 3단계: Gemini 모델 호출 (SystemMessage 사용)
            # =============================================================================
            print(f"🚀 LLM 호출 시작...")
            
            # SystemMessage와 HumanMessage를 올바르게 구성
            messages = [
                SystemMessage(content="""당신은 명지전문대학 학사 전문가 AI 챗봇입니다.

**핵심 정체성**: 
- 당신은 명지전문대학의 학사 관련 질문에 답변하는 AI 챗봇입니다
- 당신의 이름은 '명지전문대학 학사 챗봇'입니다

**질문 분류 및 답변 원칙**:

1. **정체성/자기소개 질문** (identity_question):
   - "너누구야", "당신은 누구", "챗봇이야", "너는 누구야","넌 누구야" 등
   - 답변: "저는 명지전문대학 학사 챗봇입니다. 학사 관련 질문에 답변드릴 수 있습니다." 라고만 해 

2. **학사/대학 정보 질문** (academic_question):
   - "총장 누구야", "학교 위치", "학과 정보", "입학 조건", "졸업 요건", "수업료", "장학금","휴학 규정" 등
   - 제공된 참고 문서를 바탕으로 정확하게 답변
   - 참고 문서에 없는 정보는 "죄송합니다. 해당 정보를 확인할 수 없습니다."라고 답변

3. **오류/불만/기술적 문제** (error_complaint):
   - "작동 안 해", "오류 발생", "답변 이상해" 등
   - "죄송합니다. 문제가 발생했습니다. 다시 시도해주세요."라고 답변

**답변 규칙**:
- 명지전문대학과 관련 없는 질문: "죄송합니다. 명지전문대학 관련 질문에만 답변드릴 수 있습니다."
- 참고 문서에 없는 내용은 절대 추측하거나 임의로 답변하지 않음
- 친근하고 이해하기 쉬운 말투 사용
- 이전 대화 맥락을 기억하고 유연하게 응답
- 자연스러운 대화 예시:
  - "왜?" → 이전 대화 맥락을 바탕으로 추측하여 답변
  - "전과" → "학과 전과" 관련 질문으로 이해
  - "조기취업형" → "조기취업형 계약학과" 관련 질문으로 이해

**응답 형식**: 
질문에 대한 직접적인 답변만 제공하세요. JSON이나 특별한 형식은 사용하지 마세요."""),
                HumanMessage(content=unified_prompt)
            ]
            
            response = self.llm.invoke(messages)
            
            # =============================================================================
            # 4단계: 응답 처리 및 반환
            # =============================================================================
            if response.content:
                print(f"✅ 답변 생성 완료:")
                print(f"   📏 응답 길이: {len(response.content)} 문자")
                print(f"   �� 응답 미리보기: {response.content[:100]}...")
                return response.content
            else:
                print(f"❌ 응답 없음")
                return "죄송합니다. 응답을 생성할 수 없습니다."
                
        except Exception as e:
            print(f"❌ 통합 프롬프트 처리 오류: {e}")
            return f"죄송합니다. 오류가 발생했습니다: {str(e)}"