function onClick()  {
    const chat_element = document.getElementById("chat_link")
    const href = chat_element.getAttribute("value");
    const chat_id = chat_element.getAttribute("chat_id")
    newWindow = window.open(href,
    "Chat " + chat_id,
    "width=500, height=700",
    toolbar=0,
    statusbar=0,
    locationbar=0,
    );
}
