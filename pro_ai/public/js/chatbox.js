const chatContainer = document.getElementById("chat-container");
const userInput = document.getElementById("user-input");
const sendBtn = document.getElementById("send-btn");

// 로컬 스토리지 채팅 데이터 저장
function saveChatToLocalStorage() {
    const chatData = Array.from(chatContainer.children).map((message) => ({
        text: message.innerText,
        className: message.className,
    }));
    localStorage.setItem("chatData", JSON.stringify(chatData));
}

// 로컬 스토리지 채팅 데이터 복원
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

// 타이핑 애니메이션
function simulateTyping(fullText, speed = 20) {
    const botMessageElement = document.createElement("div");
    botMessageElement.classList.add("message", "received");
    chatContainer.appendChild(botMessageElement);

    let index = 0;

    function typeNextChar() {
        if (index < fullText.length) {
            botMessageElement.innerText += fullText.charAt(index);
            index++;
            chatContainer.scrollTop = chatContainer.scrollHeight;
            setTimeout(typeNextChar, speed);
        } else {
            saveChatToLocalStorage();
        }
    }

    typeNextChar();
}

// 메시지 전송
sendBtn.addEventListener("click", () => {
    const message = userInput.value.trim();
    if (message !== "") {
        // 사용자 메시지 추가
        const userMessageElement = document.createElement("div");
        userMessageElement.classList.add("message", "sent");
        userMessageElement.innerText = message;
        chatContainer.appendChild(userMessageElement);

        simulateTyping(`TEST: ${message.trim()}`);

        // 입력창 초기화
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

// 로컬 스토리지 채팅 내용 가져오기
window.addEventListener("load", () => {
    loadChatFromLocalStorage();

    const savedChatData = JSON.parse(localStorage.getItem("chatData"));
    if (!savedChatData || savedChatData.length === 0) {
        simulateTyping("안녕하세요! 무엇을 도와드릴까요?", 30);
    }
});
