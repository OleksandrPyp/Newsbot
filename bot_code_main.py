from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, ConversationHandler, MessageHandler, filters
import re
import logging
import httpx
from database_file import *
import os
from dotenv import load_dotenv

load_dotenv()
tg_token = os.getenv("TOKEN")
news_api_token = os.getenv("news_api_token")

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

SEARCH_QUERY = 1


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hi! Thanks for reaching out! Type /help to see what I can do")
    command = 'start'
    chat_id = update.message.chat_id
    user_id = update.message.from_user.id
    user = update.message.from_user
    create_interaction(chat_id, command, None, user_id, user.username, user.first_name, user.last_name,
                       user.language_code)


def get_usage() -> str:
    return f'''This bot allows you to query news articles from Datanews API.

Available commands:
/start - shows the welcome message.
/help - shows this help message.
/search <query> - retrieve news articles containing <query>.
   Example: "/search Capybara?"
/topnews <country> - retrieve top news for provided <country>.
   Example: "/topnews ua"
/listofcountries - shows the list of available countries.
   Example: "/listofcountries ua, us, de, es etc"
/cancel - cancel the search process.
'''


async def process_news_data(update: Update, context: ContextTypes.DEFAULT_TYPE, news_data: dict):
    article_counter = 0

    for article in news_data["articles"]:
        if article_counter >= 3:
            break
        title = article["title"]
        description = article["description"]
        source = article["source"]["name"]
        article_url = article["url"]
        news_message = f"Title: {title}\nSource: {source}\n\n{description}\n\nLink: {article_url}\n"
        await context.bot.send_message(chat_id=update.effective_chat.id, text=news_message)
        article_counter += 1


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_markdown(get_usage())
    command = 'help'
    chat_id = update.message.chat_id
    user_id = update.message.from_user.id
    user = update.message.from_user
    create_interaction(chat_id, command, None, user_id, user.username, user.first_name, user.last_name,
                       user.language_code)


async def search_command_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Please provide a search query or /cancel to cancel.")
    return SEARCH_QUERY


async def search_command_receive_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text.strip()
    user_id = update.message.from_user.id
    user = update.message.from_user
    chat_id = update.message.chat_id

    if query == '/cancel':
        await update.message.reply_text("Search canceled.")
        return ConversationHandler.END

    if not query:
        await update.message.reply_text("Invalid search query. Please provide a query without special characters.")
        return SEARCH_QUERY

    if len(query) < 3:
        await update.message.reply_text("Invalid search query. The query must have at least 3 characters.")
        return SEARCH_QUERY

    if not re.match(r"^[a-zA-Z\s]+$", query):
        await update.message.reply_text(
            "Invalid search query. Please provide a query without special characters or numbers.")
        return SEARCH_QUERY

    api_key = news_api_token
    url = f"https://newsapi.org/v2/everything?q={query}&apiKey={api_key}"

    async with httpx.AsyncClient() as client:
        response = await client.get(url)

        if response.status_code == 200:
            news_data = response.json()
            if "articles" in news_data and len(news_data["articles"]) > 0:
                await process_news_data(update, context, news_data)
            else:
                await context.bot.send_message(chat_id=update.effective_chat.id,
                                               text="There are no news for the provided query, please try again")

    command = 'search'
    create_interaction(chat_id, command, query, user_id, user.username, user.first_name, user.last_name, user.language_code)

    return ConversationHandler.END


async def top_news_command_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Please provide a country code or /cancel to cancel.")
    return SEARCH_QUERY


async def top_news_command_receive_country(update: Update, context: ContextTypes.DEFAULT_TYPE):
    country = update.message.text.strip().lower()
    user_id = update.message.from_user.id
    user = update.message.from_user
    chat_id = update.message.chat_id

    if country == '/cancel':
        await update.message.reply_text("Top news retrieval canceled.")
        return ConversationHandler.END

    supported_countries = [
        "ae", "ar", "at", "au", "be", "bg", "br", "ca", "ch", "cn", "co", "cu", "cz", "de", "eg", "fr",
        "gb", "gr", "hk", "hu", "id", "ie", "il", "in", "it", "jp", "kr", "lt", "lv", "ma", "mx", "my",
        "ng", "nl", "no", "nz", "ph", "pl", "pt", "ro", "rs", "ru", "sa", "se", "sg", "si", "sk", "th",
        "tr", "tw", "ua", "us", "ve", "za"
    ]
    if country not in supported_countries:
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text="Invalid country code. Please provide a supported country.")
        return SEARCH_QUERY

    if country == "ru":
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text="This Bot doesn't consider any news from Mordor interesting. The only "
                                            "interesting news about this so called country we will find out "
                                            "anyway")
        return SEARCH_QUERY

    if not re.match(r"^[a-zA-Z]+$", country):
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text="Invalid country code. Please provide a country code without special "
                                            "characters or numbers.")
        return SEARCH_QUERY

    api_key = news_api_token
    url = f"https://newsapi.org/v2/top-headlines?country={country}&apiKey={api_key}"

    async with httpx.AsyncClient() as client:
        response = await client.get(url)

        if response.status_code == 200:
            news_data = response.json()
            if "articles" in news_data and len(news_data["articles"]) > 0:
                await process_news_data(update, context, news_data)
            else:
                await context.bot.send_message(chat_id=update.effective_chat.id,
                                               text="Sorry, something went wrong. Please try again later.")

    command = 'topnews'
    create_interaction(chat_id, command, country, user_id, user.username, user.first_name, user.last_name,
                       user.language_code)

    return ConversationHandler.END


async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Operation canceled.")
    return ConversationHandler.END


async def list_countries_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    supported_countries = [
        "ae", "ar", "at", "au", "be", "bg", "br", "ca", "ch", "cn", "co", "cu", "cz", "de", "eg", "fr",
        "gb", "gr", "hk", "hu", "id", "ie", "il", "in", "it", "jp", "kr", "lt", "lv", "ma", "mx", "my",
        "ng", "nl", "no", "nz", "ph", "pl", "pt", "ro", "rs", "ru", "sa", "se", "sg", "si", "sk", "th",
        "tr", "tw", "ua", "us", "ve", "za"
    ]

    countries_message = "Available countries for top news:\n"
    countries_message += "\n".join(supported_countries)

    await update.message.reply_text(countries_message)


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.text.startswith('/'):
        await update.message.reply_text("I'm sorry, I didn't understand that command.")
        return


async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f"Update {update} caused error {context.error}")


if __name__ == "__main__":
    print("Starting the bot...")
    app = Application.builder().token(tg_token).build()

    # Commands
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("list_of_countries", list_countries_command))

    # Conversation handlers for Search&Topnews
    search_command_handler = ConversationHandler(
        entry_points=[CommandHandler('search', search_command_start)],
        states={
            SEARCH_QUERY: [MessageHandler(filters.TEXT, search_command_receive_query)]
        },
        fallbacks=[CommandHandler('cancel', cancel_command)],
    )
    app.add_handler(search_command_handler)

    top_news_command_handler = ConversationHandler(
        entry_points=[CommandHandler('topnews', top_news_command_start)],
        states={
            SEARCH_QUERY: [MessageHandler(filters.TEXT, top_news_command_receive_country)]
        },
        fallbacks=[CommandHandler('cancel', cancel_command)],
    )
    app.add_handler(top_news_command_handler)

    # Messages
    app.add_handler(MessageHandler(filters.TEXT, handle_message))

    # Errors
    app.add_error_handler(error)

    print("Looking for new messages...")
    app.run_polling(poll_interval=3)

