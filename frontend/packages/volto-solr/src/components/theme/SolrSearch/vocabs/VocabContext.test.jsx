import { render, screen, act } from '@testing-library/react';
import { useContext, useState } from 'react';
import { VocabContext, VocabProvider } from './VocabContext';

describe('VocabProvider', () => {
  const TestComponent = () => {
    const { isVocabRequested, setVocabRequested, resetContext } =
      useContext(VocabContext);
    const [, rerender] = useState(false);
    return (
      <div>
        <div data-testid="vocab-state">
          {isVocabRequested('test').toString()}
        </div>
        <button onClick={() => setVocabRequested('test')}>Set Vocab</button>
        <button
          onClick={() => {
            rerender((b) => !b);
          }}
        >
          Rerender
        </button>
        <button onClick={resetContext}>Reset</button>
      </div>
    );
  };

  const addTests = (TestComponent) => {
    test('provides initial context state', () => {
      render(
        <VocabProvider>
          <TestComponent />
        </VocabProvider>,
      );
      expect(screen.getByTestId('vocab-state').textContent).toBe('false');
      act(() => {
        screen.getByRole('button', { name: 'Rerender' }).click();
      });
      expect(screen.getByTestId('vocab-state').textContent).toBe('false');
    });

    test('updates vocab state when requested', async () => {
      render(
        <VocabProvider>
          <TestComponent />
        </VocabProvider>,
      );

      screen.getByRole('button', { name: 'Set Vocab' }).click();
      act(() => {
        screen.getByRole('button', { name: 'Rerender' }).click();
      });
      expect(screen.getByTestId('vocab-state').textContent).toBe('true');
    });

    test('does not re-render component when the context has changed', async () => {
      render(
        <VocabProvider>
          <TestComponent />
        </VocabProvider>,
      );
      screen.getByRole('button', { name: 'Set Vocab' }).click();
      expect(screen.getByTestId('vocab-state').textContent).toBe('false');
    });

    test('resets context state', () => {
      render(
        <VocabProvider>
          <TestComponent />
        </VocabProvider>,
      );
      screen.getByRole('button', { name: 'Set Vocab' }).click();
      act(() => {
        screen.getByRole('button', { name: 'Rerender' }).click();
      });
      expect(screen.getByTestId('vocab-state').textContent).toBe('true');
      act(() => {
        screen.getByRole('button', { name: 'Reset' }).click();
      });
      act(() => {
        screen.getByRole('button', { name: 'Rerender' }).click();
      });
      expect(screen.getByTestId('vocab-state').textContent).toBe('false');
    });
  };

  addTests(TestComponent);

  describe('with subrequest', () => {
    const TestComponentForSubrequests = () => {
      const { isVocabRequested, setVocabRequested, resetContext } =
        useContext(VocabContext);
      const [, rerender] = useState(false);
      return (
        <div>
          <div data-testid="vocab-state">
            {isVocabRequested('test', 'subrequest').toString()}
          </div>
          <button onClick={() => setVocabRequested('test', 'subrequest')}>
            Set Vocab
          </button>
          <button
            onClick={() => {
              rerender((b) => !b);
            }}
          >
            Rerender
          </button>
          <button onClick={resetContext}>Reset</button>
        </div>
      );
    };

    addTests(TestComponentForSubrequests);
  });
});
