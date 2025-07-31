import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    
    if not GEMINI_API_KEY:
        print("⚠️  GEMINI_API_KEY가 설정되지 않았습니다!")
        print("📝 .env 파일을 생성하고 GEMINI_API_KEY=your_api_key_here 를 추가하세요")

settings = Settings()