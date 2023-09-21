"""Основной модуль - парсер.

Открывает в браузере страницу.
Авторизуется.
"""
import logging # Импортируем библиотеку для безопасного хранения логов
import inspect  # Для имени функции
import pickle  # для сохранения куки - реализует  алгоритм сериализации и десериализации объектов Python
import re
import shutil
import urllib  # понадобится для сохранения изображения

from fake_useragent import UserAgent
import requests
# from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
# from selenium.webdriver.common.action_chains import ActionChains  # Цепочка событий
from selenium.webdriver.common.keys import Keys

from time import sleep
from time import time

from random import randint

# - Подключение модулей -
from config import  USER_AGENT_MY_GOOGLE_CHROME,\
    PARAMETER_ANSWER_A_SECRET_QUESTION, PATH_TO_FILE_DRIVER_CHROME,\
    LIST_WITH_COLUMNS_COMBINED, LIST_WITH_STATUS_ACC, URL_BEST_PROXIES, USED_PROXIES
    # HEADLESS, PARAMETER_CHANGE_PASSWORD,

from utils import write_in_end_row_file_txt, generate_random_password,\
    decrypt_captcha_deform_text, read_txt_file_and_lines_to_list,\
    open_xlsx_file_and_return_active_sheet, read_parameters_from_txt_file_and_add_to_dict
# from utils import write_to_excel

# from get_proxies import rotate_proxy


# Установлены настройки логгера для текущего файла
# В переменной __name__ хранится имя пакета;
# Это же имя будет присвоено логгеру.
# Это имя будет передаваться в логи, в аргумент %(name)
logger = logging.getLogger(__name__)

PARAM_DICT = read_parameters_from_txt_file_and_add_to_dict()
"""Словарь с параметрами из файла config.txt"""

URL_YA = 'https://ya.ru'
URL_YA_AUTH = 'https://passport.yandex.ru/auth/'

dict_with_data = {}
"""Cловарь для хранения данных об аккаунте (строчке таблицы)"""

global PROXIES_LIST
PROXIES_LIST = []


def get_proxies()  -> list:
    logger.debug(f'Запуск функции {inspect.currentframe().f_code.co_name}')
    response = requests.get(URL_BEST_PROXIES)
    proxies = response.text.strip().replace('\r', '').split('\n')
    return proxies


def rotate_proxy():
    logger.debug(f'Запуск функции {inspect.currentframe().f_code.co_name}')
    if len(PROXIES_LIST) == 0:
        proxies = get_proxies()
        logger.info(f'Получены прокси: \n{proxies}')
        sleep(0.5)
        PROXIES_LIST.extend(proxies)
        proxy = PROXIES_LIST.pop(0)
    else:
        proxy = PROXIES_LIST.pop(0)
    logger.info(f'Используется прокси: {proxy}')
    return proxy

def init_driver() -> webdriver:
    """Создание браузера (драйвера).
    
    - Создание экземпляра UserAgent (с помощью библиотеки fake_user_agent);
    - Добавление аргументов в экземпляр Options для браузера (драйвера);
    - Создание браузера (экземпляра webdriver) с нужными опциями.
    """
    logger.debug(f'Запуск функции {inspect.currentframe().f_code.co_name} - инициализация браузера.')
    # Создание экземпляра UserAgent
    ua = UserAgent()  # (browsers=['chrome',])
    fake_user_agent = ua.random # (с помощью библиотеки fake_user_agent)
    # Изменение случайного юзер агента на свой chrome mac os (для теста)
    # fake_user_agent = USER_AGENT_MY_GOOGLE_CHROME
    logger.debug(f'Создан user agent: {fake_user_agent}')
    # Опции для браузера (драйвера)
    options = Options()
    options.add_argument(f'user-agent={fake_user_agent}')
    logger.debug('в options добавлен fake_user_agent')

    # Включение режима инкогнито (для chrome)
    # options.add_argument("--incognito")

    # Отключение режима Webdriver
    options.add_argument(f'--disable-blink-features=AutomationControlled'  )
    logger.debug('в options Отключен режима Webdriver')
    # Скрытый режим headless mode
    if PARAM_DICT["HEADLESS"] =='True':
        options.add_argument("--headless")
        logger.debug('в options включен скрытый режим браузера')

    # путь к chromedriver.exe (можно задать через service)
    # s = Service(PATH_TO_FILE_DRIVER_CHROME)
    if USED_PROXIES:
        proxy = rotate_proxy()
        options.add_argument('--proxy-server=%s' % proxy)

        # prox = Proxy()
        # prox.http_proxy = proxy
        # prox.socks_proxy = proxy
        # prox.ssl_proxy = proxy

        # capabilities = webdriver.DesiredCapabilities.CHROME.copy()
        # prox.to_capabilities(capabilities)

    # инициализируем драйвер с нужными опциями
    driver = webdriver.Chrome(
        options=options,
        # desired_capabilities=capabilities,
        # executable_path=PATH_TO_FILE_DRIVER_CHROME,
        # service=s,
        )
    driver.set_page_load_timeout(60)
    return driver


def get_web_page_in_browser(url: str) -> None:
    """Открывает переданный url в браузере.
    
    Args: url (str) - адрес страницы, которую нужно открыть
    Return: None
    """
    logger.debug(f'Запуск функции {inspect.currentframe().f_code.co_name}')
    try:
        driver.get(url=url)  # Открытие страницы
        logger.debug(f'В браузере открыта страница {url}')
    except Exception as exc:  # Исключения
        print(exc)
    finally:  # Выполняется всегда
        pass


def find_and_click_captcha_iam_not_robot() -> None:
    """Проверяет есть ли каптча я не робот и кликает на нее.
    """
    logger.debug(f'Запуск функции {inspect.currentframe().f_code.co_name}')
    try:
        el_captcha = driver.find_element(By.CLASS_NAME, "CheckboxCaptcha-Anchor")
        if el_captcha:
            logger.debug(f'На странице была найдена каптча. Кликаю')
            try:
                el_captcha.click()
            except:
                logger.error('Ошибка при клике на каптчу')
    except:
        logger.debug(f'Каптчи 1 не было, либо она не была найдена.')
    # try:
    #     el_captcha = driver.find_element(By.CLASS_NAME, "CheckboxCaptcha-Checkbox")
    #     if el_captcha:
    #         logger.debug(f'На странице была найдена каптча. Кликаю')
    #         try:
    #             el_captcha.click()
    #         except:
    #             logger.error('Ошибка при клике на каптчу')
    # except:
    #     logger.debug(f'Каптчи 2 не было, либо она не была найдена.')
        

