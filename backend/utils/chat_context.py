# =============================================================================
# 대화 히스토리 관리 (메모리 기반)
# =============================================================================
# 사용자와의 대화 내용을 저장하여 맥락을 유지
# 최근 10개 대화만 유지하여 메모리 효율성 확보
chat_history = []

def get_chat_context(current_message: str) -> str:
    """
    대화 히스토리를 바탕으로 맥락 구성
    - 최근 3개 대화만 사용하여 맥락 유지하면서 메모리 절약
    - AI가 이전 대화를 기억하고 자연스럽게 응답할 수 있게 함
    - 현재 메시지는 별도로 전달되므로 제외
    """
    if not chat_history:
        return ""  # 현재 메시지는 별도로 전달
    
    # 최근 3개 대화만 사용 (현재 메시지 제외)
    recent_history = chat_history[-3:]
    context = ""
    
    for msg in recent_history:
        context += f"사용자: {msg['user']}\n"
        context += f"챗봇: {msg['bot']}\n\n"
    
    return context.strip()

def update_chat_history(user_message: str, bot_response: str):
    """
    대화 히스토리 업데이트
    - 새로운 대화를 히스토리에 추가
    - 최근 10개 대화만 유지하여 메모리 효율성 확보
    """
    chat_history.append({
        'user': user_message,
        'bot': bot_response
    })
    
    # 최근 10개 대화만 유지 (메모리 절약)
    if len(chat_history) > 10:
        chat_history[:] = chat_history[-10:]