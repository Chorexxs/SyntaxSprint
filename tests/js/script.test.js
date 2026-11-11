import { readFileSync } from 'node:fs';
import path from 'node:path';

import { describe, expect, it } from 'vitest';

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
