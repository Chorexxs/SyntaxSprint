import { readFileSync } from 'node:fs';
import path from 'node:path';

import { describe, expect, it, vi } from 'vitest';

const scriptPath = path.resolve(
  process.cwd(),
  'syntax_sprint/static/js/script.js'
);
const source = readFileSync(scriptPath, 'utf8');

const { computeWpm, computeAccuracy, TypingTest } = new Function(
  `${source}\nreturn { computeWpm, computeAccuracy, TypingTest };`
)();

describe('computeWpm', () => {
  it('calcula 1 WPM con 5 caracteres en un minuto', () => {
    expect(computeWpm(5, 1)).toBe(1);
  });

  it('calcula 10 WPM con 100 caracteres en dos minutos', () => {
    expect(computeWpm(100, 2)).toBe(10);
  });

  it('devuelve 0 sin tiempo transcurrido', () => {
    expect(computeWpm(50, 0)).toBe(0);
  });
});

describe('computeAccuracy', () => {
  it('calcula 80 % con 8 correctos de 10', () => {
    expect(computeAccuracy(8, 2)).toBe(80);
  });

  it('devuelve 100 % sin pulsaciones', () => {
    expect(computeAccuracy(0, 0)).toBe(100);
  });

  it('devuelve 100 % con todo correcto', () => {
    expect(computeAccuracy(10, 0)).toBe(100);
  });
});

describe('TypingTest.countTypedChars', () => {
  it('cuenta correctos e incorrectos desde el input', () => {
    const test = new TypingTest();
    test.state.currentCode = 'const x = 1;';

    test.countTypedChars('const y');

    expect(test.state.correctChars).toBe(6);
    expect(test.state.incorrectChars).toBe(1);
    expect(test.state.totalChars).toBe(7);
  });

  it('no cuenta los caracteres que exceden el fragmento', () => {
    const test = new TypingTest();
    test.state.currentCode = 'ab';

    test.countTypedChars('abcd');

    expect(test.state.totalChars).toBe(2);
    expect(test.state.correctChars).toBe(2);
    expect(test.state.incorrectChars).toBe(0);
  });
});

function setupDom() {
  document.body.innerHTML = `
    <section id="hero-section"></section>
    <section id="results-section" class="hidden"></section>
    <section id="test-area" class="hidden"></section>
    <button id="start-btn" type="button"></button>
    <button id="restart-btn" type="button"></button>
    <select id="language-select"><option value="python">Python</option></select>
    <textarea id="words-input"></textarea>
    <div id="prompt-display"></div>
    <span id="timer"></span>
    <span id="live-wpm"></span>
    <span id="live-acc"></span>
    <span id="wpm-result"></span>
    <span id="acc-result"></span>
    <p id="save-status" class="hidden"></p>
  `;
  return new TypingTest();
}

describe('TypingTest.updateDisplay', () => {
  it('marca correctos, incorrectos y el carácter activo', () => {
    const test = setupDom();
    test.state.currentCode = 'abc';
    test.renderCode('abc');
    test.elements.wordsInput.value = 'abx';

    test.updateDisplay(3);

    const letters = test.elements.promptDisplay.querySelectorAll('letter');
    expect(letters[0].classList.contains('correct')).toBe(true);
    expect(letters[1].classList.contains('correct')).toBe(true);
    expect(letters[2].classList.contains('incorrect')).toBe(true);
    expect(letters[2].classList.contains('active')).toBe(true);
  });

  it('resalta el siguiente carácter sin marcar el resto', () => {
    const test = setupDom();
    test.state.currentCode = 'abc';
    test.renderCode('abc');
    test.elements.wordsInput.value = 'a';

    test.updateDisplay(1);

    const letters = test.elements.promptDisplay.querySelectorAll('letter');
    expect(letters[0].classList.contains('correct')).toBe(true);
    expect(letters[1].classList.contains('active')).toBe(true);
    expect(letters[2].classList.contains('active')).toBe(false);
    expect(letters[2].classList.contains('correct')).toBe(false);
    expect(letters[2].classList.contains('incorrect')).toBe(false);
  });
});

function pasteEvent(text) {
  return {
    preventDefault: vi.fn(),
    clipboardData: { getData: vi.fn(() => text) },
  };
}

describe('TypingTest.handlePaste', () => {
  it('inserta el texto, actualiza contadores y evita el pegado nativo', () => {
    const test = setupDom();
    test.state.active = true;
    test.state.currentCode = 'const x = 1;';
    test.renderCode(test.state.currentCode);

    const event = pasteEvent('const');
    test.handlePaste(event);

    expect(event.preventDefault).toHaveBeenCalledTimes(1);
    expect(test.elements.wordsInput.value).toBe('const');
    expect(test.state.correctChars).toBe(5);
    expect(test.state.incorrectChars).toBe(0);
    expect(test.state.totalChars).toBe(5);
  });

  it('recorta lo pegado al fragmento restante y termina el test', () => {
    const test = setupDom();
    test.state.active = true;
    test.state.currentCode = 'ab';
    test.state.startTime = Date.now() - 30_000;
    test.renderCode('ab');

    test.handlePaste(pasteEvent('abcdef'));

    expect(test.elements.wordsInput.value).toBe('ab');
    expect(test.state.correctChars).toBe(2);
    expect(test.state.active).toBe(false);
    expect(test.elements.resultsSection.classList.contains('hidden')).toBe(false);
  });

  it('ignora el pegado si el test no está activo', () => {
    const test = setupDom();
    test.state.active = false;

    const event = pasteEvent('const');
    test.handlePaste(event);

    expect(event.preventDefault).not.toHaveBeenCalled();
    expect(test.elements.wordsInput.value).toBe('');
  });
});

