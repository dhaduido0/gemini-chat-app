from fastapi import APIRouter
from pdf_importer import create_vector_store
from config.vector_store import initialize_vector_store

# 라우터 생성
router = APIRouter()

@router.post("/api/import-pdf")
async def import_pdf():
    """
    PDF 데이터를 벡터 스토어에 import
    - PDF 파일을 텍스트로 변환
    - 텍스트를 벡터로 변환하여 PostgreSQL에 저장
    - RAG 검색을 위한 데이터 준비
    """
    try:
        vector_store = create_vector_store()
        if vector_store:
            return {"message": "PDF import 성공!", "success": True}
        else:
            return {"message": "PDF import 실패", "success": False}
    except Exception as e:
        return {"message": f"PDF import 오류: {str(e)}", "success": False}
