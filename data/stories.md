## play song happy path
* play_song{"song_title":"something", "artist":"someone"}
  - utter_confirm_song
  - action_search_song
  
## play song with title
* play_song{"song_title":"something"}
  - utter_ask_artist_with_song_title
* inform{"artist":"someone"}
  - utter_confirm_song
  - action_search_song

## play song with artist
* play_song{"artist":"someone"}
  - utter_ask_song_title_with_artist
* inform{"song_title":"something"}
  - utter_confirm_song
  - action_search_song
  
## play song randomly
* play_song
  - utter_ask_random_title
* affirm
  - action_search_song

## out of scope
* out_of_scope
  - utter_out_of_scope
  
## ask weather
* ask_weather
  - utter_confirm_weather
  - action_search_weather

## happy path
* greet
  - utter_greet
* mood_great
  - utter_happy

## sad path 1
* greet
  - utter_greet
* mood_unhappy
  - utter_cheer_up
  - utter_did_that_help
* affirm
  - utter_happy

## sad path 2
* greet
  - utter_greet
* mood_unhappy
  - utter_cheer_up
  - utter_did_that_help
* deny
  - utter_goodbye

## say goodbye
* goodbye
  - utter_goodbye

## bot challenge
* bot_challenge
  - utter_iamabot
