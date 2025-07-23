# Volto Solr Plone Add-on

This add-on enhances Plone (Volto) with a Solr-based full-text search.

This package has to be used together with the [`kitconcept.solr`](https://github.com/kitconcept/kitconcept.solr) back-end package.

# Installation

Go to your Volto frontend package and run:

```
yarn add @kitconcept/volto-solr
```

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

### Result type icons

In addition to the result type templates, it's also possible to use which icon to use to represent any specific result icon.

`config.settings.contentTypeSearchResultIcons` is a mapping from content type name to the icon to use for the content type. In addition, `config.settings.contentTypeSearchResultDefaultIcon` specifies a fallback to be used for any content type not found in the mapping (and functions as a default).

config.settings.contentTypeSearchResultIcons is by default populated from `config.settings.contentIcons` which is usually the right thing to do. The following example uses these settings, but also defines specific icons for some specific content types.

All supported content type templates respect these settings, so an icon for a content type can be redefined without the need to redefine the entire template, if otherwise no other changes are needed.

```js
  // Icon types. This will be in effect with all supported
  // content type templates.
  config.settings.contentTypeSearchResultIcons = {
    ...config.settings.contentIcons,
    Event: calendarSVG,
    Image: imageSVG,
    'News Item': newsSVG,
  };
  config.settings.contentTypeSearchResultDefaultIcon = fileSVG;
```

### Other options

The rest of the options provide the baselines for the package and the `Search` compoment to work. You can override various components via these options, including the `Search` component and the underlying reducers and actions that it uses. There is currently no supported use case for this, so please refer to the source code if you wish to do this. You most likely won't need to do this.


