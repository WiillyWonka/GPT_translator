import io
import json
from typing import Dict, List
from dotenv import load_dotenv
from openai import OpenAI
from loguru import logger
import tiktoken

from app import schemas
from app.schemas import Glossary

load_dotenv()


def format_glossary_item(item: Glossary):
    return f"({item.term}) | ({item.translation}) |" + (
        f" ({item.comment})" if item.comment else ""
    )


class Assistant:
    def __init__(
        self,
        model: str,
        policy: str,
        temperature: float,
        max_output_token: int,
        context_window: int,
    ):
        self._client = OpenAI()
        self._model = model
        self._policy = policy
        self._temperature = temperature
        self._max_output_token = max_output_token
        self._context_window = context_window

        logger.info(self._policy)

    def __call__(
        self, messages: List[Dict[str, str]], glossary_list: list[Glossary]
    ):

        system_promt = self.make_system_promt(glossary_list)
        print(system_promt)

        response = self._client.chat.completions.create(
            model=self._model,
            messages=[{"role": "system", "content": system_promt}] + messages,
            temperature=self._temperature,
        )
        return response.choices[0].message.content

    def make_system_promt(self, glossary_list: list[Glossary]):
        # return (
        #     self._policy
        #     + "\nГлоссарий:\n"
        #     + "\n".join(
        #         [
        #             format_glossary_item(glossary_item)
        #             for glossary_item in glossary_list
        #         ]
        #     )
        #     + "\n"
        # )

        return self._policy

    def upload_dataset(
        self,
        train_samples: list[schemas.TrainSample],
        glossary_list: list[Glossary],
    ):
        system_promt = self.make_system_promt(glossary_list)

        dataset = []
        for train_sample in train_samples:
            messages = self.make_messages(train_sample, system_promt)
            dataset.append({"messages": messages})

        buffer = make_buffer(dataset)

        self._client.files.create(file=buffer, purpose="fine-tune")

        # self._client.fine_tuning.jobs.create(
        #     training_file=file_obj.id,
        #     model=self._finetune_model,
        # )

        #     # Сохраните в JSONL формате
        # with open("training_data.jsonl", "w", encoding="utf-8") as f:
        #     for messages in dataset:
        #         json_line = json.dumps(messages, ensure_ascii=False)
        #         f.write(json_line + "\n")

    def num_tokens_from_string(self, string: str) -> int:
        """Returns the number of tokens in a text string."""
        encoding = tiktoken.encoding_for_model(self._model)
        num_tokens = len(encoding.encode(string))
        return num_tokens

    def make_messages(
        self, train_sample: schemas.TrainSample, system_promt: str
    ):
        messages = [{"role": "system", "content": system_promt}]

        messages.append(
            {"role": "user", "content": train_sample.foreign_text}
        )

        translation_chunks = split_text_into_chunks(train_sample.translation)

        accumulated_translation = ""
        for i, next_translation_chunk in enumerate(translation_chunks):

            translation = join_chunks(
                [accumulated_translation, next_translation_chunk]
            )

            is_last_paragraph = i == (len(translation_chunks) - 1)
            is_first_paragraph = len(messages) == 2

            assistant_message = self._make_assistant_translation_message(
                translation, is_first_paragraph, is_last_paragraph
            )

            if (
                self.num_tokens_from_string(assistant_message)
                > self._max_output_token
            ):
                if accumulated_translation == "":
                    raise Exception(
                        f"Translation chunk is empty. Training sample ID = {train_sample.id}.\nRemove this sample from dataset."
                    )
                
                assistant_message = self._make_assistant_translation_message(
                    accumulated_translation,
                    is_first_paragraph,
                    is_last_paragraph=False,
                )

                num_tokens = self.num_tokens_from_string(assistant_message)
                if num_tokens > self._max_output_token:
                    raise Exception(
                        f"Translation chunk has {num_tokens}, while max number output tokens is {self._max_output_token}. Training sample ID = {train_sample.id}\nRemove this sample from dataset."
                    )

                messages.append(
                    {"role": "assistant", "content": assistant_message}
                )
                messages.append({"role": "user", "content": "Дальше"})

                accumulated_translation = next_translation_chunk
            elif is_last_paragraph:
                messages.append(
                    {"role": "assistant", "content": assistant_message}
                )
            else:
                accumulated_translation = translation

        num_tokens = self.num_tokens_from_string("".join([message['content'] for message in messages]))
        if num_tokens > self._context_window:
            raise Exception(
                f"Training sample has {num_tokens}, while context size is {self._context_window}. Training sample ID = {train_sample.id}\nRemove this sample from dataset."
            )

        return messages

    def _make_assistant_translation_message(
        self, translation, is_first_paragraph=False, is_last_paragraph=False
    ):
        preffix_start = "Начинаю перевод текста."
        preffix_mid = "Перевожу дальше."
        suffix_mid = "Переведена часть текста. Пожалуйста, дайте знать, чтобы я продолжил перевод."
        suffix_end = "Конец текста. Перевод завершён."
        translation_template = "{translation}"

        assistant_template = translation_template

        if is_first_paragraph and is_last_paragraph:
            # Не нужно никаких дополнительных сообщений, если перевод уместился в одно сообщение
            pass
        else:
            if is_first_paragraph:
                assistant_template = "\n".join([preffix_start, assistant_template])
            else:
                assistant_template = "\n".join([preffix_mid, assistant_template])

            if is_last_paragraph:
                assistant_template = "\n".join([assistant_template, suffix_end])
            else:
                assistant_template = "\n".join([assistant_template, suffix_mid])

        assistant_message = assistant_template.format(translation=translation)

        return assistant_message


def make_buffer(messages: List[Dict]):
    # Создаем объект io.StringIO для хранения содержимого файла в памяти
    buffer = io.BytesIO()

    # Записываем данные в объект io.StringIO в формате JSONL
    for item in messages:
        json_line = json.dumps(item, ensure_ascii=False).encode('utf-8') + b"\n"
        buffer.write(json_line)

    # Перемещаем указатель в начало объекта io.StringIO
    buffer.seek(0)
    return buffer


def split_text_into_chunks(text: str):
    return text.split("\n")


def join_chunks(chunks: List[str]):
    if len(chunks) == 1:
        return chunks[0]
    else:
        if chunks[0] == "": chunks = chunks[1:]
        return "\n".join(chunks)
