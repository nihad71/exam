from flask import Flask, render_template, request, redirect, url_for
import random
import webbrowser
from threading import Timer

app = Flask(__name__)

# Sualları fayldan oxuyan funksiya
def load_questions(file_content):
    questions = file_content.decode('utf-8').splitlines()
    return [q.strip() for q in questions if q.strip()]

# Təsadüfi sualları seçən funksiya
def get_random_questions(questions, count):
    return random.sample(questions, k=min(count, len(questions)))

@app.route('/')
def index():
    # Ana səhifəni göstərir
    return render_template('index.html')

@app.route('/exam', methods=['GET', 'POST'])
def exam():
    if request.method == 'GET':
        questions = request.args.get('questions')
        if not questions:
            # Parametr yoxdursa, istifadəçini əsas səhifəyə yönləndiririk
            return redirect(url_for('index'))  
        questions = eval(questions)  # stringi listə çevirmək
        return render_template('exam.html', questions=questions)
    
    if request.method == 'POST':
        # Cavabları göndəririk
        answers = request.form.getlist('answer')
        # Cavabları işləyirsiniz
        return render_template('result.html', answers=answers)

@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        # Fayl və sual sayı məlumatlarını əldə edirik
        file = request.files['file']
        num_questions = int(request.form['num_questions'])

        if num_questions <= 0:
            return render_template('index.html', error="Sual sayı sıfırdan böyük olmalıdır.")

        # Fayldakı sualları oxuyuruq
        questions = load_questions(file.read())
        if not questions:
            return render_template('index.html', error="Faylda suallar yoxdur və ya fayl düzgün deyil.")

        # Təsadüfi sualları seçirik
        selected_questions = get_random_questions(questions, num_questions)

        # Seçilən sualları yeni səhifəyə göndəririk
        return render_template('questions.html', questions=selected_questions)

    except ValueError:
        return render_template('index.html', error="Sual sayını düzgün daxil edin.")
    except Exception as e:
        return render_template('index.html', error=f"Xəta baş verdi: {e}")

def open_browser():
    # Flask tətbiqi işə düşdükdə brauzeri avtomatik açır
    webbrowser.open_new('http://127.0.0.1:5000/')

if __name__ == '__main__':
    # Brauzeri avtomatik açmaq üçün bir gecikmə təyin edirik
    Timer(1, open_browser).start()
    app.run(debug=True)
