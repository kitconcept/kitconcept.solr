import React from 'react';
import { Link } from 'react-router-dom';
import ResultItemDate from './helpers/ResultItemDate';
import ConcatChildren from './helpers/ConcatChildren';
import ImageType, { getImageType } from './helpers/ImageType';
import ResultItemPreviewImage from './helpers/ResultItemPreviewImage';
import IconForContentType from './helpers/IconForContentType';

const NewsItemResultItem = ({ item }) => (
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
      {(item?.effective || item?.extras?.start) && (
        <ConcatChildren if1={getImageType(item?.extras?.mime_type)}>
          <IconForContentType type={item['@type']} />
          <ImageType mimeType={item?.extras?.mime_type} />
          <ResultItemDate
            date={item?.extras?.start ? item.extras.start : item?.effective}
            showIfNotPublished={true}
          />
        </ConcatChildren>
      )}
    </div>
    <div className="visualClear" />
  </article>
);

export default NewsItemResultItem;
