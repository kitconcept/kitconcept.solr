import React from 'react';
import { Link } from 'react-router-dom';
import ResultItemPreviewImage from './helpers/ResultItemPreviewImage';
import phoneSVG from '../icons/phone.svg';
import emailSVG from '@plone/volto/icons/email.svg';
import fallbackAvatarSVG from '../icons/fallback-avatar.svg';
import { Icon } from '@plone/volto/components'; // ??
import config from '@plone/volto/registry';

const PersonResultItem = ({ item }) => (
  <article className="tileItem personResultItem">
    <div className="itemWrapper">
      {/* <span className="contentTypeLabel">
      <FormattedMessage id={mapContentTypes(item['@type'])} />
    </span> */}
      <div className="itemImageWrapper">
        <Link to={item['@id']}>
          <Icon
            size="64px"
            name={fallbackAvatarSVG}
            color={config.settings.baseColor}
          />
          <ResultItemPreviewImage
            Wrapper={null}
            className="profileImage"
            item={item}
            width="64"
            height="64"
          />
        </Link>
      </div>
      <div className="itemContent">
        <p className="url">{item['@id']}</p>
        <h2 className="tileHeadline">
          <Link to={item['@id']} className="summary url" title={item['@type']}>
            {item.title}
          </Link>
        </h2>
        {item?.highlighting && item.highlighting.length > 0 ? (
          <div className="tileBody">
            <span
              className="description"
              dangerouslySetInnerHTML={{
                __html: item.highlighting,
              }}
            />
            {' ...'}
          </div>
        ) : (
          <div className="tileBody">
            <span className="description">
              {item.description
                ? item.description.length > 200
                  ? item.description.slice(0, 199) + '...'
                  : item.description
                : ''}
            </span>
          </div>
        )}
        <div className="tileFooter">
          {item.extras.contact_phone ? (
            <span className="itemPhone itemField">
              <Icon className="itemIcon" size="18px" name={phoneSVG} />
              {item.extras.contact_phone}
            </span>
          ) : null}
          <span>&#32;</span>
          {item.extras.contact_email ? (
            <span className="itemEmail itemField">
              <Icon className="itemIcon" size="18px" name={emailSVG} />
              {item.extras.contact_email}
            </span>
          ) : null}
        </div>
      </div>
      <div className="visualClear" />
    </div>
  </article>
);

export default PersonResultItem;
