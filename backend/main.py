from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import google.generativeai as genai
import os
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from database import get_db, search_similar_questions

# 환경 변수 로드
load_dotenv()

# Gemini API 설정
api_key = os.getenv('GEMINI_API_KEY')
print(f"API 키 확인: {api_key[:10]}..." if api_key else "API 키 없음")
genai.configure(api_key=api_key)
model = genai.GenerativeModel(
    'gemini-2.5-flash',
    system_instruction="""당신은 명지전문대학 학사 전문가입니다. 

    답변 원칙:
    1. 명지전문대학 관련 질문에 정확히 답변
    2. 이전 대화 맥락을 기억하고 유연하게 응답
    3. 사용자가 간단히 말해도 정확한 의미를 파악
    4. 관련 정보가 부족해도 일반적인 학사 원칙으로 안내
    5. 친근하고 이해하기 쉬운 말투 사용
 

    자연스러운 대화 예시:
    - "왜?" → "이전 대화 맥락을 바탕으로 추측하여 답변"
    - "전과" → "학과 전과" 관련 질문으로 이해
    - "조기취업형" → "조기취업형 계약학과" 관련 질문으로 이해
    - "총장" → "명지전문대학 총장" 관련 질문으로 이해

    명지전문대학과 전혀 관련이 없는 질문에만 "죄송합니다. 명지전문대학 관련 질문에만 답변드릴 수 있습니다."라고 답변해주세요."""
)

app = FastAPI()

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 대화 히스토리 저장 (메모리 기반)
chat_history = {}

# 요청/응답 모델
class ChatMessage(BaseModel):
    message: str
    session_id: str = "default"  # 세션 구분용

class ChatResponse(BaseModel):
    response: str
    success: bool

def get_chat_context(session_id: str, current_message: str) -> str:
    """대화 히스토리를 바탕으로 맥락 구성"""
    if session_id not in chat_history:
        return current_message
    
    # 최근 3개 대화만 사용 (맥락 유지하면서 메모리 절약)
    recent_history = chat_history[session_id][-3:]
    context = ""
    
    for msg in recent_history:
        context += f"사용자: {msg['user']}\n"
        context += f"챗봇: {msg['bot']}\n"
    
    context += f"사용자: {current_message}\n"
    return context

def update_chat_history(session_id: str, user_message: str, bot_response: str):
    """대화 히스토리 업데이트"""
    if session_id not in chat_history:
        chat_history[session_id] = []
    
    chat_history[session_id].append({
        'user': user_message,
        'bot': bot_response
    })
    
    # 히스토리가 너무 길어지면 오래된 것부터 삭제 (최대 10개 유지)
    if len(chat_history[session_id]) > 10:
        chat_history[session_id] = chat_history[session_id][-10:]



@app.post("/api/chat", response_model=ChatResponse)
async def chat_with_gemini(request: ChatMessage, db: Session = Depends(get_db)):
    try:
        print(f"받은 메시지: {request.message}")
        
        # 대화 맥락 구성
        chat_context = get_chat_context(request.session_id, request.message)
        print(f"대화 맥락 길이: {len(chat_context)} 문자")
        
        # RAG: PostgreSQL에서 유사한 질문 검색 (현재 질문만)
        similar_questions = search_similar_questions(db, request.message, top_k=3)
        print(f"검색된 질문 수: {len(similar_questions)}")
        
        # 검색된 정보 구성
        relevant_knowledge = ""
        if similar_questions:
            relevant_knowledge = "참고할 수 있는 학사 정보:\n\n"
            for i, item in enumerate(similar_questions, 1):
                relevant_knowledge += f"{i}. 질문: {item.question}\n답변: {item.answer}\n\n"
            print(f"관련 정보 있음: {len(relevant_knowledge)} 문자")
        else:
            print("관련 정보 없음")
        
        # 사용자 메시지에 RAG 정보 추가
        if relevant_knowledge:
            enhanced_message = f"""참고 정보:
{relevant_knowledge}

대화 맥락:
{chat_context}

현재 질문: {request.message}

위 참고 정보를 바탕으로 명지전문대학에 대해 정확하고 친근하게 답변해주세요. 
참고 정보에 정확한 답변이 없다면, 일반적인 학사 원칙을 안내해주세요."""
        else:
            enhanced_message = f"""대화 맥락:
{chat_context}

현재 질문: {request.message}

이 질문이 명지전문대학과 관련이 있다면, 이전 대화 맥락을 고려하여 답변해주세요.
예를 들어 "전과"에 대해 물어보면 일반적인 전과 절차를, "총장"에 대해 물어보면 대학 총장의 역할을 설명해주세요.

만약 질문이 너무 간단하거나 맥락이 불분명하다면 (예: "왜?", "어떻게?"), 
이전 대화 맥락을 바탕으로 추측하여 답변해주세요.

명지전문대학과 전혀 관련이 없다면 "죄송합니다. 명지전문대학 관련 질문에만 답변드릴 수 있습니다."라고 답변해주세요."""

        print(f"Gemini에 전달할 메시지 길이: {len(enhanced_message)} 문자")
        
        # 메시지가 너무 길면 잘라내기
        if len(enhanced_message) > 8000:
            enhanced_message = enhanced_message[:8000] + "..."
            print(f"메시지가 너무 길어서 잘랐습니다: {len(enhanced_message)} 문자")

        # Gemini API 호출
        try:
            # 자연스러운 대화를 위한 설정
            response = model.generate_content(
                enhanced_message,
               generation_config={
    "temperature": 0.4,      # 정확성 중시
    "top_p": 0.8,           # 적당한 다양성
    "max_output_tokens": 2500  # 충분한 설명
}
            )
            
            print(f"Gemini 응답: {response.text if response.text else '응답 없음'}")
            
            if response.text:
                # 대화 히스토리 업데이트
                update_chat_history(request.session_id, request.message, response.text)
                return ChatResponse(response=response.text, success=True)
            else:
                return ChatResponse(response="죄송합니다. 응답을 생성할 수 없습니다.", success=False)
                
        except Exception as e:
            print(f"Gemini API 오류: {str(e)}")
            return ChatResponse(response=f"Gemini API 오류: {str(e)}", success=False)
            
    except Exception as e:
        print(f"오류 발생: {str(e)}")
        return ChatResponse(
            response=f"오류가 발생했습니다: {str(e)}", 
            success=False
        )

@app.get("/")
async def root():
    return {"message": "명지전문대학 학사 챗봇 API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 