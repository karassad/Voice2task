from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from services.calendar_service import CalendarService
from handlers.start_handler import send_main_menu



class EventCreationFlow:

    def __init__(self, calendar_service: CalendarService):
        self.calendar_service = calendar_service

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE, event: dict):
        """
            Запускает выбор календаря пользователю.
        """
        calendars = self.calendar_service.list_calendars()

        context.user_data['event'] = event  # Сохраняем event в словарь user_data, чтобы потом в
        # другом хендлере (по нажатию кнопки) мы могли его достать
        context.user_data['calendar_map'] = {} #сохраняем ID-шки календарей в коротком формате,
        # чтобы не выбрасовало ошибок из-за длины сообщения

        buttons = []
        for idx, cal in enumerate(calendars): #enumerate() даёт нам пары (0, calendar1), (1, calendar2) и т.д.
            short_id = str(idx)
            context.user_data['calendar_map'][short_id] = {
                'id': cal['id'],
                'summary': cal['summary']
            }
            buttons.append([InlineKeyboardButton(cal['summary'], callback_data=f"calendar_{short_id}")]) # опиание выбранного календаря и сам календарь

        if update.callback_query.message:
            await update.callback_query.message.reply_text(
                "В какой календарь добавить задачу?",
                reply_markup=InlineKeyboardMarkup(buttons)
            )
        else:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="В какой календарь добавить задачу?",
                reply_markup=InlineKeyboardMarkup(buttons)
            )

    async def handle_calendar_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
            Обрабатывает нажатие на кнопку календаря.
        """
        query = update.callback_query  # запрос от клиента, нажатая кнопка (название календаря)
        await query.answer()  # показываем тг что запрос принят

        if not query.data.startswith('calendar_'):  # проверяем что эта кнопка наша, не для другого модуля
            return

        short_id = query.data[len('calendar_'):]
        calendar_map = context.user_data.get('calendar_map', {})

        calendar_info = calendar_map.get(short_id)
        if not calendar_info:
            await query.edit_message_text('Не удалось найти календарь')
            return
        calendar_id = calendar_info['id']
        calendar_name = calendar_info['summary']

        event = context.user_data.get('event')
        if not event:
            from services.user_storage import UserStorage
            storage = UserStorage()
            storage.set_calendar(update.effective_user.id, calendar_id)
            await query.edit_message_text(
                f"✅ Основной календарь выбран: <b>{calendar_name}</b>\nТеперь вы можете отправлять задачи!",
                parse_mode="HTML"
            )
            await send_main_menu(update, context)

            return

        try:
            link = self.calendar_service.create_event(calendar_id, event)
            await query.edit_message_text(
                f"✅ Событие добавлено в календарь:\n{link}"
            )
        except Exception as e:
            await query.edit_message_text(
                "❌ Не удалось добавить событие."
            )
