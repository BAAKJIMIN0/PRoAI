import fitz  # PyMuPDF
import pdfplumber
import pandas as pd
from tkinter import Tk, filedialog
from pathlib import Path
from tkinter import messagebox
import os

def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    all_text = ""
    for page in doc:
        all_text += page.get_text()
    doc.close()
    return all_text

def extract_tables_from_pdf(pdf_path):
    tables = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            for table in page.extract_tables():
                df = pd.DataFrame(table[1:], columns=table[0])
                tables.append(df)
    return tables

import re

def remove_illegal_chars(text):
    # Excel에서 허용하지 않는 문자 제거 (ASCII 0~31 제외: \x00 - \x1F)
    return re.sub(r"[\x00-\x1F]", "", text)

def save_to_excel_split_text(text, tables, output_path):
    text_lines = [remove_illegal_chars(line.strip()) for line in text.split('\n') if line.strip()]
    df_text = pd.DataFrame({'Line': text_lines})

    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        df_text.to_excel(writer, sheet_name='Text', index=False)
        for i, table_df in enumerate(tables):
            sheet_name = f'Table_{i+1}'
            table_df.to_excel(writer, sheet_name=sheet_name, index=False)


def run_gui_file_select():
    # 팝업창 초기화
    root = Tk()
    root.withdraw()  # 메인 윈도우 숨기기

    # 파일 선택 창 띄우기
    file_path = filedialog.askopenfilename(
        title="PDF 파일 선택",
        filetypes=[("PDF Files", "*.pdf")]
    )

    if not file_path:
        messagebox.showinfo("안내", "파일을 선택하지 않았습니다.")
        return

    # 파일 경로 설정
    filename = Path(file_path).stem
    output_path = os.path.join(os.path.dirname(file_path), f"{filename}_Excel출력.xlsx")

    # PDF 처리 및 저장
    text = extract_text_from_pdf(file_path)
    tables = extract_tables_from_pdf(file_path)
    save_to_excel_split_text(text, tables, output_path)

    messagebox.showinfo("완료", f"Excel 파일 저장 완료!\n{output_path}")

# 실행
if __name__ == "__main__":
    run_gui_file_select()
