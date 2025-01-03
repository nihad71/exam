import os
from flask import Flask, render_template, request, redirect, url_for
import random
import webbrowser
from threading import Timer

app = Flask(__name__)

# Masaüstü yolunu təyin edirik
DESKTOP_PATH = os.path.join(os.path.expanduser("~"), "Desktop")

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
        exam_time = request.args.get('time', 30)  # Default olaraq 30 dəqiqə
        if not questions:
            return redirect(url_for('index'))  # Parametr yoxdursa, əsas səhifəyə yönləndiririk
        questions = eval(questions)  # Stringi listə çevirmək
        return render_template('exam.html', questions=questions, time=exam_time)
    
    if request.method == 'POST':
        # Cavablar və sualları oxumaq
        questions_and_answers = []
        for key, value in request.form.items():
            if key.startswith("question-"):
                index = key.split("-")[1]
                question = value
                answer = request.form.get(f"answer-{index}", "Cavab daxil edilməyib")
                questions_and_answers.append((question, answer))
        
        # Masaüstündə fayl yaratmaq
        file_path = os.path.join(DESKTOP_PATH, 'exam_results.txt')
        with open(file_path, 'w', encoding='utf-8') as f:
            for i, (question, answer) in enumerate(questions_and_answers, start=1):
                f.write(f"Sual {i}: {question}\n")
                f.write(f"Cavab: {answer}\n\n")
        
        return render_template('result.html', questions_and_answers=questions_and_answers, file_path=file_path)


@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        # Fayl və sual sayı məlumatlarını əldə edirik
        file = request.files['file']
        num_questions = int(request.form['num_questions'])
        exam_time = int(request.form['time'])

        if num_questions <= 0:
            return render_template('index.html', error="Sual sayı sıfırdan böyük olmalıdır.")

        # Fayldakı sualları oxuyuruq
        questions = load_questions(file.read())
        if not questions:
            return render_template('index.html', error="Faylda suallar yoxdur və ya fayl düzgün deyil.")

        # Təsadüfi sualları seçirik
        selected_questions = get_random_questions(questions, num_questions)

        # Seçilən sualları yeni səhifəyə göndəririk
        return redirect(url_for('exam', questions=selected_questions, time=exam_time))

    except ValueError:
        return render_template('index.html', error="Sual sayını düzgün daxil edin.")
    except Exception as e:
        return render_template('index.html', error=f"Xəta baş verdi: {e}")

def open_browser():
    # Flask tətbiqi işə düşdükdə brauzeri avtomatik açır
    webbrowser.open_new('http://127.0.0.1:5000/')

if __name__ == '__main__':
    Timer(1, open_browser).start()
    app.run(debug=True)
