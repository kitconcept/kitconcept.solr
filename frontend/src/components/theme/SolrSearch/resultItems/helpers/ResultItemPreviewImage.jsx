import { Link } from 'react-router-dom';
import config from '@plone/volto/registry';

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

const ResultItemPreviewImage = ({ item, ...rest }) => {
  const content = previewImageContent(item);
  if (content.image_scales) {
    // Show the link also conditionally.
    const Image = config.getComponent({ name: 'Image' }).component;
    return (
      <Link to={item['@id']}>
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
      </Link>
    );
  } else {
    return null;
  }
};

export default ResultItemPreviewImage;
