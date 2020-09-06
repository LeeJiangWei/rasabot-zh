# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/core/actions/#custom-actions/


from typing import Any, Text, Dict, List
import requests
from requests.exceptions import RequestException

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import AllSlotsReset

BASE_URL = "http://127.0.0.1:3000"


class SearchSongAction(Action):
    def name(self) -> Text:
        return "action_search_song"

    def search_song(self, song_title, artist) -> [bool, str]:
        keywords = ""
        if song_title:
            keywords += song_title + " "
        if artist:
            keywords += artist

        try:
            response = requests.get(BASE_URL + "/search", params={"keywords": keywords}).json()

            if 'result' not in response.keys():
                return [False, "抱歉，没有找到对应的音乐"]

            song_id = response['result']['songs'][0]['id']

            c = requests.get(BASE_URL + "/check/music", params={"id": song_id}).json()

            if not c['success']:
                return [False, "抱歉，该音乐暂无版权"]

            m = requests.get(BASE_URL + "/song/url", params={"id": song_id}).json()
            song_url = m['data'][0]['url']

            if not song_url:
                return [False, "抱歉，没有找到该音乐的播放链接"]

            return [True, song_url]

        except RequestException as e:
            print(e)

    def run(
            self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]
    ) -> List[Dict[Text, Any]]:

        dispatcher.utter_message("action_search_song executed")

        song_title = tracker.get_slot("song_title")
        artist = tracker.get_slot("artist")

        is_success, msg = self.search_song(song_title, artist)

        if is_success:
            dispatcher.utter_message("已为您找到播放链接：" + msg)
        else:
            dispatcher.utter_message(msg)

        print(song_title, artist)

        return [AllSlotsReset()]
