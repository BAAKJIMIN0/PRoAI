from langchain.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings  # 최신 방식

vectordb = Chroma(
    persist_directory=CHROMA_PERSIST_DIR,
    embedding_function=OpenAIEmbeddings(),
    collection_name="RAG_A",
)

docs = vectordb.similarity_search("테스트 문장", k=3)
print("검색된 문서 수:", len(docs))
for i, doc in enumerate(docs):
    print(f"\n--- 문서 {i+1} ---\n{doc.page_content}\n[메타데이터]: {doc.metadata}")
