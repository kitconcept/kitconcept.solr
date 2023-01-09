const { DefinePlugin } = require('webpack');
const path = require('path');
const fs = require('fs');

const getSolrFacets = () => {
  const folder = process.env.SOLR_CONTEXT_FOLDER;

  if (!folder) {
    return undefined;
  }

  const jsonPath = path.resolve(folder, 'etc', 'solr-facets.json');

  let jsonString;
  try {
    jsonString = fs.readFileSync(jsonPath, { encoding: 'utf8', flag: 'r' });
  } catch (err) {
    throw new Error(
      'Failed reading file "' + jsonPath + '" [' + err.message + ']',
    );
  }

  return jsonString;
};

const plugins = (defaultPlugins) => {
  return defaultPlugins;
};

const modify = (config, { target, dev }, webpack) => {
  config.plugins.push(
    new DefinePlugin({
      'process.env.SOLR_FACETS': getSolrFacets(),
    }),
  );
  return config;
};

module.exports = {
  plugins,
  modify,
};
