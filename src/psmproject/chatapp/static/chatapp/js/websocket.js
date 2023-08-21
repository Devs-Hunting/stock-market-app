const roomId = JSON.parse(document.getElementById("room-id").textContent);
const currentUser = JSON.parse(document.getElementById("current-user").textContent);


class NewMessage    {
    /**
    * create html template for message display in chat depending on current logged user and author
    */
    constructor(data)   {
        this.data = data;
    }
    create()    {
        let newMessageElement = document.createElement("div");
        if (this.data.author == currentUser) {
            const emptyMessage = document.querySelector("#current-user-message-template");
            newMessageElement.innerHTML = emptyMessage.innerHTML;
            newMessageElement.querySelector(".current-user-message").textContent = this.data.message;
            newMessageElement.querySelector("img").setAttribute("src", this.data.picture);
        } else  {
            const emptyMessage = document.querySelector("#other-user-message-template");
            newMessageElement.innerHTML = emptyMessage.innerHTML;
            newMessageElement.querySelector(".author").textContent = this.data.author + " :"
            newMessageElement.querySelector(".other-user-message").textContent = this.data.message;
            newMessageElement.querySelector("img").setAttribute("src", this.data.picture);
        }
        return newMessageElement
    }
}


const chatSocket = new WebSocket(
    "ws://"
    + window.location.host
    + "/ws/chat/room/"
    + roomId
    + "/"
);

chatSocket.onmessage = function(e) {
    const data = JSON.parse(e.data);
    const chatLog = document.querySelector("#chat-log");
    newMessage = new NewMessage(data)
    chatLog.append(newMessage.create());
};

chatSocket.onclose = function(e) {
    console.error("Chat socket closed unexpectedly");
};

const messageInputDom = document.querySelector("#chat-message-input");
const messageSubmitDom = document.querySelector("#chat-message-submit")

messageInputDom.focus();
messageInputDom.onkeyup = function(e) {
    if (e.key === "Enter") {
        messageSubmitDom.click();
    }
};

messageSubmitDom.onclick = function(e) {
    const message = messageInputDom.value;
    chatSocket.send(JSON.stringify({
        "author": currentUser,
        "message": message
    }));
    messageInputDom.value = "";
};
