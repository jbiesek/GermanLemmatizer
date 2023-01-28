import difflib
import sys
from collections import defaultdict
from google.cloud import speech
import pyaudio
import wave
from pynput import keyboard

word_dict = {}
word_dict_base_form = defaultdict(set)
w = ""


def load_dict():
    with open("DE_morph_dict.txt") as f:
        for line in f:
            new_line = line.split(" ")
            if len(new_line) == 1:
                w = new_line[0].lower().strip('\n')
            else:
                word_dict_base_form[w].add(new_line[0].lower())
                word_dict[new_line[0].lower()] = new_line[1].lower()


def test_loop():
    with keyboard.Listener(on_press=on_press) as listener:
        while listener.running:
            word = input("Type your word: ")
            word = word.lower()
            if word not in word_dict_base_form.keys():
                print("Word not found!")
                words = difflib.get_close_matches(word, word_dict_base_form.keys())
                for w in words:
                    l = list(word_dict_base_form[w])
                    l.sort(key=len)
                    print("Possible word:", w, "Base form:", l[0])
            else:
                l = list(word_dict_base_form[word])
                l.sort(key=len)
                print("Your word:", word, "\nBase form:", l[0])


def speech_to_text(file_name):
    client = speech.SpeechClient.from_service_account_file('key.json')
    with open(file_name, 'rb') as f:
        mp3_data = f.read()
    audio_file = speech.RecognitionAudio(content=mp3_data)
    config = speech.RecognitionConfig(
        sample_rate_hertz=44100,
        enable_automatic_punctuation=True,
        language_code='de-DE'
    )

    response = client.recognize(
        config=config,
        audio=audio_file
    )
    text = ""
    for result in response.results:
        text = result.alternatives[0].transcript
    if text != "":
        print(text)
    else:
        print("ERROR")
    dict_test(text)


def dict_test(text):
    words = text.split(" ")
    for word in words:
        word = word.lower()
        word = word.rstrip('.,')
        if word not in word_dict_base_form.keys():
            print("Word not found!")
            words = difflib.get_close_matches(word, word_dict_base_form.keys())
            for w in words:
                l = list(word_dict_base_form[w])
                l.sort(key=len)
                print("Possible word:", w, "Base form:", l[0])
        else:
            l = list(word_dict_base_form[word])
            l.sort(key=len)
            print("Your word:", word, "\nBase form:", l[0])


def record_audio():
    audio = pyaudio.PyAudio()
    stream = audio.open(
        format=pyaudio.paInt16,
        channels=1,
        rate=44100,
        input=True,
        frames_per_buffer=1024,
    )
    frames = []
    print("Recording started. ESC to stop.")
    with keyboard.Listener(on_press=on_press) as listener:
        while listener.running:
            data = stream.read(1024)
            frames.append(data)

    stream.stop_stream()
    stream.close()
    audio.terminate()
    sound_file = wave.open("file.mp3", "wb")
    sound_file.setnchannels(1)
    sound_file.setsampwidth(audio.get_sample_size(pyaudio.paInt16))
    sound_file.setframerate(44100)
    sound_file.writeframes(b''.join(frames))
    sound_file.close()
    speech_to_text("file.mp3")


def on_press(key):
    if key == keyboard.Key.esc:
        return False


def menu():
    load_dict()
    while (1):
        print("1 - podstawowy lematyzator")
        print("2 - lematyzator dla nagranych wcześniej plików")
        print("3 - dyktafon + lematyzator")
        print("4 - exit")
        choice = input()
        if choice == '1':
            test_loop()
        if choice == '2':
            print("1 - Nagranie nr 1")
            print("2 - Nagranie nr 2")
            print("3 - Nagranie nr 3")
            print("4 - Nagranie nr 4")
            choice2 = input()
            if choice2 == '1':
                speech_to_text("1.mp3")
            if choice2 == '2':
                speech_to_text("2.mp3")
            if choice2 == '3':
                speech_to_text("3.mp3")
            if choice2 == '4':
                speech_to_text("4.mp3")
        if choice == '3':
            record_audio()
        if choice == '4':
            sys.exit(0)


menu()
