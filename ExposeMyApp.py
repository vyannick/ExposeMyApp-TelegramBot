import telegram
import telegram.ext
import re
import os
import subprocess
import logging
import requests
import time 
import sys
import json

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

ngrok_running = False

def expose(update, context,services,ngrok):
    global ngrok_running

    if ngrok_running:
        update.message.reply_text("Ngrok already running service " + str(ngrok_running))
        return

    service = context.args[0]
    service_port = str(services.get(service))

    if service_port == None:
        update.message.reply_text("Unknown service " + str(service))
        return

    ngrok_start = subprocess.Popen([ngrok,"http",service_port],text=True,stderr=subprocess.PIPE,stdout=subprocess.PIPE)
    
    if ngrok_start.poll() != None:
        update.message.reply_text("Ngrok failed to start app " + str(service) + ":\n " + str(ngrok_start.communicate()))
        return

    print("Ngrok started")
    ngrok_running = service

    return_active_ngrok_url(update,service=service)

def return_active_ngrok_url(update,service=None,attempts=0):
    global ngrok_running

    if service == None:
        service=ngrok_running

    time.sleep (2)
    try:
        ngrok_url_request = requests.get("http://localhost:4040/api/tunnels")
    except requests.exceptions.ConnectionError as e:
        if attempts < 3:
            return_active_ngrok_url(update,service=ngrok_running,attempts=attempts+1)
        else:
            print(e)
            update.message.reply_text("Couldn't retrieve ngrok URL:\n " + str(e.errno))
            stop_ngrok()
            return

    if ngrok_url_request.status_code != 200:
        if attempts < 3:
            return_active_ngrok_url(update,service=ngrok_running,attempts=attempts+1)
        else:
            update.message.reply_text("Couldn't retrieve ngrok URL:\n " + str(ngrok_url.stderr))
    else:
        try:
            ngrok_url = ngrok_url_request.json()["tunnels"][0]["public_url"]
        except Error as e:
            print(str(e))
            print(ngrok_url_request.json())

            if attempts < 3:
                return_active_ngrok_url(update,service=ngrok_running,attempts=attempts+1)
            else:
                update.message.reply_text("Couldn't retrieve ngrok URL:\n " + str(e))
        else:
            update.message.reply_text("You are exposing " + str(service) + " on URL:\n " + str(ngrok_url))


def stop_ngrok():
    global ngrok_running
    subprocess.run(["pkill", "ngrok"]) #TODO finegrained stop
    ngrok_running = False

def stop(update,context):
    if ngrok_running:
        return_active_ngrok_url(update)
        stop_ngrok()
        update.message.reply_text("Ngrok stopped")
    else:
        update.message.reply_text("Ngrok not active")

def main():
    if "API_KEY" in os.environ and "SERVICES_FILE" in os.environ and "NGROK_BINARY" in os.environ:
        API_KEY = str(os.environ['API_KEY'])

        with open( str(os.environ['SERVICES_FILE']), 'r') as services_file:
            services_json =services_file.read()
        services = json.loads(services_json)

        ngrok = str(os.environ['NGROK_BINARY'])

        updater = telegram.ext.Updater(API_KEY)
        dispatcher = updater.dispatcher
        dispatcher.add_handler(telegram.ext.CommandHandler('expose',lambda bot,update : expose(bot,update,services,ngrok)))
        dispatcher.add_handler(telegram.ext.CommandHandler('stop',stop))
        updater.start_polling()
        updater.idle()
    else:
        print("No API_KEY and/or SERVICES_FILE and/or NGROK_BINARY in environment")
        sys.exit(0)

if __name__ == '__main__':
    main()


