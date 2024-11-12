[![Static Badge](https://img.shields.io/badge/Telegram-Channel-Link?style=for-the-badge&logo=Telegram&logoColor=white&logoSize=auto&color=blue)](https://t.me/+jJhUfsfFCn4zZDk0)      [![Static Badge](https://img.shields.io/badge/Telegram-Bot%20Link-Link?style=for-the-badge&logo=Telegram&logoColor=white&logoSize=auto&color=blue)](https://t.me/fabrika/app?startapp=ref_2222195)



## Recommendation before use

# 🔥🔥 PYTHON version must be 3.10 🔥🔥

> 🇪🇳 README in english available [here](README)

## Функционал  
|               Функционал               | Поддерживается |
|:--------------------------------------:|:--------------:|
|            Многопоточность             |       ✅        | 
|        Привязка прокси к сессии        |       ✅        | 
| Использование вашей реферальной ссылки |       ✅        |
|               Авто фарм                |       ✅        |
|        Авто выполнение заданий         |       ✅        |
|             Авто улучшения             |       ✅        |
|         Авто вращение рулетки          |       ✅        |
|    Автоматичесие ежедневная стрики     |       ✅        |
| Поддержка telethon И pyrogram .session |       ✅        |

_Скрипт осуществляет поиск файлов сессий в следующих папках:_
* /sessions
* /sessions/pyrogram
* /session/telethon


## [Настройки](https://github.com/SP-l33t/Fabrika-Telethon/tree/main/.env-example)
|         Настройки          |                                                                                                                              Описание                                                                                                                               |
|:--------------------------:|:-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------:|
|   **API_ID / API_HASH**    |                                                                                         Данные платформы, с которой будет запущена сессия Telegram (по умолчанию - android)                                                                                         |
|   **GLOBAL_CONFIG_PATH**   | Определяет глобальный путь для accounts_config, proxies, sessions. <br/>Укажите абсолютный путь или используйте переменную окружения (по умолчанию - переменная окружения: **TG_FARM**)<br/> Если переменной окружения не существует, использует директорию скрипта |
|        **FIX_CERT**        |                                                                                              Попытаться исправить ошибку SSLCertVerificationError ( True / **False** )                                                                                              |
|         **REF_ID**         |                                                                                                Ваш реферальный идентификатор (В реферальной ссылке после startapp= )                                                                                                |
|        **SQUAD_ID**        |                                                                                                   Squad id, к которому присоединится бот (по-умолчанию: **None**)                                                                                                   |
|       **AUTO_TASK**        |                                                                                                         Выполнять задания автоматически ( **True** / False)                                                                                                         |
|        **AUTO_TAP**        |                                                                                                 Автоматически тапать, чтобы заработать поинты ( **True** / False )                                                                                                  |
|       **AUTO_BOOST**       |                                                                                             Использовать бусты для перезарядки энергии автоматичеки ( **True** / False)                                                                                             |
|       **TAP_COUNT**        |                                                                                                    Случайное количество нажатий за раз (default: **[50, 200]**)                                                                                                     |
|     **TAP_MIN_ENERGY**     |                                                                                           Минимальное количество энергии, ниже которого цикл тапа прекращается ( **50** )                                                                                           |
|  **AUTO_MANAGE_FACTORY**   |                                                                        Автоматически управлять фабрикой (собирать награды за работу и отправлять сотрудников работать) ( **True** / False )                                                                         |
|   **UPGRADE_WORKPLACES**   |                                                                                                   Автоматически покупать новые рабочие места ( **True** / False)                                                                                                    |
|    **AUTO_BUY_WORKER**     |                                                                                                         Автоматически покупать рабочих ( **True** / False )                                                                                                         |
| **ATTEMPTS_TO_BUY_WORKER** |                                                                                                 Количество попыток купить рабочего (количество страниц) ( **10** )                                                                                                  |
|    **WORKER_MAX_PRICE**    |                                                                                                               Максимальная цена рабочего ( **1500** )                                                                                                               |
|  **SESSION_START_DELAY**   |                                                                                           Случайная задержка при запуске. От 1 до указанного значения (например, **30**)                                                                                            |
|   **SESSIONS_PER_PROXY**   |                                                                                            Количество сессий, которые могут использовать один и тот же прокси ( **1** )                                                                                             |
|  **USE_PROXY_FROM_FILE**   |                                                                                             Использовать ли прокси из файла `bot/config/proxies.txt` (**True** / False)                                                                                             |
| **DISABLE_PROXY_REPLACE**  |                                                                                   Отключить автоматическую проверку и замену нерабочих прокси перед стартом ( True / **False** )                                                                                    |
|     **DEVICE_PARAMS**      |                                                                                 Введите настройки устройства, чтобы телеграмм-сессия выглядела более реалистично (True / **False**)                                                                                 |
|     **DEBUG_LOGGING**      |                                                                                                Включить логирование трейсбэков ошибок в лог файл (True / **False**)                                                                                                 |

## Быстрый старт 📚

Для быстрой установки и последующего запуска - запустите файл run.bat на Windows или run.sh на Unix

## Предварительные условия
Прежде чем начать, убедитесь, что у вас установлено следующее:
- [Python](https://www.python.org/downloads/) **версии 3.10**

## Получение API ключей
1. Перейдите на сайт [my.telegram.org](https://my.telegram.org) и войдите в систему, используя свой номер телефона.
2. Выберите **"API development tools"** и заполните форму для регистрации нового приложения.
3. Запишите `API_ID` и `API_HASH` в файле `.env`, предоставленные после регистрации вашего приложения.

## Установка
Вы можете скачать [**Репозиторий**](https://github.com/SP-l33t/Fabrika-Telethon) клонированием на вашу систему и установкой необходимых зависимостей:
```shell
git clone https://github.com/SP-l33t/Fabrika-Telethon.git
cd Fabrika-Telethon
```

Затем для автоматической установки введите:

Windows:
```shell
run.bat
```

Linux:
```shell
run.sh
```

# Linux ручная установка
```shell
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
cp .env-example .env
nano .env  # Здесь вы обязательно должны указать ваши API_ID и API_HASH , остальное берется по умолчанию
python3 main.py
```

Также для быстрого запуска вы можете использовать аргументы, например:
```shell
~/Fabrika-Telethon >>> python3 main.py --action (1/2)
# Or
~/Fabrika-Telethon >>> python3 main.py -a (1/2)

# 1 - Запускает кликер
# 2 - Создает сессию
```


# Windows ручная установка
```shell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env-example .env
# Указываете ваши API_ID и API_HASH, остальное берется по умолчанию
python main.py
```

Также для быстрого запуска вы можете использовать аргументы, например:
```shell
~/Fabrika-Telethon >>> python main.py --action (1/2)
# Или
~/Fabrika-Telethon >>> python main.py -a (1/2)

# 1 - Запускает кликер
# 2 - Создает сессию
```
