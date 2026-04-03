/**
 * SyntaxSprint - Minimalist Typing Test
 * JavaScript (ES6+) - No jQuery
 * Inspired by MonkeyType
 */

const keysToTrack = new Set([
  'Numpad0', 'Numpad1', 'Numpad2', 'Numpad3', 'Numpad4', 'Numpad5', 'Numpad6', 'Numpad7', 'Numpad8', 'Numpad9',
  'NumpadMultiply', 'NumpadAdd', 'NumpadSubtract', 'NumpadDivide', 'NumpadDecimal', 'NumpadEqual',
  'Digit0', 'Digit1', 'Digit2', 'Digit3', 'Digit4', 'Digit5', 'Digit6', 'Digit7', 'Digit8', 'Digit9',
  'Backquote', 'Minus', 'Equal',
  'KeyA', 'KeyB', 'KeyC', 'KeyD', 'KeyE', 'KeyF', 'KeyG', 'KeyH', 'KeyI', 'KeyJ', 'KeyK', 'KeyL', 'KeyM',
  'KeyN', 'KeyO', 'KeyP', 'KeyQ', 'KeyR', 'KeyS', 'KeyT', 'KeyU', 'KeyV', 'KeyW', 'KeyX', 'KeyY', 'KeyZ',
  'BracketLeft', 'BracketRight', 'Backslash',
  'Semicolon', 'Quote', 'Comma', 'Period', 'Slash',
  'Space', 'Enter', 'Tab', 'IntlBackslash',
  'NoCode'
]);

class TypingTest {
  constructor() {
    this.elements = {
      heroSection: document.getElementById('hero-section'),
      testArea: document.getElementById('test-area'),
      resultsSection: document.getElementById('results-section'),
      startBtn: document.getElementById('start-btn'),
      restartBtn: document.getElementById('restart-btn'),
      themeToggle: document.getElementById('theme-toggle'),
      languageSelect: document.getElementById('language-select'),
      wordsInput: document.getElementById('words-input'),
      promptDisplay: document.getElementById('prompt-display'),
      timer: document.getElementById('timer'),
      liveWpm: document.getElementById('live-wpm'),
      liveAcc: document.getElementById('live-acc'),
      wpmResult: document.getElementById('wpm-result'),
      accResult: document.getElementById('acc-result'),
      sunIcon: document.getElementById('sun-icon'),
      moonIcon: document.getElementById('moon-icon'),
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
      spacing: { first: 0, last: 0, array: [] },
      duration: { array: [] },
      keyDownData: {},
      keyOverlap: { total: 0 },
      currentAfk: true,
      afkHistory: [],
      errorHistory: [],
      isInError: false
    };
    
    this.init = this.init.bind(this);
    this.startTest = this.startTest.bind(this);
    this.restartTest = this.restartTest.bind(this);
    this.endTest = this.endTest.bind(this);
    this.toggleTheme = this.toggleTheme.bind(this);
    this.saveResult = this.saveResult.bind(this);
  }
  
  init() {
    this.elements.startBtn.addEventListener('click', () => this.startTest());
    this.elements.restartBtn.addEventListener('click', () => this.restartTest());
    this.elements.themeToggle.addEventListener('click', () => this.toggleTheme());
    
    this.elements.languageSelect.addEventListener('change', (e) => {
      this.state.language = e.target.value;
    });
    
    this.elements.testArea.addEventListener('click', () => {
      if (this.state.active) {
        this.elements.wordsInput.focus();
      }
    });
    
    this.elements.promptDisplay.addEventListener('keydown', (e) => {
      if (e.key === 'Tab' && this.state.active) {
        e.preventDefault();
        this.elements.wordsInput.focus();
      }
    });
    
    window.addEventListener('focus', () => {
      if (this.state.active && !this.state.isFocused) {
        this.elements.wordsInput.focus();
        if (this.state.timerInterval === null && this.state.timeLeft > 0) {
          this.startTimer();
        }
      }
    });
    
    window.addEventListener('blur', () => {
      if (this.state.active && this.state.timerInterval) {
        clearInterval(this.state.timerInterval);
        this.state.timerInterval = null;
      }
    });
    
    document.addEventListener('keydown', this.handleGlobalKeydown);
    document.addEventListener('keyup', this.handleGlobalKeyup);
    
    this.initTheme();
  }
  
  initTheme() {
    const savedTheme = localStorage.getItem('theme') || 'dark';
    document.documentElement.setAttribute('data-theme', savedTheme);
    this.updateThemeIcon(savedTheme);
  }
  
