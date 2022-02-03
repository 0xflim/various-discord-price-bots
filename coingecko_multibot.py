import asyncio
import requests
import tokens  # gitignore dictionary, holds CG API names & Discord API tokens
import time

from discord import Activity, ActivityType, Client, errors
from datetime import datetime as dt

################################################################################
# I keep a gitignore file (tokens.py) which contains a simple dictionary:
#
# Keys represent CoingGecko markets
# CoinGecko ex. --> https://www.coingecko.com/en/coins/<id>.
#
# Values represent Discord API tokens
# Token info here: https://discord.com/developers/docs/topics/oauth2#bots
#
# I store them both in lists here:
################################################################################
MARKET_IDS = list(tokens.tokens_dict.keys())
BOT_TOKENS = list(tokens.tokens_dict.values())
################################################################################

print("\n---------- V4 Flim's Discord x CoinGecko Multibot ----------\n")

################################################################################
# Sanity check for market IDs.
################################################################################
print(f"{dt.utcnow()} | Checking CoinGecko for market IDs.")
print(MARKET_IDS)
print(BOT_TOKENS)
tickers = []

for i in range(len(MARKET_IDS)):
    r = requests.get(f"https://api.coingecko.com/api/v3/coins/{MARKET_IDS[i]}")
    if r.status_code > 400:
        print(f"{dt.utcnow()} | Could not find {MARKET_IDS[i]}. Exiting...\n")
        exit()
    else:
        token_name = r.json()["symbol"].upper()
        print(f"{dt.utcnow()} | Found {token_name}.")
        tickers.append(token_name)
################################################################################
# Start clients.
################################################################################
print(f"{dt.utcnow()} | Starting Discord bot army of {len(MARKET_IDS)}.")
clients = []

for i in range(len(MARKET_IDS)):
    clients.append(Client())
    print(f"{dt.utcnow()} | Started {MARKET_IDS[i]} bot.")
print(clients)
################################################################################
# Client's on_ready event function. We do everything here.
################################################################################
client = clients[i]


@client.event
async def on_ready():
    errored_guilds = []
    print(f"{dt.utcnow()} | Discord client is running.\n")
    while True:
        for i in range(len(clients)):
            try:
                response = requests.get(
                    f"https://api.coingecko.com/api/v3/coins/{MARKET_IDS[i]}"
                )
                price = response.json()["market_data"]["current_price"]["usd"]
                pctchng = response.json()["market_data"][
                    "price_change_percentage_24h_in_currency"
                ]["usd"]
                print(f"{dt.utcnow()} | response status code: {response.status_code}.")
                print(f"{dt.utcnow()} | {tickers[i]} price: {price}.")
                print(f"{dt.utcnow()} | client: {clients[i]}.")
                print(f"{dt.utcnow()} | token: {BOT_TOKENS[i]}.")
                print(
                    f"{dt.utcnow()} | {tickers[i]} 24hr % change: {round(pctchng,2)}%."
                )
                for guild in clients[i].guilds:
                    try:
                        await guild.me.edit(nick=f"{tickers[i]} ${round(price,2):,}")
                        await clients[i].change_presence(
                            activity=Activity(
                                name=f"24h: {round(pctchng,2)}%",
                                type=ActivityType.watching,
                            )
                        )
                    except errors.Forbidden:
                        if guild not in errored_guilds:
                            print(
                                f"{dt.utcnow()} | {guild}:{guild.id} hasn't set "
                                "nickname permissions for the bot!"
                            )
                        errored_guilds.append(guild)
                    except Exception as e:
                        print(f"{dt.utcnow()} | Unknown error: {e}.")
            except ValueError as e:
                print(f"{dt.utcnow()} | ValueError: {e}.")
            except TypeError as e:
                print(f"{dt.utcnow()} | TypeError: {e}.")
            except OSError as e:
                print(f"{dt.utcnow()} | OSError: {e}.")
            except Exception as e:
                print(f"{dt.utcnow()} | Unknown error: {e}.")
            finally:
                await asyncio.sleep(3)


################################################################################
# Run the clients.
################################################################################
loop = asyncio.get_event_loop()
for i in range(len(clients)):
    loop.create_task(clients[i].start(BOT_TOKENS[i]))
loop.run_forever()
################################################################################
