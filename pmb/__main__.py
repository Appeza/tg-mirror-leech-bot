import os
import shutil, psutil
import signal
import pickle
from pyrogram import idle
from pmb import app
from os import execl, kill, path, remove
from sys import executable
from datetime import datetime
import pytz
import time
from telegram import ParseMode
from telegram import Update
from telegram.ext import CallbackContext, CommandHandler
from pmb import bot, dispatcher, updater, botStartTime, AUTHORIZED_CHATS, IMAGE_URL
from pmb.helper.ext_utils import fs_utils
from pmb.helper.telegram_helper.bot_commands import BotCommands
from pmb.helper.telegram_helper.message_utils import *
from .helper.ext_utils.bot_utils import get_readable_file_size, get_readable_time
from .helper.telegram_helper.filters import CustomFilters
from .helper.config import editor
from .helper.config.subproc import killAll
from .helper.config import sync
from .helper.config.dynamic import configList, DYNAMIC_CONFIG
from .modules import authorize, list, cancel_mirror, mirror_status, mirror, clone, watch, shell, eval, anime, stickers, search, delete, speedtest, usage

from pyrogram import idle
from pmb import app

now=datetime.now(pytz.timezone('Asia/Dhaka'))

def stats(update: Update, context: CallbackContext):
    currentTime = get_readable_time(time.time() - botStartTime)
    current = now.strftime('%Y/%m/%d %I:%M:%S')
    total, used, free = shutil.disk_usage('.')
    total = get_readable_file_size(total)
    used = get_readable_file_size(used)
    free = get_readable_file_size(free)
    sent = get_readable_file_size(psutil.net_io_counters().bytes_sent)
    recv = get_readable_file_size(psutil.net_io_counters().bytes_recv)
    cpuUsage = psutil.cpu_percent(interval=0.5)
    memory = psutil.virtual_memory().percent
    disk = psutil.disk_usage('/').percent
    stats = f'<b>Bot UpTime ⏲:</b> {currentTime}\n\n' \
            f'<b>Start Time 🔊:</b> {current}\n' \
            f'<b>CPU Usage 🖥️:</b> {cpuUsage}%\n' \
            f'<b>RAM Usage 🚀:</b> {memory}%\n' \
            f'<b>DISK Usage 📦:</b> {disk}%\n\n' \
            f'<b>Total Disk Space:</b> {total}\n' \
            f'<b>Used 📦:</b> {used}\n' \
            f'<b>Free 🗂:</b> {free}\n\n' \
            f'<b>📑 Data Usage 📑:</b>\n' \
            f'<b>Upload 📤:</b> {sent}\n' \
            f'<b>Download 📥:</b> {recv}'
    update.effective_message.reply_photo(IMAGE_URL, stats, parse_mode=ParseMode.HTML)


def start(update: Update, context: CallbackContext):
    start_string = f'''
This is a bot which can mirror all your links to Google drive!

👲 Modded By: @ZEUTS

Type /{BotCommands.HelpCommand} to get a list of available commands
'''
    update.effective_message.reply_photo(IMAGE_URL, start_string, parse_mode=ParseMode.MARKDOWN)


def chat_list(update: Update, context: CallbackContext):
    chatlist =''
    chatlist += '\n'.join(str(id) for id in AUTHORIZED_CHATS)
    sendMessage(f'<b>Authorized List:</b>\n{chatlist}\n', context.bot, update)


def repo(update: Update, context: CallbackContext):
    bot.send_message(update.message.chat_id,
    reply_to_message_id=update.message.message_id,
    text="Repo: https://github.com/priiiyo/priiiyo-mirror-bot\nGroup: https://t.me/PriiiyoMirror", disable_web_page_preview=True)


def restart(update, context):
    restart_message = sendMessage("Restarting, Please wait!", context.bot, update)
    # Save restart message ID and chat ID in order to edit it after restarting
    with open(".restartmsg", "w") as f:
        f.truncate(0)
        f.write(f"{restart_message.chat.id}\n{restart_message.message_id}\n")
    fs_utils.clean_all()
    os.execl(executable, executable, "-m", "pmb")


def ping(update: Update, context: CallbackContext):
    start_time = int(round(time.time() * 1000))
    reply = sendMessage("Starting Ping...", context.bot, update)
    end_time = int(round(time.time() * 1000))
    editMessage(f'{end_time - start_time} ms', reply)


