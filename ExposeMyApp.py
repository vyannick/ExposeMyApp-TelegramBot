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

    try:

        if ngrok_running:
            update.message.reply_text("Ngrok already running service " + str(ngrok_running))
            return

        service = context.args[0]
        service_object = services.get(service)
        if service_object is None:
            logging.info("Unknown service: " + str(service))
            update.message.reply_text("Unknown service " + str(service))
            return
        service_port = service_object.get("port")
        service_type = service_object.get("type")

        if service_port is None or service_type is None:
            logging.info("Service: " + str(service) + " not well defined")
            update.message.reply_text("Service: " + str(service) + " not well defined")
            return


        service_port = str(service_port)
        service_type = str(service_type)

        logging.info("Running " + service + " on port: " + service_port)
        ngrok_start = subprocess.Popen([ngrok,service_type,service_port],text=True,stderr=subprocess.PIPE,stdout=subprocess.PIPE)
    
        if ngrok_start.poll() != None:
            update.message.reply_text("Ngrok failed to start app " + str(service) + ":\n " + str(ngrok_start.communicate()))
            return

        logging.info("Ngrok started")
        ngrok_running = service

        return_active_ngrok_url(update,service=service)
    except Exception as e:
        update.message.reply_text("An error occured")
        logging.error(e)

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
            logging.error(e)
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
            logging.error(str(e))
            logging.error(ngrok_url_request.json())

            if attempts < 3:
                return_active_ngrok_url(update,service=ngrok_running,attempts=attempts+1)
            else:
                update.message.reply_text("Couldn't retrieve ngrok URL:\n " + str(e))
        else:
            update.message.reply_text("You are exposing " + str(service) + " on URL:\n " + str(ngrok_url))


def stop_ngrok():
    global ngrok_running
    subprocess.run(["pkill", "ngrok"])
    ngrok_running = False
    logging.info("Ngrok stopped")

def stop(update,context):
    if ngrok_running:
        return_active_ngrok_url(update)
        stop_ngrok()
        update.message.reply_text("Ngrok stopped")
    else:
        update.message.reply_text("Ngrok not active")

def unknown_command():
    update.message.reply_text("Unknown command")
    logging.info("Unknown command received")
    return

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
        dispatcher.add_handler(telegram.ext.MessageHandler(telegram.ext.Filters.all, unknown_command))
        updater.start_polling()
        updater.idle()
    else:
        logging.error("No API_KEY and/or SERVICES_FILE and/or NGROK_BINARY in environment")
        sys.exit(0)

if __name__ == '__main__':
    main()



