// ==========================================
// 1. ІНІЦІАЛІЗАЦІЯ ДАНИХ ТЕСТУ ТА ЗМІННИХ
// ==========================================
var currentQuestionIndex = 0;
var userChoice = null;
var correctChoice = null;
var currentSelected = null;
var allQuizzes = [];

function loadQuizzesFromHTML() {
    // Шукаємо безпечний скрипт, створений за допомогою json_script
    const quizzesScriptEl = document.getElementById('quizzes-data');

    if (quizzesScriptEl) {
        // Забираємо внутрішній текст тегу
        const rawContent = quizzesScriptEl.textContent;

        if (rawContent && rawContent.trim() !== "") {
            try {
                // Оскільки всередині json_script дані вже є JSON-рядком,
                // спочатку дістаємо з нього чистий рядок, а потім парсимо його
                const parsedString = JSON.parse(rawContent);

                // Якщо Django передав рядок, парсимо його в масив об'єктів
                allQuizzes = typeof parsedString === 'string' ? JSON.parse(parsedString) : parsedString;

                console.log("Тести успішно розпарсено через json_script! Кількість:", allQuizzes.length);
            } catch (e) {
                console.error("Помилка JSON.parse у main.js:", e);
            }
        } else {
            console.warn("Вміст тегу quizzes-data порожній!");
        }
    } else {
        console.error("Критична помилка: Елемент з id='quizzes-data' не знайдено на сторінці!");
    }
}

// Запускаємо
loadQuizzesFromHTML();

// ==========================================
// 2. КЕРУВАННЯ МОДАЛЬНИМИ ВІКНАМИ
// ==========================================

function openQuiz() {
    console.log("Функція openQuiz викликана!");

    const modal = document.getElementById("quizModal");
    if (!modal) {
        console.error("Елемент quizModal не знайдено в HTML!");
        return;
    }

    if (allQuizzes.length === 0) {
        alert("Тести для цього уроку ще не завантажені.");
        return;
    }

    currentQuestionIndex = 0;
    displayQuestion();

    modal.style.setProperty('display', 'flex', 'important');
    document.body.style.overflow = "hidden";
}

function closeQuiz() {
    document.getElementById("quizModal").style.display = "none";
    document.body.style.overflow = "auto";
}

function showSuccess() {
    // 1. Ховаємо вікно тесту
    document.getElementById("quizModal").style.display = "none";

    // 2. Показуємо красиву фінальну модалку зі змійкою
    document.getElementById("successModal").style.setProperty('display', 'flex', 'important');

    // 3. Відправляємо запит на сервер для збереження в базу даних SQLite
    saveProgressOnServer();
}
function saveProgressOnServer() {
    fetch('/save-quiz-result/', { // URL в urls.py
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
        },
        body: JSON.stringify({
            'lesson_id': currentLessonId, // Переконайся, що ця змінна доступна
            'status': 'completed'
        })
    })
    .then(response => response.json())
    .then(data => console.log("Прогрес збережено в БД:", data))
    .catch(error => console.error("Помилка збереження:", error));
}
// ==========================================
// 3. ЛОГІКА РОБОТИ ТЕСТУВАННЯ
// ==========================================
// 1. Функція вибору відповіді — окремо (глобально)
function selectOption(btn, choice, correct) {
    // Знімаємо підсвітку з усіх кнопок
    document.querySelectorAll('.option-btn').forEach(b => {
        b.style.background = "#FFFFFF";
    });
    // Підсвічуємо вибрану кнопку
    btn.style.background = "#E8EDFF";

    currentSelected = btn;
    userChoice = choice;
    correctChoice = correct;
}

