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

BASE_URL = "http://127.0.0.1:3000"


class SearchSongAction(Action):
    def name(self) -> Text:
        return "action_search_song"

    def run(
            self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]
    ) -> List[Dict[Text, Any]]:

        dispatcher.utter_message("action_search_song executed")

        song_title = tracker.get_slot("song_title")
        artist = tracker.get_slot("artist")

        keywords = ""
        if song_title:
            keywords += song_title
        if artist:
            keywords += " " + artist

        try:
            response = requests.get(BASE_URL + "/search", params={"keywords": keywords}).json()

            if 'result' not in response.keys():
                dispatcher.utter_message("抱歉，没有找到对应的音乐")
                return []

            song_id = response['result']['songs'][0]['id']

            c = requests.get(BASE_URL + "/check/music", params={"id": song_id}).json()

            if not c['success']:
                dispatcher.utter_message("抱歉，该音乐暂无版权")
                return []

            m = requests.get(BASE_URL + "/song/url", params={"id": song_id}).json()
            song_url = m['data'][0]['url']

            dispatcher.utter_message("已为您找到音乐，链接：" + song_url)

        except RequestException as e:
            print(e)

        print(song_title, artist)

        return []
