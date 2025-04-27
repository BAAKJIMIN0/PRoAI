import fitz  # PyMuPDF
import pandas as pd

pdf_path = r'C:\Users\HeeWoong\heewoong\PRoAI\DataScrapping\ExampleData\Ulsan\Ulsan_PR.pdf'
doc = fitz.open(pdf_path)

text_lines = []
for page in doc:
    text = page.get_text()
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    text_lines.extend(lines)

df = pd.DataFrame({'OCR_Text': text_lines})
df.to_excel("울산과학대학교_시나리오_텍스트추출결과.xlsx", index=False)
