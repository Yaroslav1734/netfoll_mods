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
        "processing": "<b>⏱ Your request is being processed...</b>",
        "where_args?": "<b>🚫 Specify arguments!</b>",
        "set_token": "<b>🚫 Set token in config!</b>",
        "incorrect_token": "<b>🚫 You specified incorrect token in config!</b>",
        "unknown_openai_error": "<b>🚫 An OpenAI related error has occurred!</b>\n<code>{}: {}</code>",
        "unknown_error": "<b>🚫 An unknown error occurred!</b>\n<code>{}: {}</code>",
        "result": (
            "<b>❓ Your question: </b><code>{}</code>"
            "\n\n<b>🙋🏼‍♂️ ChatGPT answer: </b><code>{}</code>"
        ),
        "debug_result": (
            "<b>❓ Your question: </b><code>{}</code>"
            "\n\n<b>🙋🏼‍♂️ ChatGPT answer: </b><code>{}</code>"
            "\n\n<b>ℹ️ Used tokens: </b><code>{}</code>"
        ),
        "edit_result": (
            "<b>❌ Original text: </b><code>{}</code>"
            "\n\n<b>✔️ Corrected text: </b><code>{}</code>"
        ),
        "edit_debug_result": (
            "<b>❌ Original text: </b><code>{}</code>"
            "\n\n<b>✔️ Corrected text: </b><code>{}</code>"
            "\n\n<b>ℹ️ Used tokens: </b><code>{}</code>"
        ),
        "edit_code_result": (
            "<b>❌ Original code: </b><code>{}</code>"
            "\n\n<b>✔️ Corrected code: </b><code>{}</code>"
        ),
        "edit_code_debug_result": (
            "<b>❌ Original code: </b><code>{}</code>"
            "\n\n<b>✔️ Corrected code: </b><code>{}</code>"
            "\n\n<b>ℹ️ Used tokens: </b><code>{}</code>"
        ),
        "_cfg_doc_debug_info": "Whether information about used tokens will be shown",
        "_cfg_doc_openai_token": "OpenAI API token",
    }

    strings_ru = {
        "where_args?": "<b>🚫 Укажи аргументы!</b>",
        "set_token": "<b>🚫 Поставь токен в конфиге!</b>",
        "incorrect_token": "<b>🚫 Ты указал неверный токен в конфиге!</b>",
        "unknown_openai_error": "<b>🚫 Произошла ошибка связанная с OpenAI!</b>\n<code>{}: {}</code>",
        "unknown_error": "<b>🚫 Произошла неизвестная ошибка!</b>\n<code>{}: {}</code>",
        "processing": "<b>⏱ Твой запрос обрабатывается...</b>",
        "result": (
            "<b>❓ Твой вопрос: </b><code>{}</code>"
            "\n\n<b>🙋🏼‍♂️ Ответ ChatGPT: </b><code>{}</code>"
        ),
        "debug_result": (
            "<b>❓ Твой вопрос: </b><code>{}</code>"
            "\n\n<b>🙋🏼‍♂️ Ответ ChatGPT: </b><code>{}</code>"
            "\n\n<b>ℹ️ Использовано токенов: </b><code>{}</code>"
        ),
        "edit_result": (
            "<b>❌ Оригинальный текст: </b><code>{}</code>"
            "\n\n<b>✔️ Исправленный текст: </b><code>{}</code>"
        ),
        "edit_debug_result": (
            "<b>❌ Оригинальный текст: </b><code>{}</code>"
            "\n\n<b>✔️ Исправленный текст: </b><code>{}</code>"
            "\n\n<b>ℹ️ Использовано токенов: </b><code>{}</code>"
        ),
        "edit_code_result": (
            "<b>❌ Оригинальный код: </b><code>{}</code>"
            "\n\n<b>✔️ Исправленный код: </b><code>{}</code>"
        ),
        "edit_code_debug_result": (
            "<b>❌ Оригинальный код: </b><code>{}</code>"
            "\n\n<b>✔️ Исправленный код: </b><code>{}</code>"
            "\n\n<b>ℹ️ Использовано токенов: </b><code>{}</code>"
        ),
        "_cfg_doc_debug_info": "Будет ли показываться информация об использованных токенах",
        "_cfg_doc_openai_token": "Токен OpenAI API",
        "_cls_doc": "Модуль для общения с ChatGPT. Основан на OpenAI API.",
        "_cmd_doc_chatgpt": "Спросить ChatGPT о чём-нибудь. В аргументах укажи свой вопрос.",
        "_cmd_doc_edits": "Исправь орфографические ошибки в своём тексте.",
        "_cmd_doc_editscode": "Исправь ошибки в своём коде",
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
        # не хочу вам логи забивать

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
