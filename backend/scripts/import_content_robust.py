"""Robust import of a plone.exportimport dump into the local site.

NOT part of the daily workflow — for everyday use of the bundled example
content, use the stock ``plone-importer`` via ``make
import-example-content``. This script exists for one-time operations on
dumps that may contain content types not installed on this site, e.g.
re-importing the original intranet source tree (which contains Person,
Organisational Unit and Location from the intranet distribution).

Usage:
    zconsole run instance/etc/zope.conf ./scripts/import_content_robust.py <path>

<path> is a plone.exportimport base directory (containing content/ and
optionally principals.json).

Unlike the stock plone-importer CLI, content items whose portal type is
not installed on this site are skipped with a warning instead of
aborting the import; children of a skipped container are skipped as
well (their container is missing).
"""

from AccessControl.SecurityManagement import newSecurityManager
from collections import Counter
from pathlib import Path
from plone import api
from plone.exportimport.importers import Importer
from plone.exportimport.importers.content import ContentImporter
from Testing.makerequest import makerequest
from zope.component import hooks

import sys
import transaction


class SkipUnknownTypesContentImporter(ContentImporter):
    """Content importer that skips items of uninstalled portal types."""

    skipped_types: Counter

    def __init__(self, site):
        super().__init__(site)
        self.skipped_types = Counter()

    def all_objects(self):
        allowed = set(api.portal.get_tool("portal_types").objectIds())
        for data in super().all_objects():
            portal_type = data.get("@type")
            if portal_type not in allowed:
                self.skipped_types[portal_type] += 1
                continue
            yield data


class SkipUnknownTypesImporter(Importer):
    def all_importers(self):
        importers = super().all_importers()
        importers["plone.importer.content"] = SkipUnknownTypesContentImporter(self.site)
        return importers


def main(path: Path):
    app = makerequest(globals()["app"])
    admin = app.acl_users.getUserById("admin")
    newSecurityManager(None, admin.__of__(app.acl_users))
    site = app.Plone
    with hooks.site(site):
        importer = SkipUnknownTypesImporter(site)
        report = importer.import_site(path)
        # Commit inside the site context: commit-time indexing (e.g.
        # image_scales following relations) needs the local components.
        transaction.commit()
    for line in report:
        print(line)
    content_importer = importer.importers["plone.importer.content"]
    skipped = content_importer.skipped_types
    if skipped:
        print(f"Skipped items of uninstalled types: {dict(skipped)}")


if __name__ == "__main__":
    # zconsole passes its own arguments through; the dump path is last
    arg = sys.argv[-1]
    if arg.endswith(".py"):
        # no path argument given: default to the bundled German corpus
        arg = "./src/kitconcept/solr/setuphandlers/examplecontent"
    base_path = Path(arg).resolve()
    if not (base_path / "content").exists():
        raise SystemExit(f"No content/ directory under {base_path}")
    main(base_path)
