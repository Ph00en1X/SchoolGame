from threading import Thread
import os
import time
from typing import Dict, List, Any
from collections import defaultdict
import telebot
from telebot.types import Message, ReplyKeyboardMarkup, KeyboardButton
import requests


class GameConfig:
    """Конфигурация игры с вопросами и настройками."""

    INITIAL_COINS = 3

    # Сценарий игры
    SCENARIO: List[Dict[str, Any]] = [
        # Сцена 1
        {
            'text': 'Вы открываете глаза и оглядываясь видите, что вы находитесь в закрытой валуном пещере вместе со странно одетым человеком и кучей хлама на полу.',
            'image': 'https://disk.yandex.com/i/PG-h5XFN1Ecxrw',
            'choices': [
                {
                    'text': 'Что?',
                    'next_scene': 2-1
                }
            ]
        },
        # Сцена 2
        {
            'text': '???:\n"Здравствуйте, молодой человек! Извините, что побеспокоил вас, но мне не обойтись без вашей помощи, поэтому я призвал вас сюда."',
            'image': 'https://disk.yandex.com/i/SpkXIH4MxMdQjw',
            'choices': [
                {
                    'text': 'Вы кто, и почему я здесь?',
                    'next_scene': 3-1
                }
            ]
        },
        # Сцена 3
        {
            'text': '???:\n"Я волшебник, и пока я искал ингредиенты для своего нового зелья, меня завалило в этой пещере. Я попробовал много разных способов, чтобы выбраться, но у меня ничего не получилось. Меня, кстати, зовут Григорий, <b>а вас как?</b>"',
            'image': 'https://disk.yandex.com/i/gKNOBLJb7_B-0w',
            'expect_input': 'player_name'
        },
        # Сцена 4
        {
            'text': '<b>Волшебник Григорий</b>:\n"Приятно познакомиться, <b>{player_name}</b>, теперь помоги мне, пожалуйста, выбраться отсюда, после чего я тебя отправлю назад в твой мир."',
            'choices': [
                {
                    'text': 'Придется помочь, что поделаешь!',
                    'next_scene': 5-1
                }
            ]
        },
        # Сцена 5 - Первое задание
        {
            'text': 'Перед вами огромный валун, преграждающий выход из пещеры.',
            'image': 'https://disk.yandex.com/i/J6uIRNufxWNBAg',
            'question': 'Камень весит 120 кг. Рычаг поставлен так, что его плечи относятся как 1:3, считая от камня. g = 10 м/с^2. Какую силу нужно приложить, чтобы поднять камень? \nОтвет напишите числом в ньютонах.',
            'answers': ['400'],
            'reward': 1,
            'emoji': '🛠️',
            'next_scene': 6-1
        },
        # Сцена 6
        {
            'text': '<b>Волшебник Григорий</b>:\n"Спасибо тебе за помощь, <b>{player_name}</b>, теперь перейдем к твоему возвращению. Пойдем ко мне домой, мне понадобятся оттуда важные ингредиенты."',
            'image': 'https://disk.yandex.com/i/oGk1WXMd1Qfc3w',
            'choices': [
                {
                    'text': 'Не за что.',
                    'next_scene': 7-1
                }
            ]
        },
        # Сцена 7
        {
            'text': '<b>Волшебник Григорий</b>:\n"Постой пока тут, а я сбегаю за ингредиентами."',
            'image': 'https://disk.yandex.com/i/w-lZvyYudMTYuA',
            'choices': [
                {
                    'text': 'Хорошо.',
                    'next_scene': 8-1
                }
            ]
        },
        # Сцена 8
        {
            'text': 'Ожидая, пока волшебник ищет ингредиенты у себя дома, вы слышите его недовольные возгласы:\n\nВолшебник Григорий:\n"Как же так?!? ГДЕ ЖЕ МОИ ДОРОГИЕ ИНГРЕДИЕНТЫ?!? ГДЕ МОЯ ПРЕКРАСНАЯ КНИГА АЛХИМИИ???"\n\nСлушая эти возгласы, вы понимаете, что еще не скоро вернетесь...',
            'image': 'https://disk.yandex.com/i/oRGDwtNaauXbjw',
            'choices': [
                {
                    'text': '...',
                    'next_scene': 9-1
                }
            ]
        },
        # Сцена 9
        {
            'text': '<b>Волшебник Григорий</b>:\n"Я глубочайше извиняюсь, ведь пока я сидел в пещере, из моего дома украли все ингредиенты и мою любимую книгу алхимии, так что вам придется найти другую и принести важный ингредиент, про который говорится на странице 22."',
            'image': 'https://disk.yandex.com/i/mMRfmO20yc1t0w',
            'choices': [
                {
                    'text': 'А где мне её найти?',
                    'next_scene': 10-1
                }
            ]
        },
        # Сцена 10
        {
            'text': '<b>Волшебник Григорий</b>:\n"Она находится в великой запечатанной библиотеке. Давай я подскажу тебе дорогу."',
            'image': 'https://disk.yandex.com/i/jyhga6ldiSWcPA',
            'choices': [
                {
                    'text': 'Ну так пойдёмте!',
                    'next_scene': 11-1
                }
            ]
        },
        # Сцена 11 - Второе задание
        {
            'text': 'Вы находитесь в великой запечатанной библиотеке. Вы замечаете золотую шкатулку, которая будто светится в темноте.',
            'image': 'https://disk.yandex.com/i/4tLSD6woqtamuw',
            'question': '<b>(x+7)(-8x + 5) = 0</b> \nКодом от шкатулки является меньший из корней уравнения.',
            'answers': ['-7'],
            'reward': 1,
            'emoji': '🔑',
            'next_scene': 12-1
        },
        # Сцена 12
        {
            'text': '<b>Волшебник Григорий</b>:\n"Ты молодец!"',
            'choices': [
                {
                    'text': 'Осталось найти страницу 22 и достать ингредиент. Вот же он, \'Цветок бытия\' и его можно найти... Что это? Какой-то шифр?',
                    'next_scene': 13-1
                }
            ]
        },
        # Сцена 13 - Третье задание
        {
            'text': 'В книге на странице 22 вы находите шифр.',
            'image': 'https://disk.yandex.com/i/Oc7qe5cT2KV24w',
            'question': 'Л|X- \nВ|X--\nА|-X-\nЕ|-X\nМ|--\nС|-\nРасшивруйте: <b>x--x---</b>',
            'answers': ['лес'],
            'reward': 1,
            'emoji': '📖',
            'next_scene': 14-1
        },
        # Сцена 14
        {
            'text': 'Наконец-то разгадав шифр книги, вы вычитываете, что волшебный цветок растет глубоко в подземелье, находящемся под библиотекой, и решаете за ним туда спуститься.',
            'image': 'https://disk.yandex.com/i/Ln1MSVng7gJKoA',
            'choices': [
                {
                    'text': '...',
                    'next_scene': 15-1
                }
            ]
        },
        # Сцена 15
        {
            'text': 'Проходя вдоль еле освещенных стен, вы осматриваетесь вокруг в поисках нужного вам цветка, как неожиданно на вас выходит орк!',
            'image': 'https://disk.yandex.com/i/A66GaJ4s8OomRQ',
            'choices': [
                {
                    'text': '...',
                    'next_scene': 16-1
                }
            ]
        },
        # Сцена 16
        {
            'text': '<b>Орк</b>:\n"Здравствуй, человечишка! Что ты забыл в моем подземелье?!?"',
            'image': 'https://disk.yandex.com/i/8mojvztfy6ZshQ',
            'choices': [
                {
                    'text': 'Я... Я пришел за цветком бытия для зелья волшебника.',
                    'next_scene': 17-1
                }
            ]
        },
        # Сцена 17
        {
            'text': '<b>Орк</b>:\n"Ну просто так я тебе его не отдам, так что ответь-ка мне на три вопроса, и тогда я подумаю, давать тебе его или нет!"',
            'next_scene': 18-1
        },
        # Сцена 18 - Вопросы орка
        # Вопрос 1
        {
            'text': '<b>Орк</b>:\n"Первый вопрос: Брусок имеет массу 15кг. g = 9.81 м/с^2."',
            'question': 'Какую силу надо приложить чтобы поднять брусок?',
            'answers': ['147'],
            'reward': 1,
            'emoji': '🤔',
            'next_scene': 19-1
        },
        # Вопрос 2
        {
            'text': '<b>Орк</b>:\n"Второй вопрос: <b>15x - 17 = 9x + 19</b>"',
            'question': 'Найди X!',
            'answers': ['6'],
            'reward': 1,
            'emoji': '🧠',
            'next_scene': 20-1
        },
        # Вопрос 3
        {
            'text': '<b>Орк</b>:\n"<b>Третий вопрос:</b> \nР|₽?\nЫ|??₽\nБ|??\nК|?₽\nА|?₽?"',
            'question': 'Разгадай - <b>????₽?₽</b>!!!',
            'answers': ['бык'],
            'reward': 1,
            'emoji': '⏳',
            'next_scene': 21-1
        },
        # Сцена 21
        {
            'text': '<b>Орк</b>:\n"Хорошо, отдам я тебе этот цветок, только больше не возвращайся!"',
            'image': 'https://disk.yandex.com/i/_d3Qgei7TYOa5w',
            'choices': [
                {
                    'text': 'Конечно.',
                    'next_scene': 22-1
                }
            ]
        },
        # Сцена 22
        {
            'text': 'Дом волшеника.',
            'image': 'https://disk.yandex.com/i/OpRXR5WG8ZU9yQ',
            'choices': [
                {
                    'text': 'Григорий, выходите! Я достал нужный ингредиент!',
                    'next_scene': 23-1
                }
            ]
        },
        # Сцена 23
        {
            'text': '<b>Волшебник Григорий</b>:\n"Здравствуй, <b>{player_name}</b>, слава богу, ты вернулся! Давай сюда этот ингредиент, и я тебя наконец-то отправлю домой."',
            'image': 'https://disk.yandex.com/i/MzhK065Ejwve0w',
            'choices': [
                {
                    'text': 'Держите.',
                    'next_scene': 24-1
                }
            ]
        },
        # Сцена 24
        {
            'text': 'Стоя снаружи, вы слышите, как волшебник трудится над зельем:\n\nВолшебник Григорий:\n"Так, мандрагору сюда, цветок сюда, чуть-чуть этого, чуть-чуть того, уже почти всё готово, осталась последняя капля и... ВСЁ!!!"',
            'image': 'https://disk.yandex.com/i/yhI1WIsrcMzlhg',
            'choices': [
                {
                    'text': 'Ура!',
                    'next_scene': 25-1
                }
            ]
        },
        # Сцена 25
        {
            'text': 'Волшебник выходит из своего дома, и вы замечаете в его руках заветное зелье, которое вернет вас домой. Перед тем как выпить его, вы прощаетесь с волшебником. Вы пьете его и за секунду до забвения слышите:\n\n"Прощайте, молодой человек, я вас никогда не забуду!"',
            'image': 'https://disk.yandex.com/i/VoDN66rJ-cMyTw',
            'choices': [
                {
                    'text': 'Прощайте!',
                    'next_scene': 26-1
                }
            ]
        },
        # Сцена 26
        {
            'text': 'Вы просыпаетесь у себя дома, почти не осознавая, что происходило последние часа 2, но вы всегда будете помнить, что знание — сила!\n\n<b>КОНЕЦ</b>',
            'game_end': True
        }
    ]