def find_and_click_btn_close_window() -> None:
    """Проверяет есть ли вслывающее окно и кликает на кнопку его закрытия.
    """
    logger.debug(f'Запуск функции {inspect.currentframe().f_code.co_name}')
    try:
        el_btn_close_window = driver.find_element(By.CLASS_NAME, "modal__close")
        logger.debug(f'На странице было найдено всплывающее окна. Закрываю его.')
        try:
            el_btn_close_window.click()
        except:
            logger.error('Ошибка при клике на кнопку закрытия окна')
    except:
        # кнопка закрытия всплывающего окна не было
        pass


def find_add_favorite_and_click_btn_close_window() -> None:
    """Проверяет есть ли вслывающее окно "Добавить в избранное" и кликает на кнопку его закрытия.
    """
    logger.debug(f'Запуск функции {inspect.currentframe().f_code.co_name}')
    try:
        el_btn_close_window = driver.find_element(By.CLASS_NAME, 'dist-favourites__close')
        logger.debug(f'Найдено всплывающее окно добавить в избранное. Закрываю его.')
        try:
            el_btn_close_window.click()
        except:
            logger.error('Ошибка при клике на кнопку закрытия окна')
    except:
        # кнопка закрытия всплывающего окна не было
        pass
    

def find_and_click_btn_signin() -> None:
    """Проверяет есть ли кнопка Войти и кликает на неё.
    """
    logger.debug(f'Запуск функции {inspect.currentframe().f_code.co_name}')
    try:
        el_btn_signin = driver.find_element(By.CSS_SELECTOR, "body > main > div.headline > div > a")
        logger.debug(f'На странице была найдена кнопка "Войти". Кликаю')
        try:
            el_btn_signin.click()
        except:
            logger.error('Ошибка при клике на кнопку "Войти"')
    except:
        logger.debug(f'Кнопка "Войти" не найдена')


def find_and_click_btn_email() -> None:
    """Проверяет есть ли кнопка Почта и кликает на неё.
    """
    logger.debug(f'Запуск функции {inspect.currentframe().f_code.co_name}')
    try:
        el_btn_email = driver.find_element(By.CSS_SELECTOR, "#root > div > div.passp-page > div.passp-flex-wrapper > div > div > div.passp-auth-content > div:nth-child(3) > div > div > div > div > form > div > div.layout_content > div.AuthLoginInputToggle-wrapper.AuthLoginInputToggle-wrapper_theme_contrast > div:nth-child(1) > button")
        logger.debug(f'На странице была найдена кнопка "Почта". Кликаю')
        try:
            el_btn_email.click()
        except:
            logger.error('Ошибка при клике на кнопку "Почта"')
    except:
        logger.debug(f'Кнопка "Почта" не найдена')


def find_field_and_insert_email_text(login_email: str) -> None:
    """Проверяет есть ли поле email и вставляет текстовое значение email.
    """
    logger.debug(f'Запуск функции {inspect.currentframe().f_code.co_name}')
    try:
        el_field_login_email = driver.find_element(By.CSS_SELECTOR, "#passp-field-login")
        logger.debug(f'На странице было поле login-email')
        try:
            el_field_login_email.send_keys(login_email, Keys.ENTER)
        except:
            logger.error('Ошибка при заполнении поле login-email')
    except:
        logger.debug(f'Поле login-email не найдено')


def find_field_and_insert_passwd_text(passwd: str) -> None:
    """Проверяет есть ли поле passwd и вставляет текстовое значение пароля.
    """
    logger.debug(f'Запуск функции {inspect.currentframe().f_code.co_name}')
    try:
        el_field_login_passwd = driver.find_element(By.CSS_SELECTOR, "#passp-field-passwd")
        logger.debug(f'На странице было поле passwd')
        try:
            el_field_login_passwd.send_keys(passwd, Keys.ENTER)
        except:
            logger.error('Ошибка при заполнении поле passwd')
    except:
        logger.debug(f'Поле passwd не найдено')


def find_field_invalid_password() -> None:
    """Проверяет есть ли поле passwd и вставляет текстовое значение пароля.
    """
    logger.debug(f'Запуск функции {inspect.currentframe().f_code.co_name}')
    try:
        el_field_invalid_passwd = driver.find_element(By.ID, 'field:input-passwd:hint')
        logger.info(f'На странице было поле неверный пароль')
        dict_with_data['Status'] = 'invalid'
    except:
        logger.debug(f'Поле неверный пароль не найдено')


def check_security_question_and_insert_answer_text(security_answer: str) -> None:
    """Проверяет есть ли поле security_question и вставляет текстовое значение ответа.
    """
    logger.debug(f'Запуск функции {inspect.currentframe().f_code.co_name}')
    try:
        el_security_question = driver.find_element(By.ID, "passp-field-question")
        if el_security_question:
            logger.info(f'Требуется вход по секретному вопросу. Обрабатывается...')
            # symbol = input('Войти по секретному вопросу? (y, n): ')
            # if symbol == 'y':
            if PARAMETER_ANSWER_A_SECRET_QUESTION:
                try:
                    el_security_question.send_keys(security_answer, Keys.ENTER)
                    if PARAM_DICT['NEED_PAUSE_BEFORE_ANSWER_QUESTION'] == True:
                        pause = input('Пауза. Нажмите любую клавишу для продолжения')
                    sleep(randint(1, 3))  # задержка, перед дальнейшей проверкой аватара
                except:
                    logger.error('Ошибка при заполнении поле passwd')
            else:
                logger.debug('Вход по секретному вопросу производиться не будет.')
    except:
        logger.debug(f'Поле security_question не найдено')


def check_entry_only_sms() -> bool:
    """Проверяет если вход возможен только по смс возвращает true.
    """
    logger.debug(f'Запуск функции {inspect.currentframe().f_code.co_name}')
    try:
        el_entry_sms = driver.find_element(By.ID, "passp-field-phoneCode")
        if el_entry_sms:
            logger.info(f'Требуется вход по смс.')
            return True
    except:
        logger.debug(f'Входа по смс не было, либо оно не была найдена.')


