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
selectedTheme = "기본"

let loadingInterval;
function showLoadingMessage() {
    const loadingMessageElement = document.createElement("div");
    loadingMessageElement.classList.add("message", "received");

    const textElement = document.createElement("div");
    textElement.classList.add("receivedText");
    loadingMessageElement.appendChild(textElement);

    chatContainer.appendChild(loadingMessageElement);
    chatContainer.scrollTop = chatContainer.scrollHeight;

    let dotCount = 0;
    loadingInterval = setInterval(() => {
        dotCount = (dotCount + 1) % 4; // 0, 1, 2, 3
        textElement.innerText = "응답 대기 중" + ".".repeat(dotCount);
    }, 500);

    return loadingMessageElement;
}

// 채팅 저장
function saveChatToLocalStorage() {
    const chatData = Array.from(chatContainer.children).map((message) => {
        let text = "";
        if (message.classList.contains("received")) {
            const receivedTextElem = message.querySelector(".receivedText");
            text = receivedTextElem ? receivedTextElem.innerText : "";
        } else if (message.classList.contains("sent")) {
            text = message.innerText;
        }

        return {
            text,
            className: message.className,
        };
    });
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

                // 텍스트 요소 생성
                const textElement = document.createElement("div");
                if (message.className.includes("received")) {
                    textElement.classList.add("receivedText");
                } else {
                    textElement.classList.add("text");
                }
                textElement.innerText = message.text;
                messageElement.appendChild(textElement);

                // 복사 버튼은 'received' 메시지에만 생성
                if (message.className.includes("received")) {
                    const copyButton = document.createElement("button");
                    copyButton.classList.add("copy-button");
                    copyButton.innerText = "📋";
                    copyButton.title = "복사";

                    copyButton.addEventListener("click", () => {
                        // 받은 텍스트만 복사
                        const receivedTextElement = messageElement.querySelector(".receivedText");
                        if (receivedTextElement) {
                            navigator.clipboard.writeText(receivedTextElement.innerText).then(() => {
                                copyButton.innerText = "✅";
                                setTimeout(() => (copyButton.innerText = "📋"), 1000);
                            });
                        }
                    });

                    messageElement.appendChild(copyButton);
                }

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

    const copyButton = document.createElement("button");
    copyButton.classList.add("copy-button");
    copyButton.innerText = "📋";
    copyButton.title = "복사";

    copyButton.addEventListener("click", () => {
        navigator.clipboard.writeText(textElement.innerText).then(() => {
            copyButton.innerText = "✅";
            setTimeout(() => (copyButton.innerText = "📋"), 1000);
        });
    });

    botMessageElement.appendChild(textElement);
    botMessageElement.appendChild(copyButton);
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

        let chatHistory = [];
        try {
            chatHistory = JSON.parse(localStorage.getItem("chatData")) || [];
        } catch (e) {}
        const historyText = chatHistory
            .map(item => {
                if (item.className.includes("sent")) {
                    return `사용자: ${item.text}`;
                } else if (item.className.includes("received")) {
                    return `AI: ${item.text}`;
                }
                return '';
            })
            .filter(Boolean)
            .join('\n');

        let finalPrompt = "";
        if (historyText) {
            finalPrompt += "다음은 이때까지의 대화 내용입니다\n~~~\n" + historyText + "\n~~~\n\n";
        }
        finalPrompt += "질문입니다\n~~~\n" + message + "\n~~~";

        const loadingMessageElement = showLoadingMessage();

        fetch('/chatAI', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ problem: finalPrompt })
        })
        .then(response => response.json())
        .then(data => {
            clearInterval(loadingInterval);
            chatContainer.removeChild(loadingMessageElement);
            simulateTyping(data.result, 20);
        })
        .catch(err => {
            clearInterval(loadingInterval);
            chatContainer.removeChild(loadingMessageElement);
            simulateTyping('서버 오류가 발생했습니다.', 20);
        });

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

document.querySelectorAll('.theme-btn').forEach(btn => {
  btn.addEventListener('click', function() {
    const isSelected = this.classList.contains('selected');
    document.querySelectorAll('.theme-btn').forEach(b => b.classList.remove('selected'));
    if (!isSelected) {
      this.classList.add('selected');
      selectedTheme = this.textContent;
    } else {
      selectedTheme = "기본";
    }
  });
});

// 제출 버튼 클릭
submitButton.addEventListener("click", () => {
    const inputData = {
        theme: selectedTheme,
        background: problemInput.value.trim(),
        solution: taskInput.value.trim(),
        target: targetInput.value.trim(),
        content: infoInput.value.trim(),
        assistance: keywordInput.value.trim(),
    };

    const loadingMessageElement = showLoadingMessage();

    fetch('/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(inputData)
    })
    .then(response => response.json())
    .then(data => {
        clearInterval(loadingInterval);
        chatContainer.removeChild(loadingMessageElement);
        simulateTyping(data.result, 20);
    })
    .catch(err => {
        simulateTyping('서버 오류가 발생했습니다.', 20);
    });
});

// 페이지 로드 시
window.addEventListener("load", () => {
    loadChatFromLocalStorage();

    const savedChatData = JSON.parse(localStorage.getItem("chatData"));
    if (!savedChatData || savedChatData.length === 0) {
        simulateTyping("안녕하세요! 무엇을 도와드릴까요?", 30);
    }
});
