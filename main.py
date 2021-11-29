from pywebio import start_server
from pywebio.input import *
from pywebio.output import *
from pywebio.session import run_async, run_js

import asyncio

chat_messages = []
online_users = set()

MAX_MESSAGES_COUNT = 50


async def main():
    global chat_messages

    put_markdown("Welcome to zeoBlocks chat")

    msg_box = output()
    put_scrollable(msg_box, height=300, keep_bottom=True)

    nickname = await input("Join", required=True, placeholder="Your name",
                           validate=lambda n: "Change your name!" if n in online_users or n == '' else None)
    online_users.add(nickname)

    chat_messages.append(f"{nickname} welcome!")
    msg_box.append(put_markdown(f"{nickname} welcome!"))

    refresh_task = run_async(refresh_msg(nickname, msg_box))

    while True:
        data = await input_group("New message", [
            input(placeholder="Text", name="msg"),
            actions(name="cmd", buttons=["Send", {'label': "Exit", 'type': 'cancel'}])
        ], validate=lambda m: ('msg', "write your message") if m["cmd"] == "Send" and not m["msg"] else None)

        if data is None:
            break

        msg_box.append(put_markdown(f"{nickname} : {data['msg']}"))
        chat_messages.append((nickname, data['msg']))

    refresh_task.close()

    online_users.remove(nickname)
    toast("Bye!")
    msg_box.append(put_markdown(f"{nickname}, leave from chat"))
    chat_messages.append(f"User {nickname}, leave from chat")

    put_buttons(["restart"], onclick=lambda btn: run_js('window.location.reload'))


async def refresh_msg(nickname, msg_box):
    global chat_messages
    last_index = len(chat_messages)

    while True:
        await asyncio.sleep(1)

        for m in chat_messages[last_index:]:
            if m[0] != nickname:
                msg_box.append(put_markdown(f"{m[0]} : {m[1]}"))

        if len(chat_messages) > MAX_MESSAGES_COUNT:
            chat_messages = chat_messages[len(chat_messages) // 2:]

        last_index = len(chat_messages)


if __name__ == "__main__":
    start_server(main, debug=True, port=8081, cdn=False)
