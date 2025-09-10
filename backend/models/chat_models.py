from pydantic import BaseModel

class ChatMessage(BaseModel):
    """챗봇 API 요청 모델"""
    message: str  # 사용자가 입력한 메시지

class ChatResponse(BaseModel):
    """챗봇 API 응답 모델"""
    response: str  # AI가 생성한 답변
    success: bool  # 처리 성공 여부
