# =============================================================================
# 다국어 번역 서비스 모듈
# =============================================================================
# 주요 기능:
# 1. 입력 텍스트의 언어 자동 감지
# 2. 한국어가 아닌 언어를 한국어로 번역
# 3. AI 답변을 사용자 언어로 번역
# 지원 언어: 한국어, 미얀마어, 영어, 베트남어
# =============================================================================

from googletrans import Translator
from typing import Tuple

class TranslationService:
    """
    다국어 번역을 담당하는 서비스 클래스
    - Google Translate API를 사용하여 언어 감지 및 번역 수행
    - 챗봇의 다국어 지원을 위한 핵심 모듈
    """
    
    def __init__(self):
        # Google Translate API 초기화
        self.translator = Translator()
    
    # =============================================================================
    # 입력 텍스트 번역 함수
    # =============================================================================
    def detect_and_translate(self, text: str) -> Tuple[str, str, bool]:
        """
        사용자 입력 텍스트의 언어를 감지하고 필요시 한국어로 번역
        
        처리 과정:
        1. Google Translate API로 언어 감지
        2. 미얀마어(my), 영어(en), 베트남어(vi)인 경우 한국어로 번역
        3. 한국어(ko)인 경우 그대로 유지
        
        Args:
            text: 사용자가 입력한 텍스트
            
        Returns:
            Tuple[번역된_텍스트, 원본_언어코드, 번역_필요여부]
            - 번역된_텍스트: 한국어로 번역된 텍스트 (또는 원본)
            - 원본_언어코드: 감지된 언어 코드 (ko, my, en, vi 등)
            - 번역_필요여부: 번역이 수행되었는지 여부 (True/False)
        """
        try:
            # 1단계: 언어 자동 감지
            detected_lang = self.translator.detect(text).lang
            print(f" 언어 감지: {detected_lang}")
            
            # 2단계: 지원 언어인 경우 한국어로 번역
            # 미얀마어(my), 영어(en), 베트남어(vi) → 한국어(ko)
            if detected_lang in ['my', 'en', 'vi']:
                translated_text = self.translator.translate(text, dest='ko').text
                print(f"{detected_lang} 언어 감지됨: {text} -> {translated_text}")
                return translated_text, detected_lang, True
            
            # 3단계: 한국어는 그대로 유지
            print(f"번역 불필요: {detected_lang} 언어는 그대로 유지")
            return text, detected_lang, False
            
        except Exception as e:
            print(f"번역 오류: {str(e)}")
            # 오류 발생 시 원본 텍스트 그대로 반환
            return text, 'unknown', False
    
    # =============================================================================
    # 출력 텍스트 번역 함수
    # =============================================================================
    def translate_response(self, text: str, target_lang: str) -> str:
        """
        AI가 생성한 한국어 답변을 사용자 언어로 번역
        
        처리 과정:
        1. 사용자가 입력한 언어 코드 확인
        2. 영어, 미얀마어, 베트남어 사용자에게는 해당 언어로 번역
        3. 한국어 사용자에게는 번역 없이 그대로 반환
        
        Args:
            text: AI가 생성한 한국어 답변
            target_lang: 사용자가 입력한 언어 코드
                        - 'en': 영어 사용자 → 영어로 번역
                        - 'my': 미얀마어 사용자 → 미얀마어로 번역
                        - 'vi': 베트남어 사용자 → 베트남어로 번역
                        - 'ko': 한국어 사용자 → 번역 없음
            
        Returns:
            str: 사용자 언어로 번역된 응답 (또는 원본)
        """
        try:
            # 1단계: 지원 언어 사용자에게 번역 제공
            # 영어, 미얀마어, 베트남어 사용자 → 해당 언어로 번역
            if target_lang in ['en', 'my', 'vi']:
                translated = self.translator.translate(text, dest=target_lang).text
                print(f"답변 번역: {text} -> {translated}")
                return translated
            
            # 2단계: 한국어 사용자에게는 번역 없이 그대로 반환
            print(f"번역 불필요: {target_lang} 언어는 그대로 반환")
            return text
            
        except Exception as e:
            print(f"답변 번역 오류: {str(e)}")
            # 오류 발생 시 원본 텍스트 그대로 반환
            return text