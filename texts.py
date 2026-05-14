back = "⬅ Назад"
cancel = "🚫 Отмена"
mini_tests_list_button = "💣 Пройти мини-тест"
friendship_test_button = "❤️ Сертификат дружбы"
my_mini_tests_button = "🧩 Мои тесты"
random_mini_test_button = "🎲 Случайный тест"
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

test_share_text = "<a href='https://max.ru/{bot_username}?start={test_id}'>Нажми, чтобы пройти тест «{title}»</a>"

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
