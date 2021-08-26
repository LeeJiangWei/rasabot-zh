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


class ResponseCommandAction(Action):
    def name(self) -> Text:
        return "action_response_command"

    def run(
            self, dispatcher, tracker: Tracker, domain: Dict[Text, Any]
    ) -> List[Dict[Text, Any]]:
        obj = tracker.get_slot("object")
        color = tracker.get_slot("color")
        on = tracker.get_slot("on")
        near = tracker.get_slot("near")
        intent = tracker.latest_message["intent"]["name"]

        reply = {"intent": intent, "object": obj, "color": color, "on": on, "near": near}

        print(reply)
        dispatcher.utter_message(json_message=reply)

        return [AllSlotsReset()]


class TuringDialogue(Action):
    def name(self) -> Text:
        return "action_turing_dialogue"

    def run(
            self, dispatcher, tracker: Tracker, domain: Dict[Text, Any]
    ) -> List[Dict[Text, Any]]:

        input_text = tracker.latest_message["text"]
        print(input_text)

        with open("./profile.json") as f:
            profile = json.load(f)
            key = profile["turing_api_key"]

        body = {
            "reqType": 0,
            "perception": {
                "inputText": {
                    "text": input_text
                },
                "selfInfo": {
                    "location": {
                        "city": "广州",
                        "province": "广东"
                    }
                }
            },
            "userInfo": {
                "apiKey": key,
                "userId": "nano"
            }
        }

        try:
            results = requests.post("http://openapi.turingapi.com/openapi/api/v2", json=body).json()["results"]

            for result in results:
                if result["resultType"] == "text":
                    dispatcher.utter_message(result["values"]["text"])

        except RequestException as e:
            print(e)
            dispatcher.utter_message("网络发生错误，请检查服务器状态。")

        return [AllSlotsReset()]


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

    def __search_song(self, song_title, artist) -> [bool, any]:
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

            song = response['result']['songs'][0]

            song_name = song['name']
            song_id = song['id']
            artist_name = song['ar'][0]['name']
            album_url = song['al']['picUrl']

            c = requests.get(BASE_URL + "/check/music", cookies=self.cookies,
                             params={"id": song_id}).json()

            if not c['success']:
                return [False, "抱歉，该音乐暂无版权。"]

            m = requests.get(BASE_URL + "/song/url", cookies=self.cookies,
                             params={"id": song_id}).json()
            song_url = m['data'][0]['url']
            print(m)
            if not song_url:
                return [False, "抱歉，没有找到该音乐的播放链接。"]

            return [True, {"name": song_name, "url": song_url, "artist": artist_name, "cover": album_url}]

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
            print("song_msg: ", msg)
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

        if not location:
            location = "广州"

        if not time:
            time = 0
        else:
            try:
                time = int(time)
            except ValueError:
                dispatcher.utter_message("对不起，我无法知道您指定的时间噢，现在为您查询现在的天气。")
                time = 0

        print(f"Querying: location:{location}, time:{time}")

        with open("./profile.json") as f:
            profile = json.load(f)
            key = profile['weather_api_key']

            geo_response = requests.get("https://geoapi.heweather.net/v2/city/lookup", params={
                "location": location,
                "key": key,
                "range": "cn",
                "number": 1
            }).json()

            # location_id = None
            if geo_response['code'] == "200":
                loc = geo_response['location'][0]
                location_id = loc['id']
                location_adm1 = loc['adm1']
                location_adm2 = loc['adm2']
                location_name = loc['name']

                # 直辖区
                if location_adm1 == location_adm2:
                    location = f"{location_adm2}市"
                else:
                    location = f"{location_adm1}{location_adm2}市"
                # 查询城市精确到区级
                if location_name != location_adm2:
                    location += f"{location_name}"

            else:
                dispatcher.utter_message(f"对不起，没有找到指定的城市，{location}。")
                return [AllSlotsReset()]

            # weather_url = "https://devapi.heweather.net/v7/weather/now"
            if time == -1:
                weather_url = "https://devapi.heweather.net/v7/weather/now"
            elif time <= 3:
                weather_url = "https://devapi.heweather.net/v7/weather/3d"
            elif time <= 7:
                weather_url = "https://devapi.heweather.net/v7/weather/7d"
            else:
                weather_url = "https://devapi.heweather.net/v7/weather/7d"

            weather_response = requests.get(weather_url, params={
                "location": location_id,
                "key": key
            }).json()

            if weather_response['code'] != "200":
                dispatcher.utter_message("对不起，天气查询失败。")
                return [AllSlotsReset()]
            else:
                link = weather_response["fxLink"]
                if "now" in weather_response.keys():
                    now = weather_response['now']

                    text = now['text']
                    temp = now['temp']
                    feelsLike = now['feelsLike']
                    windDir = now['windDir']
                    windScale = now['windScale']

                    message = f"{location}现在的天气，天气{text}，气温{temp}摄氏度，" \
                              f"体感温度{feelsLike}摄氏度，{windDir}，风力等级{windScale}级。"

                    dispatcher.utter_message(message, link=link)
                    return [AllSlotsReset()]

                elif "daily" in weather_response.keys():
                    daily = weather_response['daily']
                    if 0 <= time < len(daily) - 1:
                        day = daily[time]

                        fxDate = day['fxDate']
                        tempMax = day['tempMax']
                        tempMin = day['tempMin']
                        textDay = day['textDay']
                        windDirDay = day['windDirDay']
                        windScaleDay = day['windScaleDay']
                        textNight = day['textNight']
                        windDirNight = day['windDirNight']
                        windScaleNight = day['windScaleNight']

                        fxDate_list = fxDate.split("-")
                        fxDate = f"{fxDate_list[0]}年{fxDate_list[1]}月{fxDate_list[2]}日"

                        message = f"{location}{fxDate}的天气，最高温{tempMax}摄氏度，最低温{tempMin}摄氏度。" \
                                  f"日间天气{textDay}，{windDirDay}，风力等级{windScaleDay}级。" \
                                  f"夜间天气{textNight}，{windDirNight}，风力等级{windScaleNight}级。"

                        dispatcher.utter_message(message, link=link)
                        return [AllSlotsReset()]
                    else:
                        for day in daily:
                            fxDate = day['fxDate']
                            tempMax = day['tempMax']
                            tempMin = day['tempMin']
                            textDay = day['textDay']
                            windDirDay = day['windDirDay']
                            windScaleDay = day['windScaleDay']
                            textNight = day['textNight']
                            windDirNight = day['windDirNight']
                            windScaleNight = day['windScaleNight']

                            message = f"{location}{fxDate}的天气，最高温{tempMax}摄氏度，最低温{tempMin}摄氏度。" \
                                      f"日间天气{textDay}，{windDirDay}，风力等级{windScaleDay}级。" \
                                      f"夜间天气{textNight}，{windDirNight}，风力等级{windScaleNight}级。"

                            dispatcher.utter_message(message)
                        dispatcher.utter_message(link=link)
                        return [AllSlotsReset()]
