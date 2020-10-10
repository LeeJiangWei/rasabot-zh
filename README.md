# rasabot-zh
Simple dialogue & song search

## Rasa version
`Rasa 1.10.11` <br>
P.S. 刚写完没过两个月，就更新了RASA 2.0，真的佛了。

## Profile.json
A profile.json is required. (Not in git)
|Key|Value Example|Usage|
| ---- | ---- | ---- |
|phone|137xxxxxxxx|netease music account|
|password|password|netease music password|
|md5_password (optional)|aqwase5df8h6y7...|md5 hashed password|
|weather_api_key|ed435wqe125yh... |key to use weather api|
- Netease Music API: [NeteaseCloudMusicApi](https://github.com/Binaryify/NeteaseCloudMusicApi)
- Weather API: [和风天气](https://dev.heweather.com/)

## Run Scripts
|Module|Script|Usage|
| ---- | ---- | ---- |
|Rasa chatbot|`rasa run`|dialogue|
|Rasa custom actions|`rasa run actions`|search songs|
|Netease music service|`cd ./music-service` `npm start`|provide songs|
