# REMI Discord Bot

## Dependencies
```
pip install discord
pip install configparser
pip install dataclasses
pip install python-dateutil
pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib
```

## Troubleshooting

If you accidentally posted the discord and google calendar tokens to github or the internet, they will get revoked and you will need to regen new tokens. Go to the developer [portal](https://discord.com/developers/applications) to generate a new discord token and paste it into the config.ini file. For the calendar, go to the google dev [portal](https://console.cloud.google.com/welcome?project=discord-remi-bot), then navigate to APIs & Services -> credentials -> click on remi-bot-discord and download a new credentials.json file. Delete the token.json file from this directory and run the bot again with the new credentials file. It will ask you to sign in to the soonerroverteam@gmail.com google account and will auto generate a new token.json file for you.