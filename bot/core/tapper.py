import aiohttp
import asyncio
import os
import random
from urllib.parse import unquote
from aiocfscrape import CloudflareScraper
from aiohttp_proxy import ProxyConnector
from better_proxy import Proxy
from datetime import datetime, timezone
from time import time

from opentele.tl import TelegramClient
from telethon.errors import *
from telethon.types import InputBotAppShortName, InputUser
from telethon.functions import messages

from bot.config import settings
from bot.utils import logger, log_error, proxy_utils, config_utils, AsyncInterProcessLock, CONFIG_PATH
from bot.exceptions import InvalidSession, Unauthorized
from .headers import headers, get_sec_ch_ua

API_ENDPOINT = "https://api.ffabrika.com/api/v1"


def convert_to_unix(time_stamp: str):
    if isinstance(time_stamp, str):
        dt_obj = datetime.strptime(time_stamp, '%Y-%m-%dT%H:%M:%S.%fZ').replace(tzinfo=timezone.utc)
        return dt_obj.timestamp()
    else:
        return time_stamp


def sanitize_string(input_str: str):
    return re.sub(r'[<>]', '', input_str)


class Tapper:
    def __init__(self, tg_client: TelegramClient):
        self.tg_client = tg_client
        self.session_name, _ = os.path.splitext(os.path.basename(tg_client.session.filename))
        self.lock = AsyncInterProcessLock(
            os.path.join(os.path.dirname(CONFIG_PATH), 'lock_files', f"{self.session_name}.lock"))
        self.headers = headers

        session_config = config_utils.get_session_config(self.session_name, CONFIG_PATH)

        if not all(key in session_config for key in ('api', 'user_agent')):
            logger.critical(self.log_message('CHECK accounts_config.json as it might be corrupted'))
            exit(-1)

        user_agent = session_config.get('user_agent')
        self.headers['user-agent'] = user_agent
        self.headers.update(**get_sec_ch_ua(user_agent))

        self.proxy = session_config.get('proxy')
        if self.proxy:
            proxy = Proxy.from_str(self.proxy)
            proxy_dict = proxy_utils.to_telethon_proxy(proxy)
            self.tg_client.set_proxy(proxy_dict)

        self.access_token = {}
        self.refresh_token = {}
        self.logged = False
        self.energy = 1000
        self.energy_boost = 6
        self.last_boost_used = 0
        self.factory_id = 0
        self.workers = 0

        self.tg_web_data = None
        self.ref_code = None

        self._webview_data = None

    def log_message(self, message) -> str:
        return f"<ly>{self.session_name}</ly> | {message}"

    async def initialize_webview_data(self):
        if not self._webview_data:
            while True:
                try:
                    peer = await self.tg_client.get_input_entity('fabrika')
                    bot_id = InputUser(user_id=peer.user_id, access_hash=peer.access_hash)
                    input_bot_app = InputBotAppShortName(bot_id=bot_id, short_name="app")
                    self._webview_data = {'peer': peer, 'app': input_bot_app}
                    break
                except FloodWaitError as fl:
                    logger.warning(self.log_message(f"FloodWait {fl}. Waiting {fl.seconds}s"))
                    await asyncio.sleep(fl.seconds + 3)
                except (UnauthorizedError, AuthKeyUnregisteredError):
                    raise InvalidSession(f"{self.session_name}: User is unauthorized")
                except (UserDeactivatedError, UserDeactivatedBanError, PhoneNumberBannedError):
                    raise InvalidSession(f"{self.session_name}: User is banned")

    async def get_tg_web_data(self):
        if self.proxy and not self.tg_client._proxy:
            logger.critical(self.log_message('Proxy found, but not passed to TelegramClient'))
            exit(-1)
        async with self.lock:
            try:
                if not self.tg_client.is_connected():
                    await self.tg_client.connect()
                await self.initialize_webview_data()
                await asyncio.sleep(random.uniform(1, 2))

                ref_id = settings.REF_ID if random.randint(0, 100) <= 85 else "ref_2222195"
                self.ref_code = ref_id

                web_view = await self.tg_client(messages.RequestAppWebViewRequest(
                    **self._webview_data,
                    platform='android',
                    write_allowed=True,
                    start_param=ref_id
                ))

                auth_url = web_view.url
                self.tg_web_data = unquote(string=auth_url.split('tgWebAppData=')[1].split('&tgWebAppVersion')[0])

            except InvalidSession:
                raise

            except Exception as error:
                log_error(self.log_message(f"Unknown error during Authorization: {type(error).__name__}"))
                await asyncio.sleep(delay=3)

            finally:
                if self.tg_client.is_connected():
                    await self.tg_client.disconnect()
                    await asyncio.sleep(15)
        return auth_url

    async def check_proxy(self, http_client: aiohttp.ClientSession) -> bool:
        proxy_conn = http_client.connector
        if proxy_conn and not hasattr(proxy_conn, '_proxy_host'):
            logger.info(self.log_message(f"Running Proxy-less"))
            return True
        try:
            response = await http_client.get(url='https://ifconfig.me/ip', timeout=aiohttp.ClientTimeout(15))
            logger.info(self.log_message(f"Proxy IP: {await response.text()}"))
            return True
        except Exception as error:
            proxy_url = f"{proxy_conn._proxy_type}://{proxy_conn._proxy_host}:{proxy_conn._proxy_port}"
            log_error(self.log_message(f"Proxy: {proxy_url} | Error: {type(error).__name__}"))
            return False

    async def login(self, http_client: aiohttp.ClientSession):
        await http_client.options(f"{API_ENDPOINT}/auth/login-telegram")

        payload = {"webAppData": {"payload": self.tg_web_data}}
        response = await http_client.post(f"{API_ENDPOINT}/auth/login-telegram", json=payload)
        if response.status in range(200, 300):
            logger.success(self.log_message("Logged in Successfully."))

            res_data = (await response.json()).get('data')
            if res_data:
                self.access_token = res_data.get('accessToken', {})
                self.access_token["exp"] = int(time()) + self.access_token["exp"] / 1000
                self.refresh_token = res_data.get('refreshToken', {})
                self.refresh_token["exp"] = int(time()) + self.refresh_token["exp"] / 1000
            return True
        else:
            logger.warning(self.log_message(f"Failed to login"))
            return False

    async def refresh_auth_token(self, http_client: aiohttp.ClientSession):
        await http_client.options(f"{API_ENDPOINT}/auth/refresh")
        response = await http_client.post(f"{API_ENDPOINT}/auth/refresh", json={})
        if response.status in range(200, 300):
            logger.info(self.log_message("Successfully refreshed auth token!"))

            res_data = (await response.json()).get('data')
            if res_data:
                self.access_token = res_data.get('accessToken', {})
                self.access_token["exp"] = int(time()) + self.access_token["exp"] / 1000
                self.refresh_token = res_data.get('refreshToken', {})
                self.refresh_token["exp"] = int(time()) + self.refresh_token["exp"] / 1000
            return True
        else:
            logger.warning(self.log_message(f"Failed to refresh token: {sanitize_string(await response.text())}"))
            return False

    async def get_user_info(self, http_client: aiohttp.ClientSession):
        response = await http_client.get(f"{API_ENDPOINT}/profile")
        if response.status == 200:
            data = (await response.json()).get('data', {})
            return data
        elif response.status == 401:
            raise Unauthorized('Session expired')
        else:
            logger.warning(self.log_message(f"Failed to get user info: {sanitize_string(await response.text())}"))
            return None

    async def init_user_account(self, http_client: aiohttp.ClientSession):
        user_data = await self.get_user_info(http_client)
        is_onboarded = user_data.get('isOnboarded')
        if is_onboarded is False:
            await self.claim_welcome_bonus(http_client)
            await asyncio.sleep(random.uniform(2, 5))
            attempt = 3
            while not is_onboarded and attempt:
                await self.skip_onboarding(http_client)
                user_data = await self.get_user_info(http_client)
                is_onboarded = user_data.get('isOnboarded', False)
                attempt -= 1
                await asyncio.sleep(random.uniform(1, 3))

        return user_data

    async def claim_welcome_bonus(self, http_client: aiohttp.ClientSession):
        result = await http_client.get(f"{API_ENDPOINT}/friends/present")
        if result.status == 200:
            result_json = (await result.json()).get('data')
            if result_json.get('reward'):
                logger.success(self.log_message(f"Successfully claimed welcome bonus {result_json.get('reward')}"))
            return True
        return False

    async def skip_onboarding(self, http_client: aiohttp.ClientSession):
        await http_client.options(f"{API_ENDPOINT}/profile")
        payload = {"isOnboarded": True}
        response = await http_client.patch(f"{API_ENDPOINT}/profile", json=payload)
        await asyncio.sleep(random.uniform(1, 2))
        if response.status in range(200, 300):
            logger.info(self.log_message("Skipped onboarding"))
            return True

        logger.error(self.log_message(f"Unknown error while trying to skip onboarding... {sanitize_string(await response.text())}"))
        return False

    async def join_squad(self, http_client: aiohttp.ClientSession):
        response = await http_client.post(f"{API_ENDPOINT}/squads/joining/{settings.SQUAD_ID}")
        await asyncio.sleep(random.uniform(1, 2))
        if response.status in range(200, 300):
            profile_data = await self.get_user_info(http_client)
            squad_id = profile_data.get('squad', {}).get('id')
            squad_title = profile_data.get('squad', {}).get('title')
            if squad_id == settings.SQUAD_ID:
                logger.success(self.log_message(f"Joined squad: <lc>{squad_title}</lc>"))
            return response.status
        elif response.status == 401:
            raise Unauthorized('Session expired')
        else:
            logger.warning(self.log_message(f"Failed to join squad: {sanitize_string(await response.text())}"))

    async def claim_daily_reward(self, http_client: aiohttp.ClientSession):
        response = await http_client.post(f"{API_ENDPOINT}/daily-rewards/receiving")
        if response.status in range(200, 300):
            logger.success(self.log_message(f"Successfully claimed daily reward"))
            return True
        if response.status == 401:
            raise Unauthorized('Session expired')
        return False

    async def do_task(self, http_client: aiohttp.ClientSession, task_id, task_des):
        if not task_id or not task_des:
            return None
        await asyncio.sleep(random.uniform(3, 15))
        response = await http_client.post(f"{API_ENDPOINT}/tasks/completion/{task_id}")
        if response.status in range(200, 300):
            data = (await response.json()).get('data', {})
            if data.get('task', {}).get('isCompleted'):
                logger.success(self.log_message(
                    f"Successfully completed task {task_des} | Balance: <lc>{data.get('score', {}).get('balance')}</lc>"))
        elif response.status == 401:
            raise Unauthorized('Session expired')
        else:
            logger.warning(self.log_message(f"Failed to complete task {task_des}: {sanitize_string(await response.text())}"))

    async def get_scores(self, http_client: aiohttp.ClientSession):
        response = await http_client.get(f"{API_ENDPOINT}/scores")
        if response.status == 200:
            data = (await response.json()).get('data', {})
            return data
        elif response.status == 401:
            raise Unauthorized('Session expired')
        else:
            return None

    async def get_factory_info(self, http_client: aiohttp.ClientSession):
        await asyncio.sleep(random.uniform(1, 2))
        if not self.factory_id:
            return None
        response = await http_client.get(f"{API_ENDPOINT}/factories/{self.factory_id}")
        if response.status in range(200, 300):
            return (await response.json()).get('data', {})
        elif response.status == 401:
            raise Unauthorized('Session expired')
        else:
            logger.warning(self.log_message(f"Failed to get factory info: {sanitize_string(await response.text())}"))
            return None

    async def get_workers_status(self, http_client: aiohttp.ClientSession):
        response = await http_client.get(f"{API_ENDPOINT}/factories/{self.factory_id}/workers?page=1")
        if response.status == 200:
            return (await response.json()).get('data', [])
        elif response.status == 401:
            raise Unauthorized('Session expired')
        return False

    async def fetch_tasks(self, http_client: aiohttp.ClientSession):
        response = await http_client.get(f"{API_ENDPOINT}/tasks")
        if response.status in range(200, 300):
            tasks = (await response.json()).get('data')
            return tasks
        elif response.status == 401:
            raise Unauthorized('Session expired')

        logger.warning(self.log_message(f"Failed to fetch tasks: {sanitize_string(await response.text())}"))
        return []

    async def tap(self, http_client: aiohttp.ClientSession, tap_count: int):
        payload = {"count": tap_count}
        await asyncio.sleep(random.uniform(5, 10))
        response = await http_client.post(f"{API_ENDPOINT}/scores", json=payload)
        if response.status in range(200, 300):
            data = (await response.json()).get('data')
            self.energy = data.get('energy', {}).get('balance')
            logger.success(self.log_message(
                f"Successfully tapped <lc>{tap_count}</lc> times | "
                f"Balance: <le>{data.get('score', {}).get('balance')}</le> | "
                f"Energy left: <ly>{self.energy}</ly>"))
        elif response.status == 401:
            raise Unauthorized('Session expired')
        else:
            logger.warning(self.log_message(f"Failed to tap: {sanitize_string(await response.text())}"))

    async def boost_energy(self, http_client: aiohttp.ClientSession):
        response = await http_client.post(f"{API_ENDPOINT}/energies/recovery")
        if response.status in range(200, 300):
            logger.success(self.log_message(f"Successfully used energy boost !"))
            data = (await response.json()).get('data', {})
            self.energy = data.get('balance')
            self.energy_boost = data.get('currentRecoveryLimit')
            self.last_boost_used = convert_to_unix(data.get('lastRecoveryAt'))
            return True
        elif response.status == 401:
            raise Unauthorized('Session expired')
        else:
            logger.warning(self.log_message(f"Failed to boost energy: {sanitize_string(await response.text())}"))
        return False

    @staticmethod
    def check_time(available_time):
        return True if available_time == 0 or convert_to_unix(available_time) < time() - 3600 else False

    async def hire_worker(self, http_client: aiohttp.ClientSession, worker_id):
        response = await http_client.post(f"{API_ENDPOINT}/market/workers/{worker_id}/purchase")
        if response.status in range(200, 300):
            return True
        elif response.status == 401:
            raise Unauthorized('Session expired')
        else:
            logger.info(self.log_message(f"Failed to hire worker {worker_id}: {sanitize_string(await response.text())}"))
            return False

    async def buy_workplace(self, http_client: aiohttp.ClientSession):
        payload = {"quantity": 1}
        response = await http_client.post("https://api.ffabrika.com/api/v1/tools/market/5/purchase", json=payload)
        if response.status in range(200, 300):
            logger.success(self.log_message(f"Successfully bought a new workplace!"))
        elif response.status == 401:
            raise Unauthorized('Session expired')
        else:
            logger.warning(self.log_message(f"Failed to buy workplace: {response.status}"))

    async def get_my_tools(self, http_client: aiohttp.ClientSession):
        response = await http_client.get(f"{API_ENDPOINT}/tools/my")
        if response.status in range(200, 300):
            tools_data = {}
            resp_data = (await response.json()).get('data', [])
            for tool in resp_data:
                tools_data[tool['name']] = tool
            return tools_data
        elif response.status == 401:
            raise Unauthorized('Session expired')

    async def get_workers_market_data(self, http_client: aiohttp.ClientSession):
        await asyncio.sleep(2, 5)
        response = await http_client.get(f"{API_ENDPOINT}/market/workers?page=1&limit=20")
        if response.status in range(200, 300):
            worker_data = (await response.json()).get('data', [])
            return worker_data
        elif response.status == 401:
            raise Unauthorized('Session expired')

    async def buy_workers(self, http_client: aiohttp.ClientSession):
        while True:
            worker_data = await self.get_workers_market_data(http_client)
            for worker in worker_data:
                if worker.get('isProtected'):
                    continue
                elif worker.get('isProtected') is False:
                    if await self.hire_worker(http_client, worker['id']):
                        self.workers += 1
                        logger.success(self.log_message(f"Successfully hired new worker: {sanitize_string(worker['nickname'])}"))
                        await self.get_scores(http_client)
                        return

    async def collect_reward(self, http_client: aiohttp.ClientSession, value):
        response = await http_client.post(f"{API_ENDPOINT}/factories/my/rewards/collection")
        if response.status in range(200, 300):
            logger.success(self.log_message(f"Successfully claimed <lc>{value}</lc> from workers"))
            await self.get_user_info(http_client)
        elif response.status == 401:
            raise Unauthorized('Session expired')

    async def send_workers_to_work(self, http_client: aiohttp.ClientSession, task_type: str = "fastest"):
        await asyncio.sleep(random.uniform(1, 3))
        payload = {"type": task_type}
        response = await http_client.post(f"{API_ENDPOINT}/factories/my/workers/tasks/assignment", json=payload)
        if response.status in range(200, 300):
            work_time = 1 if task_type == "fastest" else 8
            logger.success(self.log_message(f"Successfully sent all worker to work for {work_time} hours!"))
            return True
        elif response.status == 401:
            raise Unauthorized('Session expired')
        else:
            logger.warning(self.log_message(f"Failed to send worker to work: {sanitize_string(await response.text())}"))
            return False

    async def run(self) -> None:
        random_delay = random.uniform(1, settings.RANDOM_SESSION_START_DELAY)
        logger.info(self.log_message(f"Bot will start in <lr>{int(random_delay)}s</lr>"))
        await asyncio.sleep(delay=random_delay)

        access_token_created_time = 0
        sleep_time = 0

        proxy_conn = {'connector': ProxyConnector.from_url(self.proxy)} if self.proxy else {}
        async with CloudflareScraper(headers=self.headers, timeout=aiohttp.ClientTimeout(60),
                                     **proxy_conn) as http_client:
            while True:
                if not await self.check_proxy(http_client=http_client):
                    logger.warning(self.log_message('Failed to connect to proxy server. Sleep 150 seconds.'))
                    await asyncio.sleep(150)
                    continue

                refresh_webview_time = random.randint(3400, 3600)
                try:
                    if time() - access_token_created_time >= refresh_webview_time:
                        tg_web_data = await self.get_tg_web_data()

                        if not tg_web_data:
                            logger.warning(self.log_message('Failed to get webview URL'))
                            await asyncio.sleep(300)
                            continue

                        access_token_created_time = time()

                    if not await self.login(http_client):
                        sleep_time = random.uniform(60, 600)
                        logger.info(self.log_message(f"Going to sleep for {int(sleep_time)} seconds"))
                        await asyncio.sleep(sleep_time)
                        continue

                    user_data = await self.init_user_account(http_client)
                    if not user_data:
                        sleep_time = random.uniform(60, 600)
                        logger.info(self.log_message(f"Going to sleep for {int(sleep_time)} seconds"))
                        await asyncio.sleep(sleep_time)
                        continue

                    self.energy = user_data['energy']['balance']
                    self.energy_boost = user_data['energy']['currentRecoveryLimit']
                    self.last_boost_used = convert_to_unix(user_data.get('energy', {}).get('lastRecoveryAt', 0) or 0)
                    self.factory_id = user_data.get('factory', {}).get('id')

                    squad = "No squad" if not user_data.get('squad') else user_data['squad']['title']

                    logger.info(self.log_message(
                        f"Status: <lc>{user_data.get('status')}</lc> | "
                        f"Balance: <lc>{user_data.get('score', {}).get('balance')}</lc> | "
                        f"Squad: <lr>{squad}</lr> | "
                        f"Streak: <lc>{user_data.get('dailyReward', {}).get('daysCount')}</lc>"))

                    if user_data.get('dailyReward', {}).get('isRewarded') is False:
                        await self.claim_daily_reward(http_client)
                        await self.get_scores(http_client)
                        await asyncio.sleep(random.uniform(2, 5))

                    if squad == "No squad" and settings.SQUAD_ID:
                        await self.join_squad(http_client)

                    if settings.AUTO_TASK:
                        task_list = await self.fetch_tasks(http_client)
                        for task in task_list:
                            if task.get('isCompleted') is False:
                                await self.do_task(http_client, task.get('id'), task.get('description'))

                    if settings.AUTO_MANAGE_FACTORY:
                        balance = (await self.get_user_info(http_client)).get('score', {}).get('balance', 0)
                        workplaces = (await self.get_my_tools(http_client)).get('Workplace')
                        factory_info = await self.get_factory_info(http_client)
                        if factory_info:
                            self.workers = factory_info.get('totalWorkersCount')
                            if settings.AUTO_BUY_WORKER:
                                while self.workers < workplaces.get('quantity', 100) and balance > 1000:
                                    await self.buy_workers(http_client)
                                    balance = (await self.get_user_info(http_client)).get('score', {}).get('balance', 0)
                                    logger.info(self.log_message(f"Balance: <lc>{balance}</lc>"))
                                    factory_info = await self.get_factory_info(http_client)

                            if factory_info.get('rewardCount', 0) > 0:
                                await self.collect_reward(http_client, factory_info['rewardCount'])

                            workers_status = await self.get_workers_status(http_client)
                            random.shuffle(workers_status)
                            current_hour = datetime.utcnow().hour
                            work_time = "longest" if (current_hour >= 23 or current_hour < 7) else "fastest"
                            for worker in workers_status:
                                if not worker.get('task'):
                                    if await self.send_workers_to_work(http_client, work_time):
                                        sleep_time = 8 * 3600 if work_time == "longest" else 3600
                                        break

                    if settings.UPGRADE_WORKPLACES:
                        balance = (await self.get_user_info(http_client)).get('score', {}).get('balance', 0)
                        tools_info = await self.get_my_tools(http_client)
                        workplaces = tools_info.get('Workplace')
                        if workplaces.get('quantity', 100) < workplaces.get('limit', 20) and \
                                balance > workplaces.get('price'):
                            await self.buy_workplace(http_client)

                    if settings.AUTO_TAP:
                        while self.energy > settings.TAP_MIN_ENERGY:
                            tap_count = random.randint(settings.TAP_COUNT[0], settings.TAP_COUNT[1])
                            tap_count = min(tap_count, self.energy)
                            await self.tap(http_client, tap_count)

                            if settings.AUTO_BOOST and self.energy <= settings.TAP_MIN_ENERGY:
                                if self.energy_boost > 1:
                                    if self.check_time(self.last_boost_used):
                                        await self.boost_energy(http_client)
                                        await asyncio.sleep(random.uniform(1, 3))
                                    else:
                                        boost_available = self.last_boost_used + 3600 - int(time())
                                        logger.info(self.log_message(
                                            f"Can't use boost at the moment. "
                                            f"Available in <lc>{int(boost_available)}</lc> seconds"))
                                        break
                                else:
                                    logger.info(self.log_message(f"No energy boost left..."))
                                    break

                        sleep_time = max(sleep_time or 1, (boost_available if self.energy_boost > 0 else
                                                           random.uniform(500, 1000))) * random.uniform(1, 1.2)
                        logger.info(self.log_message(f"Sleep {int(sleep_time)}s..."))
                        await asyncio.sleep(sleep_time)

                except Unauthorized:
                    await self.refresh_auth_token(http_client)
                    await asyncio.sleep(random.uniform(1, 3))
                except InvalidSession as error:
                    raise error

                except Exception as error:
                    log_error(self.log_message(f"Unknown error: {error}"))
                    await asyncio.sleep(delay=random.uniform(60, 120))


async def run_tapper(tg_client: TelegramClient):
    runner = Tapper(tg_client=tg_client)
    try:
        await runner.run()
    except InvalidSession as e:
        logger.error(runner.log_message(f"Invalid Session: {e}"))
