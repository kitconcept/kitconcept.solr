import { create } from 'react-test-renderer';
import IconForContentType from './IconForContentType';
import config from '@plone/volto/registry';

describe('IconForContentType', () => {
  let origContentTypeSearchResultIcons;
  let origContentTypeSearchResultDefaultIcon;

  beforeEach(() => {
    origContentTypeSearchResultIcons =
      config.settings.contentTypeSearchResultIcons;
    origContentTypeSearchResultDefaultIcon =
      config.settings.contentTypeSearchResultDefaultIcon;
    config.settings.contentTypeSearchResultIcons = {
      Event: { content: `calendarSVG` },
      Image: { content: `imageSVG` },
    };
    config.settings.contentTypeSearchResultDefaultIcon = { content: 'fileSVG' };
  });

  afterEach(() => {
    config.settings.contentTypeSearchResultIcons = origContentTypeSearchResultIcons;
    config.settings.contentTypeSearchResultDefaultIcon = origContentTypeSearchResultDefaultIcon;
  });

  test('default icon', () => {
    const component = create(<IconForContentType type={'Foo'} />);
    const rendered = component.toJSON();
    expect(rendered).toMatchSnapshot();
  });

  test('Event icon', () => {
    const component = create(<IconForContentType type={'Event'} />);
    const rendered = component.toJSON();
    expect(rendered).toMatchSnapshot();
  });

  test('Image icon', () => {
    const component = create(<IconForContentType type={'Image'} />);
    const rendered = component.toJSON();
    expect(rendered).toMatchSnapshot();
  });
});
