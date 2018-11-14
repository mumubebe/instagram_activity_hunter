# Instagram Activity Hunter

Tool to collect a user's activities (comments, likes, tags) on other users profiles

usage
-----
```
usage: ActivityHunter.py -t <username_to_track> -f <from_usernames> [options]

optional arguments:
  -h, --help            show this help message and exit
  -t TARGET_USER, --target-user TARGET_USER
                        This is the user' activity to track
  -f FROM_USERS [FROM_USERS ...], --from_users FROM_USERS [FROM_USERS ...]
                        Track activity on these users profiles, separated with
                        space: (ex. -f user1 user2 user3)
  --login-name LOGIN_NAME, --login_name LOGIN_NAME
                        Login name (required if user acc is private)
  --login-password LOGIN_PASSWORD, --login_pw LOGIN_PASSWORD
                        Login password (required if user acc is private)
  --likes               track likes by target
  --tags                track tags in media of target
  --comments            track comments by target
  --popularity POPULARITY
                        Set limit to amount of likes on media to track
                        (recommended)
  --from-time FROM_TIME, --from_time FROM_TIME
                        check media after date uploaded, d/m/Y format (ex.
                        --from-time 22/3/2018 will only check media after this
                        date)
  --to-time TO_TIME, --to_time TO_TIME
                        check media before date, d/m/Y format (ex. --to-time
                        22/3/2018 will only check media before this date)
```

example
-------
Collect all of kimkardashian's likes on khloekardashian profile:
```
$ python3 ActivityHunter.py -f kimkardashian -t khloekardashian --likes
```
output:
```
Scraping activity...
--------------------------------------------------------------------------------------------------------------
TARGET NAME         ACTION    ON USER             UPLOAD TIME  MEDIA URL                   ACTION CONTENT      
--------------------------------------------------------------------------------------------------------------
khloekardashian     like      kimkardashian       11/13/18     instagr.am/p/BqFli4uHUwO                        
khloekardashian     like      kimkardashian       11/11/18     instagr.am/p/Bp7Qkb_HZh7                        
khloekardashian     like      kimkardashian       11/09/18     instagr.am/p/Bp3BB7MHf5C                       
khloekardashian     like      kimkardashian       11/06/18     instagr.am/p/Bp7Qkb_HZh7
....
```
