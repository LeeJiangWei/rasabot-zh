## play song happy path
* play_song{"song_title":"something", "artist":"someone"}
  - utter_reject_song
  
## play song with title
* play_song{"song_title":"something"}
  - utter_reject_song

## play song with artist
* play_song{"artist":"someone"}
  - utter_reject_song
  
## ask object position
* ask_object_position
  - action_response_command
  - reset_slots
  
## ask object color
* ask_object_color
  - action_response_command
  - reset_slots
  
## ask object quantity
* ask_object_quantity
  - action_response_command
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
