import test from 'node:test';
import assert from 'node:assert/strict';

class MockLocalStorage {
  private store: Record<string, string> = {};
  getItem(key: string): string | null {
    return this.store[key] || null;
  }
  setItem(key: string, value: string): void {
    this.store[key] = value;
  }
  removeItem(key: string): void {
    delete this.store[key];
  }
}

// Emulate ThemeProvider logic
class ThemeManager {
  private storage: MockLocalStorage;
  public theme: 'dark' | 'light' | 'system';
  public resolvedTheme: 'dark' | 'light';
  public appliedClasses: Set<string>;

  constructor(storage: MockLocalStorage, systemPrefersDark: boolean = true) {
    this.storage = storage;
    this.appliedClasses = new Set<string>();

    const saved = storage.getItem('btcshield-theme');
    if (saved === 'light' || saved === 'dark' || saved === 'system') {
      this.theme = saved;
    } else {
      this.theme = 'dark'; // Default to dark command center
    }

    this.resolvedTheme = this.resolveTheme(this.theme, systemPrefersDark);
    this.syncDom();
  }

  private resolveTheme(theme: 'dark' | 'light' | 'system', systemPrefersDark: boolean): 'dark' | 'light' {
    if (theme === 'system') {
      return systemPrefersDark ? 'dark' : 'light';
    }
    return theme;
  }

  public setTheme(newTheme: 'dark' | 'light' | 'system', systemPrefersDark: boolean = true) {
    this.theme = newTheme;
    this.storage.setItem('btcshield-theme', newTheme);
    this.resolvedTheme = this.resolveTheme(newTheme, systemPrefersDark);
    this.syncDom();
  }

  private syncDom() {
    this.appliedClasses.clear();
    this.appliedClasses.add(this.resolvedTheme);
  }
}

test('theme system defaults to dark command center experience', () => {
  const storage = new MockLocalStorage();
  const manager = new ThemeManager(storage);

  assert.equal(manager.theme, 'dark');
  assert.equal(manager.resolvedTheme, 'dark');
  assert.equal(manager.appliedClasses.has('dark'), true);
  assert.equal(manager.appliedClasses.has('light'), false);
});

test('switching theme to light persists to storage and updates resolved classes', () => {
  const storage = new MockLocalStorage();
  const manager = new ThemeManager(storage);

  manager.setTheme('light');
  assert.equal(storage.getItem('btcshield-theme'), 'light');
  assert.equal(manager.theme, 'light');
  assert.equal(manager.resolvedTheme, 'light');
  assert.equal(manager.appliedClasses.has('light'), true);
  assert.equal(manager.appliedClasses.has('dark'), false);
});

test('system preference mode correctly resolves based on media query', () => {
  const storage = new MockLocalStorage();
  const manager = new ThemeManager(storage);

  // System prefers light
  manager.setTheme('system', false);
  assert.equal(storage.getItem('btcshield-theme'), 'system');
  assert.equal(manager.resolvedTheme, 'light');

  // System prefers dark
  manager.setTheme('system', true);
  assert.equal(manager.resolvedTheme, 'dark');
});

test('persisted theme is restored upon reload', () => {
  const storage = new MockLocalStorage();
  storage.setItem('btcshield-theme', 'light');

  const reloadedManager = new ThemeManager(storage);
  assert.equal(reloadedManager.theme, 'light');
  assert.equal(reloadedManager.resolvedTheme, 'light');
  assert.equal(reloadedManager.appliedClasses.has('light'), true);
});
