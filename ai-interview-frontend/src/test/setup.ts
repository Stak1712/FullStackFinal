import "@testing-library/jest-dom/vitest";
import { afterEach, beforeEach, vi } from "vitest";
import { cleanup } from "@testing-library/react";

type StorageMock = Storage & { _store: Record<string, string> };

function createStorageMock(): StorageMock {
  const storage = {
    _store: {} as Record<string, string>,
    get length() {
      return Object.keys(this._store).length;
    },
    clear() {
      this._store = {};
    },
    getItem(key: string) {
      return Object.prototype.hasOwnProperty.call(this._store, key) ? this._store[key] : null;
    },
    key(index: number) {
      return Object.keys(this._store)[index] ?? null;
    },
    removeItem(key: string) {
      delete this._store[key];
    },
    setItem(key: string, value: string) {
      this._store[key] = String(value);
    },
  };

  return storage as StorageMock;
}

const testLocalStorage = createStorageMock();

Object.defineProperty(globalThis, "localStorage", {
  value: testLocalStorage,
  configurable: true,
});

Object.defineProperty(window, "localStorage", {
  value: testLocalStorage,
  configurable: true,
});

beforeEach(() => {
  testLocalStorage.clear();
});

afterEach(() => {
  cleanup();
  vi.clearAllMocks();
  vi.useRealTimers();
});
