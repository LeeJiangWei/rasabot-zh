# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/core/actions/#custom-actions/


from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher


class SearchSongAction(Action):
    def name(self) -> Text:
        return "action_search_song"

    def run(
            self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]
    ) -> List[Dict[Text, Any]]:
        song_title = tracker.get_slot("song_title")
        artist = tracker.get_slot("artist")

        dispatcher.utter_message("action_search_song executed")
        print(song_title, artist)

        return []
