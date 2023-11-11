import random
from chatbot.message import Message


class ChatbotAgent:
    def __init__(self):
        self.messages = []
        self.first_incentive_used = False
        self.date_message_used = False

        self.user_information_text = ''
        self.trip_date_text = None

        init_message = ("Witaj w wirtualnym biurze informacji turystycznej. "
                        "Powiedz mi więcej o tym, w jaki sposób lubisz odwiedzać nowe miejsca, "
                        "abym mógł pomóc Ci z wyborem atrakcji.")

        self.add_bot_message(init_message)

    def get_all_messages(self):
        return self.messages

    def add_user_message(self, message: str):
        self.messages.append(Message('user', message))
        self.generate_answer()

    def add_bot_message(self, message: str):
        self.messages.append(Message('bot', message))

    def end_conversation(self):
        self.messages.append(Message('bot_final', "Oto wycieczka przygotowana specjalnie dla Ciebie, "
                                                  "mam nadzieję, że pomogłem."))

    def generate_answer(self):
        user_input_len = 0

        for message in self.messages:
            if message.author == 'user':
                user_input_len += len(message.text)

        if user_input_len < 250:
            if not self.first_incentive_used:
                more_text = ("Podaj więcej informacji o sobie - czym się interesujesz? Jakie jest twoje hobby? "
                             "W jakich miejscach lubisz spędzać czas i jeść posiłki? "
                             "Jakie rodzaje atrakcji turystycznych lubisz? "
                             "Wolisz aktywne, czy bierne sposoby spędzania swojego czasu?")
                self.first_incentive_used = True

            else:
                more_text = ("Wciąż mam zbyt mało informacji, aby pomóc Ci zaplanować wycieczkę "
                             "- pomóż mi lepiej poznać Twoje preferencje.")

            self.add_bot_message(more_text)

        elif not self.date_message_used:

            for message in self.messages:
                if message.author == 'user':
                    self.user_information_text += message.text + ' '

            self.date_message_used = True
            date_text = "Podaj mi planowany termin Twojej wycieczki."
            self.add_bot_message(date_text)

        else:
            if self.trip_date_text is None:
                self.trip_date_text = self.messages[-1].text

            self.add_bot_message(f"Podane preferencje: {self.user_information_text} "
                                 f"Podana data: {self.trip_date_text}")

            self.end_conversation()

            # TODO - something like propose_trip(self.user_information_text, self.trip_date_text)
