var chats = document.getElementsByClassName("chat_link")
for (let i=0; i<chats.length; i++)  {
    const elem = chats[i];
    elem.onclick = function()   {
        const href = elem.getAttribute("value");
        const chat_id = elem.getAttribute("chat_id");
        newWindow = window.open(href,
        "Chat " + chat_id,
        "width=500, height=" + window.screen.height
        );
    };
}
