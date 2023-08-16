import React from 'react';
import { Link } from 'react-router-dom';
import { Icon } from '@plone/volto/components';
import ResultItemDate from './helpers/ResultItemDate';
import locationSVG from '../icons/location.svg';
import ResultItemPreviewImage from './helpers/ResultItemPreviewImage';
import IconForContentType from './helpers/IconForContentType';

const EventResultItem = ({ item }) => (
  <article className="tileItem">
    {/* <span className="contentTypeLabel">
      <FormattedMessage id={mapContentTypes(item['@type'])} />
    </span> */}
    <ResultItemPreviewImage item={item} />
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
      <div>
        <IconForContentType type={item['@type']} />
        <ResultItemDate
          date={item?.extras?.start ? item.extras.start : item?.effective}
          showTime={true}
          hasExcerpt={item?.extras?.end}
        />
        {item?.extras?.end ? (
          <ResultItemDate date={item?.extras?.end} showTime={true} />
        ) : null}
      </div>
      {item.extras?.location ? (
        <div>
          <Icon className="itemIcon" size="20px" name={locationSVG} />
          {item.extras.location}
        </div>
      ) : null}
    </div>
    <div className="visualClear" />
  </article>
);

export default EventResultItem;
