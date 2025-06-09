import '@testing-library/jest-dom';

declare global {
  namespace jest {
    interface Matchers<R> {
      toBeInTheDocument(): R;
      toBeVisible(): R;
      toBeChecked(): R;
      toHaveValue(value: string | number): R;
      toHaveTextContent(text: string): R;
      toHaveAttribute(attr: string, value?: string): R;
      toHaveClass(className: string): R;
      toBeDisabled(): R;
      toBeEnabled(): R;
      toHaveFocus(): R;
      toBeRequired(): R;
      toBeValid(): R;
      toBeInvalid(): R;
    }
  }
}
