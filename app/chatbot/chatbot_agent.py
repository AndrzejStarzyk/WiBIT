from datetime import date, timedelta

from models.mongo_utils import MongoUtils
from chatbot.message import Message
from chatbot.chatbot_models import TextPreferences
from creating_trip.algorythm_models.constraint import CategoryConstraint
from date_from_text.date_recognition import parse_date_text
from creating_trip.poi_provider import PoiProvider
from creating_trip.recommender import Recommender
from chatbot.text_to_prefs import TextProcessor
from chatbot.text_to_prefs_knowledge import TextProcessorKnowledge


class ChatbotAgent:
    def __init__(self, recommender: Recommender, poi_provider: PoiProvider, db_connection: MongoUtils,
                 text_processor_experience: TextProcessor, text_processor_knowledge: TextProcessorKnowledge,
                 state_dict: dict):

        self.recommender = recommender
        self.db_connection = db_connection
        self.poi_provider = poi_provider
        self.text_processor_experience = text_processor_experience
        self.text_processor_knowledge = text_processor_knowledge

        self.messages = [Message(msg_dict['author'], msg_dict['text']) for msg_dict in
                         state_dict.get('messages', [])]
        self.first_incentive_used = state_dict.get('first_incentive_used', False)
        self.date_message_used = state_dict.get('date_message_used', False)
        self.region_message_used = state_dict.get('region_message_used', False)
        self.user_information_text = state_dict.get('user_information_text', '')
        self.trip_date_text = state_dict.get('trip_date_text', None)
        self.region_text = state_dict.get('region_text', None)
        self.mode = state_dict.get('mode', 'experience')
        self.is_finished = state_dict.get('is_finished', False)

        init_message = ("Witaj w wirtualnym biurze informacji turystycznej. "
                        "Powiedz mi więcej o tym, w jaki sposób lubisz odwiedzać nowe miejsca, "
                        "abym mógł pomóc Ci z wyborem atrakcji.")

        if not self.messages:
            self.add_bot_message(init_message)

    def get_all_messages(self):
        return self.messages

    def add_user_message(self, message: str, mode: str):
        self.messages.append(Message('user', message))
        self.mode = mode
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

        if user_input_len < 180:
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

            self.add_bot_message("Tworzę wycieczkę...")

            dates, classes = self.parse_user_text(self.user_information_text, self.trip_date_text, self.region_text,
                                                  self.recommender, self.poi_provider, self.db_connection, self.mode)

            region_found = self.poi_provider.last_fetch_success
            if not region_found:
                self.add_bot_message("Nie znaleziono regionu o nazwie: " + self.region_text)
            self.is_finished = True
            self.end_conversation()

    def parse_user_text(self, user_information: str, user_date: str, user_region: str,
                        recommender: Recommender, poi_provider: PoiProvider, db_connection: MongoUtils, mode: str):

        poi_provider.fetch_pois(user_region)

        schedule_parameters = parse_date_text(user_date)

        start_date: date = schedule_parameters.start_date
        tmp = start_date
        dates = [start_date.isoformat()]
        i = 1
        while tmp != schedule_parameters.end_date:
            tmp = start_date + timedelta(days=i)
            dates.append(tmp.isoformat())
            i += 1

        recommender.dates = dates
        recommender.days = len(dates)

        schedule_hours = [('10:00', '18:00')
                          for _ in range(0, len(dates))]
        recommender.hours = schedule_hours
        recommender.create_schedule()

        if mode == 'experience':
            classes = self.text_processor_experience.predict_classes(user_information)
        elif mode == 'knowledge':
            classes = self.text_processor_knowledge.predict_classes(user_information)
        else:
            classes = []

        recommender.add_constraint(CategoryConstraint(classes, db_connection))

        return dates, classes

    def store_as_dict(self):
        chatbot_agent_dict = {
            'messages': self.messages,
            'first_incentive_used': self.first_incentive_used,
            'date_message_used': self.date_message_used,
            'region_message_used': self.region_message_used,
            'user_information_text': self.user_information_text,
            'trip_date_text': self.trip_date_text,
            'region_text': self.region_text,
            'mode': self.mode,
            'is_finished': self.is_finished
        }

        return chatbot_agent_dict
