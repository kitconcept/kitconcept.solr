# Volto add-on for Solr support

This package has to be used together with the `volto-solr` back-end package.

## Configuration

The configuration is provided by default and can be overwritten from any package.


### Result type templates

The search results are rendered by default components, which are customizable.

The `config.views.contentTypeSearchResultViews` object contains a mapping from type name to the component that renders them. These can be overridden, and renderer components for new types can be added as well.

Additionally. the `config.views.contentTypeSearchResultDefaultView` defines the component that is used as a default renderer for all the result types not specified in `config.views.contentTypeSearchResultViews`.

```js
  // View mapper can be specified here. with the desired type rendererers.
  // The default view applies for all content types not in the array.
  // Or just use the built in mapper.
  config.views.contentTypeSearchResultViews = {
    Event: searchResultItems.EventResultItem,
    Image: searchResultItems.ImageResultItem,
    'News Item': searchResultItems.NewsItemResultItem,
  };
  config.views.contentTypeSearchResultDefaultView =
    searchResultItems.DefaultResultItem;
```


### Other options

The rest of the options provide the baselines for the package and the `Search` compoment to work. You can override various components via these options, including the `Search` component and the underlying reducers and actions that it uses. There is currently no supported use case for this, so please refer to the source code if you wish to do this. You most likely won't need to do this.


