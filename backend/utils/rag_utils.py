from typing import List
from config.vector_store import get_vector_store

def search_similar_documents(query: str, top_k: int = 3) -> List[str]:
    """
    LangChain 벡터 스토어에서 유사한 문서 검색
    - 사용자 질문과 유사한 PDF 문서 조각들을 찾아서 반환
    - AI가 정확한 답변을 생성할 수 있도록 참고 자료 제공
    """
    vector_store = get_vector_store()
    if not vector_store:
        return []
    
    try:
        print(f"🔍 RAG 검색: '{query}'")
        
        # 벡터 유사도 검색으로 관련 문서 찾기 (상위 3개)
        docs = vector_store.similarity_search(query, k=top_k)
        
        # 문서 내용을 참고 자료 형태로 변환
        reference_docs = []
        for i, doc in enumerate(docs, 1):
            # 문서 내용이 너무 길면 500자로 제한
            content = doc.page_content[:500] + "..." if len(doc.page_content) > 500 else doc.page_content
            reference_docs.append(f"문서 {i}: {content}")
            print(f"📄 문서 {i}: {content[:100]}...")
        
        print(f"✅ 선택된 문서: {len(reference_docs)}개")
        return reference_docs
        
    except Exception as e:
        print(f"❌ RAG 검색 오류: {e}")
        return []
