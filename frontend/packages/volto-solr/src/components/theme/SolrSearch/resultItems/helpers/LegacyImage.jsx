import { Link } from 'react-router-dom';
import { flattenToAppURL } from '@plone/volto/helpers';

// Compatibility layer for Volto < 17, where the Image content type
// is not present.

export const previewImageLink = (
  { image_scales, image_field },
  minWidth = 250,
) => {
  const requiredPixels = minWidth * window.devicePixelRatio;
  let download;
  // Find the next larger resolution to what we require
  if (image_scales) {
    const scales = Object.values(image_scales?.[image_field]?.[0].scales).sort(
      (a, b) => a.width - b.width,
    );
    for (const scale of scales) {
      if (scale.width >= requiredPixels) {
        download = scale.download;
        break;
      }
    }
    if (!download) {
      // if no best scale, try using the largest
      download = scales[scales.length - 1]?.download;
    }
  }
  // In case of missing scale no image.
  return download;
};

const LegacyImage = ({ item, minWidth, ...rest }) => {
  const download = previewImageLink(item, minWidth);
  if (download) {
    return (
      <Link to={item['@id']}>
        <img
          src={flattenToAppURL(`${item['@id']}/${download}`)}
          alt={item.title}
          {...rest}
        />
      </Link>
    );
  } else {
    return null;
  }
};

export default LegacyImage;
