"""class Message:
    def __init__(self, author: str, text: str):
        self.author = author
        self.text = text

    def to_dict(self) -> dict:
        return {'author': self.author, 'text': self.text}"""

from dataclasses import dataclass


@dataclass
class Message:
    author: str
    text: str
