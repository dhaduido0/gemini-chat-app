from googletrans import Translator
from typing import Tuple

class TranslationService:
    def __init__(self):
        self.translator = Translator()
    # 입력 번역 함수
    def detect_and_translate(self, text: str) -> Tuple[str, str, bool]:
        """
        텍스트의 언어를 감지하고 필요시 한국어로 번역
        
        Args:
            text: 입력 텍스트
            
        Returns:
            Tuple[번역된_텍스트, 원본_언어, 번역_필요여부]
        """
        try:
            detected_lang = self.translator.detect(text).lang
            print(f" 언어 감지: {detected_lang}")
            
            # 미얀마어, 영어, 베트남어인 경우 한국어로 번역
            if detected_lang in ['my', 'en', 'vi']:
                translated_text = self.translator.translate(text, dest='ko').text
                print(f"{detected_lang} 언어 감지됨: {text} -> {translated_text}")
                return translated_text, detected_lang, True
            
            # 한국어는 그대로 유지
            print(f"번역 불필요: {detected_lang} 언어는 그대로 유지")
            return text, detected_lang, False
            
        except Exception as e:
            print(f"번역 오류: {str(e)}")
            return text, 'unknown', False
    # 출력 번역 함수
    def translate_response(self, text: str, target_lang: str) -> str:
        """
        응답 텍스트를 사용자 언어로 번역
        
        Args:
            text: 한국어로 생성된 AI 응답
            target_lang: 사용자가 입력한 언어 코드
                        - 'en': 영어 사용자 → 영어로 번역
                        - 'my': 미얀마어 사용자 → 미얀마어로 번역
                        - 'vi': 베트남어 사용자 → 베트남어로 번역
                        - 'ko': 한국어 사용자 → 번역 없음
            
        Returns:
            사용자 언어로 번역된 응답
        """
        try:
            # 영어, 미얀마어, 베트남어 사용자에게 번역
            if target_lang in ['en', 'my', 'vi']:
                translated = self.translator.translate(text, dest=target_lang).text
                print(f"답변 번역: {text} -> {translated}")
                return translated
            
            # 한국어는 그대로 반환
            print(f"번역 불필요: {target_lang} 언어는 그대로 반환")
            return text
            
        except Exception as e:
            print(f"답변 번역 오류: {str(e)}")
            return text