import { GET_CONTENT } from '@plone/volto/constants/ActionTypes';
import config from '@plone/volto/registry';
import navigation_with_excluded from './navigation_with_excluded';
import { GET_NAVIGATION_WITH_EXCLUDED } from '../../actions/navigation_with_excluded/navigation_with_excluded';

const { settings } = config;

describe('Navigation reducer', () => {
  it('should return the initial state', () => {
    expect(navigation_with_excluded()).toEqual({
      error: null,
      items: [],
      loaded: false,
      loading: false,
    });
  });

  it('should handle GET_NAVIGATION_WITH_EXCLUDED_PENDING', () => {
    expect(
      navigation_with_excluded(undefined, {
        type: `${GET_NAVIGATION_WITH_EXCLUDED}_PENDING`,
      }),
    ).toEqual({
      error: null,
      items: [],
      loaded: false,
      loading: true,
    });
  });

  it('should handle GET_NAVIGATION_WITH_EXCLUDED_SUCCESS', () => {
    expect(
      navigation_with_excluded(undefined, {
        type: `${GET_NAVIGATION_WITH_EXCLUDED}_SUCCESS`,
        result: {
          items: [
            {
              title: 'Welcome to Plone!',
              description:
                'Congratulations! You have successfully installed Plone.',
              '@id': `${settings.apiPath}/front-page`,
            },
          ],
        },
      }),
    ).toEqual({
      error: null,
      items: [
        {
          '@id': 'http://localhost:8080/Plone/front-page',
          title: 'Welcome to Plone!',
          description:
            'Congratulations! You have successfully installed Plone.',
          url: '/front-page',
        },
      ],
      loaded: true,
      loading: false,
    });
  });

  it('should handle GET_NAVIGATION_WITH_EXCLUDED_SUCCESS with navigation depth', () => {
    expect(
      navigation_with_excluded(undefined, {
        type: `${GET_NAVIGATION_WITH_EXCLUDED}_SUCCESS`,
        result: {
          items: [
            {
              title: 'Welcome to Plone!',
              description:
                'Congratulations! You have successfully installed Plone.',
              '@id': `${settings.apiPath}/front-page`,
            },
            {
              title: 'Folder1',
              description: 'Folder description',
              '@id': `${settings.apiPath}/folder1`,
              items: [
                {
                  title: 'FolderInFolder1',
                  description: 'Sub-folder description',
                  '@id': `${settings.apiPath}/folderinfolder1`,
                },
              ],
            },
          ],
        },
      }),
    ).toEqual({
      error: null,
      items: [
        {
          '@id': 'http://localhost:8080/Plone/front-page',
          title: 'Welcome to Plone!',
          description:
            'Congratulations! You have successfully installed Plone.',
          url: '/front-page',
        },
        {
          '@id': 'http://localhost:8080/Plone/folder1',
          title: 'Folder1',
          description: 'Folder description',
          url: '/folder1',
          items: [
            {
              '@id': 'http://localhost:8080/Plone/folderinfolder1',
              title: 'FolderInFolder1',
              description: 'Sub-folder description',
              url: '/folderinfolder1',
            },
          ],
        },
      ],
      loaded: true,
      loading: false,
    });
  });

  it('should handle GET_NAVIGATION_WITH_EXCLUDED_FAIL', () => {
    expect(
      navigation_with_excluded(undefined, {
        type: `${GET_NAVIGATION_WITH_EXCLUDED}_FAIL`,
        error: 'failed',
      }),
    ).toEqual({
      error: 'failed',
      items: [],
      loaded: false,
      loading: false,
    });
  });
});

describe('Navigation reducer (NAVIGATION_WITH_EXJUDED)GET_CONTENT', () => {
  beforeEach(() => {
    config.settings.apiExpanders = [
      {
        match: '',
        GET_CONTENT: ['navigation_with_excluded'],
      },
    ];
  });

  it('should handle (NAVIGATION_WITH_EXCLUDED)GET_CONTENT_SUCCESS', () => {
    expect(
      navigation_with_excluded(undefined, {
        type: `${GET_CONTENT}_SUCCESS`,
        result: {
          '@components': {
            navigation_with_excluded: {
              items: [
                {
                  title: 'Welcome to Plone!',
                  description:
                    'Congratulations! You have successfully installed Plone.',
                  '@id': `${settings.apiPath}/front-page`,
                },
              ],
            },
          },
        },
      }),
    ).toEqual({
      error: null,
      items: [
        {
          '@id': 'http://localhost:8080/Plone/front-page',
          title: 'Welcome to Plone!',
          description:
            'Congratulations! You have successfully installed Plone.',
          url: '/front-page',
        },
      ],
      loaded: true,
      loading: false,
    });
  });

  it('should handle (NAVIGATION_WITH_EXCLUDED)GET_CONTENT_SUCCESS reset state if no expander info', () => {
    config.settings.apiExpanders = [
      {
        match: '',
        GET_CONTENT: [],
      },
    ];
    const state = {
      error: null,
      items: [
        {
          '@id': 'http://localhost:8080/Plone/front-page',
          title: 'Welcome to Plone!',
          description:
            'Congratulations! You have successfully installed Plone.',
          url: '/front-page',
        },
      ],
      loaded: true,
      loading: false,
    };
    expect(
      navigation_with_excluded(state, {
        type: `${GET_CONTENT}_SUCCESS`,
        result: {
          '@components': {},
        },
      }),
    ).toEqual({
      error: null,
      items: [],
      loaded: false,
      loading: false,
    });
  });

  it('should handle (NAVIGATION_WITH_EXCLUDED)GET_NAVIGATION_WITH_EXCLUDED_SUCCESS (standalone with apiExpander enabled)', () => {
    expect(
      navigation_with_excluded(undefined, {
        type: `${GET_NAVIGATION_WITH_EXCLUDED}_SUCCESS`,
        result: {
          items: [
            {
              title: 'Welcome to Plone!',
              description:
                'Congratulations! You have successfully installed Plone.',
              '@id': `${settings.apiPath}/front-page`,
            },
          ],
        },
      }),
    ).toEqual({
      error: null,
      items: [
        {
          '@id': 'http://localhost:8080/Plone/front-page',
          title: 'Welcome to Plone!',
          description:
            'Congratulations! You have successfully installed Plone.',
          url: '/front-page',
        },
      ],
      loaded: true,
      loading: false,
    });
  });
});
