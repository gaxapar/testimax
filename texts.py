back = "⬅ Назад"
cancel = "🚫 Отмена"
mini_tests_list_button = "💣 Пройти минитест"
friendship_test_button = "❤️ Сертификат дружбы"
my_mini_tests_button = "🧩 Мои минитесты"
random_mini_test_button = "🎲 Случайный минитест"
interactive_tests_button = "📋 Интерактивные тесты"
save_mini_test_button = "✅ Сохранить"
share_mini_test_button = "📤 Поделиться"
add_mini_test_photo_button = "🎆 Добавить облолжку"
mini_test_answers_button = "🌀 Варианты ответов"
delete_mini_test_button = "❌ Удалить минитест"
delete_mini_test_confirm_button = "Да, удалить"
add_mini_test_answer_button = "➕ Добавить вариант"
remove_mini_test_answer_button = "➖ Удалить вариант"
create_mini_test_button = "➕ Создать минитест"
proceed_mini_test_button = "💥 Пройти"
previous_page_button = "⬅️"
next_page_button = "➡️"
proceed_interactive_test_button = "👉🏻 Пройти"

start = """
<b>👋 Привет, {full_name}!

Я бот, в котором ты можешь пройти разные минитесты и тесты-квизы, а также создавать собственные тесты и делиться ими с другими.</b>
"""  # noqa: E501

main_menu = "💼 Меню бота:"


enter_mini_test_title = """
<b>⭐️ Придумай название для минитеста

✍️ Отправь мне название или вопрос твоего будущего минитеста 🤩

💡 Пример:</b> <i>«Какой ты зайка?»</i>

<i>🔒 Созданный минитест появится в общем списке после 5 использований.</i>
"""

enter_mini_test_title_invalid = "Введи название для минитеста в виде текста. Например: «Какой ты зайка?»"

enter_mini_test_answers = """
<b>🌟 Придумай ответы

✍️ Отлично, теперь оправь мне варианты ответов для своего минитеста

💡 Пример:</b> <i>«Сегодня ты черный зайка :)»</i>

<i>🖼 Можно отправлять фото с подписью</i>
"""

enter_mini_test_answers_invalid = """
Введи вариант ответа в виде текста или фото с подписью. Например: «Сегодня ты черный зайка :)»
"""

enter_more_mini_test_answers = """
<b>✅ Вариант ответа успешно добавлен! ✅</b>

<i>✨ Отправляй следующие варианты ответов к своему минитесту или сохраняй варианты</i>
"""

mini_test_menu = """
<b>⚙️ Меню управления твоим мини-тестом:</b>

<b>✏️ Название минитеста</b> - {title}
<b>📊 Количество использований</b> - {usages}
<b>🏆 Позиция минитеста в топе</b> - {place_in_top}
"""

mini_test_share_text = """
Нажми, чтобы пройти минитест «{title}»

https://max.ru/{bot_username}?start=mini-{test_id}
"""

my_mini_tests_list = """
<b>🗂 Ваши минитесты:

💫 Создано</b> - <i>{user_tests_count}</i>
"""

delete_mini_test_confirm = """
<b>🗑 Удаление минитеста</b>

Ты правда хочешь удалить минитест <code>{title}</code>?
"""

mini_test_not_found = "Минитест не найден"
mini_test_answer_not_found = "Вариант ответа не найден"

mini_test_answers_menu = """
<b>⚙️ Меню управления твоим минитестом:</b>

<b>Варианты:</b> {answers}
"""

remove_mini_test_answer_menu = """
<b>🗑 Удаление варианта ответа</b>

💬 Выбери ответ который хочешь удалить из минитеста.
"""

no_tests_available = "Пока нет ни одного минитеста 😔"
no_answers_available = "Пока нет ни одного варианта ответа 😔"

mini_tests_list_menu = "<b>Лучшие минитесты, собранные со всего Max! 🌐</b>"

send_mini_test_photo = """
<b>🖼 Добавление обложки</b>

💬 Отправь фото для обложки к своему минитесту.
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
quizzes_list_button = "🧠 Пройти тест"
my_quizzes_button = "📚 Мои тесты"
random_quiz_button = "🎲 Случайный тест"
save_quiz_button = "✅ Сохранить тест"
share_quiz_button = "📤 Поделиться тестом"
add_quiz_photo_button = "🖼 Добавить обложку теста"
quiz_questions_button = "❓ Вопросы"
delete_quiz_button = "❌ Удалить тест"
delete_quiz_confirm_button = "Да, удалить"
add_quiz_question_button = "➕ Добавить вопрос"
save_quiz_answers_button = "✅ Сохранить ответы"
create_quiz_button = "➕ Создать тест"
proceed_quiz_button = "▶️ Пройти тест"
proceed_quiz_review_button = "▶️ Пройти"
approve_quiz_button = "✅ Подтвердить"
decline_quiz_button = "❌ Отклонить"

quizzes_list_menu = "<b>Лучшие тесты, собранные со всего Max! 🌐</b>"

quiz_not_found = "Тест не найден"
quiz_question_not_found = "Вопрос теста не найден"

quiz_questions_menu = """
<b>⚙️ Меню управления тестом:</b>