def log(update: Update, context: CallbackContext):
    sendLogFile(context.bot, update)


def bot_help(update: Update, context: CallbackContext):
    help_string = f'''
/{BotCommands.HelpCommand}: To get this message

/{BotCommands.MirrorCommand} [download_url][magnet_link]: Start mirroring the link to google drive

/{BotCommands.UnzipMirrorCommand} [download_url][magnet_link]: Starts mirroring and if downloaded file is any archive, extracts it to google drive

/{BotCommands.TarMirrorCommand} [download_url][magnet_link]: Start mirroring and upload the archived (.tar) version of the download

/{BotCommands.CloneCommand}: Copy file/folder to google drive

/{BotCommands.WatchCommand} [youtube-dl supported link]: Mirror through youtube-dl. Click /{BotCommands.WatchCommand} for more help.

/{BotCommands.TarWatchCommand} [youtube-dl supported link]: Mirror through youtube-dl and tar before uploading

/{BotCommands.CancelMirror}: Reply to the message by which the download was initiated and that download will be cancelled

/{BotCommands.StatusCommand}: Shows a status of all the downloads

/{BotCommands.ListCommand} [search term]: Searches the search term in the Google drive, if found replies with the link

/{BotCommands.StatsCommand}: Show Stats of the machine the bot is hosted on

/{BotCommands.AuthorizeCommand}: Authorize a chat or a user to use the bot (Can only be invoked by owner of the bot)

/{BotCommands.AuthListCommand}: See Authorized list (Can only be invoked by owner of the bot)

/{BotCommands.LogCommand}: Get a log file of the bot. Handy for getting crash reports

/{BotCommands.UsageCommand}: To see Heroku Dyno Stats (Owner only).

/{BotCommands.SpeedCommand}: Check Internet Speed of the Host

/{BotCommands.RepoCommand}: Get the bot repo.

/tshelp: Get help for torrent search module.

/weebhelp: Get help for anime, manga and character module.

/stickerhelp: Get help for stickers module.
'''
    sendMessage(help_string, context.bot, update)


def main():
    fs_utils.start_cleanup()
    # Check if the bot is restarting
    if os.path.isfile(".restartmsg"):
        with open(".restartmsg") as f:
            chat_id, msg_id = map(int, f)
        bot.edit_message_text("Restarted successfully!", chat_id, msg_id)
        os.remove(".restartmsg")
        
    start_handler = CommandHandler(BotCommands.StartCommand, start,
                                   filters=CustomFilters.authorized_chat | CustomFilters.authorized_user, run_async=True)
    ping_handler = CommandHandler(BotCommands.PingCommand, ping,
                                  filters=CustomFilters.authorized_chat | CustomFilters.authorized_user, run_async=True)
    restart_handler = CommandHandler(BotCommands.RestartCommand, restart,
                                     filters=CustomFilters.owner_filter, run_async=True)
    help_handler = CommandHandler(BotCommands.HelpCommand,
                                  bot_help, filters=CustomFilters.authorized_chat | CustomFilters.authorized_user, run_async=True)
    stats_handler = CommandHandler(BotCommands.StatsCommand,
                                   stats, filters=CustomFilters.authorized_chat | CustomFilters.authorized_user, run_async=True)
    log_handler = CommandHandler(BotCommands.LogCommand, log, filters=CustomFilters.owner_filter, run_async=True)
    repo_handler = CommandHandler(BotCommands.RepoCommand, repo,
                                   filters=CustomFilters.authorized_chat | CustomFilters.authorized_user, run_async=True)
    authlist_handler = CommandHandler(BotCommands.AuthListCommand, chat_list, filters=CustomFilters.owner_filter, run_async=True)
    config_handler = editor.handler
    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(ping_handler)
    dispatcher.add_handler(restart_handler)
    dispatcher.add_handler(help_handler)
    dispatcher.add_handler(stats_handler)
    dispatcher.add_handler(log_handler)
    dispatcher.add_handler(repo_handler)
    dispatcher.add_handler(authlist_handler)
    dispatcher.add_handler(config_handler)
    updater.start_polling()
    LOGGER.info("Bot Started!")
    signal.signal(signal.SIGINT, fs_utils.exit_clean_up)

app.start()
main()
idle()