class GameState:
    """Управление состоянием игры для пользователя."""

    def __init__(self, initial_coins: int = GameConfig.INITIAL_COINS):
        self.coins = initial_coins
        self.player_name: str = None
        self.current_scene_index = 0
        # Возможные состояния: 'playing', 'awaiting_input', 'awaiting_answer', 'game_over'
        self.state = 'playing'
        self.awaiting_input_key: str = None
        self.time_sleep: float = 0.25

    def add_coins(self, amount: int) -> None:
        """Добавить монеты."""
        self.coins += amount

    def remove_coins(self, amount: int = 1) -> None:
        """Удалить монеты."""
        self.coins = max(0, self.coins - amount)

    def is_game_over(self) -> bool:
        """Проверка окончания игры."""
        return self.state == 'game_over' or self.coins <= 0

    def reset(self) -> None:
        """Сбросить состояние игры."""
        self.coins = GameConfig.INITIAL_COINS
        self.player_name = None
        self.current_scene_index = 0
        self.state = 'playing'
        self.awaiting_input_key = None


class GameBot:
    """Основной класс бота игры."""

    def __init__(self, token: str):
        self.bot = telebot.TeleBot(token, parse_mode='HTML')
        self.user_states: Dict[int, GameState] = defaultdict(GameState)
        self._register_handlers()

    def _register_handlers(self) -> None:
        """Регистрация обработчиков сообщений."""
        self.bot.message_handler(commands=['start'])(self.start_menu)
        self.bot.message_handler(
            func=lambda message: message.text.lower() == 'начать игру')(self.start_game)
        self.bot.message_handler(
            func=lambda message: message.text.lower() == 'правила')(self.show_rules)
        self.bot.message_handler(
            func=lambda message: message.text.lower() == 'начать заново')(self.restart_game)
        self.bot.message_handler(
            func=lambda message: True)(self.handle_message)

    def start_menu(self, message: Message) -> None:
        """Стартовое меню с выбором действий."""
        chat_id = message.chat.id
        user_name = message.from_user.first_name or "Игрок"

        markup = ReplyKeyboardMarkup(
            resize_keyboard=True, one_time_keyboard=True)
        start_button = KeyboardButton("Начать игру")
        rules_button = KeyboardButton("Правила")
        markup.add(start_button, rules_button)

        welcome_message = (
            f"👋 Привет, <b>{user_name}</b>!\n\n"
            "🎮 Добро пожаловать в захватывающее квест-приключение!\n\n"
            "Выбери, что хочешь сделать:\n"
            "• <i>Начать игру</i> - немедленно погрузиться в приключение\n"
            "• <i>Правила</i> - узнать больше о игровом процессе"
        )

        self.bot.send_message(chat_id, welcome_message, reply_markup=markup)

    def show_rules(self, message: Message) -> None:
        """Отображение правил игры."""
        chat_id = message.chat.id
        user_name = message.from_user.first_name or "Игрок"

        markup = ReplyKeyboardMarkup(
            resize_keyboard=True, one_time_keyboard=True)
        start_button = KeyboardButton("Начать игру")
        markup.add(start_button)

        rules_message = (
            f"📜 <b>Правила игры для {user_name}</b>\n\n"
            "🎲 <b>Основные механики:</b>\n"
            "• У вас есть <u>3 начальные монеты</u>\n"
            "• За каждый правильный ответ вы получаете монеты\n"
            "• За неправильный ответ теряете монету\n\n"
            "❗ <b>Условия завершения игры:</b>\n"
            "• Игра заканчивается, если монеты закончились\n"
            "• Победа - пройдены все задания\n\n"
            "💡 <b>Советы:</b>\n"
            "• Внимательно читайте вопросы\n"
            "• Регистр ответа не важен\n"
            "• Можно использовать разные формы ответа\n\n"
            "🍀 <b>Удачи в приключении!</b>"
        )

        self.bot.send_message(chat_id, rules_message, reply_markup=markup)

    def start_game(self, message: Message) -> None:
        """Начало новой игры."""
        chat_id = message.chat.id
        user_name = message.from_user.first_name or "Игрок"

        self.user_states[chat_id] = GameState()

        welcome_message = (
            f"🎮 Привет, <b>{user_name}</b>! Твое приключение начинается!\n"
            "🪙 У тебя <b>3 монеты</b> для захватывающего квеста.\n"
            "❓ Готов отправиться в путешествие?"
        )

        self.bot.send_message(chat_id, welcome_message)
        time.sleep(self.user_states[chat_id].time_sleep)
        self.send_scene(chat_id)

    def restart_game(self, message: Message) -> None:
        """Перезапуск игры."""
        chat_id = message.chat.id
        self.user_states[chat_id].reset()

        restart_message = "🔄 Игра начата заново!"

        self.bot.send_message(chat_id, restart_message)
        time.sleep(self.user_states[chat_id].time_sleep)
        self.send_scene(chat_id)

    def send_scene(self, chat_id: int) -> None:
        """Отправка текущей сцены."""
        user_state = self.user_states[chat_id]

        if user_state.is_game_over():
            self.handle_game_end(chat_id)
            return

        if user_state.current_scene_index >= len(GameConfig.SCENARIO):
            user_state.state = 'game_over'
            self.handle_game_end(chat_id)
            return

        scene = GameConfig.SCENARIO[user_state.current_scene_index]
        text = scene['text'].format(
            player_name=user_state.player_name or 'Игрок')
        image = scene.get('image')

        if image:
            self.send_image_with_caption(chat_id, image, text)
        else:
            self.bot.send_message(chat_id, text)
        time.sleep(self.user_states[chat_id].time_sleep)

        if 'choices' in scene:
            markup = ReplyKeyboardMarkup(
                resize_keyboard=True, one_time_keyboard=True)
            for choice in scene['choices']:
                button = KeyboardButton(choice['text'])
                markup.add(button)
            self.bot.send_message(
                chat_id, 'Выберите действие', reply_markup=markup)
        elif 'expect_input' in scene:
            user_state.awaiting_input_key = scene['expect_input']
            user_state.state = 'awaiting_input'
        elif 'question' in scene:
            user_state.state = 'awaiting_answer'
            question = scene['question']
            self.bot.send_message(chat_id, question)
        elif 'game_end' in scene:
            user_state.state = 'game_over'
            self.handle_game_end(chat_id)
        else:
            user_state.current_scene_index = scene.get(
                'next_scene', user_state.current_scene_index + 1)
            self.send_scene(chat_id)

    def handle_message(self, message: Message) -> None:
        """Обработка входящих сообщений."""
        chat_id = message.chat.id
        user_state = self.user_states.get(chat_id)

        if user_state is None:
            self.start_menu(message)
            return

        if user_state.state == 'awaiting_input':
            input_key = user_state.awaiting_input_key
            setattr(user_state, input_key, message.text.strip())
            user_state.awaiting_input_key = None
            user_state.state = 'playing'
            user_state.current_scene_index += 1
            self.send_scene(chat_id)
        elif user_state.state == 'awaiting_answer':
            self.process_answer(message)
        elif user_state.state == 'playing':
            self.process_choice(message)
        elif user_state.state == 'game_over':
            if message.text.strip().lower() == 'начать заново':
                self.restart_game(message)
            else:
                self.bot.send_message(
                    chat_id, "Игра окончена. Нажмите 'Начать заново', чтобы сыграть еще раз.")

    def process_choice(self, message: Message) -> None:
        """Обработка выбора пользователя."""
        chat_id = message.chat.id
        user_state = self.user_states[chat_id]
        scene = GameConfig.SCENARIO[user_state.current_scene_index]

        choices = scene.get('choices', [])
        user_choice_text = message.text.strip()

        for choice in choices:
            if choice['text'] == user_choice_text:
                user_state.current_scene_index = choice.get(
                    'next_scene', user_state.current_scene_index + 1)
                self.send_scene(chat_id)
                return

        self.bot.send_message(
            chat_id, "Пожалуйста, выберите один из доступных вариантов.")

    def process_answer(self, message: Message) -> None:
        """Обработка ответа пользователя на вопрос."""
        chat_id = message.chat.id
        user_state = self.user_states[chat_id]
        scene = GameConfig.SCENARIO[user_state.current_scene_index]

        user_answer = message.text.strip().lower()
        correct_answers = scene.get('answers', [])

        if user_answer in correct_answers:
            reward = scene.get('reward', 0)
            user_state.add_coins(reward)
            success_message = (
                f"{scene.get('emoji', '🎉')} Правильно!\n"
                f"🪙 Вы получаете {reward} монет.\n"
                f"💰 Всего монет: {user_state.coins}"
            )
            self.bot.send_message(chat_id, success_message)
            time.sleep(self.user_states[chat_id].time_sleep)
            user_state.state = 'playing'
            user_state.current_scene_index = scene.get(
                'next_scene', user_state.current_scene_index + 1)
            self.send_scene(chat_id)
        else:
            user_state.remove_coins()
            if user_state.is_game_over():
                self.handle_game_end(chat_id)
            else:
                error_message = (
                    "❌ Неправильный ответ!\n"
                    f"🪙 У вас осталось {user_state.coins} монет.\n"
                    "🔄 Попробуйте снова."
                )
                self.bot.send_message(chat_id, error_message)

    def handle_game_end(self, chat_id: int) -> None:
        """Обработка окончания игры."""
        user_state = self.user_states[chat_id]
        user_state.state = 'game_over'

        if user_state.coins <= 0:
            end_message = "❌ Игра окончена. У вас закончились монеты."
        else:
            end_message = "🏆 Поздравляем! Вы прошли все испытания!"

        self.bot.send_message(chat_id, end_message)

        markup = ReplyKeyboardMarkup(
            resize_keyboard=True, one_time_keyboard=True)
        restart_button = KeyboardButton("Начать заново")
        markup.add(restart_button)

        self.bot.send_message(
            chat_id, "Хотите начать игру заново?", reply_markup=markup)

    def send_image_with_caption(self, chat_id: int, image_name: str, caption: str) -> None:
        """Отправка изображения с подписью."""
        try:
            self.bot.send_photo(chat_id, image_name, caption=caption)
        except FileNotFoundError:
            self.bot.send_message(chat_id, caption)

    def run(self) -> None:
        """Запуск бота."""
        # Запускаем бота
        self.bot.infinity_polling()


def main():
    API_TOKEN = os.getenv('BOT_TOKEN')
    game_bot = GameBot(API_TOKEN)
    game_bot.run()


if __name__ == '__main__':
    main()
