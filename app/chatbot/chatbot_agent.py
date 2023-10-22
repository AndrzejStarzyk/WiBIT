import random
from chatbot.message import Message


class ChatbotAgent:
    def __init__(self):
        self.messages = []
        init_message = ("Witaj w wirtualnym biurze informacji turystycznej. "
                        "Powiedz mi więcej o tym, w jaki sposób lubisz odwiedzać nowe miejsca, "
                        "abym mógł pomóc Ci z wyborem atrakcji")
        self.add_bot_message(init_message)

    def get_all_messages(self):
        return self.messages

    def add_user_message(self, message: str):
        self.messages.append(Message('user', message))
        self.generate_answer()

    def add_bot_message(self, message: str):
        self.messages.append(Message('bot', message))

    def generate_answer(self):
        # TODO chatbot login should be done here - currently placeholder only
        texts = ["Lorem ipsum dolor sit amet, consectetur adipiscing elit. ",
                 "Vestibulum ut lobortis dui. ",
                 "Praesent placerat iaculis mauris. ",
                 "Donec maximus ultrices felis, at aliquam tortor auctor efficitur. ",
                 "Vestibulum pulvinar, turpis iaculis fringilla tempor, nisi mauris iaculis nunc, in tempus libero massa vehicula arcu. "]

        random_num = random.randint(1, len(texts))

        answer = ""

        for i in range(random_num):
            answer += texts[i]

        self.add_bot_message(answer)
