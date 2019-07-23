# WISPR - Telegram $WSP Tipbot.
 
#### WISPR crypto currency tipbot for [Telegram](https://telegram.org)


## Dependencies 

*  `apt-get install python3`
*  `apt-get install python3-pip`
*  `pip3 install python-telegram-bot --upgrade`

* Setup ufw firewall to only allow the connectivity between the Wispr Wallet * The network, all other ports can be forced to be down.

* In order to run the tip-bot effectively, a Bitcoin-core based client is needed. For this git Wispr-cli is used , but any major alternate crypto-currency client could easily be incorporated. 

## Setup

* Download the repo from git

* Rename the config.json.example to config.json and change the values in it to match Your needs.
#### Configuration
* Setup a bot with the user @BotFather through PM on Telegram, after going through a setup you will be given a bot token.

"COINMARKETCAP_CACHE_UPDATE_INTERVAL" is timer which defines how often should the coin data cache be updated.
Time is in seconds and default value 180 equals 3m.

"CHAT_ACTIVITY_TIME" is timer for which to check users activity when rain command is used.
Time is in seconds and default value 28800 equals 8h. So if user was last active more than 8 hours ago then the user won't receive anything from the rain.
#### Running the bot
* Run the script:

`python3 main.py &' 
 
or use some proper process manager to run the python3 script, just running it as a background process with the & on the end worked for 1.5 years- 0 downtime ;)

* Initiate the bot by inviting it to a chat or via PM and start the bot. To find out the format related to tip others and withdrawal of funds use `/commands`.
* For rain to work as intended, You have to disable privacy mode @botFather. This will enable user message tracking.

### Setting up the bot as so still leaves the wallet unencrypted, so please go to extra measures to provide extra security. Make sure to have SSH encryption on whatever device/droplet you run it on. 

Any improvements or adjustments, just issue pull requests! 
Would be appreciated! 



