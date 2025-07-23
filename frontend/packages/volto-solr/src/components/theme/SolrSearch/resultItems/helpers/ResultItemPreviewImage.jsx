import { Link } from 'react-router-dom';
import config from '@plone/volto/registry';
import LegacyImage from './LegacyImage';

export const previewImageContent = ({
  '@id': id,
  extras: { image_scales: rawImageScales },
  image_field,
}) => {
  let image_scales;
  try {
    image_scales = JSON.parse(rawImageScales);
  } catch {}
  // In case of json error, image_scales will be undefined..
  return {
    '@id': id,
    image_scales,
    image_field,
  };
};

const LinkToImage = ({ item, children }) => (
  <Link to={item['@id']}>{children}</Link>
);

const EmptyWrapper = ({ item, children }) => <>{children}</>;

const ResultItemPreviewImage = ({ item, Wrapper = LinkToImage, ...rest }) => {
  const content = previewImageContent(item);
  Wrapper = Wrapper !== null ? Wrapper : EmptyWrapper;
  if (content.image_scales) {
    // Show the wrapper also conditionally.
    let Image;
    if (!config.settings.contentTypeSearchResultAlwaysUseLegacyImage) {
      Image = config.getComponent({ name: 'Image' }).component;
    }
    if (!Image) {
      // Volto < 17 does not have the Image component. We provide a legacy fallback.
      // This will be a simple sourced image, no srcset, with the required resolution
      // to be used.
      if (rest.sizes) {
        throw new Error(
          'The `sizes` attribute of ResultItemPreviewImage does not work with the legacy image component. You must use Volto >= 17 with the Volto Image component for this to work.',
        );
      }
      return (
        <Wrapper item={item}>
          <LegacyImage
            item={content}
            /* Default hints provided, can be overridden via rest */
            className="previewImage"
            loading="lazy"
            width="250"
            height="125"
            {...rest}
          />
        </Wrapper>
      );
    }
    return (
      <Wrapper item={item}>
        <Image
          item={content}
          alt={item.title}
          /* Default hints provided, can be overridden via rest */
          className="previewImage"
          loading="lazy"
          sizes="250px"
          /* width + height practically mandatory, see https://github.com/plone/volto/issues/5096 */
          width="250"
          height="125"
          {...rest}
        />
      </Wrapper>
    );
  } else {
    return null;
  }
};

export default ResultItemPreviewImage;
