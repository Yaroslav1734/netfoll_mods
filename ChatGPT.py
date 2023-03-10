# meta developer: @netfoll_mods
# requires: openai


import logging


import openai
import openai.error


from datetime import datetime


from telethon.tl.custom import Message


from .. import loader, utils


@loader.tds
class ChatGPTMod(loader.Module):
    """Module for chatting with ChatGPT. Based on OpenAI api."""

    strings = {
        "name": "ChatGPT",
        "processing": "<b>âą Your request is being processed...</b>",
        "where_args?": "<b>đĢ Specify arguments!</b>",
        "set_token": "<b>đĢ Set token in config!</b>",
        "incorrect_token": "<b>đĢ You specified incorrect token in config!</b>",
        "unknown_openai_error": "<b>đĢ An OpenAI related error has occurred!</b>\n<code>{}: {}</code>",
        "unknown_error": "<b>đĢ An unknown error occurred!</b>\n<code>{}: {}</code>",
        "result": (
            "<b>â Your question: </b><code>{}</code>"
            "\n\n<b>đđŧââī¸ ChatGPT answer: </b><code>{}</code>"
        ),
        "debug_result": (
            "<b>â Your question: </b><code>{}</code>"
            "\n\n<b>đđŧââī¸ ChatGPT answer: </b><code>{}</code>"
            "\n\n<b>âšī¸ Used tokens: </b><code>{}</code>"
        ),
        "edit_result": (
            "<b>â Original text: </b><code>{}</code>"
            "\n\n<b>âī¸ Corrected text: </b><code>{}</code>"
        ),
        "edit_debug_result": (
            "<b>â Original text: </b><code>{}</code>"
            "\n\n<b>âī¸ Corrected text: </b><code>{}</code>"
            "\n\n<b>âšī¸ Used tokens: </b><code>{}</code>"
        ),
        "edit_code_result": (
            "<b>â Original code: </b><code>{}</code>"
            "\n\n<b>âī¸ Corrected code: </b><code>{}</code>"
        ),
        "edit_code_debug_result": (
            "<b>â Original code: </b><code>{}</code>"
            "\n\n<b>âī¸ Corrected code: </b><code>{}</code>"
            "\n\n<b>âšī¸ Used tokens: </b><code>{}</code>"
        ),
        "_cfg_doc_debug_info": "Whether information about used tokens will be shown",
        "_cfg_doc_openai_token": "OpenAI API token",
    }

    strings_ru = {
        "where_args?": "<b>đĢ ĐŖĐēĐ°ĐļĐ¸ Đ°ŅĐŗŅĐŧĐĩĐŊŅŅ!</b>",
        "set_token": "<b>đĢ ĐĐžŅŅĐ°Đ˛Ņ ŅĐžĐēĐĩĐŊ Đ˛ ĐēĐžĐŊŅĐ¸ĐŗĐĩ!</b>",
        "incorrect_token": "<b>đĢ ĐĸŅ ŅĐēĐ°ĐˇĐ°Đģ ĐŊĐĩĐ˛ĐĩŅĐŊŅĐš ŅĐžĐēĐĩĐŊ Đ˛ ĐēĐžĐŊŅĐ¸ĐŗĐĩ!</b>",
        "unknown_openai_error": "<b>đĢ ĐŅĐžĐ¸ĐˇĐžŅĐģĐ° ĐžŅĐ¸ĐąĐēĐ° ŅĐ˛ŅĐˇĐ°ĐŊĐŊĐ°Ņ Ņ OpenAI!</b>\n<code>{}: {}</code>",
        "unknown_error": "<b>đĢ ĐŅĐžĐ¸ĐˇĐžŅĐģĐ° ĐŊĐĩĐ¸ĐˇĐ˛ĐĩŅŅĐŊĐ°Ņ ĐžŅĐ¸ĐąĐēĐ°!</b>\n<code>{}: {}</code>",
        "processing": "<b>âą ĐĸĐ˛ĐžĐš ĐˇĐ°ĐŋŅĐžŅ ĐžĐąŅĐ°ĐąĐ°ŅŅĐ˛Đ°ĐĩŅŅŅ...</b>",
        "result": (
            "<b>â ĐĸĐ˛ĐžĐš Đ˛ĐžĐŋŅĐžŅ: </b><code>{}</code>"
            "\n\n<b>đđŧââī¸ ĐŅĐ˛ĐĩŅ ChatGPT: </b><code>{}</code>"
        ),
        "debug_result": (
            "<b>â ĐĸĐ˛ĐžĐš Đ˛ĐžĐŋŅĐžŅ: </b><code>{}</code>"
            "\n\n<b>đđŧââī¸ ĐŅĐ˛ĐĩŅ ChatGPT: </b><code>{}</code>"
            "\n\n<b>âšī¸ ĐŅĐŋĐžĐģŅĐˇĐžĐ˛Đ°ĐŊĐž ŅĐžĐēĐĩĐŊĐžĐ˛: </b><code>{}</code>"
        ),
        "edit_result": (
            "<b>â ĐŅĐ¸ĐŗĐ¸ĐŊĐ°ĐģŅĐŊŅĐš ŅĐĩĐēŅŅ: </b><code>{}</code>"
            "\n\n<b>âī¸ ĐŅĐŋŅĐ°Đ˛ĐģĐĩĐŊĐŊŅĐš ŅĐĩĐēŅŅ: </b><code>{}</code>"
        ),
        "edit_debug_result": (
            "<b>â ĐŅĐ¸ĐŗĐ¸ĐŊĐ°ĐģŅĐŊŅĐš ŅĐĩĐēŅŅ: </b><code>{}</code>"
            "\n\n<b>âī¸ ĐŅĐŋŅĐ°Đ˛ĐģĐĩĐŊĐŊŅĐš ŅĐĩĐēŅŅ: </b><code>{}</code>"
            "\n\n<b>âšī¸ ĐŅĐŋĐžĐģŅĐˇĐžĐ˛Đ°ĐŊĐž ŅĐžĐēĐĩĐŊĐžĐ˛: </b><code>{}</code>"
        ),
        "edit_code_result": (
            "<b>â ĐŅĐ¸ĐŗĐ¸ĐŊĐ°ĐģŅĐŊŅĐš ĐēĐžĐ´: </b><code>{}</code>"
            "\n\n<b>âī¸ ĐŅĐŋŅĐ°Đ˛ĐģĐĩĐŊĐŊŅĐš ĐēĐžĐ´: </b><code>{}</code>"
        ),
        "edit_code_debug_result": (
            "<b>â ĐŅĐ¸ĐŗĐ¸ĐŊĐ°ĐģŅĐŊŅĐš ĐēĐžĐ´: </b><code>{}</code>"
            "\n\n<b>âī¸ ĐŅĐŋŅĐ°Đ˛ĐģĐĩĐŊĐŊŅĐš ĐēĐžĐ´: </b><code>{}</code>"
            "\n\n<b>âšī¸ ĐŅĐŋĐžĐģŅĐˇĐžĐ˛Đ°ĐŊĐž ŅĐžĐēĐĩĐŊĐžĐ˛: </b><code>{}</code>"
        ),
        "_cfg_doc_debug_info": "ĐŅĐ´ĐĩŅ ĐģĐ¸ ĐŋĐžĐēĐ°ĐˇŅĐ˛Đ°ŅŅŅŅ Đ¸ĐŊŅĐžŅĐŧĐ°ŅĐ¸Ņ ĐžĐą Đ¸ŅĐŋĐžĐģŅĐˇĐžĐ˛Đ°ĐŊĐŊŅŅ ŅĐžĐēĐĩĐŊĐ°Ņ",
        "_cfg_doc_openai_token": "ĐĸĐžĐēĐĩĐŊ OpenAI API",
        "_cls_doc": "ĐĐžĐ´ŅĐģŅ Đ´ĐģŅ ĐžĐąŅĐĩĐŊĐ¸Ņ Ņ ChatGPT. ĐŅĐŊĐžĐ˛Đ°ĐŊ ĐŊĐ° OpenAI API.",
        "_cmd_doc_chatgpt": "ĐĄĐŋŅĐžŅĐ¸ŅŅ ChatGPT Đž ŅŅĐŧ-ĐŊĐ¸ĐąŅĐ´Ņ. Đ Đ°ŅĐŗŅĐŧĐĩĐŊŅĐ°Ņ ŅĐēĐ°ĐļĐ¸ ŅĐ˛ĐžĐš Đ˛ĐžĐŋŅĐžŅ.",
        "_cmd_doc_edits": "ĐŅĐŋŅĐ°Đ˛Ņ ĐžŅŅĐžĐŗŅĐ°ŅĐ¸ŅĐĩŅĐēĐ¸Đĩ ĐžŅĐ¸ĐąĐēĐ¸ Đ˛ ŅĐ˛ĐžŅĐŧ ŅĐĩĐēŅŅĐĩ.",
        "_cmd_doc_editscode": "ĐŅĐŋŅĐ°Đ˛Ņ ĐžŅĐ¸ĐąĐēĐ¸ Đ˛ ŅĐ˛ĐžŅĐŧ ĐēĐžĐ´Đĩ",
    }

    def __init__(self):
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "openai_token",
                None,
                lambda: self.strings["_cfg_doc_openai_token"],
                validator=loader.validators.Hidden(),
            ),
            loader.ConfigValue(
                "debug_info",
                False,
                lambda: self.strings["_cfg_doc_debug_info"],
                validator=loader.validators.Boolean(),
            ),
        )

    async def client_ready(self, _, __):
        logging.getLogger("openai").propagate = False
        # ĐŊĐĩ ŅĐžŅŅ Đ˛Đ°Đŧ ĐģĐžĐŗĐ¸ ĐˇĐ°ĐąĐ¸Đ˛Đ°ŅŅ

    async def chatgptcmd(self, message: Message) -> None:
        """Ask ChatGPT about something. Specify your question in arguments."""

        args = utils.get_args_raw(message)
        if not args:
            await utils.answer(message, self.strings["where_args?"])
            return

        await utils.answer(message, self.strings["processing"])

        openai.api_key = self.config["openai_token"]

        try:
            day = datetime.today().day
            month = datetime.today().month
            year = datetime.today().year

            json_result = await openai.ChatCompletion.acreate(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "Hello. You are ChatGPT, a large language model trained by OpenAI."
                            "Answer as concisely as possible."
                            "Current date: {} {} {}"
                        ).format(day, month, year),
                    },
                    {
                        "role": "user",
                        "content": args,
                    },
                ],
            )
            answer = json_result["choices"][0]["message"]["content"]
            tokens = json_result["usage"]["total_tokens"]

        except Exception as e:
            if isinstance(e, openai.error.AuthenticationError):
                if str(e).startswith("No API key provided"):
                    await utils.answer(message, self.strings["set_token"])
                    return

                elif str(e).startswith("Incorrect API key provided"):
                    await utils.answer(message, self.strings["incorrect_token"])
                    return

                else:
                    await utils.answer(
                        message,
                        self.strings["unknown_openai_error"].format(
                            e.__class__.__name__,
                            utils.escape_html(str(e)),
                        ),
                    )
                    return
            else:
                await utils.answer(
                    message,
                    self.strings["unknown_error"].format(
                        e.__class__.__name__,
                        utils.escape_html(str(e)),
                    ),
                )
                return

        await utils.answer(
            message,
            self.strings["result"].format(
                utils.escape_html(args),
                utils.escape_html(answer),
            )
            if not self.config["debug_info"]
            else self.strings["debug_result"].format(
                utils.escape_html(args), utils.escape_html(answer), tokens
            ),
        )
        openai.api_key = None

    async def editscmd(self, message: Message):
        """Correct spelling errors in your text."""

        args = utils.get_args_raw(message)
        if not args:
            await utils.answer(message, self.strings["where_args?"])
            return

        await utils.answer(message, self.strings["processing"])

        openai.api_key = self.config["openai_token"]

        try:
            json_result = await openai.Edit.acreate(
                model="text-davinci-edit-001",
                input=args,
                instruction="Fix the spelling mistakes.",
            )

            result = json_result["choices"][0]["text"]
            tokens = json_result["usage"]["total_tokens"]
        except Exception as e:
            if isinstance(e, openai.error.AuthenticationError):
                if str(e).startswith("No API key provided"):
                    await utils.answer(message, self.strings["set_token"])
                    return

                elif str(e).startswith("Incorrect API key provided"):
                    await utils.answer(message, self.strings["incorrect_token"])
                    return

                else:
                    await utils.answer(
                        message,
                        self.strings["unknown_openai_error"].format(
                            e.__class__.__name__,
                            utils.escape_html(str(e)),
                        ),
                    )
                    return
            else:
                await utils.answer(
                    message,
                    self.strings["unknown_error"].format(
                        e.__class__.__name__,
                        utils.escape_html(str(e)),
                    ),
                )
                return

        await utils.answer(
            message,
            self.strings["edit_result"].format(
                utils.escape_html(args),
                utils.escape_html(result),
            )
            if not self.config["debug_info"]
            else self.strings["edit_debug_result"].format(
                utils.escape_html(args),
                utils.escape_html(result),
                tokens,
            ),
        )

        openai.api_key = None

    async def editscodecmd(self, message: Message):
        """Correct errors in your code."""

        args = utils.get_args_raw(message)
        if not args:
            await utils.answer(message, self.strings["where_args?"])
            return

        await utils.answer(message, self.strings["processing"])

        openai.api_key = self.config["openai_token"]

        try:
            json_result = await openai.Edit.acreate(
                model="code-davinci-edit-001",
                input=args,
                instruction="Fix errors in this code.",
            )

            result = json_result["choices"][0]["text"]
            tokens = json_result["usage"]["total_tokens"]
        except Exception as e:
            if isinstance(e, openai.error.AuthenticationError):
                if str(e).startswith("No API key provided"):
                    await utils.answer(message, self.strings["set_token"])
                    return

                elif str(e).startswith("Incorrect API key provided"):
                    await utils.answer(message, self.strings["incorrect_token"])
                    return

                else:
                    await utils.answer(
                        message,
                        self.strings["unknown_openai_error"].format(
                            e.__class__.__name__,
                            utils.escape_html(str(e)),
                        ),
                    )
                    return
            else:
                await utils.answer(
                    message,
                    self.strings["unknown_error"].format(
                        e.__class__.__name__,
                        utils.escape_html(str(e)),
                    ),
                )
                return

        await utils.answer(
            message,
            self.strings["edit_code_result"].format(
                utils.escape_html(args),
                utils.escape_html(result),
            )
            if not self.config["debug_info"]
            else self.strings["edit_code_debug_result"].format(
                utils.escape_html(args),
                utils.escape_html(result),
                tokens,
            ),
        )
