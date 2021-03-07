# ExposeMyApp TelegramBot

This a python Telegram Bot that allows you to expose your local webapplication at anytime. It uses NGROK to create a tunnel from your local machine to the ngrok servers. The URL that is returned by the bot can be used to reach your application from anywhere you want.

# Use case
I created this service to temporarily open a local application to the internet when I need access to it when not at home. I didn't want to permenantely expose an application because of security risks, port forwarding, SLL certificates, dynamic hostnames,...

# Requirements
[NGROK](https://ngrok.com)
python-telegram-bot library (pip3 install python-telegram-bot)

# Usage

The free tier of ngrok only allows 1 tunnel to be active. 

## Bot commands
- /expose <service_name> Exposes the given service/application
- /stop Stops the active ngrok tunnel

# Configuration

The python application expects the following parameters to be set:
- API_KEY the API key of your telegram bot
- SERVICES_FILE the location of your services file
- NGROK_BINARY The location of the ngrok binary

## Services file

The services file is a json file that maps application names (that you pass to the /expose command) to a local port.
e.g.: 
{
    "secure_app" : "https://localhost:8443",
    "apache" : 8080
}
