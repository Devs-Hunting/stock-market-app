class MessageAuthorNotInChat(Exception):
    """
    Raised when user is not chat participant but sends a message
    """


class DeleteMessageRightsMissing(Exception):
    """
    Raised when user deleting message is not its author or is not Moderator
    """
