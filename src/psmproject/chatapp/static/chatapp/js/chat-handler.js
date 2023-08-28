import {NewMessage} from "./message-dom.js";


const roomId = JSON.parse(document.getElementById("room-id").textContent);
const currentUser = JSON.parse(document.getElementById("current-user").textContent);


class Chat  {
    /**
    * manage websocket
    */
    constructor(roomId, currentUser)   {
        this.socket = new WebSocket(
            "ws://"
            + window.location.host
            + "/ws/chat/room/"
            + roomId
            + "/"
        );
        this.currentUser = currentUser
        this.chatLog = document.querySelector("#chat-log");
        this.messageInputDom = document.querySelector("#chat-message-input");
        this.messageSubmitDom = document.querySelector("#chat-message-submit");
        this.letterCount = document.querySelector("#letter-count");
    }

    displayNewMessage(e)   {
        /**
        * get message from websocket and display it in the chat
        */
        const data = JSON.parse(e.data);
        data.timestamp = this.get_timestamp()
        const newMessage = new NewMessage(data);
        this.chatLog.append(newMessage.create(this.currentUser));
        this.chatLog.scrollTo(0, this.chatLog.scrollHeight);
    };

    submitMessage(e)    {
        /**
        * send user's message
        */
        const message = this.messageInputDom.value;
        if (message)    {
            this.socket.send(JSON.stringify({
                "author": this.currentUser,
                "message": message
            }));
            this.messageInputDom.value = "";
            this.letterCount.textContent = 0;
        };
    };

    chatClosed(e) {
        /**
        * display message when connection with websocket has been terminated
        */
        alert("Chat connection has been terminated, please close and restart the chat.\n"
            + "If the issue persists, please contact the administrator.\n"
            + "Error " + e.code + ": " + e.reason);
        console.error("Connection has been closed", e);
    };

    chatError(e)    {
        /**
        * display message when connection with websocket has encountered an error
        */
        console.log("WebSocket error: ", e);
    };

    manageMessageInput(e)  {
        /**
        * listen to key entries in message input field :
        * - avoid submission of empty messages (whether the message blank or there are only blank characters
        * - count letters in message
        * - submit message when hitting Enter key
        */
        if (this.messageInputDom.value.match(/^\s/))  {
            this.messageInputDom.value = "";
        } else {
            const characterCount = this.messageInputDom.value.length;
            this.letterCount.textContent = characterCount;
        };
        if (e.key === "Enter" && !e.shiftKey) {
            this.messageSubmitDom.click();
        };
    };

    initEventListeners() {
        /**
        * init envent listeners for chat
        */
        this.socket.onmessage = (e) => {
            this.displayNewMessage(e);
        };
        this.messageSubmitDom.onclick = (e) => {
            this.submitMessage(e)
        };
        if (this.socket.readyState === 1)    {
            this.socket.onclose = (e) => {
                this.chatClosed(e);
            };
            this.socket.onerror = (e) => {
                this.chatError(e);
            };
        };
        this.messageInputDom.onkeyup = (e) => {
            this.manageMessageInput(e);
        };
    };

    get_timestamp() {
        const now = new Date();
        return new Intl.DateTimeFormat("default",
            {
                hour12: true,
                hour: "numeric",
                minute: "numeric",
                second: "numeric"
            }).format(now);
    };
}


const chat = new Chat(roomId, currentUser);
chat.initEventListeners();
