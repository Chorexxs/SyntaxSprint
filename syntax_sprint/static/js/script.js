$(document).ready(function () {
    $("#start-test").click(function () {
      const testHTML = `
            <main id="game">
                <section>
                    <time>30</time>
                    <p id="code-area"></p>  <!-- Aquí es donde se mostrará el código -->
                    <input autofocus>
                </section>
                <section id="results">
                    <h2>WPM</h2>
                    <h3 id="results-wpm"></h3>
                    <h2>Precisión</h2>
                    <h3 id="results-accuracy"></h3>
                </section>
            </main>
        `;
  
      // Inserta el HTML dinámico en el DOM
      $("#test-area").html(testHTML).show();
  
      if (!$("link[href$='css/styles.css']").length) {
        $("<link/>", {
          rel: "stylesheet",
          type: "text/css",
          href: "{% static 'css/styles.css' %}",
        }).appendTo("head");
      }
  
      fetch(apiUrl)
        .then((response) => response.json())
        .then((data) => {
          const code = data.code;
          const codeArea = document.getElementById("code-area");
  
          const words = code.split(/\s+/);
          codeArea.innerHTML = words
            .map((word) => {
              return `<word>${word
                .split("")
                .map((letter) => `<letter>${letter}</letter>`)
                .join("")}</word>`;
            })
            .join(" ");
  
          initGame();
        })
        .catch((error) => {
          console.error("Error al obtener el código:", error);
        });
  
      function initGame() {
        const $time = document.querySelector("time");
        const $paragraph = document.querySelector("p");
        const $input = document.querySelector("input");
        const $results = document.querySelector("#results");
        const $wpm = $results.querySelector("#results-wpm");
        const $accuracy = $results.querySelector("#results-accuracy");
  
        let playing = false;
        let currentTime = 30;
        let intervalId;
        $time.textContent = currentTime;
  
        const $firstWord = $paragraph.querySelector("word");
        if ($firstWord) {
          $firstWord.classList.add("active");
          $firstWord.querySelector("letter").classList.add("active");
        }
  
        document.addEventListener("keydown", () => {
          $input.focus();
          if (!playing) {
            playing = true;
            intervalId = setInterval(() => {
              currentTime--;
              $time.textContent = currentTime;
  
              if (currentTime === 0) {
                clearInterval(intervalId);
                gameOver();
              }
            }, 1000);
          }
        });
  
        $input.addEventListener("keydown", onKeyDown);
        $input.addEventListener("keyup", onKeyUp);
  
        function onKeyDown(event) {
          const $currentWord = $paragraph.querySelector("word.active");
          const $currentLetter = $currentWord?.querySelector("letter.active");
  
          const { key } = event;
          if (key === " ") {
            event.preventDefault();
            const $nextWord = $currentWord?.nextElementSibling;
            const $nextLetter = $nextWord?.querySelector("letter");
  
            $currentWord?.classList.remove("active", "marked");
            $currentLetter?.classList.remove("active");
  
            if ($nextWord) {
              $nextWord.classList.add("active");
              $nextLetter?.classList.add("active");
            }
  
            $input.value = "";
  
            const hasMissedLetters =
              $currentWord?.querySelectorAll("letter:not(.correct)").length > 0;
            $currentWord?.classList.add(hasMissedLetters ? "marked" : "correct");
  
            if (!$nextWord) {
              clearInterval(intervalId); // Detener el temporizador si termina de escribir todas las palabras
              gameOver();
            }
            return;
          }
  
          if (key === "Backspace") {
            const $prevWord = $currentWord?.previousElementSibling;
            const $prevLetter = $currentLetter?.previousElementSibling;
  
            if (!$prevWord && !$prevLetter) {
              event.preventDefault();
              return;
            }
  
            const $wordMarked = $paragraph.querySelector("word.marked");
            if ($wordMarked && !$prevLetter) {
              event.preventDefault();
              $prevWord.classList.remove("marked");
              $prevWord.classList.add("active");
  
              const $letterToGo = $prevWord.querySelector("letter:last-child");
  
              $currentLetter?.classList.remove("active");
              $letterToGo.classList.add("active");
  
              $input.value = [
                ...$prevWord.querySelectorAll("letter.correct, letter.incorrect"),
              ]
                .map(($el) => {
                  return $el.classList.contains("correct")
                    ? $el.innerText
                    : "*";
                })
                .join("");
            }
          }
        }
  
        function onKeyUp() {
          const $currentWord = $paragraph.querySelector("word.active");
          const $currentLetter = $currentWord?.querySelector("letter.active");
  
          const currentWord = $currentWord?.innerText.trim();
          $input.maxLength = currentWord?.length || 0;
  
          const $allLetters = $currentWord?.querySelectorAll("letter");
  
          $allLetters?.forEach(($letter) =>
            $letter.classList.remove("correct", "incorrect")
          );
  
          $input.value.split("").forEach((char, index) => {
            const $letter = $allLetters[index];
            const isCorrect = char === currentWord[index];
            $letter.classList.add(isCorrect ? "correct" : "incorrect");
          });
  
          $currentLetter?.classList.remove("active", "is-last");
          const inputLength = $input.value.length;
          const $nextActiveLetter = $allLetters?.[inputLength];
  
          if ($nextActiveLetter) {
            $nextActiveLetter.classList.add("active");
          } else {
            $currentLetter?.classList.add("active", "is-last");
            if (!$currentWord?.nextElementSibling) {
              clearInterval(intervalId); // Detener el temporizador si el usuario termina de escribir
              gameOver();
            }
          }
        }
  
        function gameOver() {
          const correctWords = $paragraph.querySelectorAll("word.correct").length;
          const correctLetter = $paragraph.querySelectorAll("letter.correct").length;
          const incorrectLetter = $paragraph.querySelectorAll("letter.incorrect").length;
      
          const totalLetters = correctLetter + incorrectLetter;
          const accuracy = totalLetters > 0 ? (correctLetter / totalLetters) * 100 : 0;
          const wpm = (correctWords * 60) / 30;
      
          $wpm.textContent = wpm;
          $accuracy.textContent = `${accuracy.toFixed(2)}%`;
      
          $results.style.display = "block";

           // Deshabilitar el campo de entrada para evitar que el usuario siga escribiendo
          $input.setAttribute("disabled", "disabled");
      
          // Enviar resultados al servidor
          fetch(saveResultUrl, {
              method: "POST",
              headers: {
                  "Content-Type": "application/json",
                  "X-CSRFToken": getCookie('csrftoken')
              },
              body: JSON.stringify({
                  wpm: wpm,
                  accuracy: accuracy.toFixed(2)
              })
          })
          .then(response => response.json())
          .then(data => {
              if (data.message) {
                  console.log("Resultados guardados exitosamente");
              } else {
                  console.error("Error al guardar los resultados:", data.error);
              }
          })
          .catch(error => {
              console.error("Error al guardar los resultados:", error);
          });
      }
      
      // Función para obtener el token CSRF
      function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    
      
      }
    });
  });
  
