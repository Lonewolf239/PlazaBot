import hashlib


class Hacher:
    @staticmethod
    def hash(data: str, has_limit: bool = True) -> str:
        if has_limit:
            return hashlib.sha256(data.encode()).hexdigest()[:24]
        return hashlib.sha256(data.encode()).hexdigest()
