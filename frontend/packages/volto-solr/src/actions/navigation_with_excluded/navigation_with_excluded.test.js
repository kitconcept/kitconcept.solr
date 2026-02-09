import { getNavigationWithExcluded } from './navigation_with_excluded';
import { GET_NAVIGATION_WITH_EXCLUDED } from './navigation_with_excluded';

describe('Navigation with excluded action', () => {
  describe('getNavigationWithExcluded', () => {
    it('should create an action to get the navigation with excluded items', () => {
      const url = 'http://localhost';
      const action = getNavigationWithExcluded(url);

      expect(action.type).toEqual(GET_NAVIGATION_WITH_EXCLUDED);
      expect(action.request.op).toEqual('get');
      expect(action.request.path).toEqual(`${url}/@navigation_with_excluded`);
    });

    it('should create an action to get the navigation with depth', () => {
      const url = 'http://localhost';
      const depth = 3;
      const action = getNavigationWithExcluded(url, depth);

      expect(action.type).toEqual(GET_NAVIGATION_WITH_EXCLUDED);
      expect(action.request.op).toEqual('get');
      expect(action.request.path).toEqual(
        `${url}/@navigation_with_excluded?expand.navigation_with_excluded.depth=${depth}`,
      );
    });
  });
});
