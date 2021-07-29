from pydub import AudioSegment
from pydub.playback import play
import simpleaudio.functionchecks as fc
import os
import sys
import getopt

def speed_change(sound, speed=1.0):
    # FROM https://stackoverflow.com/questions/51434897/how-to-change-audio-playback-speed-using-pydub
    # Manually override the frame_rate. This tells the computer how many
    # samples to play per second
    sound_with_altered_frame_rate = sound._spawn(sound.raw_data, overrides={
         "frame_rate": int(sound.frame_rate * speed)
      })
     # convert the sound with altered frame rate to a standard frame rate
     # so that regular playback programs will work right. They often only
     # know how to play audio at standard frame rate (like 44.1k)
    return sound_with_altered_frame_rate.set_frame_rate(sound.frame_rate)

def detect_leading_silence(sound, silence_threshold=-50.0, chunk_size=2):
        # from https://stackoverflow.com/questions/29547218/remove-silence-at-the-beginning-and-at-the-end-of-wave-files-with-pydub
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

def trim_silence(sound, silence_threshold=-50.0, chunk_size=2):
    # from https://stackoverflow.com/questions/29547218/remove-silence-at-the-beginning-and-at-the-end-of-wave-files-with-pydub

    start_trim = detect_leading_silence(sound, silence_threshold, chunk_size)
    end_trim = detect_leading_silence(sound.reverse(), silence_threshold, chunk_size)

    duration = len(sound)    
    trimmed_sound = sound[start_trim:duration-end_trim]
    return trimmed_sound

def run():
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
        sound = trim_silence(sound)
        letter = s.split("/")[-1].split(".")[0].split("_")[-1]
        while letter in sounds:
            letter += "_"
        sounds[letter] = sound

    print("play sounds? (y/n)")
    res = input()
    if res in ["Yes", "yes", "y"]:
        print("playing sounds...")
        for letter, sound in sounds.items():
            print(letter)
            play(sound)

    return sounds

def wait(sounds):
    list_sounds = sorted(list(sounds), key=lambda x: len(x), reverse=True)
    while(True):
        print("[IN]: ", end="")
        s = input()
        if s in sounds:
            play(sounds[s])
        else:
            word = AudioSegment.silent(duration=0)
            for c in list(s):
                if c in sounds:
                    word += trim_silence(sounds[c], silence_threshold=-70)
                elif c in [' ', ',', ';', '.']:
                    word += AudioSegment.silent(duration=50)
            # NORMAL
            # play(word)
            # FUN
            play(speed_change(word, 3))

def main(argv):
    # Command line parsing
    longOpts = ['help']
    try:
        opts, args = getopt.getopt(argv, shortopts='h', longopts=longOpts)
    except getopt.GetoptError:
        print("Invalid options. Usage:\nmain.py " + '=<value> '.join([f'--{e}' for e in longOpts]))
        sys.exit(2)
    for opt, arg in opts:
        if opt in ('-h', '--help'):
            print('main.py ' + '=<value> '.join([f'--{e}' for e in longOpts]), end='=<value>\n')
            sys.exit()
    
    # RUN
    sounds = run()
    wait(sounds)


if __name__ == "__main__":
    main(sys.argv[1:])