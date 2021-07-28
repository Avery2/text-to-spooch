from pydub import AudioSegment
from pydub.playback import play
import simpleaudio.functionchecks as fc
import os


def trim_silence(sound):
    # from https://stackoverflow.com/questions/29547218/remove-silence-at-the-beginning-and-at-the-end-of-wave-files-with-pydub
    def detect_leading_silence(sound, silence_threshold=-50.0, chunk_size=10):
        '''
        sound is a pydub.AudioSegment
        silence_threshold in dB
        chunk_size in ms

        iterate over chunks until you find the first one with sound
        '''
        trim_ms = 0 # ms

        assert chunk_size > 0 # to avoid infinite loop
        while sound[trim_ms:trim_ms+chunk_size].dBFS < silence_threshold and trim_ms < len(sound):
            trim_ms += chunk_size

        return trim_ms

    start_trim = detect_leading_silence(sound)
    end_trim = detect_leading_silence(sound.reverse())

    duration = len(sound)    
    trimmed_sound = sound[start_trim:duration-end_trim]
    return trimmed_sound

sound_files = []
for i in range(1,8):
    for root, dirs, files in os.walk(f"british_english/group{i}/"):
        for file in files:
            if ".mp3" in file:
                sound_files.append(os.path.join(root, file))

sounds = dict()

print("loading sounds...")
for s in sound_files:
    sound = AudioSegment.from_file(s, format="mp3")[:2000]
    sound = trim_silence(sound)
    sound = sound[:1000]
    letter = s.split("/")[-1].split(".")[0].split("_")[-1]
    while letter in sounds:
        letter += "_"
    sounds[letter] = sound

print("playing sounds...")
for letter, sound in sounds.items():
    print(letter)
    play(sound)