const getSolrConfig = () => {
  // The SOLR_CONFIG env var is fetched by Webpack, and it contains the
  // data fetched from the file
  //   `${SOLR_CONTEXT_FOLDER}/etc/solr-config.json`
  const json = process.env.SOLR_CONFIG;
  if (!json) {
    throw new Error('SOLR_CONTEXT_FOLDER must be defined');
  }
  return json;
};

const solrConfig = getSolrConfig();

export default solrConfig;
