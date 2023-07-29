<div align="center">

  # ☁️ Cloudy

  <sub>A simple & basic Discord API wrapper built on top of [nextcore](https://github.com/nextsnake/nextcore).</sub>

</div>

> *Cloudy is a Discord API wrapper I decided to make because I wanted to escape the harsh reality of working on my Discord bot framework [Goldy Bot V5](https://github.com/Goldy-Bot/Goldy-Bot-V5).*

> ### ⚠️ Work in progress...

## *WHAT DA HELL! WHAT IS WRONG WITH YOU PYTHON DEVELOPERS? ANOTHER FU#KING DISCORD API WRAPPER!!!*
Yes, another fu#king python Discord API wrapper; but *let me 🍲cook this time...*

- **Quick to script.** Cloudy is built for quick write-ups, before you know it you essentially have a functioning bot.
- **The Design is Very Human!** Even a script kiddy would know what they're doing.
- **Lightweight,** I try to keep the codebase as lite and least complex as possible, mostly for maintainability reasons.
- **Fast as fu#k!** Yeah *totally* all because of my hard work. [~~nextcore~~](https://github.com/nextsnake/nextcore)
- **Touch the low-end even harder!!! 😳** *wait what...* alright this is getting out of hand now...

*ANYWAYS, here's some code:*

```python
from cloudy.impl import Bot, Droplet

bot = Bot()

@bot.command()
async def ping(droplet: Droplet):
    await droplet.send("Pong!")

bot.run()
```

<div align="center">

  <img src="./assets/pong.png">

</div>

> #### Hate it? ~~Skill issue.~~

### Where do I pass my bot token?
Cloudy by default uses the ``BOT_TOKEN`` environment variable so we recommend using ``.env`` files to store your bot token and other sensitive information.

Just create a file named ``.env`` and enter your bot token like so:
```env
BOT_TOKEN="..."
```
*~~"you can pass it in bot class"~~*
