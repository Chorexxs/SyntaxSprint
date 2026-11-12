/**
 * SyntaxSprint - Minimalist Typing Test
 * JavaScript (ES6+) - No jQuery
 * Inspired by MonkeyType
 */

/**
 * WPM = (caracteres correctos / 5) / minutos transcurridos (RF-004-04).
 * @param {number} correctChars
 * @param {number} elapsedMinutes
 * @returns {number}
 */
function computeWpm(correctChars, elapsedMinutes) {
  if (elapsedMinutes <= 0) return 0;
  return Math.round((correctChars / 5) / elapsedMinutes);
}

/**
 * Precisión = correctos / (correctos + incorrectos) × 100 (RF-004-05).
 * @param {number} correctChars
 * @param {number} incorrectChars
 * @returns {number}
 */
function computeAccuracy(correctChars, incorrectChars) {
  const total = correctChars + incorrectChars;
  if (total === 0) return 100;
  return Math.round((correctChars / total) * 100);
}

class TypingTest {
  constructor() {
    this.elements = {
      heroSection: document.getElementById('hero-section'),
      testArea: document.getElementById('test-area'),
      resultsSection: document.getElementById('results-section'),
      startBtn: document.getElementById('start-btn'),
      restartBtn: document.getElementById('restart-btn'),
      languageSelect: document.getElementById('language-select'),
      wordsInput: document.getElementById('words-input'),
      promptDisplay: document.getElementById('prompt-display'),
      timer: document.getElementById('timer'),
      liveWpm: document.getElementById('live-wpm'),
      liveAcc: document.getElementById('live-acc'),
      wpmResult: document.getElementById('wpm-result'),
      accResult: document.getElementById('acc-result'),
      startError: document.getElementById('start-error'),
    };

    this.state = {
      active: false,
      testTime: 30,
      timeLeft: 30,
      currentCode: '',
      startTime: null,
      timerInterval: null,
      language: 'python',
      isComposing: false,
      isFocused: true,
      correctChars: 0,
      incorrectChars: 0,
      totalChars: 0,
      pausedMs: 0,
      pauseStartedAt: null,
      starting: false
    };

    this.init = this.init.bind(this);
    this.startTest = this.startTest.bind(this);
    this.restartTest = this.restartTest.bind(this);
    this.endTest = this.endTest.bind(this);
    this.saveResult = this.saveResult.bind(this);
  }

  init() {
    this.elements.startBtn.addEventListener('click', () => this.startTest());
    this.elements.restartBtn.addEventListener('click', () => this.restartTest());

    this.elements.languageSelect.addEventListener('change', (e) => {
      this.state.language = e.target.value;
    });

    this.elements.testArea.addEventListener('click', () => {
      if (this.state.active) {
        this.elements.wordsInput.focus();
      }
    });

    window.addEventListener('focus', () => {
      if (!this.state.active) return;
      if (!this.state.isFocused) {
        this.elements.wordsInput.focus();
      }
      if (this.state.timerInterval === null && this.state.timeLeft > 0) {
        this.resumeTest();
      }
    });

    window.addEventListener('blur', () => {
      if (this.state.active) {
        this.pauseTest();
      }
    });
  }

