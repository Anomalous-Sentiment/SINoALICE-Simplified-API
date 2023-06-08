from Crypto.Util.Padding import pad, unpad
from Crypto.Cipher import AES
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA1
from Crypto.PublicKey import RSA
import asyncio
import aiohttp
from .constants.Config import APP_VERSION, UUID_PAYMENT, USER_ID, PRIV_KEY, AES_KEY, X_UID
import msgpack, base64, datetime, random, logging, time, urllib3
from .constants.DeviceInformation import DeviceInfo
from google_play_scraper import app

class BasicCrypto():
    def __init__(self):
        self.aes = AES_KEY

    def encrypt(self, payload):
        packed_request_content = msgpack.packb(payload)
        iv = packed_request_content[0:16]
        padded_request_content = pad(packed_request_content, 16)
        aes = AES.new(self.aes, AES.MODE_CBC, iv)
        encrypted_request_content = aes.encrypt(padded_request_content)
        return iv + encrypted_request_content

    def _decrypt_response(self, response_content):
        iv = response_content[0:16]
        aes = AES.new(self.aes, AES.MODE_CBC, iv)
        pad_text = aes.decrypt(response_content[16:])
        text = unpad(pad_text, 16)
        data_loaded = msgpack.unpackb(text)
        return data_loaded

