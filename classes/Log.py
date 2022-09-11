from functions.constants import LOG_V

class Log:
    """The class handling messages for the server running the bot"""
    def __init__(self):
        pass
    def show(self, message:str, priority=0) -> None:
        """
        For now this just prints the message on the server terminal if it is equal to or above the value in LOG_V
        Parameters
        ----------
        message : str
            The message to be shown
        priority : int (optional, defaults to 0)
            The priority of the message. 0 is for regular system messages
        """
        try:
            message = str(message)
        except Exception as e:
            emessage = f"message should be a string or convertable to a string. Found type {type(message)}"
            raise Exception(emessage)

        if priority >= LOG_V:
            print(message)