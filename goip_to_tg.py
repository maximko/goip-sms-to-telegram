#!/usr/bin/env python3

import aiosmtpd.controller
import email
import re
import base64
from telegram.ext import Updater
import asyncio

class TgSender:
    def __init__(self):
        self.tg_token = "your_tg_bot_token_here"
        self.chat_id = "your_chat_id_here"
        self.updater = Updater(self.tg_token)

    def send(self, chat_id, text):
        self.updater.bot.sendMessage(chat_id=chat_id, text=text)

    async def goip_data_send(self, data):
        if "error" in data:
            self.send(self.chat_id, "Error processing incoming message")
        else:
            message = "%s G%s\n%s" % (data["sender"], data["channel"], data["text"])
            self.send(self.chat_id, message)
    
class GOIPSMTPHandler:
    def __init__(self):
        self.regexp = re.compile("SN:(?P<sn>.+)\s{1}Channel:(?P<channel>[0-9]+)\s{1}Sender:(?P<time>[0-9-:\s]+),(?P<sender>.+?),(?P<text>.*)")
        self.sender = TgSender()

    async def handle_DATA(self, server, session, envelope):
        print("Got a message from goip")
        msg = envelope.content.decode()
        text_b64 = email.message_from_string(msg).get_payload()
        text = base64.b64decode(text_b64).decode()
        result = self.regexp.match(text).groupdict()
        if len(result) > 0:
            data = result
        else:
            data = {"error": True}
        asyncio.create_task(self.sender.goip_data_send(data))
        return '250 OK'

print("Starting service...")

goip_handler = GOIPSMTPHandler()
goip_server = aiosmtpd.controller.Controller(goip_handler, hostname='0.0.0.0', port=25)
goip_server.start()

asyncio.get_event_loop().run_forever()