  async startTest() {
    if (this.state.starting) return;

    this.state.starting = true;
    this.stopTimer();
    this.hideStartError();
    const language = this.elements.languageSelect.value;

    try {
      const response = await fetch(document.body.dataset.apiUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': this.getCookie('csrftoken')
        },
        body: JSON.stringify({ language })
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const data = await response.json();
      if (!data || typeof data.code !== 'string' || !data.code) {
        throw new Error('Fragmento no válido');
      }

      this.elements.heroSection.classList.add('hidden');
      this.elements.resultsSection.classList.add('hidden');
      this.elements.testArea.classList.remove('hidden');

      this.state.correctChars = 0;
      this.state.incorrectChars = 0;
      this.state.totalChars = 0;

      this.renderCode(data.code);

      this.state = {
        ...this.state,
        active: true,
        testTime: 30,
        timeLeft: 30,
        currentCode: data.code,
        startTime: Date.now(),
        timerInterval: null,
        language,
        isComposing: false,
        isFocused: true,
        pausedMs: 0,
        pauseStartedAt: null
      };

      this.elements.timer.textContent = this.state.timeLeft;
      this.elements.wordsInput.value = '';
      this.elements.wordsInput.focus();

      this.startTimer();

    } catch (error) {
      console.error('Error starting test:', error);
      this.showStartError('No se pudo cargar el fragmento. Inténtalo de nuevo.');
    } finally {
      this.state.starting = false;
    }
  }

  showStartError(message) {
    this.state.active = false;
    this.stopTimer();
    this.elements.heroSection.classList.remove('hidden');
    this.elements.testArea.classList.add('hidden');
    this.elements.resultsSection.classList.add('hidden');
    if (this.elements.startError) {
      this.elements.startError.textContent = message;
      this.elements.startError.classList.remove('hidden');
    }
  }

  hideStartError() {
    if (this.elements.startError) {
      this.elements.startError.textContent = '';
      this.elements.startError.classList.add('hidden');
    }
  }

  renderCode(code) {
    const fragment = document.createDocumentFragment();
    code.split('').forEach(char => {
      const letter = document.createElement('letter');
      letter.textContent = char;
      fragment.appendChild(letter);
    });

    this.elements.promptDisplay.replaceChildren(fragment);

    const firstLetter = this.elements.promptDisplay.querySelector('letter');
    if (firstLetter) {
      firstLetter.classList.add('active');
    }
  }

  startTimer() {
    this.stopTimer();
    this.state.timerInterval = setInterval(() => {
      this.state.timeLeft--;
      this.elements.timer.textContent = this.state.timeLeft;

      this.updateLiveStats();

      if (this.state.timeLeft <= 0) {
        this.endTest();
      }
    }, 1000);
  }

  stopTimer() {
    if (this.state.timerInterval !== null) {
      clearInterval(this.state.timerInterval);
      this.state.timerInterval = null;
    }
  }

  pauseTest() {
    if (this.state.pauseStartedAt === null) {
      this.state.pauseStartedAt = Date.now();
    }
    this.stopTimer();
  }

  resumeTest() {
    if (this.state.pauseStartedAt !== null) {
      this.state.pausedMs += Date.now() - this.state.pauseStartedAt;
      this.state.pauseStartedAt = null;
    }
    this.startTimer();
  }

  elapsedMinutes() {
    if (!this.state.startTime) return 0;

    const now = this.state.pauseStartedAt ?? Date.now();
    const elapsedMs = Math.max(
      now - this.state.startTime - this.state.pausedMs,
      0
    );
    return elapsedMs / 1000 / 60;
  }

  handleInput = (e) => {
    if (!this.state.active || this.state.isComposing) return;

    this.syncTypedValue(e.target.value);
  }

  /**
   * Recalcula contadores y pinta el input actual.
   *
   * Centraliza el bloque que compartían input, Enter, Tab, pegado e IME
   * para que un cambio de recuento no se olvide en ningún manejador.
   */
  syncTypedValue(value) {
    this.elements.wordsInput.value = value;
    this.countTypedChars(value);
    this.updateDisplay(value.length);
    this.updateLiveStats();

    if (value.length >= this.state.currentCode.length) {
      this.endTest();
    }
  }

  /**
   * Recalcula los contadores desde el valor actual del input.
   *
   * Evita que pegar, borrar o una composición IME desincronicen
   * `correctChars`/`incorrectChars`/`totalChars` (T004-10).
   */
  countTypedChars(value) {
    let correctChars = 0;
    let incorrectChars = 0;
    const limit = Math.min(value.length, this.state.currentCode.length);

    for (let i = 0; i < limit; i++) {
      if (value[i] === this.state.currentCode[i]) {
        correctChars++;
      } else {
        incorrectChars++;
      }
    }

    this.state.correctChars = correctChars;
    this.state.incorrectChars = incorrectChars;
    this.state.totalChars = limit;
  }

