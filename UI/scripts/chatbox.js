const chatContainer = document.getElementById("chat-container");
const userInput = document.getElementById("user-input");
const sendBtn = document.getElementById("send-btn");

// 메시지 전송
sendBtn.addEventListener("click", () => {
  const message = userInput.value.trim();
  if (message !== "") {
    const userMessageElement = document.createElement("div");
    userMessageElement.classList.add("message", "sent");
    userMessageElement.innerText = message;
    chatContainer.appendChild(userMessageElement);
    
    // 임시로 TEST 메시지 응답(추후 LLM과 연동 필요)
    const botMessageElement = document.createElement("div");
    botMessageElement.classList.add("message", "received");
    botMessageElement.innerText = "test";
    chatContainer.appendChild(botMessageElement);
    
    // 칸 초기화
    userInput.value = "";
    userInput.style.height = "40px";
    chatContainer.scrollTop = chatContainer.scrollHeight;
  }
});

// textarea 높이 조절
userInput.addEventListener("input", () => {
  userInput.style.height = "auto";
  userInput.style.height = userInput.scrollHeight + "px";
});
