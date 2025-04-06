from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time
import pandas as pd
import os
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# 크롬 드라이버 실행 (경로는 알아서 변경! - 예시로 두었음)
driver = webdriver.Chrome()

# 네이버 뉴스 검색 결과 URL (윤석열 탄핵 관련 검색)
base_url = "https://search.naver.com/search.naver?sm=tab_hty.top&where=news&ssc=tab.news.all&query=%EA%B9%80%EC%88%98%ED%98%84+%EC%97%B0%ED%95%A9%EB%89%B4%EC%8A%A4&oquery=%EC%97%B0%ED%95%A9%EB%89%B4%EC%8A%A4+%EC%A2%8C%ED%8C%8C&tqi=i90U%2Fdqo1LVss51OK7lssssstuR-054504"

list_url = []  # 기사 URL을 저장할 리스트

for i in range(0, 5):  # 0부터 370까지 반복
    url = base_url + str(i * 10 + 1)  # 네이버 뉴스 페이지 번호
    driver.get(url)
    time.sleep(1)  # 페이지 로딩 대기

    # 페이지 소스 가져와서 BeautifulSoup으로 파싱
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')

    # 뉴스 기사 링크 찾기 (네이버 뉴스의 경우 `.news_tit` 사용)
    for link in soup.find_all("a", class_="news_tit"):
        if link.has_attr("href"):  # href 속성이 있는지 확인
            news_url = link["href"] # href 속성이 있으면 news_url에 저장장
            print("✅ Found URL:", news_url) #news_url 출력력
            list_url.append(news_url) #list_url에 news_url append
        

# 브라우저 종료
driver.quit()

# 데이터를 crawled_data.csv에 저장 (중간에 크롤링이 멈춰도 저장되도록 함)
data_url = pd.DataFrame(list_url, columns=['url'])
data_url.to_csv('crawled_data.csv', encoding='cp949', index=False)

print("✅ 크롤링 완료! 뉴스 링크가 crawled_data.csv에 저장됨!")
print("파일 저장 위치:", os.path.abspath("crawled_data.csv"))


# ✅ CSV 파일에서 URL 리스트 불러오기 (경로 수정)
df = pd.read_csv("./crawled_data.csv")
urls = df["url"]

# ChromeDriver 경로
CHROMEDRIVER_PATH = "C:/dev_python/Webdriver/chromedriver.exe"

# Chrome 옵션 설정
chrome_options = Options()
chrome_options.add_argument("--start-maximized")

# ✅ 크롬 드라이버 실행 (한 번만 실행)
service = Service(CHROMEDRIVER_PATH)
driver = webdriver.Chrome(service=service, options=chrome_options)
driver.implicitly_wait(5)  # 최대 5초 대기

content_list = []

#파이썬 dictionary
site_more_button_selectors = {
    "news.naver.com": "a.u_cbox_btn_more",  # 네이버
    "daum.net": "button.link_fold",  # 다음 (예제)
    "news.sbs.co.kr": "button.more_btn",  # SBS 뉴스 (예제)
    "yna.co.kr" : "button.btn-type300.style20.arr01" #연합뉴스
}

site_comment_button_selectors = {
    "naver.com": "a.pi_btn_count",  # 네이버
    "daum.net": "button.open_comments",  # 다음 (예제)
    "yna.co.kr" : "button.btn-type300.style20.arr01" #연합뉴스
}


# ✅ 각 뉴스 기사 URL 방문 & 댓글 크롤링
for i, url in enumerate(urls[:1]):  # 최대 1326개 기사 크롤링
    print(f"🔍 ({i+1}/{len(urls)}) URL 크롤링 중: {url}")
    driver.get(url)
    time.sleep(2)  # 페이지 로딩 대기

    site_domain = None
    for domain in site_more_button_selectors.keys():
        if domain in url:
            site_domain = domain
            break

    if not site_domain:
        print("⚠️ 지원되지 않는 사이트! 계속 진행")
        continue

    # ✅ 댓글창 열기 버튼 클릭 (예외 처리)
    try:
        comment_selector = site_comment_button_selectors.get(site_domain)
        if comment_selector:
            comment_btn = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, comment_selector))
            )
            comment_btn.click()
            time.sleep(2)
    except:
        print("⚠️ 댓글 버튼 없음! 계속 진행")
        
    #해당 도메인에 저장돼있는 태그를 찾아서 저장시켜라라

    # ✅ '더보기' 버튼 반복 클릭 (사이트별 다른 선택자 사용)
    more_selector = site_more_button_selectors.get(site_domain)

    while True:
        try:
            more_btn = WebDriverWait(driver, 2).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, more_selector))
            )
            more_btn.click()
            time.sleep(1.5)
        except:
            break  # 더 이상 버튼이 없으면 종료

    # ✅ 댓글 내용 크롤링
    comments = driver.find_elements(By.CSS_SELECTOR, 'span[style="white-space: pre-line"]')
    for comment in comments:
        content_list.append(comment.text)


# ✅ 크롤링 종료
driver.quit()

# ✅ 수집된 데이터 저장
df = pd.DataFrame({'comment': content_list})

df.to_csv('2017_0809-1231.csv', encoding='utf-8-sig', index=False)

print("✅ 크롤링 완료! 데이터가 2017_0809-1231.csv에 저장됨.")

