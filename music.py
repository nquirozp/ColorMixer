from midiutil.MidiFile import MIDIFile
from io import BytesIO
import pygame.mixer
from pygame.time import Clock
from threading import Thread
from pandas import read_csv
from typing import List
scale = read_csv('scale.csv')

keep_playing = False


def __get_tones(tone: str, octave: str):
    filtered = scale.loc[(scale['TONE'] == tone) & (scale['OCTAVE'] == int(octave))]['MIDI'].values
    return filtered[0]


def __play(arg_time, tone: str, octave: str):
    keep_playing = True
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
    MyMIDI.addTempo(track, time, 60)

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
        if keep_playing:
            clock.tick(1)
        else:
            pygame.mixer.stop()
            return


def start_mixer():
    pygame.init()
    pygame.mixer.init()
    pygame.mixer.set_num_channels(20)


def stop_mixer():
    global keep_playing
    keep_playing = False
    pygame.mixer.stop()


def play_note(time, tone, octave):
    thread = Thread(target=__play, args=[time, tone, octave])
    thread.start()


def get_notes():
    values = scale['TONE'].values
    octaves = scale['OCTAVE'].values
    return list(f'{value},{octave}' for value, octave in zip(values, octaves))


class Nota:
    def __init__(self, nota: str):
        self.nota = nota
        self.color = None


class Tono:
    def __init__(self, nota: Nota, octava: int, tiempo: int):
        self.nota = nota
        self.octava = octava
        self.tiempo = tiempo

    def __str__(self):
        return f'<Nota= {self.nota.nota}, Octava = {self.octava}, Tiempo= {self.tiempo}>'


class TonoFactory:
    def __init__(self):
        self.possible_tones = get_notes()
        self.notas = {
            'C': Nota('C'),
            'C#/Db': Nota('C#/Db'),
            'D': Nota('D'),
            'D#/Eb': Nota('D#/Eb'),
            'E': Nota('E'),
            'F': Nota('F'),
            'F#/Gb': Nota('F#/Gb'),
            'G': Nota('G'),
            'G#/Ab': Nota('G#/Ab'),
            'A': Nota('A'),
            'A#/Bb': Nota('A#/Bb'),
            'B': Nota('B'),
        }
        self.tonos: List[Tono] = []

    def new_tono(self, nota, octava, tiempo):
        for tono in self.tonos:
            if tono.nota.nota == nota and tono.octava == octava or f'{nota},{octava}' not in self.possible_tones:
                return False
            else:
                pass
        tono = Tono(self.notas[nota], octava, tiempo)
        self.tonos.append(tono)
        return True

    def remove_tono(self, row: int):
        if not isinstance(row, int):
            raise TypeError(f'expected int got {type(row)}')
        self.tonos.pop(row)

if __name__ == '__main__':
    get_notes()
