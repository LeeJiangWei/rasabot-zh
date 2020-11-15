# Rasabot-Zh
Simple dialogue, song search, weather query

## Rasa version
`Rasa 2.0.0` <br>

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
