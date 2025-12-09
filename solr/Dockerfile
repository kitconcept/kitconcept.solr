# syntax=docker/dockerfile:1
FROM solr:9.10

LABEL maintainer="kitconcept, GmbH <info@kitconcept.com>" \
      org.label-schema.name="ghcr.io/kitconcept/solr" \
      org.label-schema.description="Solr 9 image with Plone default settings" \
      org.label-schema.vendor="kitconcept, GmbH"

# Copy default plone configuration for this image
COPY etc /plone-config
