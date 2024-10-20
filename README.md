[![Static Badge](https://img.shields.io/badge/Telegram-Channel-Link?style=for-the-badge&logo=Telegram&logoColor=white&logoSize=auto&color=blue)](https://t.me/+jJhUfsfFCn4zZDk0)      [![Static Badge](https://img.shields.io/badge/Telegram-Bot%20Link-Link?style=for-the-badge&logo=Telegram&logoColor=white&logoSize=auto&color=blue)](https://t.me/fabrika/app?startapp=ref_2222195)



## Recommendation before use

# 🔥🔥 Use PYTHON 3.10 🔥🔥

> 🇷 🇺 README in Russian available [here](README-RU.md)

## Features  
|                                  Feature                                   | Supported |
|:--------------------------------------------------------------------------:|:---------:|
|                               Multithreading                               |     ✅     |
|                          Proxy binding to session                          |     ✅     |
|                            Using your referral                             |     ✅     |
|                                  Auto Tap                                  |     ✅     |
|                                 Auto boost                                 |     ✅     |
| Auto manage factory (buy worker, send worker to work, claim worker reward) |     ✅     |
|                            Auto buy workplaces                             |     ✅     |
|                                 Auto tasks                                 |     ✅     |
|                              Auto join squad                               |     ✅     |
|                  Supports telethon AND pyrogram .session                   |     ✅     |

_Script searches for session files in the following folders:_
* /sessions
* /sessions/pyrogram
* /session/telethon


## [Settings](https://github.com/SP-l33t/Fabrika-Telethon/tree/main/.env-example)

# Use default setting for best performance !
|            Settings            |                                                                                                                  Description                                                                                                                  |
|:------------------------------:|:---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------:|
|     **API_ID / API_HASH**      |                                                                                  Platform data from which to run the Telegram session (by default - android)                                                                                  |
|     **GLOBAL_CONFIG_PATH**     | Specifies the global path for accounts_config, proxies, sessions. <br/>Specify an absolute path or use an environment variable (default environment variable: **TG_FARM**) <br/>If no environment variable exists, uses the script directory. |
|          **FIX_CERT**          |                                                                                           Try to fix  SSLCertVerificationError ( True / **False** )                                                                                           |
|           **REF_ID**           |                                                                                         Your referral id (part of the referral link after startapp=)                                                                                          |
|          **SQUAD_ID**          |                                                                                             Squad id to join when start bot (default: **None** )                                                                                              |
|         **AUTO_TASK**          |                                                                                                       Auto do tasks ( **True** / False)                                                                                                       |
|          **AUTO_TAP**          |                                                                                                  Auto tap to earn point ( **True** / False )                                                                                                  |
|         **AUTO_BOOST**         |                                                                                              Auto use energy recharge boost ( **True** / False)                                                                                               |
|         **TAP_COUNT**          |                                                                                                Random ammount of taps (default: **[50, 200]**)                                                                                                |
|       **TAP_MIN_ENERGY**       |                                                                                                   Minium energy to stop tapping ( **50** )                                                                                                    |
|    **AUTO_MANAGE_FACTORY**     |                                                                                                   Auto manage factory ( **True** / False )                                                                                                    |
|     **UPGRADE_WORKPLACES**     |                                                                                                 Auto buy more workplaces ( **True** / False)                                                                                                  |
|      **AUTO_BUY_WORKER**       |                                                                                                     Auto Buy workers ( **True** / False )                                                                                                     |
| **RANDOM_SESSION_START_DELAY** |                                                                                        Random delay at session start from 1 to set value (e.g. **30**)                                                                                        |
|     **SESSIONS_PER_PROXY**     |                                                                                            Amount of sessions, that can share same proxy ( **1** )                                                                                            |
|    **USE_PROXY_FROM_FILE**     |                                                                               Whether to use a proxy from the `bot/config/proxies.txt` file (**True** / False)                                                                                |
|   **DISABLE_PROXY_REPLACE**    |                                                                      Disable automatic checking and replacement of non-working proxies before startup (True / **False**)                                                                      |
|       **DEVICE_PARAMS**        |                                                                          Enter device settings to make the telegram session look more realistic  (True / **False**)                                                                           |
|       **DEBUG_LOGGING**        |                                                                                     Whether to log error's tracebacks to /logs folder (True / **False**)                                                                                      |


## Quick Start 📚

To fast install libraries and run bot - open run.bat on Windows or run.sh on Linux

## Prerequisites
Before you begin, make sure you have the following installed:
- [Python](https://www.python.org/downloads/) **version 3.10**

## Obtaining API Keys
1. Go to [my.telegram.org](https://my.telegram.org) and log in using your phone number.
2. Select **"API development tools"** and fill out the form to register a new application.
3. Record the **API_ID** and **API_HASH** provided after registering your application in the `.env` file.

## Installation
You can download [**Repository**](https://github.com/SP-l33t/Fabrika-Telethon) by cloning it onto your system and installing the necessary dependencies:
```shell
git clone https://github.com/SP-l33t/Fabrika-Telethon.git
cd Fabrika-Telethon
```

# Linux manual installation
```shell
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
cp .env-example .env
nano .env  # Here you must specify your API_ID and API_HASH, the rest is taken by default
python3 main.py
```

You can also use arguments for quick start, for example:
```shell
~/Fabrika-Telethon >>> python3 main.py --action (1/2)
# Or
~/Fabrika-Telethon >>> python3 main.py -a (1/2)

# 1 - Run clicker
# 2 - Creates a session
```

# Windows manual installation
```shell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env-example .env
# Here you must specify your API_ID and API_HASH, the rest is taken by default
python main.py
```

You can also use arguments for quick start, for example:
```shell
~/Fabrika-Telethon >>> python main.py --action (1/2)
# Or
~/Fabrika-Telethon >>> python main.py -a (1/2)

# 1 - Run clicker
# 2 - Creates a session
```
