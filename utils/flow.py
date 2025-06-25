from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from utils.calendar import get_calendar_list, create_event_in_calendar


class EventCreationFlow:
    @staticmethod
    async def start(update: Update, context: ContextTypes.DEFAULT_TYPE, event: dict):
        """
            Инициирует процесс добавления события — показывает список календарей.
        """
        calendars = get_calendar_list()
        context.user_data['event'] = event  # Сохраняем event в словарь user_data, чтобы потом в
        # другом хендлере (по нажатию кнопки) мы могли его достать
        context.user_data['calendar_map'] = {} #сохраняем ID-шки календарей в коротком формате,
        # чтобы не выбрасовало ошибок из-за длины сообщения

        # buttons = [
        #     [InlineKeyboardButton(cal['summary'], callback_data=f"calendar_{cal['id']}")]
        #     for cal in calendars
        # ]


        buttons = []
        for idx, cal in enumerate(calendars): #enumerate() даёт нам пары (0, calendar1), (1, calendar2) и т.д.
            short_id = str(idx)
            context.user_data['calendar_map'][short_id] = cal['id']
            buttons.append([InlineKeyboardButton(cal['summary'], callback_data=f"calendar_{short_id}")]) # опиание выбранного календаря и сам календарь

        await update.message.reply_text(
            "В какой календарь добавить задачу?",
            reply_markup=InlineKeyboardMarkup(buttons)
        )

    @staticmethod
    async def handle_calendar_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
            Обрабатывает нажатие на кнопку календаря.
        """
        query = update.callback_query  # запрос от клиента, нажатая кнопка (название календаря)
        await query.answer()  # показываем тг что запрос принят

        if not query.data.startswith('calendar_'):  # проверяем что эта кнопка наша, не для другого модуля
            return

        short_id = query.data[len('calendar_'):]
        calendar_map = context.user_data.get('calendar_map', {})
        calendar_id = calendar_map.get(short_id)

        if not calendar_id:
            await query.edit_message_text('Не удалось найти календарь')
            return

        event = context.user_data.get('event')
        if not event:
            await query.edit_message_text('Событие не найдено')
            return

        try:
            link = create_event_in_calendar(calendar_id, event)
            await query.edit_message_text(
                f"✅ Событие добавлено в календарь:\n{link}"
            )
        except Exception as e:
            await query.edit_message_text(
                "❌ Не удалось добавить событие."
            )