def check_need_recovery() -> bool:
    """Проверяет, требует ли сайт восстановить доступ к аккаунту.
    """
    logger.debug(f'Запуск функции {inspect.currentframe().f_code.co_name}')
    try:
        el_btn_recovery = driver.find_element(By.CLASS_NAME, "Button2-Text")
        if el_btn_recovery.text == 'Восстановить доступ':
            logger.debug(f'На странице необходимо восстановить доступ к аккаунту.')
            return True
    except:
        logger.debug(f'Восстановить доступ нет на странице, либо он не был найден.')


# def check_invalid_account_user_data() -> bool:
#     """Проверяет, есть ли ошибка в введенных данных авторизации.
#     """
#     logger.info(f'Запуск функции {inspect.currentframe().f_code.co_name}')
#     for _ in range(0, 600):
#         print('-', end='')
#         sleep(1)
#     try:
#         el_btn_recovery = driver.find_element(By.CLASS_NAME, "Button2-Text")
#         if el_btn_recovery.text == 'Восстановить доступ':
#             logger.info(f'На странице необходимо восстановить доступ к аккаунту.')
#         return True
#     except:
#         logger.debug(f'Восстановить доступ нет на странице, либо он не был найден.')


def check_avatar_on_page_and_click() -> object:
    """Проверяет если есть аватар пользователя, то возвращает элемент автара на странице.
    Если аватар не найден, то возвращает None
    """
    logger.debug(f'Запуск функции {inspect.currentframe().f_code.co_name}')
    try:
        el_avatar = driver.find_element(By.CLASS_NAME, "avatar__image-wrapper")
        logger.debug(f'На странице был найден аватар.')
        return el_avatar
    except:
        logger.debug(f'Аватара нет на странице, либо он не был найден.')


def check_avatar2_on_page_and_click() -> object:
    """Проверяет если есть аватар пользователя, то возвращает элемент автара на странице.
    Если аватар не найден, то возвращает None
    """
    logger.debug(f'Запуск функции {inspect.currentframe().f_code.co_name}')
    try:
        el_avatar = driver.find_element(By.CSS_SELECTOR, "#__next > div > header > div.Header_user__1Whuh > div > button > div > div.UserID-Avatar")
        logger.debug(f'На странице был найден аватар.')
        return el_avatar
    except:
        logger.debug(f'Аватара нет на странице, либо он не был найден.')


def check_account_for_signin() -> object:
    """Проверяет если есть ли элемент выбрать аккаунт для входа, кликает на него.
    """
    logger.debug(f'Запуск функции {inspect.currentframe().f_code.co_name}')
    try:
        el_check_account = driver.find_element(By.CLASS_NAME, "AuthAccountListItem-block")
        logger.debug(f'На странице был найден аккаунт для входа.')
        try:
            el_check_account.click()
        except:
            logger.error('Ошибка при клике на аккаунт для входа"')
    except:
        logger.debug(f'Аккаунта для входа нет на странице, либо он не был найден.')


def find_field_and_text(field_id: str, text_for_field: str, press_key_enter=False) -> None:
    """Проверяет есть ли поле c переданным id и вставляет переданное текстовое значение.
    """
    logger.debug(f'Запуск функции {inspect.currentframe().f_code.co_name}')
    try:
        el_field = driver.find_element(By.ID, field_id)
        logger.debug(f'Поле {field_id} найдено.')
        try:
            if press_key_enter:
                el_field.send_keys(text_for_field, Keys.ENTER)
            else:
                el_field.send_keys(text_for_field)
        except:
            logger.error(f'Ошибка при заполнении поля {field_id}')
    except:
        logger.error(f'Поле {field_id} не найдено.')


def find_captcha_and_save_img(el_id: str):
    """
    """
    logger.debug(f'Запуск функции {inspect.currentframe().f_code.co_name}')
    try:
        el_сaptcha = driver.find_element(By.ID, el_id)
        if el_сaptcha:
            logger.info(f'Элемент каптча {el_id} найдена через id.')
        url_for_image_captcha = el_сaptcha.get_attribute('src')
        print(f'url_for_image_captcha -- {url_for_image_captcha}')
        image_captcha = requests.get(url_for_image_captcha)
        sleep(2)
        with open('image_captcha.jpg', 'wb') as f:
            f.write(image_captcha.content)
        # el_captcha = driver.find_element(By.XPATH, '//*[@id="captcha-image"]')
        # if image_captcha:
        #     logger.info(f'Изображение каптчи найдено через xpath.')
        #     print(image_captcha)
        #     urllib.urlretrieve(image_captcha, "image_captcha.png")
        return image_captcha.content
    except:
        logger.error(f'Элемент каптча {el_id} не найдена.')


def navigate_menu_and_change_password(el_avatar, dict_with_data) -> str:
    """Переходит через аватар или по ссылке по меню для изменения пароля.
    """
    try:
        el_avatar.click()
    except:
        logger.error('Ошибка при клике на аватар')
    
    get_web_page_in_browser(url='https://id.yandex.ru/security/')
    sleep(randint(1, 10)/10+0.5)  # от 0.6 до 1.4 секунды
    
    get_web_page_in_browser(url='https://id.yandex.ru/profile/password?backpath=https%3A%2F%2Fid.yandex.ru%2Fsecurity')
    sleep(randint(1, 10)/10+0.5)  # от 0.6 до 1.4 секунды
    find_field_and_text(field_id='currentPassword', text_for_field=dict_with_data['Password'])
    sleep(randint(1, 10)/10+0.5)  # от 0.6 до 1.4 секунды
    
    new_psw = generate_random_password(number_symbols=12) # генерируем новый пароль
    print(f'Был сгенерирован пароль {new_psw}')
    find_field_and_text(field_id='newPassword', text_for_field=new_psw)
    sleep(randint(1, 10)/10+0.5)  # от 0.6 до 1.4 секунды
    find_field_and_text(field_id='repeatPassword', text_for_field=new_psw)

    try:
        image_captcha_content = find_captcha_and_save_img(el_id='captcha-image')
    except:
        logger.error(f'Каптча не найдена на странице')
    if image_captcha_content:
            captcha_code = decrypt_captcha_deform_text(PARAM_DICT['API_KEY_FOR_RUCAPTCHA'])
            if captcha_code:
                logger.info(f'Каптча расшифрована. Кодовая фраза: {captcha_code}')
                # Заполнить поле каптча
                find_field_and_text(field_id='captcha', text_for_field=captcha_code, press_key_enter=True)
                sleep(randint(4, 6))
    # Если каптча во второй раз не была найдена, считаем результат успешным
    try:
        image_captcha_content = find_captcha_and_save_img(el_id='captcha-image')
        # возвращаем новый пароль
        return new_psw
    except:
        # Остается старый пароль, ничего не возвращаем
        return  None


