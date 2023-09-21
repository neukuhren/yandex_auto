"""Основной модуль - парсер.

Открывает в браузере страницу.
Авторизуется.
"""
import logging # Импортируем библиотеку для безопасного хранения логов
import inspect  # Для имени функции

from time import time

# # - Подключение модулей -
from config import DICT_WORK_MODES

from read_combined import read_combined_main
from check_accounts import check_accounts_main, change_password_for_ok_accs_main,\
    delete_unvalid_accounts_from_xlsx, set_password_app_main
from read_links import read_links_main
from send_messages import send_messages_main



logger = logging.getLogger(__name__)


# PARAM_DICT = read_parameters_from_txt_file_and_add_to_dict()
# """Словарь с параметрами из файла config.txt"""


def main(*selected_work_mode :int) -> None:
    """Основная функция работы приложения auth_yandex"""
    logger.debug(f'Запуск функции {inspect.currentframe().f_code.co_name}')
    try:
        print(f'Выберите режим работы:')
        for key, mode in DICT_WORK_MODES.items():
            print(f'{key} - {mode}')
        selected_work_mode = int(input(f'Введите цифру: '))
        logger.info(f'Выбран режим {selected_work_mode} - {DICT_WORK_MODES[selected_work_mode]}')
        if selected_work_mode == 1:
            read_combined_main()
        elif selected_work_mode == 2:
            check_accounts_main()
        elif selected_work_mode == 3:
            read_links_main()
        elif selected_work_mode == 4:
            send_messages_main()
        elif selected_work_mode == 5:
            change_password_for_ok_accs_main()
        elif selected_work_mode == 6:
            delete_unvalid_accounts_from_xlsx()
        elif selected_work_mode == 7:
            set_password_app_main()
        elif selected_work_mode not in DICT_WORK_MODES.keys():
            logger.debug(f'Выбранного режима "{selected_work_mode}" нет в списке {DICT_WORK_MODES}')
            print(f'Ошибка! Выбранного режима "{selected_work_mode}" не существует.'\
                f'Требуется перезагрузить программу.')
            
    except:
        logger.critical('КРИТИЧЕСКАЯ ОШИБКА: при выполнении главной функции. Требуется перезапуск программы.')



if __name__ == '__main__':
    start_time = time()
    # Здесь задана глобальная конфигурация для всех логгеров
    logging.basicConfig(
        handlers=[logging.StreamHandler()],
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        # filename='main.log',
        # filemode='w'
        # w — содержимое файла перезаписывается при каждом запуске программы;
        # x — создать файл и записывать логи в него; если файл с таким именем уже существует — возникнет ошибка;
        # a — дописывать новые логи в конец указанного файла.
    )
    
    main()

    print('\n\n')
    print('Время работы программы составило: ')
    print("--- %s seconds ---" % round((time() - start_time), 0))
    print('[!] Программа выполнена.')
