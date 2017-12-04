from midiutil.MidiFile import MIDIFile
from io import BytesIO
import pygame.mixer
from pygame.time import Clock
from threading import Thread
from pandas import read_csv

scale = read_csv('scale.csv')

def __get_tones(tone: str, octave: str):
    filtered = scale.loc[(scale['TONE'] == tone) & (scale['OCTAVE'] == int(octave))]['MIDI'].values
    return filtered[0]


def __play(arg_time, tone:str, octave:str):
    # CREATE MEMORY FILE
    memFile = BytesIO()
    MyMIDI = MIDIFile(1, adjust_origin=True)
    track = 0
    time = 0
    channel = 0
    pitch = int(__get_tones(tone, octave))
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


def start_mixer():
    pygame.init()
    pygame.mixer.init()
    pygame.mixer.set_num_channels(20)


def play_note(time, tone, octave):
    thread = Thread(target=__play, args=[time, tone, octave])
    thread.start()
