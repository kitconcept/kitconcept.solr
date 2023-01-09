const getSolrFacets = () => {
  // The SOLR_FACETS env var is fetched by Webpack, and it contains the
  // data fetched from the file
  //   `${SOLR_CONTEXT_FOLDER}/etc/solr-facets.json`
  const json = process.env.SOLR_FACETS;
  if (!json) {
    throw new Error('SOLR_CONTEXT_FOLDER must be defined');
  }
  return json;
};

const solrFacets = getSolrFacets();

export default solrFacets;