def check_account():
    """Начинает проверку акаунта. Изменяет словарь с данными аккаунта."""
    logger.debug(f'Запуск функции {inspect.currentframe().f_code.co_name}')
    # logger.debug(f'\nТекущее значение dict_with_data:\n{dict_with_data}')
    global driver
    if len(dict_with_data) != 0:
        try:
            logger.debug('Запускается инициализация драйвера')
            driver = init_driver()
        except:
            logger.error('Ошибка при инициализации экземпляра driver')

        get_web_page_in_browser(url=URL_YA_AUTH)
        sleep(2)
        find_and_click_captcha_iam_not_robot()
        sleep(0.5)
        find_and_click_btn_close_window()
        sleep(0.5)
        find_add_favorite_and_click_btn_close_window()
        sleep(0.5)
        if PARAM_DICT['NEED_PAUSE_BEFORE_PRESS_SIGNIN']  == 'True':  # Строка, так как из текстового конфига
            pause = input('нажмите любую клавишу для продолжения')
        find_and_click_btn_signin()
        sleep(randint(1, 3))
        find_and_click_btn_email()
        sleep(randint(1, 3))
        find_field_and_insert_email_text(login_email=dict_with_data['Login'])
        sleep(1)
        find_field_and_insert_passwd_text(passwd=dict_with_data['Password'])
        sleep(randint(1, 3))
        find_field_invalid_password()
        check_security_question_and_insert_answer_text(security_answer=dict_with_data['Answer'])
        sleep(randint(1, 3))
        cur_avatar_obj = None

        # Если вход возможен только по коду из смс
        if check_entry_only_sms():
            dict_with_data['Status'] = 'sms'
        
        elif check_need_recovery():
            dict_with_data['Status'] = 'recovery'

        else:
            # print('Проверяю аватар')
            el_avatar = check_avatar_on_page_and_click()  # аватар 1 вида
            el_avatar2 = check_avatar2_on_page_and_click()  # аватар 2 вида
            if el_avatar or el_avatar2:
                logger.info(f'Вход выполнен успешно')
                dict_with_data['Status'] = 'ok'
                if el_avatar: 
                    cur_avatar_obj = el_avatar
                elif el_avatar2:
                    cur_avatar_obj = el_avatar2
                if PARAM_DICT['PARAMETER_CHANGE_PASSWORD_USE_PSW'] == 'True':
                    new_psw = navigate_menu_and_change_password(el_avatar=cur_avatar_obj, dict_with_data=dict_with_data)
                    if new_psw:
                        dict_with_data['Password'] = new_psw

                # получаем cookies
                current_cookies = driver.get_cookies()
                # print(f'\n\n{current_cookies}\n\n')
                # сохраняем cookies в словарь
                dict_with_data['Cookies'] = current_cookies

                #получаем и сохраняем куки с помощью pickle
                pickle.dump(driver.get_cookies(), open(f"cookies/{dict_with_data['Login']}.pkl", "wb"))
                

    # print(user_data)
    # forward_to_next_account = input('Перейти к следующему аккаунту? (y/n): ')
    # if forward_to_next_account == 'y':
        # удаляем cookies
        driver.delete_all_cookies()
        # sleep(0.5)
        if PARAM_DICT['NEED_PAUSE_BEFORE_CLOSED_BROWSER']  == 'True':  # Строка, так как из текстового конфига
            pause = input('нажмите любую клавишу для продолжения')
        driver.close()  # Закрытие окна браузера
        driver.quit()  # Выход
    # print(f'Обновленные данные {dict_with_data}')


