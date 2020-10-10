## play song happy path
* play_song{"song_title":"something", "artist":"someone"}
  - utter_confirm_song
  - action_search_song
  - reset_slots
  
## play song with title
* play_song{"song_title":"something"}
  - utter_confirm_song_title
  - action_search_song
   - reset_slots

## play song with artist
* play_song{"artist":"someone"}
  - utter_confirm_song_artist
  - action_search_song
  - reset_slots

## play song randomly happy
* play_song
  - utter_ask_random_title
* affirm
  - action_search_song
  - reset_slots
  
## play song randomly sad 1
* play_song
  - utter_ask_song
* inform{"song_title":"something"}
  - utter_confirm_song_title
  - action_search_song
  - reset_slots
  
## play song randomly sad 2
* play_song
  - utter_ask_song
* inform{"artist":"someone"}
  - utter_confirm_song_artist
  - action_search_song
  - reset_slots

## direct inform song title
* inform{"song_title":"something"}
  - utter_confirm_song_title
  - action_search_song
  - reset_slots

## direct inform artist
* inform{"artist":"someone"}
  - utter_confirm_song_artist
  - action_search_song
  - reset_slots

## out of scope
* out_of_scope
  - utter_out_of_scope
  
## ask weather
* ask_weather{"location":"somewhere"}
  - action_search_weather
  - reset_slots
  
## ask weather without location
* ask_weather
  - utter_ask_location
* inform{"location":"somewhere"}
  - action_search_weather
  - reset_slots   

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
