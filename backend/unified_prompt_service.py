from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import SystemMessage, HumanMessage
from typing import Dict, Any, List
import json

class UnifiedPromptService:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash-lite",
              model_kwargs={
                "temperature": 0.2,        # 낮은 온도로 일관된 응답
                "max_output_tokens": 150,  # 최대 출력 토큰 제한
                "top_p": 0.6,            # 일관성
                "system_instruction": """당신은 명지전문대학 학사 전문가 AI 챗봇입니다.

**핵심 정체성**: 
- 당신은 명지전문대학의 학사 관련 질문에 답변하는 AI 챗봇입니다
- 당신의 이름은 '명지전문대학 학사 챗봇'입니다

**질문 분류 및 답변 원칙**:

1. **정체성/자기소개 질문** (identity_question):
   - "너누구야", "당신은 누구", "챗봇이야", "너는 누구야" 등
   - 답변: "저는 명지전문대학 학사 챗봇입니다. 학사 관련 질문에 답변드릴 수 있습니다."

2. **학사/대학 정보 질문** (academic_question):
   - "총장 누구야", "학교 위치", "학과 정보", "입학 조건", "졸업 요건", "수업료", "장학금","휴학 규정" 등
   - 제공된 참고 문서를 바탕으로 정확하게 답변
   - 참고 문서에 없는 정보는 "죄송합니다. 해당 정보를 확인할 수 없습니다."라고 답변

3. **일반 대화/인사** (general_chat):
   - "안녕하세요", "고마워", "잘 있어", "반가워","안녕" 등
   - 간결하고 친근하게 인사만 하세요.
   - 불필요한 상세한 설명은 피하세요.

4. **오류/불만/기술적 문제** (error_complaint):
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
질문에 대한 직접적인 답변만 제공하세요. JSON이나 특별한 형식은 사용하지 마세요."""
            }
        )
    
    def process_question(self, question: str, reference_docs: List[str] = None, chat_context: str = None) -> str:
        """
        질문을 처리하고 적절한 답변 생성
        
        Args:
            question: 사용자 질문
            reference_docs: 참고 문서 리스트 (RAG 검색 결과)
            chat_context: 이전 대화 맥락
            
        Returns:
            답변 텍스트
        """
        try:
            print(f"\n🔍 프롬프트 구성 시작:")
            print(f"   원본 질문: {question}")
            
            # 프롬프트 구성
            prompt_parts = []
            
            # 참고 문서가 있으면 추가
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
            
            # 대화 맥락이 있으면 추가
            if chat_context:
                context_preview = chat_context[:100] + "..." if len(chat_context) > 100 else chat_context
                print(f"   💬 대화 맥락 포함: {context_preview}")
                prompt_parts.append(f"대화 맥락:\n{chat_context}")
                prompt_parts.append("")
            else:
                print(f"   💬 대화 맥락: 없음")
            
            # 현재 질문 추가
            print(f"   ❓ 현재 질문: {question}")
            prompt_parts.append(f"현재 질문: {question}")
            prompt_parts.append("")
            
            # 지시사항 추가
            if reference_docs:
                print(f"   📋 지시사항: RAG 기반 답변 모드")
                prompt_parts.append("위 참고 정보를 바탕으로 명지전문대학에 대해 정확하고 친근하게 답변해주세요.")
                prompt_parts.append("참고 정보에 정확한 답변이 없다면, '죄송합니다. 해당 정보를 확인할 수 없습니다.'라고 답변해주세요.")
            else:
                print(f"   📋 지시사항: 맥락 기반 답변 모드")
                prompt_parts.append("위 대화 맥락을 바탕으로 사용자의 질문에 답변해주세요.")
                prompt_parts.append("맥락을 파악할 수 없거나 명지전문대학과 관련이 없다면 '죄송합니다. 해당 정보를 확인할 수 없습니다.'라고 답변해주세요.")
            
            # 통합된 프롬프트 생성
            unified_prompt = "\n".join(prompt_parts)
            
            print(f"🔀 통합 프롬프트 생성 완료:")
            print(f"   📏 총 길이: {len(unified_prompt)} 문자")
            print(f"   📝 프롬프트 미리보기:")
            print(f"      {unified_prompt[:200]}...")
            
            # LangChain LLM 호출 - 올바른 형식 사용
            print(f"🚀 LLM 호출 시작...")
            messages = [HumanMessage(content=unified_prompt)]
            response = self.llm.invoke(messages)
            
            if response.content:
                print(f"✅ 답변 생성 완료:")
                print(f"   📏 응답 길이: {len(response.content)} 문자")
                print(f"   💬 응답 미리보기: {response.content[:100]}...")
                return response.content
            else:
                print(f"❌ 응답 없음")
                return "죄송합니다. 응답을 생성할 수 없습니다."
                
        except Exception as e:
            print(f"❌ 통합 프롬프트 처리 오류: {e}")
            return f"죄송합니다. 오류가 발생했습니다: {str(e)}"
    
    def get_identity_response(self) -> str:
        """정체성 질문에 대한 기본 응답"""
        return "저는 명지전문대학 학사 챗봇입니다. 학사 관련 질문에 답변드릴 수 있습니다."