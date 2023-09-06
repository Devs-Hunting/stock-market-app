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
            + "/user/"
            + currentUser
            + "/"
        );
        this.currentUser = currentUser
        this.chatLog = document.querySelector("#chat-log");
        this.messageInputDom = document.querySelector("#chat-message-input");
        this.messageSubmitDom = document.querySelector("#chat-message-submit");
        this.letterCount = document.querySelector("#letter-count");
        this.loadMessagesButton = document.querySelector("#load-messages");
        this.connectionTimestamp = new Date().toJSON();
        this.nbVisibleMessages = 0;
    };

    initChat()  {
        chat.fetchMessages();
    };

    socketReceiver(e)   {
        const data = JSON.parse(e.data);
        const action = data["action"];
        switch(action)  {
            case "send_new_message":
                this.displayNewMessage(data);
            case "fetch_messages":
                this.loadMessages(data);
        };
    };

    displayNewMessage(data)   {
        /**
        * get message from websocket and display it in the chat
        */
        const newMessage = new NewMessage(data["message"]);
        this.chatLog.append(newMessage.create(this.currentUser));
        this.chatLog.scrollTo(0, this.chatLog.scrollHeight);
    };

    loadMessages(data)  {
        const message_list = data["messages"];
        for (let i in message_list)   {
            const message = new NewMessage(message_list[i]);
            this.loadMessagesButton.after(message.create(this.currentUser));
        }
        if (this.nbVisibleMessages === 10)  {
            this.chatLog.scrollTo(0, this.chatLog.scrollHeight);
        };
    };

    submitMessage()    {
        /**
        * send user's message
        */
        const content = this.messageInputDom.value;
        if (content)    {
            this.socket.send(JSON.stringify({
                "action": "send_new_message",
                "author": this.currentUser,
                "content": content
            }));
            this.messageInputDom.value = "";
            this.letterCount.textContent = 0;
        };
    };

    fetchMessages() {
        this.nbVisibleMessages += 10;
        this.socket.send(JSON.stringify({
            "action": "fetch_messages",
            "chat_connection_timestamp": this.connectionTimestamp,
            "visible_messages": this.nbVisibleMessages,
        }));
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
            this.socketReceiver(e);
        };
        this.messageSubmitDom.onclick = () => {
            this.submitMessage()
        };
        this.socket.onclose = (e) => {
            this.chatClosed(e);
        };
        this.socket.onerror = (e) => {
            this.chatError(e);
        };
        this.messageInputDom.onkeyup = (e) => {
            this.manageMessageInput(e);
        };
        this.loadMessagesButton.onclick = () =>   {
            this.fetchMessages();
        };
    };

}

const chat = new Chat(roomId, currentUser);
chat.socket.onopen = (e) => {
    chat.initEventListeners();
    chat.initChat();
}
