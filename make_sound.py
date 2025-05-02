import mido as md
from midi2audio import FluidSynth
from mido import Message, MidiFile, MidiTrack
from time import sleep

notes_alph = {}
i = 24
for octv in [-3, -2, -1, 1, 2, 3]:
    for letter in ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']:
        notes_alph[letter+str(octv)] = i
        i += 1
#print(* notes_alph)

def make_sound(notes_input):
    global notes_alph
    chords = notes_input.split(' ')
    port = md.open_output('Microsoft GS Wavetable Synth 0')
    
    mid = MidiFile()
    track = MidiTrack()
    mid.tracks.append(track)

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
            track.append(Message('note_on', note=notes_alph[note], velocity=64, time=0))
            print(notes_alph[note])
        
        sleep(length)
        for note in notes:
            port.send(md.Message('note_off', note=notes_alph[note]))
        track.append(Message('note_off', note=notes_alph[notes[0]], velocity=64, time=int(length * 480 * 2)))

    mid.save('output.mid')
    FluidSynth("FluidR3_GM.sf2").midi_to_audio('output.mid', 'static/output.wav')