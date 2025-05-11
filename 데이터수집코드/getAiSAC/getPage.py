from datetime import datetime
#pip install playwright
#python -m playwright install
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    page.goto("https://aisac.kobaco.co.kr/site/main/copy/gallery")
    print("페이지 접속 성공")
    
    tone = int(input("톤앤 매너 선택 : 0(기본), 1(리뷰), 2(행동촉구), 3(질문), 4(언어유희)"))
    dateStart = input("검색 시작 기간 설정(EX : 2025-01-01 / 전체 검색은 0)")
    if (dateStart == "0"):
        dateStart = "2001-01-01"
    dateEnd = input("검색 종료 기간 설정(EX : 2025-05-01 / 전체 검색은 0)")
    if (dateEnd == "0"):
        dateEnd = datetime.today().strftime("%Y-%m-%d")

    page.click("text=상세검색")
    page.wait_for_selector("#searchDetailModal", state="visible")

    toneLabels = ["기본", "리뷰", "행동촉구", "질문", "언어유희"]
    page.click(f".tone:has-text('{toneLabels[tone]}')")
    print(f"톤앤매너 '{toneLabels[tone]}' 선택 완료")

    startDateInput = page.locator("input[name='searchStartDate']")
    startDateInput.fill(dateStart)
    endDateInput = page.locator("input[name='searchEndDate']")
    endDateInput.fill(dateEnd)

    page.click('div.searchDetailButton:has-text("검색")')
    page.wait_for_timeout(3000)

    with open("getAiSAC.txt", "a", encoding="utf-8") as f:
            pageNo = 1

            while True:
                # 카드 스크래핑
                cards = page.locator("div.tab-con.on div.card.shadow")
                cardCount = cards.count()
                print(f"게시글 수: {cardCount}")
                
                if cardCount == 0:
                    print("게시글이 없습니다.")
                    break

                for i in range(cardCount):
                    card = cards.nth(i)
                    contentRaw = card.get_attribute("data-copycontents") or ""
                    fullSaveData = card.get_attribute("data-copysavedate") or ""
                    content = contentRaw.strip().split("\t")[0]
                    savedate = fullSaveData.split(" ")[0] if fullSaveData else ""
                    if content and savedate:
                        print(f"{savedate} {content[:15]}...")
                        f.write(f"{savedate} {content}\n")
                    #필요하다면 텍스트 파일이 아닌 데이터베이스에 저장 가능

                #페이지 이동
                pageNo += 1
                pageButton = page.locator(f"a:has-text('{pageNo}')")
                if pageButton.count() == 0:
                    nextButton = page.locator("a.next")
                    if nextButton.count() == 0:
                        print("마지막 페이지입니다.")
                        break
                    nextButton.click()
                    print(f"페이지 {pageNo}")
                    page.wait_for_timeout(3000)
                else:
                    pageButton.click()
                    print(f"페이지 {pageNo}")
                    page.wait_for_timeout(3000)

    print("완료")

    input("아무거나 입력하여 종료")
    browser.close()