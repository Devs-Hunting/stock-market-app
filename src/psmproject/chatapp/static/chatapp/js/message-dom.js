export class NewMessage    {
    /**
    * create html template for message display in chat depending on current logged user and author
    */
    constructor(data)   {
        this.data = data;
        this.currentUserMessageTemplate = document.querySelector("#current-user-message-template");
        this.otherUserMessageTemplate = document.querySelector("#other-user-message-template");
    }
    create(currentUser)    {
        let newMessageElement = document.createElement("div");
        if (this.data.author == currentUser) {
            newMessageElement.innerHTML = this.currentUserMessageTemplate.innerHTML;
        } else  {
            newMessageElement.innerHTML = this.otherUserMessageTemplate.innerHTML;
            newMessageElement.querySelector(".author").textContent = this.data.author + " :"
        };
        newMessageElement.querySelector(".message").textContent = this.data.message;
        newMessageElement.querySelector(".message").setAttribute("title", "Today, " + this.data.timestamp);
        newMessageElement.querySelector("img").setAttribute("src", this.data.picture);
        return newMessageElement;
    }
};