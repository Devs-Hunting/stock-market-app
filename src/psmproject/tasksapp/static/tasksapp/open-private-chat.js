function openChatWindow(el) {
    const href = el.getAttribute("value");
    newWindow = window.open(href,
    "Private chat",
    "width=500, height=" + window.screen.height
    );
}
