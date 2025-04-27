const chatContainer = document.getElementById("chat-container");
const userInput = document.getElementById("user-input");
const sendBtn = document.getElementById("send-btn");

// 로컬 스토리지 채팅 데이터 저장 함수
function saveChatToLocalStorage() {
    const chatData = Array.from(chatContainer.children).map((message) => ({
        text: message.innerText,
        className: message.className,
    }));
    localStorage.setItem("chatData", JSON.stringify(chatData));
}

// 로컬 스토리지 채팅 데이터 복원 함수
function loadChatFromLocalStorage() {
    const savedChatData = JSON.parse(localStorage.getItem("chatData"));

    if (savedChatData) {
        savedChatData.forEach((message) => {
            const messageElement = document.createElement("div");
            messageElement.className = message.className;
            messageElement.innerText = message.text;
            chatContainer.appendChild(messageElement);
        });
    }
}

// 답변 생성 중 안내
function simulateTyping(message, delay = 300) {
    const botMessageElement = document.createElement("div");
    botMessageElement.classList.add("message", "received");
    botMessageElement.innerText = "답변 생성 중...";
    chatContainer.appendChild(botMessageElement);

    setTimeout(() => {
        botMessageElement.innerText = message;
        saveChatToLocalStorage();
    }, delay);
}

// 메시지 전송
sendBtn.addEventListener("click", () => {
    const message = userInput.value.trim();
    if (message !== "") {
        // 임시로 TEST 메시지 응답(추후 LLM과 연동 필요)
        const userMessageElement = document.createElement("div");
        userMessageElement.classList.add("message", "sent");
        userMessageElement.innerText = message;
        chatContainer.appendChild(userMessageElement);
        simulateTyping(`TEST: ${message.trim()}`);

        // 칸 초기화
        userInput.value = "";
        userInput.style.height = "40px";
        chatContainer.scrollTop = chatContainer.scrollHeight;

        saveChatToLocalStorage();
    }
});

// textarea 높이 조절
userInput.addEventListener("input", () => {
    userInput.style.height = "auto";
    userInput.style.height = userInput.scrollHeight + "px";
});

// 로컬 스토리지 채팅 내용 가져오기
window.addEventListener("load", () => {
    loadChatFromLocalStorage();

    // 첫 인사 메세지 출력
    const savedChatData = JSON.parse(localStorage.getItem("chatData"));
    if (!savedChatData || savedChatData.length === 0) {
        const botMessageElement = document.createElement("div");
        botMessageElement.classList.add("message", "received");
        botMessageElement.innerText = "안녕하세요! 무엇을 도와드릴까요?";
        chatContainer.appendChild(botMessageElement);
        saveChatToLocalStorage();
    }
});