import os
import subprocess

import speech_recognition as sr


class Recognition:
    def __init__(self, file_name, lang):
        self.file_name = file_name
        self.lang = lang

    def audio_to_text(self, name: str):
        r = sr.Recognizer()
        message = sr.AudioFile(name)
        with message as source:
            audio = r.record(source)
        result = r.recognize_google(audio, language=self.lang)
        return result

    def get_audio_messages(self):
        try:
            self.new_file = self.file_name.split(".")[0] + ".wav"
            subprocess.call(
                f'bin/ffmpeg.exe -i {self.file_name} {self.new_file}')
            result = self.audio_to_text(self.new_file)
            return result

        except Exception as e:
            return False

        finally:
            pass
            # os.remove(self.new_file)
            # os.remove(self.file_name)
