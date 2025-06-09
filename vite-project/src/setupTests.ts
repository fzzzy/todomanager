import '@testing-library/jest-dom';
import { jest } from '@jest/globals';


Object.defineProperty(global, 'fetch', {
  value: jest.fn(),
  writable: true,
});
