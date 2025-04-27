const logo = document.getElementById("logo");

// 로컬 스토리지 삭제 및 채팅 내역 초기화
logo.addEventListener("click", (event) => {
    event.preventDefault();

    const chatContainer = document.getElementById("chat-container");
    chatContainer.innerHTML = "";

    localStorage.removeItem("chatData");

    location.reload();
});