  handleKeydown = (e) => {
    if (!this.state.active) return;

    const key = e.key;
    const ctrlOrMeta = e.ctrlKey || e.metaKey;

    if (key === 'Tab') {
      e.preventDefault();
      this.insertIndentation();
      return;
    }

    if (key === 'Escape') {
      e.preventDefault();
      return;
    }

    if (key === 'Enter') {
      e.preventDefault();
      if (!ctrlOrMeta) {
        this.insertNewline();
      }
      return;
    }

    if (ctrlOrMeta || (key.startsWith('F') && !isNaN(key.slice(1)))) {
      return;
    }

    if (['Control', 'Alt', 'Shift', 'Meta', 'CapsLock', 'NumLock', 'ScrollLock'].includes(key)) {
      return;
    }

    const navigationKeys = [
      'ArrowLeft', 'ArrowRight', 'ArrowUp', 'ArrowDown',
      'Home', 'End', 'PageUp', 'PageDown',
    ];

    if (navigationKeys.includes(key)) {
      e.preventDefault();
      this.elements.wordsInput.focus();
      setTimeout(() => {
        const input = this.elements.wordsInput;
        input.setSelectionRange(input.value.length, input.value.length);
      }, 0);
      return;
    }

    if (key === 'Backspace') {
      const inputValue = e.target.value;
      if (inputValue.length > 0) {
        e.target.value = inputValue.slice(0, -1);
        this.countTypedChars(e.target.value);
        this.updateDisplay(e.target.value.length);
        this.updateLiveStats();
      }
      e.preventDefault();
      return;
    }

    if (key === ' ' && e.target.value.length === 0) {
      e.preventDefault();
      return;
    }

    if (key.length === 1 && !e.altKey && !e.ctrlKey && !e.metaKey) {
      if (this.elements.wordsInput !== document.activeElement) {
        this.elements.wordsInput.focus();
      }
    }
  }

  insertNewline() {
    if (!this.state.active) return;

    const input = this.elements.wordsInput;
    const code = this.state.currentCode;
    const position = input.value.length;
    const room = code.length - position;
    if (room <= 0) return;

    let text = '\n';
    if (code[position] === '\n') {
      const indent = code.slice(position + 1).match(/^[ \t]+/);
      if (indent) {
        text += indent[0].slice(0, room - 1);
      }
    }

    input.value += text;
    this.syncTypedValue(input.value);
  }

  insertIndentation() {
    if (!this.state.active) return;

    const input = this.elements.wordsInput;
    const remaining = this.state.currentCode.slice(input.value.length);
    const indent = remaining.match(/^ +/);
    if (!indent) return;

    const room = this.state.currentCode.length - input.value.length;
    input.value += indent[0].slice(0, room);
    this.syncTypedValue(input.value);
  }

  handlePaste = (e) => {
    if (!this.state.active) return;

    e.preventDefault();

    const pastedText = e.clipboardData.getData('text');
    const currentValue = this.elements.wordsInput.value;
    const remainingLength = this.state.currentCode.length - currentValue.length;

    if (remainingLength <= 0) return;

    const textToInsert = pastedText.slice(0, remainingLength);
    const newValue = currentValue + textToInsert;

    this.syncTypedValue(newValue);
  }

  handleCompositionStart = (e) => {
    if (!this.state.active) return;
    this.state.isComposing = true;
  }

  handleCompositionEnd = () => {
    if (!this.state.active || !this.state.isComposing) return;
    this.state.isComposing = false;
    this.syncTypedValue(this.elements.wordsInput.value);
  }

