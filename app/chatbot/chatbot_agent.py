from chatbot.message import Message
from chatbot.chatbot_models import TextPreferences
from models.mongo_utils import MongoUtils
from chatbot.user_texts_parser import parse_user_text
from recommending_v2.point_of_interest.poi_provider import PoiProvider
from recommending_v2.recommender import Recommender


class ChatbotAgent:
    def __init__(self, recommender: Recommender, poi_provider:PoiProvider, db_connection: MongoUtils):
        self.messages = []
        self.first_incentive_used = False
        self.date_message_used = False
        self.region_message_used = False

        self.user_information_text = ''
        self.trip_date_text = None
        self.region_text = None

        self.recommender = recommender
        self.db_connection = db_connection
        self.poi_provider = poi_provider

        self.is_finished = False

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

    def save_text_prefs(self, mongo_utils, user_id=None):
        texts_collection = mongo_utils.get_collection('text-inputs')
        if user_id is not None:
            to_save = TextPreferences(user_id=user_id,
                                      preferences_text=self.user_information_text,
                                      date_text=self.trip_date_text)

            texts_collection.insert_one(to_save.to_bson())

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
                             "- pomóż mi lepiej poznać Twoje preferencje i opowiedz o tym, co lubisz.")

            self.add_bot_message(more_text)

        elif not self.region_message_used:
            for message in self.messages:
                if message.author == 'user':
                    self.user_information_text += message.text + ' '
            self.add_bot_message("Podaj nazwę miasta lub regionu, w którym ma się odbyć wycieczka.")
            self.region_message_used = True
        elif not self.date_message_used:
            if self.region_text is None:
                self.region_text = self.messages[-1].text

            date_text = "Kiedy odbędzie się i jak długo będzie trwała Twoja wycieczka?"
            self.add_bot_message(date_text)
            self.date_message_used = True
        else:
            if self.trip_date_text is None:
                self.trip_date_text = self.messages[-1].text

            self.add_bot_message(f"Podane preferencje: {self.user_information_text} \n"
                                 f"Podana data: {self.trip_date_text} \n"
                                 f"Miejsce wycieczki: {self.region_text}")

            dates, classes = parse_user_text(self.user_information_text, self.trip_date_text, self.region_text,
                                             self.recommender, self.poi_provider, self.db_connection)

            self.add_bot_message(f"Kategorie atrakcji turystycznych, które powinieneś polubić: {classes} \n"
                                 f"Daty: {dates}")

            region_found = self.poi_provider.last_fetch_success
            if not region_found:
                self.add_bot_message("Nie znaleziono regionu o nazwie: " + self.region_text)
            self.is_finished = True
            self.end_conversation()
