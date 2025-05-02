from flask import Flask, render_template, request, redirect, url_for, flash
from make_sound import make_sound, notes_alph
from os.path import join
#from tensorflow.keras.models import load_model
from analyse_audio import make_mel_spec, resize_spec, encoder, model
import numpy as np

#model = load_model('model.keras')

application = Flask(__name__)
UPLOAD_FOLDER = 'uploads'

@application.route('/')
def home():
    return render_template('home.html')

@application.route('/page1')
def page1():
    return render_template('page1.html')

@application.route('/page2')
def page2():
    return render_template('page2.html')

@application.route('/process', methods=['GET', 'POST'])
def process_text():
    if request.method  == 'POST':
        notes_input = request.form.get('notes_input')
        if notes_input:
            notes_input = ' '.join(notes_input.split())
            print(notes_input)
            make_sound(notes_input)
            return render_template('page1.html', notes_input=notes_input)
        else:
            print('Текст не введен')
            return render_template('page1.html', notes_input='_')
    return render_template('page1.html')

@application.route('/upload_audio', methods=['POST'])
def upload_audio():
    file = request.files['audio_file']
    if file.filename == '':
        flash('Файл не выбран.')
        return redirect(url_for('page2'))
    filepath = join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)
    print(f'Аудио сохранено: {filepath}')
    mel = resize_spec(make_mel_spec(filepath))
    pred = model.predict(mel[np.newaxis, ...])
    pred_label = np.argmax(pred)
    note_result = encoder.inverse_transform([pred_label])[0]
    
    return render_template('page2.html', note_result=note_result)

if __name__ == '__main__':
    application.run(host='0.0.0.0')