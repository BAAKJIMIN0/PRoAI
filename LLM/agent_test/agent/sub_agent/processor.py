import os, json
from typing import Dict, List, Optional
from bson.objectid import ObjectId 
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from pymongo import MongoClient

class RAGDataProcessor:
    """RAG 데이터 처리를 위한 기본 클래스"""

    def __init__(self):
        # 현재 스크립트의 디렉토리 경로 찾기
        current_dir = os.path.dirname(os.path.abspath(__file__))
        chroma_persist_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(current_dir))), 'db', 'test')
        embedding_model = HuggingFaceEmbeddings(
            model_name="jhgan/ko-sroberta-multitask"
        )
        mongo_client = MongoClient("mongodb://localhost:27017/") # mongodb://localhost:27017/ | mongodb://mskim:1q2w3e4r@ubuntu-server.tplinkdns.com:27017
        db = mongo_client["pro"]   # 데이터베이스 이름
        self.mongoDB = db["pro"]     # 컬렉션 이름

        # Chroma 벡터 DB 초기화
        try:
            # self.vectordbA = Chroma(
            #     persist_directory=chroma_persist_dir,
            #     embedding_function=embedding_model,
            #     collection_name="RAG_A",
            # )
            self.vectordbB = Chroma(
                persist_directory=chroma_persist_dir,
                embedding_function=embedding_model,
                collection_name="RAG_B",
            )
        except Exception as e:
            print(f"VectorDB 초기화 실패: {e}")
            self.vectordbB = None

    def query_vectordb(self, query: str, purpose: str, k: int = 3) -> List[Dict]:
        """벡터 DB에서 관련 문서 검색"""
        if not self.vectordbB:
            print("VectorDB가 초기화되지 않았습니다.")
            return []

        try:
            # section 필터로 관련 문서 검색
            retriever = self.vectordbB.as_retriever(
                search_type="similarity",
                search_kwargs={"k": 10}
            )

            # 1. 10개 문서 가져오기
            docs = retriever.invoke(query)

            # 2. 섹션의 문서만 필터링
            rag_docs = [doc for doc in docs if doc.metadata.get('section') == purpose]

            # 3. 문서가 3개 이상이면 상위 3개만 선택
            if not rag_docs:
                # 필터링된 문서가 없으면, 원본 목록의 상위 3개를 선택합니다.
                final_docs = docs[:k]
            else:
                # 필터링된 문서가 있으면, 해당 문서를 사용합니다.
                final_docs = rag_docs[:k]
            
            idx_list = [doc.metadata['idx'] for doc in final_docs if doc.metadata.get('idx')]
            object_id_list = [ObjectId(doc_id) for doc_id in idx_list]
            docs = list(self.mongoDB.find({"_id": {"$in": object_id_list}}))
            
            for doc in docs:
                if '_id' in doc:
                    # ObjectId는 str() 함수를 사용하여 안전하게 문자열로 변환할 수 있습니다.
                    doc['_id'] = str(doc['_id'])
            
            return docs
        except Exception as e:
            print(f"VectorDB 검색 오류: {e}")
            return []
            
processor = RAGDataProcessor()