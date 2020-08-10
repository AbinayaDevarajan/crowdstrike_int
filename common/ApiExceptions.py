class APIException(Exception):
    """
    This exception is returned when a API Exec is not successful.
    """
    def __init__(self, nberror):
        self.message = nberror

    def __repr__(self):
        return self.message

    def __str__(self):
        return self.message
