import { create } from 'react-test-renderer';
import { Router } from 'react-router-dom';
import { createMemoryHistory } from 'history';
import LegacyImage, { previewImageLink } from './LegacyImage';

jest.mock('@plone/volto/helpers', () => {
  return {
    __esModule: true,
    flattenToAppURL: jest.fn((url) =>
      url.replace(/http:\/\/localhost:3000/, ''),
    ),
    isInternalURL: jest.fn(
      (url) =>
        url.search(/http:\/\/localhost:3000/) !== -1 ||
        url.search(/http:\/\//) === -1,
    ),
  };
});

const data = {
  '@id': '/testnews1',
  image_field: 'preview_image',
  image_scales: {
    preview_image: [
      {
        filename: 'GOPR9639.JPG',
        'content-type': 'image/jpeg',
        size: 6446468,
        download:
          '@@images/preview_image-4000-5496e5d01152aa6661428d9e264d3757.jpeg',
        width: 4000,
        height: 3000,
        scales: {
          icon: {
            download:
              '@@images/preview_image-32-e743dcfb64ce39b0660285a04e7f842b.jpeg',
            width: 32,
            height: 24,
          },
          tile: {
            download:
              '@@images/preview_image-64-9ad26e8053451aec63586d66e111deb8.jpeg',
            width: 64,
            height: 48,
          },
          thumb: {
            download:
              '@@images/preview_image-128-88f2831a9f099921f03d3244021b03ab.jpeg',
            width: 128,
            height: 96,
          },
          mini: {
            download:
              '@@images/preview_image-200-2a8af40b17e1f5562607a1cf876244b1.jpeg',
            width: 200,
            height: 150,
          },
          preview: {
            download:
              '@@images/preview_image-400-1a82684a51b55644eef2807c2761b711.jpeg',
            width: 400,
            height: 300,
          },
          teaser: {
            download:
              '@@images/preview_image-600-71895aac86b72d21dd0f2bad189871c3.jpeg',
            width: 600,
            height: 450,
          },
          large: {
            download:
              '@@images/preview_image-800-b30bff7dbaa62fc6aca82639c9f5ee97.jpeg',
            width: 800,
            height: 600,
          },
          larger: {
            download:
              '@@images/preview_image-1000-e97d87c2a35fdc6262f429262854faed.jpeg',
            width: 1000,
            height: 750,
          },
          great: {
            download:
              '@@images/preview_image-1200-0723c41835b6498e598780419cc25a4f.jpeg',
            width: 1200,
            height: 900,
          },
          huge: {
            download:
              '@@images/preview_image-1600-7c8256769b8c48d0392c6a51ef34a139.jpeg',
            width: 1600,
            height: 1200,
          },
        },
      },
    ],
  },
};

const dataMissingScales = {
  '@id': '/testnews1',
  image_field: 'preview_image',
  image_scales: undefined,
};

describe('ResultItemPreviewImageLegacy previewImageLink', () => {
  beforeEach(() => {
    window.devicePixelRatio = 1;
  });

  describe('generates image link', () => {
    it('normal', () => {
      expect(previewImageLink(data)).toBe(
        '@@images/preview_image-400-1a82684a51b55644eef2807c2761b711.jpeg',
      );
    });
    it('minWidth chooses smallest possible scale', () => {
      expect(previewImageLink(data, 600)).toBe(
        '@@images/preview_image-600-71895aac86b72d21dd0f2bad189871c3.jpeg',
      );
    });
    it('minWidth works with devicePixelRatio', () => {
      window.devicePixelRatio = 2.0;
      expect(previewImageLink(data, 600)).toBe(
        '@@images/preview_image-1200-0723c41835b6498e598780419cc25a4f.jpeg',
      );
    });
    it('minWidth chooses largest scale if they are all too small', () => {
      expect(previewImageLink(data, 6000)).toBe(
        '@@images/preview_image-1600-7c8256769b8c48d0392c6a51ef34a139.jpeg',
      );
    });
  });
  describe('fallback', () => {
    it('missing scales', () => {
      expect(previewImageLink(dataMissingScales)).toBe(undefined);
    });
    it('minWidth works with missing scales', () => {
      expect(previewImageLink(dataMissingScales, 250)).toBe(undefined);
    });
  });
});

describe('LegacyImage', () => {
  let history;

  beforeEach(() => {
    history = createMemoryHistory();
    history.push = jest.fn();
    window.devicePixelRatio = 1;
  });

  test('normal', () => {
    const component = create(
      <Router history={history}>
        <LegacyImage item={data} />
      </Router>,
    );
    const rendered = component.toJSON();
    expect(rendered).toMatchSnapshot();
  });

  test('minWidth', () => {
    const component = create(
      <Router history={history}>
        <LegacyImage item={data} minWidth={600} />
      </Router>,
    );
    const rendered = component.toJSON();
    expect(rendered).toMatchSnapshot();
  });

  test('minWidth and devicePixelRatio', () => {
    window.devicePixelRatio = 2;
    const component = create(
      <Router history={history}>
        <LegacyImage item={data} minWidth={600} />
      </Router>,
    );
    const rendered = component.toJSON();
    expect(rendered).toMatchSnapshot();
  });

  test('renders null if resolution is not available', () => {
    const component = create(
      <Router history={history}>
        <LegacyImage
          item={dataMissingScales}
          minWidth={600}
          className="foo"
          width="120"
          height="130"
          loading="eager"
        />
      </Router>,
    );
    const rendered = component.toJSON();
    expect(rendered).toBe(null);
  });

  test('override via rest', () => {
    const component = create(
      <Router history={history}>
        <LegacyImage
          item={data}
          minWidth={600}
          className="foo"
          width="120"
          height="130"
          loading="eager"
        />
      </Router>,
    );
    const rendered = component.toJSON();
    expect(rendered).toMatchSnapshot();
  });
});
