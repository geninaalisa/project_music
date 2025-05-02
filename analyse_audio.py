import librosa as lb
import mido as md
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from make_sound import notes_alph
import pretty_midi as pmid
import soundfile as sf
import matplotlib.pyplot as plt
import librosa.display
from skimage.transform import resize
from tensorflow.keras import layers, models
from random import randint
import matplotlib.pyplot as plt
#from nsynth.new_data import x, y

def make_sound(notes_input): # добавляет новый файл из переданных нот
    global notes_alph
    chords = notes_input.split(' ')
    mid = md.MidiFile()
    track = md.MidiTrack()
    mid.tracks.append(track)
    for chord in chords:
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
            track.append(md.Message('note_on', note=notes_alph[note]))
            
        track.append(md.Message('note_off', note=0, time=int(length * 480)))
        for note in notes:
            track.append(md.Message('note_off', note=notes_alph[note]))
    mid.save('file.mid')


def make_mel_spec(file_path, n_mels=64, duration=120.0, sr=22050): # аудио -> спектограмма
    audio = lb.load(file_path, sr=sr, duration=duration)[0]
    if len(audio) == 0:
        print('!')
    mel_spec = lb.feature.melspectrogram(y=audio, sr=sr, n_mels=n_mels) # вычислить спектограмму
    mel_spec_db = lb.power_to_db(mel_spec, ref=np.max) # в децибелы
    return mel_spec_db


def resize_spec(spec, standart=(64, 65)): #привести к размеру
    res = resize(spec, standart, mode='constant', preserve_range=True)
    res = (res - res.min()) / (res.max() - res.min() + 1e-9)
    return res#[..., np.newaxis] #(64, 65)->(64, 65, 1)

def print_spec(note): # нарисовать спектограмму
    make_sound(note)
    midi_obj = pmid.PrettyMIDI("file.mid")
    audio = midi_obj.fluidsynth(fs=22050)
    sf.write("output.wav", audio, samplerate=22050)
    mel = make_mel_spec("output.wav")
    print(len(mel), len(mel[0]))
    plt.figure(figsize=(10, 4))
    librosa.display.specshow(mel, sr=22050, x_axis='time', y_axis='mel')
    plt.colorbar(format='%+2.0f dB')
    plt.title('Mel Spectrogram')
    plt.tight_layout()
    plt.show()
#print_spec("C-3_2")

n_classes = len(notes_alph)

def distribute_notes(shape=(64, 65, 1), n_classes=n_classes):
    model = models.Sequential([
        layers.Conv2D(32, (3, 3), activation='relu', input_shape=shape),
        layers.MaxPooling2D((2, 2)), # уменьшает размер признаков вдвое, чтобы ускорить обучение и убрать шум.
        layers.Conv2D(64, (3, 3), activation='relu'),
        layers.MaxPooling2D((2, 2)),
        layers.Flatten(), # выравнивает входные данные
        layers.Dense(128, activation='relu'), # анализирует все признаки и выбирает наиболее важные
        layers.Dropout(0.3), # обнуляет 30% нейронов, чтобы не переобучиться
        layers.Dense(n_classes, activation='softmax') # softmax - обобщение логистической функции, вектор чисел -> распределение вероятностей
    ])

    model.compile(optimizer='adam', # градиентный спуск, сам подбирает темп обучения для каждого веса
              loss='sparse_categorical_crossentropy',
              metrics=['accuracy'])
    return model

x = []
y = []
#print(notes_alph)
for note in notes_alph:
    s = 4
    for i in range(7):
        y.append(note)
        make_sound(note + '_' + str(s))
        midi_obj = pmid.PrettyMIDI("file.mid")
        audio = midi_obj.fluidsynth(fs=22050)
        sf.write("output.wav", audio, samplerate=22050)
        mel = make_mel_spec("output.wav")
        x.append(resize_spec(mel))
        s /= 2
x = np.array(x)
y = np.array(y)

encoder = LabelEncoder()
y_encoded = encoder.fit_transform(y) #ноты -> числовые метки (целые числа)
x_train, x_test, y_train, y_test = train_test_split(
    x, y_encoded, test_size=0.5, random_state=42
)

#Обучение
model = distribute_notes()
model.fit( #сначала модель учится на маленьких порциях, и после каждой полной тренировки проверяет себя на отложенных данных
    x_train, y_train,
    epochs=15, #сколько раз пройтись по данным, обновляя веса каждый раз
    batch_size=16, #делит на батчи, чтобы за раз обработать(прогноз) 1 батч, а потом сравнить с правильным ответом и скорректировать веса 
    validation_data=(x_test, y_test) #проверка на независимых данных
)

loss, acc = model.evaluate(x_test, y_test)
print(f"accuracy: {acc * 100:.2f}%")
#Проверка
for _ in range(10):
    i = randint(0, len(x_test) - 1)
    sample = x_test[i]
    true_label = y_test[i]
    pred = model.predict(sample[np.newaxis, ...])
    pred_label = np.argmax(pred)
    print(f"Настоящая нота: {true_label} {encoder.inverse_transform([true_label])[0]}")
    print(f"Предсказанная: {pred_label} {encoder.inverse_transform([pred_label])[0]}")

    plt.imshow(sample.squeeze(), aspect='auto', origin='lower', cmap='magma')
    plt.title(f"True: {true_label} {encoder.inverse_transform([true_label])[0]} | Predicted: {pred_label}  {encoder.inverse_transform([pred_label])[0]}")
    plt.colorbar()
    plt.show()

model.save("model.keras") 