<b>Вопросы:</b>
{questions}
"""

no_quizzes_available = "Пока нет ни одного теста 😔"
no_questions_available = "Пока нет ни одного вопроса 😔"

my_quizzes_list = """
<b>🗂 Ваши тесты:

💫 Создано</b> - <i>{user_quizzes_count}</i>
"""

send_quiz_photo = """
<b>🖼 Добавление обложки теста</b>

💬 Отправь фото для обложки к своему тесту.
"""

send_quiz_photo_invalid = "Пожалуйста, отправь фото для обложки к своему тесту."


delete_quiz_confirm = """
<b>🗑 Удаление теста</b>

Ты правда хочешь удалить тест <code>{title}</code>?
"""

enter_quiz_title = """
<b>⭐️ Придумай название для теста

✍️ Отправь мне название твоего будущего теста

💡 Пример:</b> <i>«Узнай твою профессию»</i>

<i>🔒 Созданный тест появится в общем списке после 5 использований.</i>
"""

enter_quiz_title_invalid = "Введи название для теста в виде текста. Например: «Узнай твою профессию»"

enter_quiz_description = """
<b>📝 Придумай описание для теста

✍️ Отправь мне описание теста, чтобы люди поняли о чем он

💡 Пример:</b> <i>«Пройдите тест из 5 вопросов и узнайте, кем вы могли бы работать в альтернативной реальности»</i>
"""

enter_quiz_description_invalid = "Введи описание для теста в виде текста."

enter_quiz_question = """
<b>✍️ Введите текст вопроса</b>

Можно отправить фото с подписью.
"""

enter_quiz_question_invalid = "Введи вопрос в виде текста или фото с подписью."

enter_quiz_answers = """
<b>🌟 Придумай варианты ответов</b>

Отправляй варианты ответов по одному, а когда закончишь — нажми <b>«Сохранить ответы»</b>.
"""

enter_quiz_answers_invalid = "Введи вариант ответа в виде текста."

enter_quiz_answer = """
<b>✍️ Введите текст ответа</b>

Можно отправить только текст.
"""

enter_quiz_answer_invalid = "Введи ответ в виде текста."

enter_more_quiz_answers = """
<b>✅ Вариант ответа успешно добавлен!</b>

Отправляй следующие варианты ответов или нажми <b>«Сохранить ответы»</b>.
"""

enter_quiz_questions_draft_menu = """
<b>🧩 Вопрос добавлен в черновик теста</b>

<b>Сейчас в черновике:</b>
{questions}

Отправляй следующий вопрос или нажми <b>«Сохранить тест»</b>.
"""

save_quiz_answers_required = "Сначала нажми «Сохранить ответы» для этого вопроса."
add_quiz_answer_button = "➕ Добавить ответ"

quiz_menu = """
<b>⚙️ Меню управления твоим тестом:</b>

<b>✏️ Название теста</b> - {title}
<b>📊 Количество использований</b> - {usages}
<b>🏆 Позиция теста в топе</b> - {place_in_top}
"""

quiz_share_text = """
Нажми, чтобы пройти тест «{title}»

https://max.ru/{bot_username}?start=quiz-{test_id}
"""

choose_correct_answer = "<b>Выберите правильный ответ для текущего вопроса:</b>"

quiz_result = """
<b>✅ Тест пройден!</b>

<b>Результат:</b> {correct}/{total} правильных ответов
"""

quiz_review_complete = """
<b>Тест пройден для проверки.</b>

Подтвердите публикацию или отклоните тест.
"""

quiz_review_approved = "<b>Тест подтверждён.</b>"

quiz_review_declined = "<b>Тест отклонён.</b>"

quiz_review_admin_message = """
<b>🛡️ ТЕСТ НА ПРОВЕРКУ</b>

<b>{title}</b>

{description}

<b>Вопросов:</b> {questions_count}
<b>Создатель:</b> <code>{creator_id}</code> {creator_username}
"""

quiz_review_approved_creator = """
<b>✅ Ваш тест <code>{title}</code> подтверждён администратором и опубликован.</b>
"""

quiz_review_declined_creator = """
<b>❌ Ваш тест <code>{title}</code> отклонён администратором.</b>
"""

quiz_sent_for_review = """
<b>✅ Ваш тест отправлен на проверку администратору!</b>

После одобрения он появится в общем списке тестов.
"""
