# Activity Hunter
```
usage: ActivityHunter.py [-h] --target-user TARGET_USER --from-users
                         FROM_USERS [FROM_USERS ...] [--login-name LOGIN_NAME]
                         [--login-password LOGIN_PASSWORD] [--likes] [--tags]
                         [--comments] [--popularity POPULARITY]
                         [--from-time FROM_TIME] [--to-time TO_TIME]

---Activity Hunter--- Track and collect a users activity on Instagram

optional arguments:
  -h, --help            show this help message and exit
  --target-user TARGET_USER
                        <Required> Track this users activity activity
  --from-users FROM_USERS [FROM_USERS ...], --from_users FROM_USERS [FROM_USERS ...]
                        <Required> Track activity on these accounts, separated
                        with space
  --login-name LOGIN_NAME, --login_name LOGIN_NAME
                        Login name (required if user acc is private)
  --login-password LOGIN_PASSWORD, --login_pw LOGIN_PASSWORD
                        Login password (required if user acc is private)
  --likes               track likes by target
  --tags                track tags in media of target
  --comments            track comments by target
  --popularity POPULARITY
                        Set limit to amount of likes on media (recommended)
  --from-time FROM_TIME, --from_time FROM_TIME
                        check media after date uploaded, d/m/Y format
  --to-time TO_TIME, --to_time TO_TIME
                        check media before date, d/m/Y format
```

example
-------
```
$ python3 ActivityHunter.py --from-users kimkardashian --target khloekardashian --likes --comments --tags
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

```
