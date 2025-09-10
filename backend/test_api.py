#!/usr/bin/env python3
"""
API 테스트 코드 - 현재 main.py와 pdf_importer.py에 맞춤
"""

import requests
import json
import time

# API 기본 URL
BASE_URL = "http://localhost:8000"

def test_health_check():
    """헬스 체크 테스트"""
    print("🏥 헬스 체크 테스트...")
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            print(f"✅ 성공: {response.json()}")
            return True
        else:
            print(f"❌ 실패 (상태코드: {response.status_code})")
            return False
    except Exception as e:
        print(f"❌ 오류: {e}")
        return False

def test_chat_api(message: str):
    """채팅 API 테스트"""
    print(f"\n💬 채팅 API 테스트...")
    print(f"메시지: {message}")
    
    # 요청 데이터
    data = {
        "message": message
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/chat",
            headers={"Content-Type": "application/json"},
            data=json.dumps(data)
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 성공 (상태코드: {response.status_code})")
            print(f"응답: {result['response']}")
            print(f"성공 여부: {result['success']}")
            return True
        else:
            print(f"❌ 실패 (상태코드: {response.status_code})")
            print(f"오류: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 오류: {e}")
        return False

def test_invalid_requests():
    """잘못된 요청 테스트"""
    print(f"\n⚠️ 잘못된 요청 테스트...")
    
    # 1. message 누락
    print("\n1️⃣ message 누락 테스트")
    data = {}
    response = requests.post(
        f"{BASE_URL}/api/chat",
        headers={"Content-Type": "application/json"},
        data=json.dumps(data)
    )
    print(f"상태코드: {response.status_code}")
    print(f"응답: {response.text}")
    
    # 2. 빈 message
    print("\n2️⃣ 빈 message 테스트")
    data = {"message": ""}
    response = requests.post(
        f"{BASE_URL}/api/chat",
        headers={"Content-Type": "application/json"},
        data=json.dumps(data)
    )
    print(f"상태코드: {response.status_code}")
    print(f"응답: {response.text}")
    
    # 3. 빈 JSON
    print("\n3️⃣ 빈 JSON 테스트")
    response = requests.post(
        f"{BASE_URL}/api/chat",
        headers={"Content-Type": "application/json"},
        data="{}"
    )
    print(f"상태코드: {response.status_code}")
    print(f"응답: {response.text}")

def test_conversation_flow():
    """대화 흐름 테스트"""
    print(f"\n🔄 대화 흐름 테스트...")
    
    # 1. 첫 번째 질문
    print(f"\n1️⃣ 첫 번째 질문")
    test_chat_api("안녕하세요")
    
    # 2. 두 번째 질문
    print(f"\n2️⃣ 두 번째 질문")
    test_chat_api("한국외국어대학교에 대해 알려주세요")
    
    # 3. 세 번째 질문
    print(f"\n3️⃣ 세 번째 질문")
    test_chat_api("입학 조건은 어떻게 되나요?")

def test_different_conversations():
    """다른 대화 테스트"""
    print(f"\n🆔 다른 대화 테스트...")
    
    # 첫 번째 대화
    print(f"\n📱 첫 번째 대화")
    test_chat_api("안녕하세요")
    
    # 두 번째 대화
    print(f"\n💻 두 번째 대화")
    test_chat_api("안녕하세요")
    
    # 첫 번째 대화에 다시 질문
    print(f"\n📱 첫 번째 대화에 다시 질문")
    test_chat_api("졸업 요건은 무엇인가요?")

def main():
    """메인 테스트 함수"""
    print("🚀 수동 채팅 테스트 시작")
    print("=" * 50)
    
    # 1. 헬스 체크
    if not test_health_check():
        print("❌ 서버가 실행되지 않았습니다. main.py를 먼저 실행하세요.")
        return
    
    print("✅ 서버 연결 성공!")
    print("\n💬 수동 채팅 모드")
    print("종료하려면 'quit' 또는 'exit'를 입력하세요.")
    print("=" * 50)
    
    # 2. 수동 채팅 루프
    while True:
        try:
            # 사용자 입력
            message = input("\n💭 질문을 입력하세요: ").strip()
            
            # 종료 조건
            if message.lower() in ['quit', 'exit', '종료', '끝']:
                print("👋 채팅을 종료합니다.")
                break
            
            if not message:
                print("⚠️ 메시지를 입력해주세요.")
                continue
            
            # API 호출
            print(f"\n🔄 API 호출 중...")
            test_chat_api(message)
            
        except KeyboardInterrupt:
            print("\n\n👋 Ctrl+C로 채팅을 종료합니다.")
            break
        except Exception as e:
            print(f"❌ 오류 발생: {e}")
            continue
    
    print("\n🎉 채팅 테스트 완료!")

if __name__ == "__main__":
    main()