describe('TypingTest.restartTest', () => {
  it('oculta resultados, muestra el test y lo reinicia', () => {
    const test = setupDom();
    test.elements.resultsSection.classList.remove('hidden');
    test.elements.testArea.classList.add('hidden');
    test.startTest = vi.fn();

    test.restartTest();

    expect(test.elements.resultsSection.classList.contains('hidden')).toBe(true);
    expect(test.elements.testArea.classList.contains('hidden')).toBe(false);
    expect(test.startTest).toHaveBeenCalledTimes(1);
  });
});

describe('TypingTest — código multilínea', () => {
  it('no bloquea Enter y cuenta el salto de línea', () => {
    const test = setupDom();
    test.state.active = true;
    test.state.currentCode = 'a\nb';
    test.state.startTime = Date.now();
    test.renderCode(test.state.currentCode);
    const input = test.elements.wordsInput;

    const event = {
      key: 'Enter',
      preventDefault: vi.fn(),
      target: input,
      ctrlKey: false,
      metaKey: false,
      altKey: false,
    };
    test.handleKeydown(event);

    input.value = 'a\n';
    test.handleInput({ target: input });

    expect(event.preventDefault).not.toHaveBeenCalled();
    expect(test.state.correctChars).toBe(2);
    expect(test.state.incorrectChars).toBe(0);
    const letters = test.elements.promptDisplay.querySelectorAll('letter');
    expect(letters[1].classList.contains('correct')).toBe(true);
  });

  it('inserta la indentación esperada con Tab (2, 4 y 8 espacios)', () => {
    for (const spaces of [2, 4, 8]) {
      const test = setupDom();
      test.state.active = true;
      test.state.currentCode = `x\n${' '.repeat(spaces)}y`;
      test.state.startTime = Date.now();
      test.elements.wordsInput.value = 'x\n';

      const event = {
        key: 'Tab',
        preventDefault: vi.fn(),
        target: test.elements.wordsInput,
      };
      test.handleKeydown(event);

      expect(event.preventDefault).toHaveBeenCalledTimes(1);
      expect(test.elements.wordsInput.value).toBe(`x\n${' '.repeat(spaces)}`);
      expect(test.state.correctChars).toBe(2 + spaces);
    }
  });

  it('no inserta espacios si la línea no está indentada', () => {
    const test = setupDom();
    test.state.active = true;
    test.state.currentCode = 'abc';
    test.state.startTime = Date.now();
    test.elements.wordsInput.value = 'a';

    test.insertIndentation();

    expect(test.elements.wordsInput.value).toBe('a');
  });
});

describe('TypingTest — pausa', () => {
  it('no cuenta el tiempo en pausa en el WPM', () => {
    vi.useFakeTimers();
    vi.setSystemTime(new Date('2026-01-01T00:00:00Z'));
    try {
      const test = setupDom();
      test.state.active = true;
      test.state.currentCode = 'abcde';
      test.state.startTime = Date.now();
      test.state.correctChars = 5;
      test.startTimer();

      vi.advanceTimersByTime(1000);
      test.pauseTest();
      vi.advanceTimersByTime(5000);
      test.resumeTest();
      vi.advanceTimersByTime(1000);

      expect(test.elapsedMinutes()).toBeCloseTo(2 / 60, 5);
      expect(test.elements.liveWpm.textContent).toBe('30');
    } finally {
      vi.useRealTimers();
    }
  });
});

describe('TypingTest — IME', () => {
  it('no duplica el carácter compuesto', () => {
    const test = setupDom();
    test.state.active = true;
    test.state.currentCode = 'ábc';
    test.state.startTime = Date.now();
    const input = test.elements.wordsInput;

    test.handleCompositionStart({});
    input.value = 'á';
    test.handleCompositionEnd({ data: 'á' });

    expect(input.value).toBe('á');
    expect(test.state.correctChars).toBe(1);
    expect(test.state.totalChars).toBe(1);
  });
});

describe('TypingTest — timer', () => {
  it('muestra 30 al comenzar y no el valor del test anterior', async () => {
    const test = setupDom();
    test.elements.timer.textContent = '0';
    vi.stubGlobal(
      'fetch',
      vi.fn(() => Promise.resolve({ json: () => Promise.resolve({ code: 'abc' }) }))
    );
    try {
      await test.startTest();
      test.stopTimer();

      expect(test.elements.timer.textContent).toBe('30');
      expect(test.state.timeLeft).toBe(30);
    } finally {
      vi.unstubAllGlobals();
      test.stopTimer();
    }
  });
});
