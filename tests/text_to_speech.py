import os

from gtts import gTTS


def text_to_speech(text, language="en", filename="output.mp3"):
    try:
        tts = gTTS(text=text, lang=language, slow=False)

        tts.save(filename)
        print(f"Файл успешно сохранен как {os.path.abspath(filename)}")

    except Exception as e:
        print(f"Произошла ошибка: {str(e)}")


if __name__ == "__main__":
    input_text = input("Введите текст для преобразования в речь: ")

    language = (
        input("Выберите язык (например 'en' для английского, 'ru' для русского): ")
        or "en"
    )
    filename = input("Введите имя файла (по умолчанию output.mp3): ") or "output.mp3"

    if input_text.strip():
        text_to_speech(input_text, language, filename)
    else:
        print("Ошибка: Введен пустой текст")
