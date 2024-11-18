from flask import Flask, render_template, request, redirect, url_for
from make_sound import make_sound, make_voice,  notes_alph

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/page1')
def page1():
    return render_template('page1.html')

@app.route('/page2')
def page2():
    return render_template('page2.html')

@app.route('/process', methods=['GET', 'POST'])
def process_text():
    if request.method == 'POST':
        notes_input = request.form.get('notes_input')
        if notes_input:
            print(notes_input)
            make_sound(notes_input)
            return render_template('page1.html', notes_input=notes_input)
        else:
            print('Текст не введен')
            return render_template('page1.html', notes_input='_')
    return render_template('page1.html')

if __name__ == '__main__':
    app.run(debug=True)
