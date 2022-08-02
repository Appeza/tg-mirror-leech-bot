from telegram.ext import MessageFilter
from telegram import Message
from bot import AUTHORIZED_CHATS, SUDO_USERS, MOD_USERS, OWNER_ID, download_dict, download_dict_lock


class CustomFilters:
    class _OwnerFilter(MessageFilter):
        def filter(self, message: Message):
            return message.from_user.id == OWNER_ID

    owner_filter = _OwnerFilter()

    class _AuthorizedUserFilter(MessageFilter):
        def filter(self, message: Message):
            id = message.from_user.id
            return id in AUTHORIZED_CHATS or id in SUDO_USERS or id == OWNER_ID

    authorized_user = _AuthorizedUserFilter()

    class _AuthorizedChat(MessageFilter):
        def filter(self, message: Message):
            return message.chat.id in AUTHORIZED_CHATS

    authorized_chat = _AuthorizedChat()

    class _SudoUser(MessageFilter):
        def filter(self, message: Message):
            return message.from_user.id in SUDO_USERS

    sudo_user = _SudoUser()

    class _ModUser(MessageFilter):
        def filter(self, message: Message):
            return message.from_user.id in MOD_USERS

    mod_user = _ModUser()

    class _MirrorOwner(MessageFilter):
        def filter(self, message: Message):
            user_id = message.from_user.id
            if user_id == OWNER_ID:
                return True
            args = str(message.text).split(' ')
            if len(args) > 1:
                # Cancelling by gid
                with download_dict_lock:
                    return any(
                        status.gid() == args[1]
                        and (
                            status.message.from_user.id == user_id
                            or status.message.from_user.is_bot
                        )
                        for message_id, status in download_dict.items()
                    )

            elif not message.reply_to_message:
                return True
            # Cancelling by replying to original mirror message
            reply_user = message.reply_to_message.from_user.id
            return reply_user == user_id
    mirror_owner_filter = _MirrorOwner()

    def _owner_query(self):
        return self == OWNER_ID or self in SUDO_USERS
