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

document.querySelectorAll('.theme-btn').forEach(btn => {
  btn.addEventListener('click', function() {
    const isSelected = this.classList.contains('selected');
    document.querySelectorAll('.theme-btn').forEach(b => b.classList.remove('selected'));
    if (!isSelected) {
      this.classList.add('selected');
      selectedTheme = this.textContent;
      selectedThemeDiv.textContent = selectedTheme;
    } else {
      selectedTheme = "기본";
      selectedThemeDiv.textContent = "기본";
    }
  });
});

// 제출 버튼 클릭
submitButton.addEventListener("click", () => {
    const inputData = {
        theme: selectedTheme,
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

    const jsonData = JSON.stringify(inputData);

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
