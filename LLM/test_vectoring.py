import os
import openai
from dotenv import load_dotenv
from langchain.document_loaders import PyPDFLoader, DirectoryLoader, TextLoader, UnstructuredMarkdownLoader, NotebookLoader
from SimpleDocxLoader import SimpleDocxLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.schema import Document

load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
if OPENAI_API_KEY is None:
    raise ValueError("환경변수 OPENAI_API_KEY가 설정되어 있지 않습니다.")
openai.api_key = OPENAI_API_KEY

# 경로 설정 (현재 파일 기준 절대 경로)
CUR_DIR = os.path.dirname(os.path.abspath(__file__))
CHROMA_PERSIST_DIR = os.path.join(CUR_DIR, 'db/test')
CHROMA_COLLECTION_NAME = "RAG_A"

# 벡터 DB에 저장할 데이터(추후 DB에서 가져오는 방식으로 변경)
client = ["USG 공유대학", "주식회사 다이웃 (사회적 기업)","거제대학교"]
background = ["USG 공유대학은 신설된 대학 모델이지만,주 타겟인 대학생들에게 존재 의의, 비전, 프로그램에 대한 인지도가 부족함.학생들의 관심과 이해를 높일 수 있는 참신한 표현 전략이 필요했음."
                ,"친환경 도시락 용기 ‘지몬’ 출시,그러나 소비자 대상 제품 가치와 혜택 전달이 부족함.환경 의식 있는 소비자층을 대상으로 한 명확한 가치 소구 필요."
                ,"강력한 산학 연계 및 취업 강점에도 불구하고,낮은 인지도와 매력도 부족으로 학생 유치에 어려움."]
solution = ["USG 공유대학이 무엇인지,어떤 프로그램과 혜택이 있는지 명확히 전달학생들의 흥미와 몰입을 유도하는 접근 방식 필요"
                ,"'지몬' 용기의 친환경성과 실용성을 부각 건강, 환경 보호라는 실질적 혜택을 쉽게 전달"
                ,"거제대학교만의 차별성과 강점을 흥미롭게 알리고,대학 선택의 매력을 높여야 함."]
target = ["대학생 및 대학 진학 예정자","환경에 관심이 많은 주부, 기관, 단체","고등학교 입시생 및 학부모"]
concept = ["꼬리에 꼬리를 무는 USG 공유대학","자연스러운 나의 선택, 지몬", "게임 잘하는 사람이 대학 선택도 잘한다 - 대학 선택 성공 비법 대공개"]
content = ["USG 공유대학의 설립 목적 및 운영 방향 소개, 제공 프로그램, 커리큘럼, 참여 이점 설명, 스토리텔링을 통해 자연스럽게 정보 전달"
                ,"자연 분해 가능성, 인체 무해성, 편리성 강조 , 착한 소비를 통한 건강과 지구 보호 메시지 전달"
                ,"거제대학교 강점 소개, 게임 중계 콘셉트를 활용해 선택 과정을 '성공 전략'으로 재해석, 학생들의 몰입과 흥미 유발"]
assistance = ["핵심 키워드: 궁금증, 연결성, 연속성 \
심리 연결:  \
탐색 욕구 자극: ""몰랐던 것을 알아가는 즐거움""\
연결 심리: ""하나의 정보가 다음 궁금증으로 이어지며 몰입""\
자기주도적 참여 심리: ""스스로 탐색하고 이해하는 과정에 매력을 느낌"" ",    \
    "핵심 키워드: 자연스러움, 착한 소비, 본능적 선택    \
심리 연결:\
도덕적 만족감: ""나는 옳은 선택을 하고 있다""\
일상 속 작은 실천 심리: ""큰 노력이 아니라 자연스럽게 좋은 행동""\
친환경 가치 내재화: ""환경을 위한 선택이 나의 본성이 된다"" " ,    \
    "핵심 키워드: 성공 전략, 게임, 재미\
심리 연결:\
승부욕 자극: ""남보다 잘하고 싶다""\
비법에 대한 호기심: ""성공하는 방법이 있다면 알고 싶다""\
즐거운 몰입: ""게임처럼 흥미로운 과정으로 느끼게 한다"" "
]

sections = ["client", "background", "solution", "target", "concept", "content", "assistance"]

# 한 프로젝트 내용을 하나의 Document로 묶음
result_a = []
for i in range(3):
    result_a.append(
        Document(
            page_content = f"클라이언트: {client[i]}\n"
                           f"문제 배경: {background[i]}\n"
                           f"해결 과제: {solution[i]}\n"
                           f"주 타겟: {target[i]}\n"
                           f"메인 커뮤니케이션 컨셉: {concept[i]}\n"
                           f"주요 내용: {content[i]}\n"
                           f"추가 분석: {assistance[i]}",
            metadata = {
                "idx":i,
            }
        )
    )

vectordb_a = Chroma.from_documents(
    documents=result_a,
    embedding=OpenAIEmbeddings(),
    persist_directory=CHROMA_PERSIST_DIR,
    collection_name="RAG_A",
)
vectordb_a.persist()
print("벡터 DB가 Ａ가 저장되었습니다.")

# 한 프로젝트의 section 별로 Document를 나누어 저장
result_b = []
for i in range(3):
    for section in sections:
        section_content = eval(section)[i]  # section 리스트에서 값 가져오기
        result_b.append(
            Document(
                page_content = section_content,
                metadata = {
                    "idx": i,
                    "section": section
                }
            )
        )

vectordb_b = Chroma.from_documents(
    documents=result_b,
    embedding=OpenAIEmbeddings(),
    persist_directory=CHROMA_PERSIST_DIR,
    collection_name="RAG_B",
)
vectordb_b.persist()
print("벡터 DB가 B가 저장되었습니다.")
