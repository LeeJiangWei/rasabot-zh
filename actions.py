# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/core/actions/#custom-actions/


from typing import Any, Text, Dict, List
import requests
from requests.exceptions import RequestException
import json
import hashlib

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import AllSlotsReset

BASE_URL = "http://127.0.0.1:3000"


class SearchSongAction(Action):
    cookies = ""

    def name(self) -> Text:
        return "action_search_song"

    def __isLogin(self) -> bool:
        try:
            response = requests.get(BASE_URL + "/login/status").json()
            if response['code'] == 200:
                return True
            else:
                return False
        except RequestException as e:
            print(e)
            return False

    def __login(self) -> bool:
        with open("./profile.json") as f:
            profile = json.load(f)
            phone = profile['phone']
            if 'md5_password' in profile.keys():
                md5_password = profile['md5_password']
            else:
                password = profile['password']
                md5_password = hashlib.md5(password.encode()).hexdigest()
            try:
                response = requests.get(BASE_URL + "/login/cellphone",
                                        params={"phone": phone, "md5_password": md5_password})

                if response.json()['code'] == 200:
                    self.cookies = response.cookies
                    return True
                else:
                    return False
            except RequestException as e:
                print(e)
                return False

    def __search_song(self, song_title, artist) -> [bool, str]:
        if not self.__isLogin():
            if not self.__login():
                return [False, "网易云账号登录失败。"]

        keywords = ""
        if song_title:
            keywords += song_title + " "
        if artist:
            keywords += artist

        try:
            response = requests.get(BASE_URL + "/cloudsearch", cookies=self.cookies,
                                    params={"keywords": keywords}).json()

            if 'result' not in response.keys():
                return [False, "抱歉，没有找到对应的音乐。"]

            song_id = response['result']['songs'][0]['id']

            c = requests.get(BASE_URL + "/check/music", cookies=self.cookies,
                             params={"id": song_id}).json()
            print(c, song_id)
            if not c['success']:
                return [False, "抱歉，该音乐暂无版权。"]

            m = requests.get(BASE_URL + "/song/url", cookies=self.cookies,
                             params={"id": song_id}).json()
            song_url = m['data'][0]['url']
            print(m)
            if not song_url:
                return [False, "抱歉，没有找到该音乐的播放链接。"]

            return [True, song_url]

        except RequestException as e:
            print(e)

    def run(
            self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]
    ) -> List[Dict[Text, Any]]:

        song_title = tracker.get_slot("song_title")
        artist = tracker.get_slot("artist")

        is_success, msg = self.__search_song(song_title, artist)

        if is_success:
            dispatcher.utter_message(attachment=msg)
        else:
            dispatcher.utter_message(msg)

        print(song_title, artist)

        return [AllSlotsReset()]


class SearchWeatherAction(Action):
    def name(self) -> Text:
        return "action_search_weather"

    def run(
            self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]
    ) -> List[Dict[Text, Any]]:
        location = tracker.get_slot("location")
        time = tracker.get_slot("time")

        print("Location: ", location, "Time: ", time)

        return [AllSlotsReset()]
