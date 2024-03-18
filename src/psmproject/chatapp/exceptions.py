class MessageAuthorNotInChat(Exception):
    """
    Raised when user is not chat participant but sends a message
    """