def check_accounts_main():
    """Основная функция работы приложения check_accounts"""
    # # ------------------------- Работа с txt файлом -----------------------------
    # try:
    #     # Читаем файл с данными юзеров в список [Login, Password, Answer]
    #     list_user_data = read_txt_file_and_lines_to_list('combined.txt')
    # except:
    #     logger.critical(f'КРИТИЧЕСКАЯ ОШИБКА: при чтении txt файла с аккаунтами.')

    # ------------------------- Работа с xlsx файлом -----------------------------
    # try:
    #     # Читаем файл с данными юзеров в список [Login, Password, Answer]
    #     list_user_data = read_xlsx_file_and_lines_to_list(file_name='combined.xlsx')
    # except:
    #     logger.critical(f'КРИТИЧЕСКАЯ ОШИБКА: при чтении xlsx файла с аккаунтами.')

    
    # Открываем xlsx книгу и активный лист
    workbook, worksheet = open_xlsx_file_and_return_active_sheet(file_name='combined.xlsx')

    
    if workbook and worksheet:  # Если xlsx книга и активный лист получены
        current_row = 2  # С какой строки читать xlsx файл
        # list_with_data = []  # список со словарями все аккаунты

        # Пройтись со второй строки до первой пустой
        try: 
            cur_cell = worksheet.cell(row=current_row, column=1)
            # while cur_cell.value is not None:
            while True:
                dict_with_data.clear()  # словарь для хранения данных об аккаунте (строчке таблицы)
                for index_, cur_col_name in enumerate(LIST_WITH_COLUMNS_COMBINED):
                    cur_cell = worksheet.cell(row=current_row, column=index_+1)
                    # Записать значение ячейки в словарь
                    dict_with_data[cur_col_name] = cur_cell.value
                print(f'Из xlsx файла получены данные: {dict_with_data["Login"]}')
                try: 
                    if len(dict_with_data) != 0:  # если словарь не пустой (был заполнен данными из файла)
                        # если статус аккаунта соответствует проверяемому (из файла config.txt)
                        if (dict_with_data['Status'] == PARAM_DICT['CHECKED_STATUS']) or (dict_with_data['Status'] == None) or (dict_with_data['Status'] not in LIST_WITH_STATUS_ACC):
                            # Начинаем проверку аккаунта, получаем после проверки обновленные данные
                            check_account()
                            # Записать данные (новый пароль, статус, куки) в xlsx файл
                            # logger.debug(f'Получен словарь {dict_with_data}')
                            cur_cell = worksheet.cell(row=current_row, column=2, value=dict_with_data['Password'])
                            print(f'В ячейку записан пароль {cur_cell.value}')
                            cur_cell = worksheet.cell(row=current_row, column=4, value=dict_with_data['Status'])
                            print(f'В ячейку записан статус {dict_with_data["Status"]}')
                            logger.info(f'Статус проверяемого аккаунта - {cur_cell.value}')
                        
                            if dict_with_data['Cookies']:
                                # print(dict_with_data['Cookies'])
                                cur_cell = worksheet.cell(row=current_row, column=5, value=str(dict_with_data['Cookies']))
                            
                            print(f'Попытка сохранить книгу')
                            workbook.save(filename='combined.xlsx')  # сохранить xlsx файл
                            if current_row % 10 == 0:
                                shutil.copyfile('combined.xlsx', f'backups/backup_combined.xlsx')
                                logger.info(f'Создан backup файла combined.xlsx')
                            logger.debug(f'файл xlsx сохранен')
                        # если статус аккаунта соответствует проверяемому (из файла config.txt)
                        if (dict_with_data['Status'] == 'ok') and  (PARAM_DICT['CHECKED_STATUS'] != 'ok'):
                            logger.info('Аккаунт со статусом "ok". Переход к следующему.')
                except:
                    logger.error(f'При проверке {dict_with_data["Login"]} возникла непредвиденная ошибка')
                finally:
                    current_row += 1
                    cur_cell = worksheet.cell(row=current_row, column=1)  # Переход на следующую строку
                    # pause = input('Нажмите любую клавишу для продолжения работы: ')
                    if cur_cell.value is None:
                        logger.info(f'Обнаружена пустая строка - {current_row}.')
                        need_retry_check = False  # нужна ли повторная проверка
                        for r in range(2, current_row):
                            c = worksheet.cell(row=r, column=LIST_WITH_COLUMNS_COMBINED.index('Status')+1)
                            # если значение статуса не содержится в словаре со статусами исключая no status
                            if c.value not in LIST_WITH_STATUS_ACC[1: ]:
                                need_retry_check = True
                        if need_retry_check:
                            current_row = 2
                            logger.info(f'Начинаю повторную проверку со строки {current_row}.')
                            cur_cell = worksheet.cell(row=current_row, column=1)
                        else:
                            print('Проверены все аккаунты из списка.')
                            shutil.copyfile('combined.xlsx', f'backups/backup_combined.xlsx')
                            logger.info(f'Создан backup файла combined.xlsx')
                            break
            logger.info('Выход из цикла проверки')
        except:
            logger.critical('КРИТИЧЕСКАЯ ОШИБКА: при выполнении главной функции. Требуется перезапуск программы.')


def start_change_password():
    """Начинает изменение пароля для аккаунта, который хранится в глобальной переменной."""
    logger.debug(f'Запуск функции {inspect.currentframe().f_code.co_name}')
    # logger.debug(f'\nТекущее значение dict_with_data:\n{dict_with_data}')
    global driver
    if len(dict_with_data) != 0:
        try:
            logger.debug('Запускается инициализация драйвера')
            driver = init_driver()
        except:
            logger.error('Ошибка при инициализации экземпляра driver')

        get_web_page_in_browser(url='https://passport.yandex.ru/')
        sleep(randint(1, 3))
        find_and_click_captcha_iam_not_robot()
        sleep(randint(1, 3))
        find_and_click_btn_close_window()
        find_add_favorite_and_click_btn_close_window()
        sleep(randint(1, 3))
        if PARAM_DICT['NEED_PAUSE_BEFORE_PRESS_SIGNIN']  == 'True':  # Строка, так как из текстового конфига
            pause = input('нажмите любую клавишу для продолжения')
        
        # Авторизация по куки текущего пользователя
        if PARAM_DICT['PARAMETER_CHANGE_PASSWORD_USE_COOKIES'] == 'True':
            # загрузить куки текущего пользователя
            logger.debug(f'Работаем с аккаунтом {dict_with_data["Login"]}')
            try:
                cookies = pickle.load(open(f'cookies/{dict_with_data["Login"]}.pkl', "rb"))
            except:
                pass
            if cookies is None:
                logger.error(f'При попытке чтения куки для пользователя {dict_with_data["Login"]} не были найдены в папке.')
            for cookie in cookies:
                try:
                    driver.add_cookie(cookie)
                except Exception as exc:
                    logger.error(f'Не удалось загрузить куки: {cookie}')
                    print(exc)
            sleep(1)
            driver.refresh()
            sleep(1)
            check_account_for_signin()
            # Проверяем результат авторизации
            cur_avatar_obj = None
            el_avatar = check_avatar_on_page_and_click()  # аватар 1 вида
            el_avatar2 = check_avatar2_on_page_and_click()  # аватар 2 вида
            if el_avatar or el_avatar2:
                logger.info(f'Вход выполнен успешно')
                dict_with_data['Status'] = 'ok'
                if el_avatar: 
                    cur_avatar_obj = el_avatar
                elif el_avatar2:
                    cur_avatar_obj = el_avatar2
                # Изменяем пароль
                new_psw = navigate_menu_and_change_password(el_avatar=cur_avatar_obj, dict_with_data=dict_with_data)
                if new_psw:
                    dict_with_data['Password'] = new_psw

                # получаем cookies
                current_cookies = driver.get_cookies()
                # print(f'\n\n{current_cookies}\n\n')
                # сохраняем cookies в словарь
                dict_with_data['Cookies'] = current_cookies

                #получаем и сохраняем куки с помощью pickle
                pickle.dump(driver.get_cookies(), open(f"cookies/{dict_with_data['Login']}.pkl", "wb"))

        else:
            logger.error(f'В файле config.txt установлено неверное значение параметра PARAMETER_CHANGE_PASSWORD_USE_COOKIES, установите True')
    else:
        logger.error(f'словарь dict_with_data с данными текущего аккаунта пуст')        
    # print(user_data)
    # forward_to_next_account = input('Перейти к следующему аккаунту? (y/n): ')
    # if forward_to_next_account == 'y':

    # удаляем cookies
    driver.delete_all_cookies()
    # sleep(0.5)
    if PARAM_DICT['NEED_PAUSE_BEFORE_CLOSED_BROWSER']  == 'True':  # Строка, так как из текстового конфига
        pause = input('нажмите любую клавишу для продолжения')
    driver.close()  # Закрытие окна браузера
    driver.quit()  # Выход
    # print(f'Обновленные данные {dict_with_data}')


