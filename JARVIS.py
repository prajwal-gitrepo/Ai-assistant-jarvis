import os
import azure.cognitiveservices.speech as speechsdk
import threading
import re
import time
from dotenv import load_dotenv
from openai import AzureOpenAI
import sys

load_dotenv()

client = AzureOpenAI(
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_KEY"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
)

DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT")


def translate_interactive():
    print("🌍 Azure OpenAI Interactive Translator")
    print("Type 'exit' to quit.")
    print("Type 'change languages' to switch languages.\n")

    source_lang = input("Source language (e.g. English): ").strip()
    target_lang = input("Target language (e.g. French): ").strip()

    print("\nStart typing text to translate:\n")

    while True:
        text = input("➜ ")

        if text.lower() in {"exit", "quit"}:
            print("👋 Goodbye!")
            break

        if text.lower() in {"change languages"}:
            source_lang = input("Source language (e.g. English): ").strip()
            target_lang = input("Target language (e.g. French): ").strip()
            print("\nStart typing text to translate:\n")
            continue

        response = client.chat.completions.create(
            model=DEPLOYMENT,
            messages=[
                {
                    "role": "system",
                    "content": f"You are a professional translator. Translate from {source_lang} to {target_lang}. Return only the translation.",
                },
                {
                    "role": "user",
                    "content": text,
                },
            ],
            temperature=0.2,
            max_tokens=500,
        )

        translation = response.choices[0].message.content
        print(f" {translation}\n")
    
def jarvis():
    while True:
        text = input("➜ ")
        response = client.chat.completions.create(
            model=DEPLOYMENT,
            messages=[
                {
                    "role": "system",
                    "content": f"you are Jarvis, Tony Stark’s AI assistant. Be concise and witty.",
                },
                {
                    "role": "user",
                    "content": text,
                },
            ],
            temperature=0.2,
            max_tokens=500,
        )

        ai_response = response.choices[0].message.content
        print(f" 🤖 {ai_response}\n")

speech_config = speechsdk.SpeechConfig(
    subscription=os.getenv("AZURE_SPEECH_KEY"),
    region=os.getenv("AZURE_SPEECH_REGION")
)

# Jarvis-like voice
speech_config.speech_synthesis_voice_name = "en-US-GuyNeural"

audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)

def create_recognizer():
    return speechsdk.SpeechRecognizer(
        speech_config=speech_config,
        audio_config=audio_config,
    )

recognizer = create_recognizer()

synthesizer = speechsdk.SpeechSynthesizer(
    speech_config=speech_config
)

is_speaking = False

def normalize_text(text):
    # Normalize punctuation/casing so wake-word matching is reliable.
    lowered = (text or "").lower()
    return re.sub(r"[^a-z0-9\s]", "", lowered).strip()

def reset_recognizer():
    global recognizer
    recognizer = create_recognizer()

def speak(text):
    synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config)
    synthesizer.speak_text_async(text).get()

def listen():
    audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)
    recognizer = speechsdk.SpeechRecognizer(
        speech_config=speech_config,
        audio_config=audio_config
    )

    print("🎤 Listening...")
    result = recognizer.recognize_once()

    if result.reason == speechsdk.ResultReason.RecognizedSpeech:
        print(f"➜ {result.text}")
        return result.text

    if result.reason == speechsdk.ResultReason.Canceled:
        cancellation = result.cancellation_details
        print(f"❌ Speech recognition canceled: {cancellation.reason}")
        print(f"   Error details: {cancellation.error_details}")

    return None

def listen_for_wake_word():
    while True:
        text = listen()
        if text and "hey jarvis" in text.lower():
            speak("Yes, sir?")
            return

def ask_jarvis(text):
    response = client.chat.completions.create(
        model=DEPLOYMENT,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are JARVIS, Tony Stark’s AI assistant. "
                    "Be concise, intelligent, slightly witty, confident, and calm. "
                    "Never ramble. If unsure, say so."
                )
            },
            {
                "role": "user",
                "content": text
            }
        ],
        temperature=0.2,
        max_tokens=300
    )

    return response.choices[0].message.content

def jarvis_2():
        listen_for_wake_word()

        while True:
            text = listen()
            if not text:
                continue

            if "go to sleep" in text.lower():
                speak("Standing by.")
                break

            response = ask_jarvis(text)
            speak(response)

if __name__ == "__main__":
    #translate_interactive()
    jarvis()