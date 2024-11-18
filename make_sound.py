import mido as md
import keyboard as kb
from time import sleep

notes_alph = {}
i = 24
for octv in range(-3, 4):
    for letter in ['C_', 'C#', 'D_', 'D#', 'E_', 'F_', 'F#', 'G_', 'G#', 'A_', 'A#', 'B_']:
        notes_alph[str(octv)+letter] = i
        i += 1

def make_sound(notes_input):
    voices = notes_input.split('|')
    for voice in voices:
        make_voice(voice)

def make_voice(voice):
    global notes_alph
    port = md.open_output('Microsoft GS Wavetable Synth 0')
    notes = voice.split(' ')
    for note in notes:
        a = 3
        if note[0] == '-':
            a = 4

        print()
        port.send(md.Message('note_on', note=notes_alph[note[:a]]))
        sleep(float(note[a:]))
        port.send(md.Message('note_off', note=notes_alph[note[:a]]))