class BaseAPI():
    URL = "https://api-sinoalice-us.pokelabo.jp"
    EXCESS_TRAFFIC = 14014

    def __init__(self):
        self.crypto = BasicCrypto()

        self.uuid_payment = UUID_PAYMENT
        self.x_uid_payment = X_UID
        self.priv_key = PRIV_KEY
        self.user_id = USER_ID
        self.session_id = ''
        self.headers = {}
        self.device_info = DeviceInfo()

        # Set the initial app version
        self.app_version = APP_VERSION

        urllib3.disable_warnings()

    def _login_account(self):
        try:
            # Get the sinoalice app store data on google store
            sino_app_data = app(
                'com.nexon.sinoalice',
                lang='en', # defaults to 'en'
                country='us' # defaults to 'us'
            )
            # Set the new app version number
            self.app_version = sino_app_data['version']
        except Exception as Argument:
            # Failed to get latest app version string
            print('Error getting latest app version')


        inner_payload = self.device_info.get_device_info_dict()
        
        # Overwrite the version from the device version dict
        inner_payload['appVersion'] = self.app_version
        
        inner_payload["uuid"] = self.uuid_payment
        inner_payload["xuid"] = self.x_uid_payment

        response = asyncio.run(self._single_main("/api/login", inner_payload, remove_header=["Cookie"]))

        # Check for errors in response
        if 'errors' in res:
            # TODO: Check what type of error is returned (Usually be a maintainence error in JP if everything is working properly)
            # Currently assumes the error is caused by maintenence
            raise ServerMaintenenceException(res)
            
        self.session_id = response["payload"]["sessionId"]

    def get_action_time(self, old_action_time=0):
        action_times = [0xfd2c030, 0x18c120b0, 0xdd98840, 0x13ee8a0, 0x1a26560, 0x21526d10, 0xe100190, 0xfbf3830]  # Todo how are those generated
        current_time = (datetime.datetime.utcnow() - datetime.datetime(1,1,1)).total_seconds() * 10**7
        time_offset = random.choice(action_times)
        next_time = int(current_time + time_offset)
        final_time = ((next_time & 0x3FFFFFFFFFFFFFFF) - 0x701CE1722770000)
        return final_time

    def _handle_response(self, response):
        decrypted_response = self.crypto._decrypt_response(response.content)
        logging.debug(f"from {response.request.path_url} {decrypted_response}")

        if decrypted_response.get("errors", None) is not None:
            if decrypted_response["errors"][0]["code"] == BaseAPI.EXCESS_TRAFFIC:
                logging.warning(f"EXCESS_TRAFFIC Exception {response.request.path_url}")
                raise ExcessTrafficException("")

        return decrypted_response

    def sign(self, data, hash_func, key):
        hashed_string = hash_func.new(data)
        base_string = base64.b64encode(hashed_string.digest())
        hashed_string = hash_func.new()
        hashed_string.update(base_string)
        signature = pkcs1_15.new(key).sign(hashed_string)
        return base64.b64encode(signature)

    def import_key(self, key):
        keyDER = base64.b64decode(key)
        keyPRIV = RSA.importKey(keyDER)
        return keyPRIV

    def _prepare_request(self, request_type, resource, inner_payload: dict, remove_header=None):
        if remove_header is None:
            remove_header = []
        
        self.action_time = self.get_action_time()

        payload = {
            "payload": inner_payload,
            "uuid": self.uuid_payment,
            "userId": self.user_id,
            "sessionId": self.session_id,
            "actionToken": None,
            "ctag": None,
            "actionTime": self.action_time
        }

        logging.debug(f"to {request_type} {resource} {payload} {self.uuid_payment}")
        payload = self.crypto.encrypt(payload)

        key = self.import_key(self.priv_key)
        mac = self.sign(payload, SHA1, key).strip().decode()

        common_headers = {
            "Expect": "100-continue",
            "User-Agent": f"UnityRequest com.nexon.sinoalice {self.app_version} (Samsung Galaxy Note10)"
                          f" Android OS 10 / API-29)",
            "X-post-signature": f"{mac}",
            "X-Unity-Version": "2018.4.19f1",
            "Content-Type": "application/x-msgpack",
            "Connection": "Keep-Alive",
            "Accept-Encoding": "gzip",
            "Cookie": f"PHPSESSID={self.session_id}",
            "Host": "api-sinoalice-us.pokelabo.jp"
        }
        for header in remove_header:
            common_headers.pop(header)

        self.headers = common_headers
        return payload

    def post(self, resource, payload: dict = None, remove_header=None) -> dict:
        self._login_account()
        resulting_response = asyncio.run(self._single_main(resource, payload, remove_header=remove_header))
        return resulting_response

    async def _single_main(self, resource, payload, session=None, remove_header=None):
        if session == None:
            async with aiohttp.ClientSession(BaseAPI.URL) as session:
                ret = await asyncio.gather(self._async_post(resource, payload, session, remove_header))
        else:
            ret = await asyncio.gather(self._async_post(resource, payload, session, remove_header))
        
        # We know it returns an array of size 1
        return ret[0]

    async def _parallel_main(self, resource, payloads, session = None, remove_header=None):
        if session == None:
            async with aiohttp.ClientSession(BaseAPI.URL) as session:
                ret = await asyncio.gather(*[self._async_post(resource, payload, session, remove_header) for payload in payloads])
        else:
            ret = await asyncio.gather(*[self._async_post(resource, payload, session, remove_header) for payload in payloads])
        return ret

    async def _async_post(self, resource, payload, session, remove_header=None):
        timeout_duration = 10
        processed_payload = self._prepare_request("POST", resource, payload, remove_header=None)
        decrypted_data = None

        while decrypted_data is None:
            try:
                async with session.post(resource, data=processed_payload, headers=self.headers) as response:
                    data = await response.read()

                    decrypted_data = self.crypto._decrypt_response(data)
                
            except ExcessTrafficException as e:
                time.sleep(timeout_duration)
                timeout_duration += 5
                if timeout_duration > 30:
                    logging.critical(f"Maximum attempts for {resource} aborting")
                    # Re-throw exception
                    raise

        return decrypted_data


    def parallel_post(self, resource, payloads: list = None, remove_header=None) -> dict:
        self._login_account()
        results = asyncio.run(self._parallel_main(resource, payloads, remove_header=remove_header))
        return results

class ExcessTrafficException(Exception):
    pass

class ServerMaintenenceException(Exception):
    def __init__(self, response, message="Server is undergoing maintenence"):
        self.response = response
        self.message = message
        super().__init__(self.message)