// 2. Функція відображення питання
function displayQuestion() {
    if (allQuizzes.length === 0) return;

    // Ховаємо кнопку "Далі" і показуємо "Відповісти" на старті кожного питання
    document.getElementById("next-question-btn").style.display = "none";
    document.getElementById("submit-btn").style.display = "block";

    if (currentQuestionIndex >= allQuizzes.length) {
        showSuccess();
        return;
    }

    const quiz = allQuizzes[currentQuestionIndex];
    document.querySelector('.question-title').innerText = quiz.question;

    const btns = [
        document.querySelector('.opt-a'),
        document.querySelector('.opt-b'),
        document.querySelector('.opt-v'),
        document.querySelector('.opt-g')
    ];

    btns.forEach(btn => {
        if (!btn) return;
        btn.style.background = "#FFFFFF";
        btn.style.display = "none";
    });

    const mapping = {'a': btns[0], 'b': btns[1], 'v': btns[2], 'g': btns[3]};
    const options = {'a': quiz.option_a, 'b': quiz.option_b, 'v': quiz.option_v, 'g': quiz.option_g};

    Object.keys(options).forEach(key => {
        if (options[key]) {
            let btn = mapping[key];
            btn.innerText = options[key];
            btn.style.display = "block";
            // Тепер ми викликаємо глобальну функцію
            btn.onclick = () => selectOption(btn, key, quiz.correct_option);
        }
    });

    // Стан кнопок
    document.getElementById("next-lesson-form").style.display = "none";
    document.getElementById("submit-btn").style.display = "block";
}
function checkFinalAnswer() {
    if (!userChoice) {
        alert("Обери варіант відповіді!");
        return;
    }

    if (userChoice === correctChoice) {
        currentSelected.style.background = "#C8E6C9";
        document.getElementById("submit-btn").style.display = "none";

        let nextForm = document.getElementById("next-lesson-form");
        let nextBtn = document.getElementById("next-question-btn");

        if (currentQuestionIndex < allQuizzes.length - 1) {
            // НЕ ОСТАННЄ ПИТАННЯ
            nextBtn.type = "button";
            nextBtn.innerText = "Далі";

            // Робимо видимими і форму, і кнопку
            nextForm.style.setProperty("display", "block", "important");
            nextBtn.style.setProperty("display", "block", "important");

            nextBtn.onclick = function() {
                currentQuestionIndex++;
                displayQuestion();

                // Ховаємо після натискання
                nextForm.style.display = "none";
                nextBtn.style.display = "none";
            };
        } else {
            // ОСТАННЄ ПИТАННЯ
            document.getElementById("quiz-container").style.display = "none";
            const modal = document.getElementById("successModal");
            modal.style.display = "flex";
        }
    } else {
        currentSelected.style.background = "#FFCDD2";
        alert("Неправильна відповідь!");
    }
}
function loadNextQuestion() {
    currentQuestionIndex++;
    displayQuestion();
}
const nextBtn = document.getElementById("next-question-btn");

function showNextButton() {
    // Видаляємо інлайновий стиль display, щоб спрацювали правила з CSS
    nextBtn.style.removeProperty('display');
    nextBtn.style.setProperty('display', 'block', 'important');

    // Переконуємось, що кнопка активна для кліків
    nextBtn.style.pointerEvents = 'auto';
}

function hideNextButton() {
    nextBtn.style.setProperty('display', 'none', 'important');
}
// ==========================================
// 4. СИНХРОНІЗАЦІЯ З БЕКЕНДОМ (DJANGO AJAX)
// ==========================================

function saveProgressOnServer() {
    const csrfTokenEl = document.querySelector('[name=csrfmiddlewaretoken]');
    const lessonNumberEl = document.getElementById('django-lesson-number');

    if (!csrfTokenEl || !lessonNumberEl) {
        console.error("Не знайдено необхідних елементів для збереження прогресу.");
        return;
    }


    const csrftoken = csrfTokenEl.value;
    const lessonNumber = lessonNumberEl.value;

    fetch(`/lesson/${lessonNumber}/complete/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken
        },
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            console.log('Прогрес успішно зафіксовано в базі даних SQLite.');
        } else {
            console.error('Сервер повернув помилку:', data.message);
        }
    })
    .catch(error => console.error('Помилка мережевого запиту fetch:', error));
}
document.addEventListener('DOMContentLoaded', function() {
    const nextBtn = document.getElementById("next-question-btn");

    if (nextBtn) {
        nextBtn.onclick = function() {
            currentQuestionIndex++;
            if (currentQuestionIndex < allQuizzes.length) {
                displayQuestion();
            } else {
                // Якщо питання закінчилися, ховаємо контейнер і показуємо форму
                document.getElementById("quiz-container").style.display = "none";

                // Якщо кнопка всередині форми, то форма вже видима або стає видимою
                let nextForm = document.getElementById("next-lesson-form");
                if (nextForm) {
                    nextForm.style.display = "block";
                }

                // Ховаємо саму кнопку "Далі" (щоб не натиснути двічі)
                nextBtn.style.display = "none";
            }
        };
    }
});