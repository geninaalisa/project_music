import mido as md
import keyboard as kb
from time import sleep

notes_alph = {}
i = 24
for octv in [-3, -2, -1, 1, 2, 3]:
    for letter in ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']:
        notes_alph[letter+str(octv)] = i
        i += 1


def make_sound(notes_input):
    global notes_alph
    chords = notes_input.split(' ')
    port = md.open_output('Microsoft GS Wavetable Synth 0')
    
    for chord in chords:
        print(chord)
        notes = []
        x = ''
        length = 1
        for i in range(len(chord)):
            if chord[i].isalpha():
                if x != '':
                    notes.append(x)
                x = ''
            elif chord[i] == '_':
                notes.append(x)
                length = float(chord[i + 1:])
                break
            x += chord[i]
        for note in notes:
            port.send(md.Message('note_on', note=notes_alph[note]))
            print(notes_alph[note])
        sleep(length)
        for note in notes:
            port.send(md.Message('note_off', note=notes_alph[note]))
        


