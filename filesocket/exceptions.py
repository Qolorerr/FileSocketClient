class ServerError(Exception):
    pass


class PathNotFoundError(Exception):
    pass


class TokenRequired(Exception):
    def __init__(self, *args, **kwargs):
        default_message = "Token is required. Use filesocket -h for help"
        if not args:
            args = (default_message,)
        super().__init__(*args, **kwargs)
