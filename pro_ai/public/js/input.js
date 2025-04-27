const submitButton = document.getElementById("submit-info");
const problemInput = document.getElementById("inProblem");
const taskInput = document.getElementById("inTask");
const infoInput = document.getElementById("inInfo");
const targetInput = document.getElementById("inTarget");
const keywordInput = document.getElementById("inKeyword");

submitButton.addEventListener("click", () => {
    // 입력된 데이터 가져오기
    const inputData = {
        problem: problemInput.value.trim(),
        task: taskInput.value.trim(),
        info: infoInput.value.trim(),
        target: targetInput.value.trim(),
        keyword: keywordInput.value.trim(),
    };

    // 공백 입력 확인
    if (!inputData.problem && !inputData.task && !inputData.info || !inputData.target) {
        alert("모든 필수 항목을 입력해주세요.");
        return;
    }

    const botMessageElement = document.createElement("div");
    botMessageElement.classList.add("message", "received");
    botMessageElement.innerText = "답변 생성 중...";
    chatContainer.appendChild(botMessageElement);

    setTimeout(() => {
        let responseMessage = `제출에 대한 응답<br>`;
        for (const [key, value] of Object.entries(inputData)) {
            responseMessage += `${key}: ${value}<br>`;
        }
        botMessageElement.innerHTML = responseMessage;
        
        const chatData = Array.from(chatContainer.children).map((message) => ({
            text: message.innerText,
            className: message.className,
        }));
        localStorage.setItem("chatData", JSON.stringify(chatData));

    }, 500);

});