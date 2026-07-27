


class AirportNotFoundError(Exception):
    def __init__(self, invalid_codes: set):
        self.invalid_codes = invalid_codes
        super().__init__(f"Airports not found: {invalid_codes}")