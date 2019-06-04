# WISPR - Telegram $WSP Tipbot.
 
#### WISPR crypto currency tipbot for [Telegram](https://telegram.org)


## Dependencies 

*  `apt-get install python3`
*  `apt-get install python3-pip`
*  `pip3 install beautifulsoup4`
*  `pip3 install python-telegram-bot --upgrade`

* `ln -ls /wispr/bin/wispr-cli /usr/bin/local/wispr-cli

* In order to run the tip-bot effectively, a Bitcoin-core based client is needed. For this git Wispr-cli is used , but any major alternate crypto-currency client could easily be incorperated. 

## Setup

* Download the git
`git clone https://github.com/tuxcmd/wisprtip-bot`

* Setup a bot with the user @BotFather through PM on Telegram, after going through a setup you will be given a bot token. Edit the command.py file and replace the parameter 'BOT_TOKEN' with the one you just recieved. 

*  Run the script 
`python3 command.py`

*  Initiate the bot by inviting it to a chat or via PM, some commands are `/balance` , `/price` , `/help` and to find out the format related to tip others and withdrawal of funds use `/commands`.

### Setting up the bot as so still leaves the wallet unencrypted, so please go to extra measures to provide extra security. Make sure to have SSH encryption on whatever device/droplet you run it on. 

*  Please fork the code, happy tipping! 



