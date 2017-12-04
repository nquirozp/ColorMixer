from midiutil.MidiFile import MIDIFile
from io import BytesIO
import pygame.mixer
from pygame.time import Clock
from threading import Thread
from pandas import read_csv


def get_tones(tone: str, octave: str):
    filtered = scale.loc[(scale['TONE'] == tone) & (scale['OCTAVE'] == int(octave))]['MIDI'].values
    return filtered[0]


def play(arg_time, tone:str, octave:str):
    # CREATE MEMORY FILE
    memFile = BytesIO()
    MyMIDI = MIDIFile(1, adjust_origin=True)
    track = 0
    time = 0
    channel = 0
    pitch = int(get_tones(tone, octave))
    duration = arg_time
    volume = 100
    MyMIDI.addProgramChange(track, channel, time, 90)
    MyMIDI.addTempo(track, time, 120)

    # WRITE A SCALE
    MyMIDI.addNote(track, channel, pitch, time, duration + 1, volume)
    MyMIDI.writeFile(memFile)

    # PLAYBACK

    clock = Clock()
    # memFile.seek(0)  # THIS IS CRITICAL, OTHERWISE YOU GET THAT ERROR!
    temp = BytesIO(memFile.getvalue())
    pygame.mixer.music.load(temp)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        clock.tick(1)


pygame.init()
pygame.mixer.init()
pygame.mixer.set_num_channels(20)
scale = read_csv('scale.csv')
print(scale)
while True:
    entry = input().split(',')
    time = entry[0]
    tone = entry[1]
    octave = entry[2]
    if not time or not tone:
        continue
    else:
        time = float(time)
    thread = Thread(target=play, args=[time, tone, octave])
    thread.start()