def change_password_for_ok_accs_main():
    """Основная функция в режиме смена пароля для успешных аккаунтов.
    Построчно читает xlsx файл и вызывает для каждого валидного аккаунта функцию смены пароля."""
    # ------------------------- Работа с xlsx файлом -----------------------------
    # try:
    #     # Читаем файл с данными юзеров в список [Login, Password, Answer]
    #     list_user_data = read_xlsx_file_and_lines_to_list(file_name='combined.xlsx')
    # except:
    #     logger.critical(f'КРИТИЧЕСКАЯ ОШИБКА: при чтении xlsx файла с аккаунтами.')
    
    # Открываем xlsx книгу и активный лист
    workbook, worksheet = open_xlsx_file_and_return_active_sheet(file_name='combined.xlsx')

    if workbook and worksheet:  # Если xlsx книга и активный лист получены
        current_row = 2  # С какой строки читать xlsx файл
        # list_with_data = []  # список со словарями все аккаунты

        # Пройтись со второй строки до первой пустой
        try: 
            cur_cell = worksheet.cell(row=current_row, column=1)
            # while cur_cell.value is not None:
            while True:
                dict_with_data.clear()  # словарь для хранения данных об аккаунте (строчке таблицы)
                for index_, cur_col_name in enumerate(LIST_WITH_COLUMNS_COMBINED):
                    cur_cell = worksheet.cell(row=current_row, column=index_+1)
                    # Записать значение ячейки в словарь
                    dict_with_data[cur_col_name] = cur_cell.value
                print(f'Из xlsx файла получены данные: {dict_with_data["Login"]}')
                try: 
                    if len(dict_with_data) != 0:  # если словарь не пустой (был заполнен данными из файла)
                        # если статус аккаунта ok
                        if dict_with_data['Status'] == 'ok':
                            # Начинаем смену пароля, получаем после проверки обновленные данные
                            start_change_password()
                            # Записать данные (новый пароль, статус, куки) в xlsx файл
                            # logger.debug(f'Получен словарь {dict_with_data}')
                            cur_cell = worksheet.cell(row=current_row, column=2, value=dict_with_data['Password'])
                            print(f'В ячейку записан пароль {cur_cell.value}')
                            cur_cell = worksheet.cell(row=current_row, column=4, value=dict_with_data['Status'])
                            print(f'В ячейку записан статус {dict_with_data["Status"]}')
                            logger.info(f'Статус проверяемого аккаунта - {cur_cell.value}')
                        
                            if dict_with_data['Cookies']:
                                # print(dict_with_data['Cookies'])
                                cur_cell = worksheet.cell(row=current_row, column=5, value=str(dict_with_data['Cookies']))
                            
                            print(f'Попытка сохранить книгу')
                            workbook.save(filename='combined.xlsx')  # сохранить xlsx файл
                            if current_row % 10 == 0:
                                shutil.copyfile('combined.xlsx', f'backups/backup_combined.xlsx')
                                logger.info(f'Создан backup файла combined.xlsx')
                            logger.debug(f'файл xlsx сохранен')

                        else: # если статус аккаунта не ok
                            logger.info('Аккаунт не имеет статус "ok". Переход к следующему.')
                except:
                    logger.error(f'При проверке {dict_with_data["Login"]} возникла непредвиденная ошибка')
                finally:
                    current_row += 1
                    cur_cell = worksheet.cell(row=current_row, column=1)  # Переход на следующую строку
                    # pause = input('Нажмите любую клавишу для продолжения работы: ')
                    if cur_cell.value is None:
                        logger.info(f'Обнаружена пустая строка - {current_row}.')
                        need_retry_check = False  # нужна ли повторная проверка
                        # for r in range(2, current_row):
                        #     c = worksheet.cell(row=r, column=LIST_WITH_COLUMNS_COMBINED.index('Status')+1)
                        #     # если значение статуса не содержится в словаре со статусами исключая no status
                        #     if c.value not in LIST_WITH_STATUS_ACC[1: ]:
                        #         need_retry_check = True
                        if need_retry_check:
                            current_row = 2
                            logger.info(f'Начинаю повторную проверку со строки {current_row}.')
                            cur_cell = worksheet.cell(row=current_row, column=1)
                        else:
                            print('Проверены все аккаунты из списка.')
                            shutil.copyfile('combined.xlsx', f'backups/backup_combined.xlsx')
                            logger.info(f'Создан backup файла combined.xlsx')
                            break
            logger.info('Выход из цикла проверки')
        except:
            logger.critical('КРИТИЧЕСКАЯ ОШИБКА: при выполнении главной функции. Требуется перезапуск программы.')


