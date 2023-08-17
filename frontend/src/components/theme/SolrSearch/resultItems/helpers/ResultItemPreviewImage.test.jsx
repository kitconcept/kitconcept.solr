import { create } from 'react-test-renderer';
import { Router } from 'react-router-dom';
import config from '@plone/volto/registry';
import { createMemoryHistory } from 'history';
import ResultItemPreviewImage, {
  previewImageContent,
} from './ResultItemPreviewImage';

const data = {
  '@id': '/testnews1',
  image_field: 'preview_image',
  extras: {
    image_scales: `{"preview_image": [{"filename": "GOPR9639.JPG", "content-type": "image/jpeg", "size": 6446468, "download": "@@images/preview_image-4000-5496e5d01152aa6661428d9e264d3757.jpeg", "width": 4000, "height": 3000, "scales": {"icon": {"download": "@@images/preview_image-32-e743dcfb64ce39b0660285a04e7f842b.jpeg", "width": 32, "height": 24}, "tile": {"download": "@@images/preview_image-64-9ad26e8053451aec63586d66e111deb8.jpeg", "width": 64, "height": 48}, "thumb": {"download": "@@images/preview_image-128-88f2831a9f099921f03d3244021b03ab.jpeg", "width": 128, "height": 96}, "mini": {"download": "@@images/preview_image-200-2a8af40b17e1f5562607a1cf876244b1.jpeg", "width": 200, "height": 150}, "preview": {"download": "@@images/preview_image-400-1a82684a51b55644eef2807c2761b711.jpeg", "width": 400, "height": 300}, "teaser": {"download": "@@images/preview_image-600-71895aac86b72d21dd0f2bad189871c3.jpeg", "width": 600, "height": 450}, "large": {"download": "@@images/preview_image-800-b30bff7dbaa62fc6aca82639c9f5ee97.jpeg", "width": 800, "height": 600}, "larger": {"download": "@@images/preview_image-1000-e97d87c2a35fdc6262f429262854faed.jpeg", "width": 1000, "height": 750}, "great": {"download": "@@images/preview_image-1200-0723c41835b6498e598780419cc25a4f.jpeg", "width": 1200, "height": 900}, "huge": {"download": "@@images/preview_image-1600-7c8256769b8c48d0392c6a51ef34a139.jpeg", "width": 1600, "height": 1200}}}]}`,
  },
};

const dataBrokenJson = {
  '@id': '/testnews1',
  image_field: 'preview_image',
  extras: {
    image_scales: `{BROKEN JSON}`,
  },
};

const dataMissingScales = {
  '@id': '/testnews1',
  image_field: 'preview_image',
  extras: {
    image_scales: undefined,
  },
};

