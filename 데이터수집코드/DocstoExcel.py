import docx
import pandas as pd

# 불러올 docx 파일 경로
docx_file = "C:/Users/HeeWoong/heewoong/PRoAI/데이터수집코드/ExampleData/2nd_data.docx"

# 섹션 타이틀
sections = ["클라이언트", "문제 배경", "해결 과제", "주 타겟", "메인 커뮤니케이션 컨셉", "주요 내용", "추가 분석"]

# 결과 저장용 리스트
rows = []

# 현재 묶음 저장용
current_data = {}
current_section = None

# 문서 열기
doc = docx.Document(docx_file)

for para in doc.paragraphs:
    text = para.text.strip()
    if not text:
        continue  # 빈 줄 스킵

    # 섹션 시작인지 확인
    if text in sections:
        current_section = text

        # 만약 클라이언트이면 → 이전 묶음 저장 후 새로 시작
        if current_section == "클라이언트":
            if current_data:
                rows.append(current_data)
            current_data = {section: "" for section in sections}

    # 섹션 안의 내용 처리
    elif current_section:
        if current_data[current_section]:
            current_data[current_section] += "\n" + text
        else:
            current_data[current_section] = text

# 마지막 묶음 저장
if current_data:
    rows.append(current_data)

# DataFrame으로 변환
df = pd.DataFrame(rows)

# 엑셀로 저장
output_excel = "USG_output.xlsx"
df.to_excel(output_excel, index=False)

print(f"엑셀 파일로 저장 완료: {output_excel}")
