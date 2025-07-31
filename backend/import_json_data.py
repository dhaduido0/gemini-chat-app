import json
import os
from database import get_db, add_knowledge, create_tables
from sqlalchemy.orm import Session

def import_jsonl_data(jsonl_file_path):
    """JSONL 파일에서 데이터를 읽어서 벡터 DB에 추가"""
    
    # 테이블 생성
    create_tables()
    
    # JSONL 파일 읽기
    try:
        data = []
        with open(jsonl_file_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    data.append(json.loads(line))
        print(f"✅ JSONL 파일 읽기 완료: {jsonl_file_path}")
        print(f"📊 총 {len(data)}개의 데이터 발견")
    except Exception as e:
        print(f"❌ JSONL 파일 읽기 오류: {e}")
        return
    
    # 데이터베이스에 추가
    db = next(get_db())
    try:
        count = 0
        for item in data:
            # JSONL 구조에 따라 필드명 조정
            instruction = item.get('instruction', '')
            input_text = item.get('input', '')
            output = item.get('output', '')
            
            # 질문과 답변 구성
            question = instruction
            answer = f"{input_text}\n\n답변: {output}"
            
            if question and answer:
                add_knowledge(db, "명지전문대학", question, answer)
                count += 1
                if count % 50 == 0:
                    print(f"진행률: {count}/{len(data)} ({count/len(data)*100:.1f}%)")
        
        print(f"✅ 총 {count}개의 데이터 추가 완료!")
        
    except Exception as e:
        print(f"❌ 데이터베이스 추가 오류: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    # JSONL 파일 경로
    jsonl_file_path = "mjc_data.jsonl"
    
    if os.path.exists(jsonl_file_path):
        import_jsonl_data(jsonl_file_path)
    else:
        print(f"❌ 파일을 찾을 수 없습니다: {jsonl_file_path}")
        print("JSONL 파일 경로를 확인해주세요.") 