  handleFocus = () => {
    if (!this.state.active) return;
    this.state.isFocused = true;
    if (this.state.timerInterval === null && this.state.timeLeft > 0) {
      this.resumeTest();
    }
  }

  handleBlur = () => {
    this.state.isFocused = false;
    if (this.state.active) {
      this.pauseTest();
    }
  }

  updateDisplay(typedLength) {
    const letters = this.elements.promptDisplay.querySelectorAll('letter');
    const inputValue = this.elements.wordsInput.value;

    letters.forEach(letter => {
      letter.classList.remove('correct', 'incorrect', 'active');
    });

    for (let i = 0; i < typedLength && i < letters.length; i++) {
      const typedChar = inputValue[i];
      const expectedChar = this.state.currentCode[i];
      const letter = letters[i];

      if (typedChar === expectedChar) {
        letter.classList.add('correct');
      } else {
        letter.classList.add('incorrect');
      }
    }

    const activeIndex = Math.min(typedLength, letters.length - 1);
    if (activeIndex >= 0 && activeIndex < letters.length) {
      letters[activeIndex].classList.add('active');
    }
  }

  updateLiveStats() {
    if (!this.state.startTime) return;

    const elapsedMinutes = this.elapsedMinutes();

    this.elements.liveWpm.textContent = computeWpm(
      this.state.correctChars,
      elapsedMinutes
    );
    this.elements.liveAcc.textContent =
      computeAccuracy(this.state.correctChars, this.state.incorrectChars) + '%';
  }

  endTest() {
    this.state.active = false;
    this.stopTimer();
    this.elements.wordsInput.blur();

    const elapsedMinutes = this.elapsedMinutes();
    this.state.pauseStartedAt = null;
    const wpm = computeWpm(this.state.correctChars, elapsedMinutes);
    const acc = computeAccuracy(this.state.correctChars, this.state.incorrectChars);

    this.elements.testArea.classList.add('hidden');
    this.elements.resultsSection.classList.remove('hidden');
    this.elements.wpmResult.textContent = wpm;
    this.elements.accResult.textContent = acc + '%';

    this.saveResult(wpm, acc);
  }

  async saveResult(wpm, acc) {
    const status = document.getElementById('save-status');
    const saveResultUrl = document.body.dataset.saveUrl;
    if (!saveResultUrl) return;

    try {
      const response = await fetch(saveResultUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': this.getCookie('csrftoken')
        },
        body: JSON.stringify({ wpm, accuracy: acc }),
        redirect: 'manual'
      });

      if (response.type === 'opaqueredirect' || response.status === 302) {
        if (status) {
          status.textContent = 'Inicia sesión para guardar tu resultado.';
          status.classList.remove('hidden');
        }
        return;
      }

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      if (status) {
        status.textContent = 'Resultado guardado.';
        status.classList.remove('hidden');
      }
    } catch (error) {
      console.error('Error saving result:', error);
      if (status) {
        status.textContent = 'No se pudo guardar el resultado.';
        status.classList.remove('hidden');
      }
    }
  }

  restartTest() {
    this.elements.resultsSection.classList.add('hidden');
    this.elements.testArea.classList.remove('hidden');
    this.startTest();
  }

  getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
      const cookies = document.cookie.split(';');
      for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        if (cookie.substring(0, name.length + 1) === name + '=') {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }
}

document.addEventListener('DOMContentLoaded', () => {
  const typingTest = new TypingTest();
  typingTest.init();

  const input = document.getElementById('words-input');
  input.addEventListener('input', typingTest.handleInput);
  input.addEventListener('keydown', typingTest.handleKeydown);
  input.addEventListener('paste', typingTest.handlePaste);
  input.addEventListener('compositionstart', typingTest.handleCompositionStart);
  input.addEventListener('compositionend', typingTest.handleCompositionEnd);
  input.addEventListener('focus', typingTest.handleFocus);
  input.addEventListener('blur', typingTest.handleBlur);
});