  toggleTheme() {
    const currentTheme = document.documentElement.getAttribute('data-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
    this.updateThemeIcon(newTheme);
  }
  
  updateThemeIcon(theme) {
    if (theme === 'dark') {
      this.elements.sunIcon.classList.remove('hidden');
      this.elements.moonIcon.classList.add('hidden');
    } else {
      this.elements.sunIcon.classList.add('hidden');
      this.elements.moonIcon.classList.remove('hidden');
    }
  }
  
  async startTest() {
    const language = this.elements.languageSelect.value;
    
    try {
      const response = await fetch(apiUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': this.getCookie('csrftoken')
        },
        body: JSON.stringify({ language })
      });
      
      const data = await response.json();
      
      this.elements.heroSection.classList.add('hidden');
      this.elements.resultsSection.classList.add('hidden');
      this.elements.testArea.classList.remove('hidden');
      
      this.state.correctChars = 0;
      this.state.incorrectChars = 0;
      this.state.totalChars = 0;
      this.state.spacing = { first: 0, last: 0, array: [] };
      this.state.duration = { array: [] };
      this.state.keyDownData = {};
      this.state.keyOverlap = { total: 0 };
      this.state.currentAfk = true;
      this.state.afkHistory = [];
      this.state.errorHistory = [];
      this.state.isInError = false;
      
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
        isFocused: true
      };
      
      this.elements.wordsInput.value = '';
      this.elements.wordsInput.focus();
      
