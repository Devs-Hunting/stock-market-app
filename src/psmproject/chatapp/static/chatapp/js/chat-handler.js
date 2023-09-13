import {NewMessage} from "./message-dom.js";


const roomId = JSON.parse(document.getElementById("room-id").textContent);
const currentUser = JSON.parse(document.getElementById("current-user").textContent);
const chatHistoryLength = JSON.parse(document.getElementById("chat-history-length").textContent);


class Chat  {
    /**
    * Chat class manage the whole chat, connection with websocket included:
    * - sends user-submitted chat messages to websocket
    * - fetch messages from chat history
    * - retrieves sent or fetched messages and display them accordingly
    * - checks message input before sending to avoid validation errors
    */
    constructor(roomId, currentUser, chatHistoryLength)   {
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
        this.chatHistoryCount = document.querySelector("#chat-history-count");
        this.warningMessageDiv = document.querySelector("#warning-msg");
        this.connectionTimestamp = new Date().toJSON();
        this.nbVisibleMessages = 0;
        this.chatHistoryLength = chatHistoryLength;

    };

    initChat()  {
        /**
        * Initialise chat view once websocket connection is ready
        */
        chat.fetchMessages();
    };

    socketReceiver(e)   {
        /**
        * When data is received from websocket, execute required action accordingly
        */
        const data = JSON.parse(e.data);
        const action = data["action"];
        switch(action)  {
            case "send_new_message":
                this.displayNewMessage(data);
                break;
            case "fetch_messages":
                this.loadMessages(data);
                break;
            case "throw_error":
                this.displayWarningMessage(data["error"]);
        };
    };

    displayNewMessage(data)   {
        /**
        * Display new message on chat and scroll down
        */
        const newMessage = new NewMessage(data["message"]);
        this.chatLog.append(newMessage.create(this.currentUser));
        this.chatLog.scrollTo(0, this.chatLog.scrollHeight);
    };

    loadMessages(data)  {
        /**
        * Display messages from chat history and change number of remaining messages
        * If it displays the first 10 messaged when starting the chat, view will scrolldown
        * Once there is no more message to display, load message button disappears
        */
        const message_list = data["messages"];
        for (let i in message_list)   {
            const message = new NewMessage(message_list[i]);
            this.loadMessagesButton.after(message.create(this.currentUser));
        }
        this.chatHistoryCount.textContent = this.chatHistoryLength - this.nbVisibleMessages;
        if (this.nbVisibleMessages === 10)  {
            this.chatLog.scrollTo(0, this.chatLog.scrollHeight);
        };
        if (this.nbVisibleMessages >= this.chatHistoryLength)   {
            this.loadMessagesButton.hidden = true;
        }
    };

    submitMessage()    {
        /**
        * Send user message to websocket and reset input
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
        /**
        * Send command to websocket to fetch messages from chat history and increase number of visible messages in chat
        * Send also timestamp when user connected to chat to avoid retrieving new messages from database
        */
        this.nbVisibleMessages += 10;
        this.socket.send(JSON.stringify({
            "action": "fetch_messages",
            "chat_connection_timestamp": this.connectionTimestamp,
            "visible_messages": this.nbVisibleMessages,
        }));
    };

    displayWarningMessage(warningMessageArray)    {
    /**
    * Display warning message in chat
    */
        this.warningMessageDiv.hidden = false;
        for (let i in warningMessageArray)  {
            const newP = document.createElement("p");
            const newContent = document.createTextNode(warningMessageArray[i]);
            newP.appendChild(newContent);
            this.warningMessageDiv.querySelector(".msg-content").append(newP);
        }
    };

    removeWarningMessage()  {
       this.warningMessageDiv.querySelector(".msg-content").innerHTML = ""
       this.warningMessageDiv.hidden = true;
    }

    chatClosed(e) {
        /**
        * Display message on UI and console when chat connection has been terminated
        */
        const warningMessageArray = [
            "Chat connection has been terminated, please close and restart the chat.",
            "If the issue persists, please contact the administrator.",
            "Error " + e.code,
            ]
        this.displayWarningMessage(warningMessageArray);
        console.error("Connection has been closed", e);
    };

    chatError(e)    {
        /**
        * Display message when connection with websocket has encountered an error
        */
        console.log("WebSocket error: ", e);
    };

    manageMessageInput(e)  {
        /**
        * Listen to key entries in message input field :
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
        * Initialize event listeners for chat
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
        this.warningMessageDiv.onclick = () =>  {
            this.removeWarningMessage();
        };
    };

}

const chat = new Chat(roomId, currentUser, chatHistoryLength);
chat.socket.onopen = (e) => {
    chat.initEventListeners();
    chat.initChat();
}
