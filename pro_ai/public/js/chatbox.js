// 요소 가져오기
const chatContainer = document.getElementById("chat-container");
const userInput = document.getElementById("user-input");
const sendBtn = document.getElementById("send-btn");
const submitButton = document.getElementById("submit-info");
const problemInput = document.getElementById("inProblem");
const taskInput = document.getElementById("inTask");
const infoInput = document.getElementById("inInfo");
const targetInput = document.getElementById("inTarget");
const keywordInput = document.getElementById("inKeyword");

// 채팅 저장
function saveChatToLocalStorage() {
    const chatData = Array.from(chatContainer.children).map((message) => ({
        text: message.innerText,
        className: message.className,
    }));
    localStorage.setItem("chatData", JSON.stringify(chatData));
}

// 채팅 로딩
function loadChatFromLocalStorage() {
    try {
        const savedChatData = JSON.parse(localStorage.getItem("chatData"));
        if (savedChatData) {
            savedChatData.forEach((message) => {
                const messageElement = document.createElement("div");
                messageElement.className = message.className;

                const textElement = document.createElement("div");
                if (message.className.includes("received")) {
                    textElement.classList.add("receivedText");
                } else {
                    textElement.classList.add("text");
                }

                textElement.innerText = message.text;
                messageElement.appendChild(textElement);
                chatContainer.appendChild(messageElement);
            });
        }
    } catch (e) {
        console.error("로컬스토리지 데이터 오류:", e);
        localStorage.removeItem("chatData");
    }
}

// 타이핑 애니메이션
function simulateTyping(fullText, speed = 20) {
    const botMessageElement = document.createElement("div");
    botMessageElement.classList.add("message", "received");

    const textElement = document.createElement("div");
    textElement.classList.add("receivedText");
    botMessageElement.appendChild(textElement);
    chatContainer.appendChild(botMessageElement);

    let index = 0;

    function typeNextChar() {
        if (index < fullText.length) {
            textElement.innerText += fullText.charAt(index);
            index++;
            chatContainer.scrollTop = chatContainer.scrollHeight;
            setTimeout(typeNextChar, speed);
        } else {
            saveChatToLocalStorage();
        }
    }

    typeNextChar();
}

// 메시지 전송 버튼 클릭
sendBtn.addEventListener("click", () => {
    const message = userInput.value.trim();
    if (message !== "") {
        const userMessageElement = document.createElement("div");
        userMessageElement.classList.add("message", "sent");
        userMessageElement.innerText = message;
        chatContainer.appendChild(userMessageElement);

        simulateTyping(`TEST: ${message.trim()}`);

        userInput.value = "";
        userInput.style.height = "40px";
        chatContainer.scrollTop = chatContainer.scrollHeight;

        saveChatToLocalStorage();
    }
});

// textarea 높이 자동 조절
userInput.addEventListener("input", () => {
    userInput.style.height = "auto";
    userInput.style.height = userInput.scrollHeight + "px";
});

// 제출 버튼 클릭
submitButton.addEventListener("click", () => {
    const inputData = {
        problem: problemInput.value.trim(),
        task: taskInput.value.trim(),
        info: infoInput.value.trim(),
        target: targetInput.value.trim(),
        keyword: keywordInput.value.trim(),
    };

    if (!inputData.problem && !inputData.task && !inputData.info || !inputData.target) {
        alert("모든 필수 항목을 입력해주세요.");
        return;
    }

    let responseMessage = `제출에 대한 응답\n`;
    for (const [key, value] of Object.entries(inputData)) {
        responseMessage += `${key}: ${value}\n`;
    }

    simulateTyping(responseMessage, 20);
});

// 페이지 로드 시
window.addEventListener("load", () => {
    loadChatFromLocalStorage();

    const savedChatData = JSON.parse(localStorage.getItem("chatData"));
    if (!savedChatData || savedChatData.length === 0) {
        simulateTyping("안녕하세요! 무엇을 도와드릴까요?", 30);
    }
});