      this.startTimer();
      
    } catch (error) {
      console.error('Error starting test:', error);
    }
  }
  
  renderCode(code) {
    const letters = code.split('').map(char => {
      return `<letter>${char}</letter>`;
    }).join('');
    
    this.elements.promptDisplay.innerHTML = letters;
    
    const firstLetter = this.elements.promptDisplay.querySelector('letter');
    if (firstLetter) {
      firstLetter.classList.add('active');
    }
  }
  
  startTimer() {
    this.state.timerInterval = setInterval(() => {
      this.state.timeLeft--;
      this.elements.timer.textContent = this.state.timeLeft;
      
      this.updateLiveStats();
      
      this.state.afkHistory.push(this.state.currentAfk);
      this.state.currentAfk = true;
      
      if (this.state.errorHistory.length > 0 && this.state.errorHistory[this.state.errorHistory.length - 1]?.count > 0) {
        this.state.errorHistory.push({ count: 0, words: [] });
      }
      
      if (this.state.timeLeft <= 0) {
        this.endTest();
      }
    }, 1000);
  }
  
  handleGlobalKeydown = (e) => {
    if (!this.state.active) return;
    const code = e.code;
    if (keysToTrack.has(code)) {
      const now = Date.now();
      if (this.state.spacing.first === 0) {
        this.state.spacing.first = now;
      } else if (this.state.spacing.last !== 0) {
        this.state.spacing.array.push(now - this.state.spacing.last);
      }
      this.state.spacing.last = now;
      this.state.currentAfk = false;
      
      if (this.state.keyDownData[code] !== undefined) {
        this.state.keyOverlap.total += now - this.state.keyDownData[code];
      }
      this.state.keyDownData[code] = now;
    }
  }
  
  handleGlobalKeyup = (e) => {
    if (!this.state.active) return;
    const code = e.code;
    if (keysToTrack.has(code)) {
      const now = Date.now();
      if (this.state.keyDownData[code] !== undefined) {
        this.state.duration.array.push(now - this.state.keyDownData[code]);
        delete this.state.keyDownData[code];
      }
    }
  }
  
  handleInput = (e) => {
    if (!this.state.active || this.state.isComposing) return;
    
    const typedLength = e.target.value.length;
    const prevLength = this.state.totalChars;
    const inputValue = this.elements.wordsInput.value;
    
    if (typedLength > prevLength) {
      for (let i = prevLength; i < typedLength && i < this.state.currentCode.length; i++) {
        const typedChar = inputValue[i];
        const expectedChar = this.state.currentCode[i];
        
        if (typedChar === expectedChar) {
          this.state.correctChars++;
        } else {
          this.state.incorrectChars++;
          this.state.isInError = true;
        }
        this.state.totalChars++;
      }
    }
    
    this.updateDisplay(typedLength);
    this.updateLiveStats();
    
    if (typedLength >= this.state.currentCode.length) {
      this.endTest();
    }
  }
  
  handleKeydown = (e) => {
    if (!this.state.active) return;
    
    const key = e.key;
    const ctrlOrMeta = e.ctrlKey || e.metaKey;
    
    if (key === 'Tab') {
      e.preventDefault();
      this.elements.wordsInput.focus();
      return;
    }
    
    if (key === 'Enter' || key === 'Escape') {
      e.preventDefault();
      return;
    }
    
    if (ctrlOrMeta || (key.startsWith('F') && !isNaN(key.slice(1)))) {
      return;
    }
    
    if (['Control', 'Alt', 'Shift', 'Meta', 'CapsLock', 'NumLock', 'ScrollLock'].includes(key)) {
      return;
    }
    
    if (['ArrowLeft', 'ArrowRight', 'ArrowUp', 'ArrowDown', 'Home', 'End', 'PageUp', 'PageDown'].includes(key)) {
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
        const lastChar = inputValue[inputValue.length - 1];
        const expectedChar = this.state.currentCode[inputValue.length - 1];
        
        if (lastChar === expectedChar) {
          this.state.correctChars = Math.max(0, this.state.correctChars - 1);
        } else {
          this.state.incorrectChars = Math.max(0, this.state.incorrectChars - 1);
        }
        
        this.state.totalChars = Math.max(0, this.state.totalChars - 1);
        e.target.value = inputValue.slice(0, -1);
        const typedLength = e.target.value.length;
        this.updateDisplay(typedLength);
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
  
  handlePaste = (e) => {
    if (!this.state.active) return;
    
    e.preventDefault();
    
    const pastedText = e.clipboardData.getData('text');
    const currentValue = this.elements.wordsInput.value;
    const remainingLength = this.state.currentCode.length - currentValue.length;
    
    if (remainingLength <= 0) return;
    
    const textToInsert = pastedText.slice(0, remainingLength);
    const newValue = currentValue + textToInsert;
    
    this.elements.wordsInput.value = newValue;
    this.updateDisplay(newValue.length);
    this.updateLiveStats();
    
    if (newValue.length >= this.state.currentCode.length) {
      this.endTest();
    }
  }
  
  handleCompositionStart = (e) => {
    if (!this.state.active) return;
    this.state.isComposing = true;
  }
  
  handleCompositionEnd = (e) => {
    if (!this.state.active || !this.state.isComposing) return;
    this.state.isComposing = false;
    
    const composedText = e.data || '';
    if (composedText) {
      const currentValue = this.elements.wordsInput.value;
      const newValue = currentValue + composedText;
      this.elements.wordsInput.value = newValue;
      this.updateDisplay(newValue.length);
      this.updateLiveStats();
      
      if (newValue.length >= this.state.currentCode.length) {
        this.endTest();
      }
    }
  }
  
  handleFocus = () => {
    if (this.state.active) {
      this.state.isFocused = true;
    }
  }
  
  handleBlur = () => {
    this.state.isFocused = false;
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
    
    const timeElapsed = (Date.now() - this.state.startTime) / 1000 / 60;
    
    if (timeElapsed > 0 && this.state.correctChars > 0) {
      const wpm = Math.round((this.state.correctChars / 5) / timeElapsed);
      this.elements.liveWpm.textContent = wpm;
    } else {
      this.elements.liveWpm.textContent = 0;
    }
    
    const totalTyped = this.state.correctChars + this.state.incorrectChars;
    if (totalTyped > 0) {
      const acc = Math.round((this.state.correctChars / totalTyped) * 100);
      this.elements.liveAcc.textContent = acc + '%';
    } else {
      this.elements.liveAcc.textContent = '100%';
    }
  }
  
  endTest() {
    this.state.active = false;
    clearInterval(this.state.timerInterval);
    this.elements.wordsInput.blur();
    
    Object.keys(this.state.keyDownData).forEach((code) => {
      if (this.state.duration.array.length > 0) {
        const avgDuration = this.state.duration.array.reduce((a, b) => a + b, 0) / this.state.duration.array.length;
        this.state.duration.array.push(avgDuration);
      }
      delete this.state.keyDownData[code];
    });
    
    const timeElapsed = (Date.now() - this.state.startTime) / 1000 / 60;
    const testSeconds = timeElapsed * 60;
    
    let wpm = 0;
    let acc = 100;
    
    if (testSeconds > 0) {
      wpm = Math.round((this.state.correctChars / 5) / timeElapsed);
    }
    
    const totalTyped = this.state.correctChars + this.state.incorrectChars;
    if (totalTyped > 0) {
      acc = Math.round((this.state.correctChars / totalTyped) * 100);
    }
    
    this.elements.testArea.classList.add('hidden');
    this.elements.resultsSection.classList.remove('hidden');
    this.elements.wpmResult.textContent = wpm;
    this.elements.accResult.textContent = acc + '%';
    
    this.saveResult(wpm, acc);
  }
  
  async saveResult(wpm, acc) {
    if (typeof saveResultUrl === 'undefined') return;
    
    try {
      await fetch(saveResultUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': this.getCookie('csrftoken')
        },
        body: JSON.stringify({ wpm, accuracy: acc })
      });
    } catch (error) {
      console.error('Error saving result:', error);
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
