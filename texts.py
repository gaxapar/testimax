back = "⬅ Назад"
cancel = "🚫 Отмена"
mini_tests_list_button = "💣 Пройти мини-тест"
friendship_test_button = "❤️ Сертификат дружбы"
my_mini_tests_button = "🧩 Мои тесты"
random_mini_test_button = "🎲 Случайный тест"
interactive_tests_button = "📋 Интерактивные тесты"
save_mini_test_button = "✅ Сохранить"
share_mini_test_button = "📤 Поделиться"
add_mini_test_photo_button = "🎆 Добавить облолжку"
mini_test_answers_button = "🌀 Варианты ответов"
delete_mini_test_button = "❌ Удалить минитест"
delete_mini_test_confirm_button = "Да, удалить"
add_mini_test_answer_button = "➕ Добавить вариант"
remove_mini_test_answer_button = "➖ Удалить вариант"
create_mini_test_button = "➕ Создать тест"
proceed_mini_test_button = "💥 Пройти"
previous_page_button = "⬅️"
next_page_button = "➡️"
proceed_interactive_test_button = "👉🏻 Пройти"

start = """
<b>👋 Привет, {full_name}!

Я бот в котором ты можешь пройти разные мини-тесты, а так же сделать тест на проверку друзей и получить сертификат дружбы ✍️❤️</b>
"""  # noqa: E501

main_menu = "💼 Меню бота:"


enter_test_title = """
<b>⭐️ Придумай название для теста

✍️ Отправь мне название или вопрос твоего будущего теста🤩

💡 Пример:</b> <i>«Какой ты зайка?»</i>

<i>🔒 Созданный тест появится в общем списке после 5 использований.</i>
"""

enter_test_title_invalid = "Введи название для теста в виде текста. Например: «Какой ты зайка?»"

enter_test_answers = """
<b>🌟 Придумай ответы

✍️ Отлично, теперь оправь мне варианты ответов для своего теста

💡 Пример:</b> <i>«Сегодня ты черный зайка :)»</i>

<i>🖼 Можно отправлять фото с подписью</i>
"""

enter_test_answers_invalid = """
Введи вариант ответа в виде текста или фото с подписью. Например: «Сегодня ты черный зайка :)»
"""

enter_more_answers = """
<b>✅ Вариант ответа успешно добавлен! ✅</b>

<i>✨ Отправляй следующие варианты ответов к своему тесту или сохраняй варианты</i>
"""

test_menu = """
<b>⚙️ Меню управления твоим мини-тестом:</b>

<b>✏️ Название теста</b> - {title}
<b>📊 Количество использований</b> - {usages}
<b>🏆 Позиция теста в топе</b> - {place_in_top}
"""

test_share_text = """
Нажми, чтобы пройти тест «{title}»

https://max.ru/{bot_username}?start={test_id}
"""

my_tests_list = """
<b>🗂 Ваши тесты:

💫 Создано</b> - <i>{user_tests_count}</i>
"""

delete_mini_test_confirm = """
<b>🗑 Удаление мини-теста</b>

Ты правда хочешь удалить мини-тест <code>{title}</code>?
"""

mini_test_not_found = "Мини-тест не найден"
mini_test_answer_not_found = "Вариант ответа не найден"

mini_test_answers_menu = """
<b>⚙️ Меню управления твоим мини-тестом:</b>

<b>Варианты:</b> {answers}
"""

remove_mini_test_answer_menu = """
<b>🗑 Удаление варианта ответа</b>

💬 Выбери ответ который хочешь удалить из мини-теста.
"""

no_tests_available = "Пока нет ни одного мини-теста 😔"
no_answers_available = "Пока нет ни одного варианта ответа 😔"

mini_tests_list_menu = "<b>Лучшие быстрые тесты, собранные со всего Telegram! 🌐</b>"

send_mini_test_photo = """
<b>🖼 Добавление обложки</b>

💬 Отправь фото для обложки к своему тесту.
"""

send_mini_test_photo_invalid = "Пожалуйста, отправь фото для обложки к своему тесту."

interactive_tests_list_menu = """
<b>Интерактивные тесты ✍️</b>

<i>Выбирай тест и проходи его!</i>
"""

interactive_test_not_found = "Интерактивный тест не найден"


interactive_test_question_wrapper = """
<b>{test_title}</b>

Вопрос {question_number}/{total_questions}
👉 Твой ответ на вопрос: <b>"{question}"</b>
"""


# Quiz texts
quizzes_list_button = "🧠 Пройти квиз"
my_quizzes_button = "📚 Мои квизы"
random_quiz_button = "🎲 Случайный квиз"
save_quiz_button = "✅ Сохранить квиз"
share_quiz_button = "📤 Поделиться квизом"
add_quiz_photo_button = "🖼 Добавить обложку квиза"
quiz_questions_button = "❓ Вопросы"
delete_quiz_button = "❌ Удалить квиз"
delete_quiz_confirm_button = "Да, удалить"
add_quiz_question_button = "➕ Добавить вопрос"
create_quiz_button = "➕ Создать квиз"
proceed_quiz_button = "▶️ Пройти квиз"

quizzes_list_menu = "<b>Лучшие квизы, собранные со всего Telegram! 🌐</b>"

quiz_not_found = "Квиз не найден"
quiz_question_not_found = "Вопрос квиза не найден"

quiz_questions_menu = """
<b>⚙️ Меню управления квизом:</b>

<b>Вопросы:</b> {questions}
"""

no_quizzes_available = "Пока нет ни одного квиза 😔"
no_questions_available = "Пока нет ни одного вопроса 😔"

my_quizzes_list = """
<b>🗂 Ваши квизы:

💫 Создано</b> - <i>{user_quizzes_count}</i>
"""

send_quiz_photo = """
<b>🖼 Добавление обложки квиза</b>

💬 Отправь фото для обложки к своему квизу.
"""

send_quiz_photo_invalid = "Пожалуйста, отправь фото для обложки к своему квизу."


delete_quiz_confirm = """
<b>🗑 Удаление квиза</b>

Ты правда хочешь удалить квиз <code>{title}</code>?
"""

enter_quiz_title = """
<b>⭐️ Придумай название для квиза

✍️ Отправь мне название твоего будущего квиза

💡 Пример:</b> <i>«Узнай твою профессию»</i>

<i>🔒 Созданный квиз появится в общем списке после 5 использований.</i>
"""

enter_quiz_title_invalid = "Введи название для квиза в виде текста. Например: «Узнай твою профессию»"

enter_quiz_question = """
<b>✍️ Введите текст вопроса</b>

Можно отправить фото с подписью.
"""

enter_quiz_question_invalid = "Введи вопрос в виде текста или фото с подписью."

enter_quiz_answers = """
<b>🌟 Придумай варианты ответов</b>

Отправляй варианты ответов по одному. Пометь правильный ответ, начав сообщение с "*".
"""

enter_quiz_answers_invalid = 'Введи вариант ответа в виде текста. Пометь правильный ответ, начав сообщение с "*".'

enter_more_quiz_answers = """
<b>✅ Вариант ответа успешно добавлен!</b>

Отправляй следующие варианты ответов или нажми сохранить вопрос.
"""

quiz_menu = """
<b>⚙️ Меню управления твоим квизом:</b>

<b>✏️ Название квиза</b> - {title}
<b>📊 Количество использований</b> - {usages}
<b>🏆 Позиция квиза в топе</b> - {place_in_top}
"""

choose_correct_answer = "<b>Выберите правильный ответ для текущего вопроса:</b>"
