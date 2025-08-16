from graphviz import Digraph

dot = Digraph(comment='Start Command Flow')

# Основной старт
dot.node('A', '/start (Telegram)')
dot.node('B', 'start_command\n(start_handler.py)')
dot.edge('A', 'B')

# Отправка приветствия
dot.node('C', 'send_new_message\n(message_send_logic.py)')
dot.edge('B', 'C')

# Авторизация
dot.node('D', 'OauthHandler().user_auth_process\n(oauth_handler.py)')
dot.edge('B', 'D')

dot.node('D1', 'get_user_token\n(user_storage.py)')
dot.node('D2', 'create_auth_url_if_needed\n(OAuth Flow)')
dot.edge('D', 'D1')
dot.edge('D', 'D2')

# Проверка календаря
dot.node('E', 'MainCalendarSetup()\n(main_calendar_setup.py)')
dot.node('E1', 'check_is_main_calendar_set')
dot.node('E2', 'start_calendar_selection_flow')
dot.edge('B', 'E')
dot.edge('E', 'E1')
dot.edge('E', 'E2')

# Главное меню
dot.node('F', 'send_main_menu\n(main_menu.py)')
dot.edge('B', 'F')

# Сохрани в файл
dot.render('start_command_flow', format='png', view=True)
