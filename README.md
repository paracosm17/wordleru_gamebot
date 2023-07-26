# Wordleru_gamebot
The implementation of the Wordle game in the form of a telegram bot

![Project Logo (if available)](https://telegra.ph/file/065d70a029f7cee685d88.jpg)

## Description
This project is an implementation of the Wordle game. Two game modes are provided: with 5 letters per word and with 6 letters. The working version of the bot is here [@wordleru_gamebot](https://t.me/wordleru_gamebot). Letters are displayed using the inline keyboard. Emoticons 🟢 and 🟠 are used to highlight the letters in green and yellow.

## Installation

Use the [docker](https://www.docker.com/) and [docker-compose](https://docs.docker.com/compose/) to deploy the project.

```bash
git clone https://github.com/paracosm17/wordleru_gamebot.git
cd wordleru_gamebot
sudo docker-compose up
```
##### Don't forget to edit the `.env.example` file and rename it to `.env`
Also, if you plan to use a Postgre database or webhooks, you need to edit the `docker-compose.yml`, `bot.py` and `tgbot\config.py` files

## Authors
[paracosm17](https://github.com/paracosm17)

## License
[Apache-2.0](https://www.apache.org/licenses/LICENSE-2.0)