def delete_unvalid_accounts_from_xlsx():
    """Основная функция работы приложения check_accounts"""
    # ------------------------- Работа с xlsx файлом -----------------------------
    # try:
    #     # Читаем файл с данными юзеров в список [Login, Password, Answer]
    #     list_user_data = read_xlsx_file_and_lines_to_list(file_name='combined.xlsx')
    # except:
    #     logger.critical(f'КРИТИЧЕСКАЯ ОШИБКА: при чтении xlsx файла с аккаунтами.')
    
    target_status_accs_for_deleted = input(f'Аккаунты с каким статусом удалить из файла combined.xlsx?\n'\
                                           f'{LIST_WITH_STATUS_ACC}\n'\
                                           f'Введите здесь: ')
    # Открываем xlsx книгу и активный лист
    workbook, worksheet = open_xlsx_file_and_return_active_sheet(file_name='combined.xlsx')
    
    if workbook and worksheet:  # Если xlsx книга и активный лист получены
        current_row = 2  # С какой строки читать xlsx файл
        # list_with_data = []  # список со словарями все аккаунты

        # Пройтись со второй строки до первой пустой
        try: 
            cur_cell = worksheet.cell(row=current_row, column=1)
            # while cur_cell.value is not None:
            while True:
                dict_with_data.clear()  # словарь для хранения данных об аккаунте (строчке таблицы)
                for index_, cur_col_name in enumerate(LIST_WITH_COLUMNS_COMBINED):
                    cur_cell = worksheet.cell(row=current_row, column=index_+1)
                    # Записать значение ячейки в словарь
                    dict_with_data[cur_col_name] = cur_cell.value
                logger.debug(f'Из xlsx файла получены данные: {dict_with_data["Login"]}')
                try: 
                    if len(dict_with_data) != 0:  # если словарь не пустой (был заполнен данными из файла)
                        # если статус аккаунта соответствует проверяемому (из файла config.txt)
                        if dict_with_data['Status'] == target_status_accs_for_deleted:
                            try:
                                # Удалить текущую строку из файла
                                worksheet.delete_rows(current_row, 1)  # индекс, кол-во
                                logger.info(f'Данные аккаунта {dict_with_data["Login"]} удалены')
                            except Exception as exc:
                                logger.error(f'При попытке удаления аккаунта {dict_with_data["Login"]} (строки - {current_row}) возникла ошибка {exc}')
                            logger.debug(f'Попытка сохранить книгу')
                            workbook.save(filename='combined.xlsx')  # сохранить xlsx файл
                            if current_row % 10 == 0:
                                shutil.copyfile('combined.xlsx', f'backups/backup_combined.xlsx')
                                logger.info(f'Создан backup файла combined.xlsx')
                            logger.debug(f'файл xlsx сохранен')
                        else:
                            # logger.debug(f'Аккаунт со статусом {dict_with_data["Status"]}. Переход к следующему.')
                            pass
                except:
                    logger.error(f'При проверке {dict_with_data["Login"]} возникла непредвиденная ошибка')
                finally:
                    current_row += 1
                    cur_cell = worksheet.cell(row=current_row, column=1)  # Переход на следующую строку
                    # pause = input('Нажмите любую клавишу для продолжения работы: ')
                    if cur_cell.value is None:
                        logger.info(f'Обнаружена пустая строка - {current_row}.')
                        need_retry_check = False  # нужна ли повторная проверка
                        for r in range(2, current_row):
                            c = worksheet.cell(row=r, column=LIST_WITH_COLUMNS_COMBINED.index('Status')+1)
                            # если значение статуса не содержится в словаре со статусами исключая no status
                            if c.value == target_status_accs_for_deleted:
                                need_retry_check = True
                        if need_retry_check:
                            current_row = 2
                            logger.info(f'Начинаю повторную проверку со строки {current_row}.')
                            cur_cell = worksheet.cell(row=current_row, column=1)
                        else:
                            print('Проверены все аккаунты из списка.')
                            shutil.copyfile('combined.xlsx', f'backups/backup_combined.xlsx')
                            logger.info(f'Создан backup файла combined.xlsx')
                            break
            logger.info('Выход из цикла проверки')
        except:
            logger.critical('КРИТИЧЕСКАЯ ОШИБКА: при выполнении главной функции. Требуется перезапуск программы.')


def start_set_password_app():
    """Функция установки пароля приложений, в качестве логина использует секретку.
    Сначала запускает такую же функцию изменения пароля, затем уходит в ответвление,
    выходит через break
    выполняет свои функции по установке пароля приложения"""
    logger.debug(f'Запуск функции {inspect.currentframe().f_code.co_name}')
    # logger.debug(f'\nТекущее значение dict_with_data:\n{dict_with_data}')
    global driver
    if len(dict_with_data) != 0:
        try:
            logger.debug('Запускается инициализация драйвера')
            driver = init_driver()
        except:
            logger.error('Ошибка при инициализации экземпляра driver')

        get_web_page_in_browser(url='https://passport.yandex.ru/')
        sleep(2)
        find_and_click_captcha_iam_not_robot()
        sleep(0.5)
        find_and_click_btn_close_window()
        sleep(0.5)
        find_add_favorite_and_click_btn_close_window()
        sleep(0.5)
        if PARAM_DICT['NEED_PAUSE_BEFORE_PRESS_SIGNIN']  == 'True':  # Строка, так как из текстового конфига
            pause = input('нажмите любую клавишу для продолжения')
        
        # Авторизация по куки текущего пользователя
        if PARAM_DICT['PARAMETER_CHANGE_PASSWORD_USE_COOKIES'] == 'True':
            # загрузить куки текущего пользователя
            logger.debug(f'Работаем с аккаунтом {dict_with_data["Login"]}')
            try:
                cookies = pickle.load(open(f'cookies/{dict_with_data["Login"]}.pkl', "rb"))
            except:
                pass
            if cookies is None:
                logger.error(f'При попытке чтения куки для пользователя {dict_with_data["Login"]} не были найдены в папке.')
            else:
                for cookie in cookies:
                    try:
                        driver.add_cookie(cookie)
                    except Exception as exc:
                        logger.error(f'Не удалось загрузить куки: {cookie}')
                        print(exc)
                sleep(1)
                driver.refresh()
                sleep(1)
                check_account_for_signin()
                # Проверяем результат авторизации
                el_avatar = check_avatar_on_page_and_click()  # аватар 1 вида
                el_avatar2 = check_avatar2_on_page_and_click()  # аватар 2 вида
                if el_avatar or el_avatar2:
                    logger.info(f'Вход выполнен успешно')
                    dict_with_data['Status'] = 'ok'
                    # get_web_page_in_browser(url='https://id.yandex.ru/security')  # безопасность
                    # sleep(2)
                    get_web_page_in_browser(url='https://id.yandex.ru/security/app-passwords')  # пароли приложений
                    sleep(2)
                    try:
                        el_mail = driver.find_element(By.CSS_SELECTOR, '#__next > div > main > div > section:nth-child(2) > div > div.List_root__CuPfW > div:nth-child(1)')
                        el_mail.click()
                    except Exception as exc:
                        logger.error(f'Ошибка при переходе в элемент "Создать пароль приложения Почта" {exc}')
                    try:
                        el_name_label = driver.find_element(By.CLASS_NAME, 'MaterialTextField_label__HE8cz')
                        if el_name_label.text == 'Придумайте имя пароля':
                                # el_name_psw_field.click()
                                # gen_name_psw = dict_with_data['Login'].split('@')[0]+'_mail_psw'
                                el_name_psw_field = driver.find_element(By.CLASS_NAME, 'MaterialTextField_input__94X76')
                                el_name_psw_field.send_keys(dict_with_data['Answer'], Keys.ENTER)
                                # dict_with_data['name_psw_for_mail'] = gen_name_psw
                    except Exception as exc:
                        logger.error(f'Ошибка при заполнении поля Имя пароля {exc}')
                    sleep(0.5)
                    try:
                        el_psw = driver.find_element(By.CSS_SELECTOR, 'body > div.Modal.Modal_visible.Modal_hasAnimation.Modal_root__smA6R.Modal_insets_none__tCHaA.app-password-wizzard_wizzard__u1u8J > div.Modal-Wrapper > div > div > div > section.Section_root__zl60G.app-password_section__AYoA5 > div > div.List_root__yESwN.variant-filled_root__baqI4.list-style-compact_root__m8IfF.size-normal_root__GrEvW.app-password_list__60lwa > div > div.UnstyledListItem_inner__Td3gb > div.Slot_root__jYlNI.Slot_content__XYDYF.alignment-center_root__ndulA.color-inherit_root__OQmPQ.Slot_direction_vertical__I3MEt > span')
                        dict_with_data['Psw_for_app_mail'] = el_psw.text
                        if dict_with_data['Psw_for_app_mail']:
                            logger.info(f'Для пользователя {dict_with_data["Login"]} получен пароль {dict_with_data["Psw_for_app_mail"]}')
                        el_btn_close = driver.find_element(By.CSS_SELECTOR, 'body > div.Modal.Modal_visible.Modal_hasAnimation.Modal_root__smA6R.Modal_insets_none__tCHaA.app-password-wizzard_wizzard__u1u8J > div.Modal-Wrapper > div > div > div > section:nth-child(4) > div > button > span')
                        el_btn_close.click()
                    except Exception as exc:
                        logger.error(f'Ошибка при получении пароля для почты" {exc}')
                        dict_with_data["Psw_for_app_mail"] = None
        else:
            logger.error(f'В файле config.txt установлено неверное значение параметра PARAMETER_CHANGE_PASSWORD_USE_COOKIES, установите True')
    else:
        logger.error(f'словарь dict_with_data с данными текущего аккаунта пуст')        
    # print(user_data)
    # forward_to_next_account = input('Перейти к следующему аккаунту? (y/n): ')
    # if forward_to_next_account == 'y':

    # удаляем cookies
    driver.delete_all_cookies()
    # sleep(0.5)
    if PARAM_DICT['NEED_PAUSE_BEFORE_CLOSED_BROWSER']  == 'True':  # Строка, так как из текстового конфига
        pause = input('нажмите любую клавишу для продолжения')
    driver.close()  # Закрытие окна браузера
    driver.quit()  # Выход
    # print(f'Обновленные данные {dict_with_data}')
    