describe('ResultItemPreviewImage previewImageContent', () => {
  it('generates image data', () => {
    expect(previewImageContent(data)).toEqual({
      '@id': '/testnews1',
      image_field: 'preview_image',
      image_scales: {
        preview_image: [
          {
            'content-type': 'image/jpeg',
            download:
              '@@images/preview_image-4000-5496e5d01152aa6661428d9e264d3757.jpeg',
            filename: 'GOPR9639.JPG',
            height: 3000,
            scales: {
              great: {
                download:
                  '@@images/preview_image-1200-0723c41835b6498e598780419cc25a4f.jpeg',
                height: 900,
                width: 1200,
              },
              huge: {
                download:
                  '@@images/preview_image-1600-7c8256769b8c48d0392c6a51ef34a139.jpeg',
                height: 1200,
                width: 1600,
              },
              icon: {
                download:
                  '@@images/preview_image-32-e743dcfb64ce39b0660285a04e7f842b.jpeg',
                height: 24,
                width: 32,
              },
              large: {
                download:
                  '@@images/preview_image-800-b30bff7dbaa62fc6aca82639c9f5ee97.jpeg',
                height: 600,
                width: 800,
              },
              larger: {
                download:
                  '@@images/preview_image-1000-e97d87c2a35fdc6262f429262854faed.jpeg',
                height: 750,
                width: 1000,
              },
              mini: {
                download:
                  '@@images/preview_image-200-2a8af40b17e1f5562607a1cf876244b1.jpeg',
                height: 150,
                width: 200,
              },
              preview: {
                download:
                  '@@images/preview_image-400-1a82684a51b55644eef2807c2761b711.jpeg',
                height: 300,
                width: 400,
              },
              teaser: {
                download:
                  '@@images/preview_image-600-71895aac86b72d21dd0f2bad189871c3.jpeg',
                height: 450,
                width: 600,
              },
              thumb: {
                download:
                  '@@images/preview_image-128-88f2831a9f099921f03d3244021b03ab.jpeg',
                height: 96,
                width: 128,
              },
              tile: {
                download:
                  '@@images/preview_image-64-9ad26e8053451aec63586d66e111deb8.jpeg',
                height: 48,
                width: 64,
              },
            },
            size: 6446468,
            width: 4000,
          },
        ],
      },
    });
  });
  describe('fallback', () => {
    it('bad json yields empty image_scales', () => {
      expect(previewImageContent(dataBrokenJson)).toEqual({
        '@id': '/testnews1',
        image_field: 'preview_image',
        image_scales: undefined,
      });
    });
    it('missing scales yields empty image_scales', () => {
      expect(previewImageContent(dataMissingScales)).toEqual({
        '@id': '/testnews1',
        image_field: 'preview_image',
        image_scales: undefined,
      });
    });
  });
});

describe('ResultItemPreviewImage', () => {
  let history;

  beforeEach(() => {
    history = createMemoryHistory();
    history.push = jest.fn();
    window.devicePixelRatio = 1;
  });

  test('normal with default props', () => {
    const component = create(
      <Router history={history}>
        <ResultItemPreviewImage item={data} />
      </Router>,
    );
    const rendered = component.toJSON();
    expect(rendered).toMatchSnapshot();
  });

  test('override via rest', () => {
    const component = create(
      <Router history={history}>
        <ResultItemPreviewImage
          item={data}
          className="foo"
          width="120"
          height="130"
          loading="eager"
          sizes="100vw"
        />
      </Router>,
    );
    const rendered = component.toJSON();
    expect(rendered).toMatchSnapshot();
  });

  describe('legacy image', () => {
    let origComponent;
    let origContentTypeSearchResultAlwaysUseLegacyImage;
    beforeEach(() => {
      origComponent = config.getComponent({ name: 'Image' }).component;
      origContentTypeSearchResultAlwaysUseLegacyImage =
        config.settings.contentTypeSearchResultAlwaysUseLegacyImage;
    });
    afterEach(() => {
      config.getComponent({ name: 'Image' }).component = origComponent;
      config.settings.contentTypeSearchResultAlwaysUseLegacyImage = origContentTypeSearchResultAlwaysUseLegacyImage;
    });

    test('if image component not available on Volto 16', () => {
      config.getComponent({ name: 'Image' }).component = undefined;
      const component = create(
        <Router history={history}>
          <ResultItemPreviewImage
            item={data}
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

    test('if contentTypeSearchResultAlwaysUseLegacyImage is true', () => {
      config.settings.contentTypeSearchResultAlwaysUseLegacyImage = true;
      const component = create(
        <Router history={history}>
          <ResultItemPreviewImage
            item={data}
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

    test('sizes prop yields error', () => {
      config.settings.contentTypeSearchResultAlwaysUseLegacyImage = true;
      let mockError = jest.spyOn(console, 'error');
      mockError.mockImplementation(() => undefined);
      expect(() =>
        create(
          <Router history={history}>
            <ResultItemPreviewImage
              item={data}
              className="foo"
              width="120"
              height="130"
              loading="eager"
              sizes="100vw"
            />
          </Router>,
        ),
      ).toThrow();
      mockError.mockRestore();
    });
  });
});
