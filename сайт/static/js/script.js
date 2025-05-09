document.addEventListener('DOMContentLoaded', function() {
    const fileInput = document.getElementById('fileInput');
    const uploadBtn = document.getElementById('btnText');
    const previewImage = document.getElementById('previewImage');
    const resultContainer = document.getElementById('resultContainer');
    const resultBreed = document.getElementById('resultBreed');
    const moreInfoBtn = document.getElementById('moreInfoBtn');
    const modal = document.getElementById('infoModal');
    const modalBreed = document.getElementById('modalBreed');
    const breedFacts = document.getElementById('breedFacts');
    const closeBtn = document.querySelector('.close');
    const thinkingText = document.getElementById('thinkingText');

    // Обработка загрузки файла
    fileInput.addEventListener('change', function(e) {
        if (e.target.files.length > 0) {
            const file = e.target.files[0];
            uploadBtn.textContent = "Загрузить другое фото"; // Изменяем текст кнопки

            const reader = new FileReader();
            reader.onload = function(event) {
                previewImage.src = event.target.result;
                resultContainer.classList.remove('hidden');
                thinkingText.classList.remove('hidden');
                moreInfoBtn.classList.add('hidden');

                // Отправка файла на сервер
                const formData = new FormData();
                formData.append('image', file);

                fetch('/api/process', {
                    method: 'POST',
                    body: formData
                })
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Network response was not ok');
                    }
                    return response.json();
                })
                .then(data => {
                    detectBreed(data.breed); // Вызов функции для получения информации о породе
                })
                .catch(error => {
                    console.error('Error:', error);
                    resultBreed.textContent = "Ошибка загрузки файла: " + error.message;
                    thinkingText.classList.add('hidden');
                });
            };
            reader.readAsDataURL(file);
        }
    });

    // Функция определения породы
    function detectBreed(breedEnglish) {
        fetch(`/get_breed_info?breed=${breedEnglish}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                resultBreed.textContent = data.breed_russian;
                currentBreed = data;
                thinkingText.classList.add('hidden');
                moreInfoBtn.classList.remove('hidden');
            })
            .catch(error => {
                console.error('Error:', error);
                resultBreed.textContent = "Ошибка определения породы: " + error.message;
                thinkingText.classList.add('hidden');
            });
    }

    // Открытие модального окна
    moreInfoBtn.addEventListener('click', function() {
        if (currentBreed) {
            modalBreed.textContent = currentBreed.breed_russian;
            breedFacts.innerHTML = `
                <li>${currentBreed.fact1}</li>
                <li>${currentBreed.fact2}</li>
                <li>${currentBreed.fact3}</li>
            `;
            modal.classList.remove('hidden');
            setTimeout(() => {
                modal.style.opacity = '1';
                modal.style.visibility = 'visible';
            }, 10);
        }
    });

    // Закрытие модального окна
    closeBtn.addEventListener('click', function() {
        modal.style.opacity = '0';
        modal.style.visibility = 'hidden';
        setTimeout(() => {
            modal.classList.add('hidden');
        }, 300);
    });

    // Закрытие по клику вне окна
    modal.addEventListener('click', function(e) {
        if (e.target === modal) {
            modal.style.opacity = '0';
            modal.style.visibility = 'hidden';
            setTimeout(() => {
                modal.classList.add('hidden');
            }, 300);
        }
    });

    // Переменная для хранения текущей породы
    let currentBreed = null;
});