def set_password_app_main():
    """Основная функция в режиме получения пароля приложения почта для успешных аккаунтов.
    Построчно читает xlsx файл и вызывает для каждого валидного аккаунта функцию смены пароля."""
    
    # Открываем xlsx книгу и активный лист
    workbook, worksheet = open_xlsx_file_and_return_active_sheet(file_name='combined.xlsx')

    if workbook and worksheet:  # Если xlsx книга и активный лист получены
        current_row = 2  # С какой строки читать xlsx файл
        # list_with_data = []  # список со словарями все аккаунты

        # Пройтись со второй строки до первой пустой
        try: 
            cur_cell = worksheet.cell(row=current_row, column=1)
            # while cur_cell.value is not None:
            while True:
                dict_with_data.clear()  # словарь для хранения данных об аккаунте (строчке таблицы)
                for index_, cur_col_name in enumerate(LIST_WITH_COLUMNS_COMBINED):
                    cur_cell = worksheet.cell(row=current_row, column=index_+1)
                    # Записать значение ячейки в словарь
                    dict_with_data[cur_col_name] = cur_cell.value
                print(f'Из xlsx файла получены данные: {dict_with_data["Login"]}')
                try: 
                    if len(dict_with_data) != 0:  # если словарь не пустой (был заполнен данными из файла)
                        # если статус аккаунта ok 
                        if (dict_with_data["Status"] == 'ok') and (dict_with_data["Psw_for_app_mail"] == None):
                            # Начинаем получение пароля, получаем после проверки обновленные данные
                            start_set_password_app()
                            # Записать данные (пароль для приложения почта) в xlsx файл
                            if dict_with_data["Psw_for_app_mail"]:
                                cur_cell = worksheet.cell(row=current_row, column=6, value=str(dict_with_data["Psw_for_app_mail"]))
                            
                            logger.info(f'Попытка сохранить книгу')
                            workbook.save(filename='combined.xlsx')  # сохранить xlsx файл
                            if current_row % 10 == 0:
                                shutil.copyfile('combined.xlsx', f'backups/backup_combined.xlsx')
                                logger.info(f'Создан backup файла combined.xlsx')
                            logger.info(f'файл xlsx сохранен')

                        else: # если статус аккаунта не ok
                            logger.info('Аккаунт не имеет статус "ok". Переход к следующему.')
                except:
                    logger.error(f'При проверке {dict_with_data["Login"]} возникла непредвиденная ошибка')
                finally:
                    current_row += 1
                    cur_cell = worksheet.cell(row=current_row, column=1)  # Переход на следующую строку
                    # pause = input('Нажмите любую клавишу для продолжения работы: ')
                    if cur_cell.value is None:
                        logger.info(f'Обнаружена пустая строка - {current_row}.')
                        need_retry_check = False  # нужна ли повторная проверка
                        for r in range(2, current_row):
                            c_status = worksheet.cell(row=r, column=LIST_WITH_COLUMNS_COMBINED.index("Status")+1)
                            c_psw_for_app_mail = worksheet.cell(row=r, column=LIST_WITH_COLUMNS_COMBINED.index("Psw_for_app_mail")+1)
                            # если значение статуса ok не содержится в словаре со статусами исключая no status
                            if (c_status.value == 'ok') and (c_psw_for_app_mail.value == None):
                                need_retry_check = True
                        if need_retry_check:
                            current_row = 2
                            logger.info(f'Начинаю повторную проверку со строки {current_row}.')
                            cur_cell = worksheet.cell(row=current_row, column=1)
                        else:
                            print('Получены пароли для всех успешных аккаунтов.')
                            shutil.copyfile('combined.xlsx', f'backups/backup_combined.xlsx')
                            logger.info(f'Создан backup файла combined.xlsx')
                            break
            logger.info('Выход из цикла проверки')
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
    
    check_accounts_main()

    print('\n\n')
    print('Время работы программы составило: ')
    print("--- %s seconds ---" % round((time() - start_time), 0))
    print('[!] Программа выполнена.')
    
