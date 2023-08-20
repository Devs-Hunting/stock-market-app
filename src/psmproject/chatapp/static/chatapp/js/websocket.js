const roomId = JSON.parse(document.getElementById("room-id").textContent);
const author = JSON.parse(document.getElementById("author").textContent);

const chatSocket = new WebSocket(
    "ws://"
    + window.location.host
    + "/ws/chat/room/"
    + roomId
    + "/"
);

chatSocket.onmessage = function(e) {
    const data = JSON.parse(e.data);
    const chatLog = document.querySelector("#chat-log")
    const emptyMessage = document.querySelector("#current-user-message-template")
    const newMessage = document.createElement("div")
    newMessage.innerHTML = emptyMessage.innerHTML
    newMessage.querySelector(".current-user-message").textContent = data.message
    newMessage.querySelector("img").setAttribute("src", data.picture)
    chatLog.append(newMessage)
};

chatSocket.onclose = function(e) {
    console.error("Chat socket closed unexpectedly");
};

document.querySelector("#chat-message-input").focus();
document.querySelector("#chat-message-input").onkeyup = function(e) {
    if (e.key === "Enter") {  // enter, return
        document.querySelector("#chat-message-submit").click();
    }
};

document.querySelector("#chat-message-submit").onclick = function(e) {
    const messageInputDom = document.querySelector("#chat-message-input");
    const message = messageInputDom.value;
    chatSocket.send(JSON.stringify({
        "author": author,
        "message": message
    }));
    messageInputDom.value = "";
};
