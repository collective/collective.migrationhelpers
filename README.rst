===========================
collective.migrationhelpers
===========================

Some helpers and examples to use during migrations.

They are mostly meant to copy & paste the code from here to your own packages.

This was written for the talk "Migrations! Migrations! Migrations!" at Plone Conference 2019 in Ferrara: https://2019.ploneconf.org/talks/migrations-migrations-migrations


Here is a list of methods this package contains:


`statistics.py <https://github.com/collective/collective.migrationhelpers/blob/master/src/collective/migrationhelpers/statistics.py>`_
-------------

Browser-Views to get information about the portal:


migrations_stats
    Get info about the content is in the portal.

migrations_contentsize
    How many MB of which content is there really?

migrations_obsoleteinfo
    Get info about content-types that may needs to be replaced

migrations_localroles
    Export info about local roles. A alternative would be zopyx.plone.cassandra



`prepare.py <https://github.com/collective/collective.migrationhelpers/blob/master/src/collective/migrationhelpers/prepare.py>`_
----------

Prepare the portal for a migration

disable_solr
    Disable solr

disable_ldap
    Disable ldap/ad-plugins

remove_overrides
    Remove any portal_skin an portal_view_customization overrides.

release_all_webdav_locks
    Release all WebDAV Locks.


`cleanup.py <https://github.com/collective/collective.migrationhelpers/blob/master/src/collective/migrationhelpers/cleanup.py>`_
----------

Fremove obsolete content and settings

delete_items_larger_than_1mb
    Deletes heavy content

remove_all_revisions
    Clear out portal_historiesstorage

disable_theme
    Disable diazo theme, enable sunburst (useful for Plone 4)

trim_content
    Remove 95% of all content leaving at least one item for each type.
    Keep all folderish items unless specified.


`addons.py <https://github.com/collective/collective.migrationhelpers/blob/master/src/collective/migrationhelpers/addons.py>`_
---------

Remove addons

remove_ploneformgen
    Example that removes Products.PloneFormGen

remove_plonekeywordmanager
    Example that removes Products.PloneKeywordManager

remove_solgema_fullcalendar
    Example that removes Solgema.fullcalendar

remove_multiple_addons
    Example that removes a cubic ton of addons

cleanup_behaviors
    Remove obsolete behaviors

remove_vocabularies
    Example that removes p4a.subtyper utilities


`persistent.py <https://github.com/collective/collective.migrationhelpers/blob/master/src/collective/migrationhelpers/persistent.py>`_
-------------

Some examples that remove various adapters, subscriber and utilities.
For example:

_unregisterUtility
    Example that removes p4a.subtyper utilities (used in collective.easyslideshow)


See also:

* Use alias_module (see `patches.py`_)
* ``profiles/migration/componentregistry.xml``
* `wildcard.fixpersistentutilities <https://pypi.org/project/wildcard.fixpersistentutilities/>`_


`import_steps.py <https://github.com/collective/collective.migrationhelpers/blob/master/src/collective/migrationhelpers/import_steps.py>`_
---------------

Remove broken and outdated import/export steps


`linguaplone.py <https://github.com/collective/collective.migrationhelpers/blob/master/src/collective/migrationhelpers/linguaplone.py>`_
--------------

Examples that can help migrating from LinguaPlone to plone.app.multilingual

cleanup_content_for_pam
    Crazy method that sets languages, adds and links translations so that we can migrate to pam.

install_pam
    Install pam and setup site

migrate_to_pam
    Migrate LinguaPlone to plone.app.multilingual
    This mostly uses the migration that is builtin in plone.app.multilingual


`dexterity.py <https://github.com/collective/collective.migrationhelpers/blob/master/src/collective/migrationhelpers/dexterity.py>`_
------------

Methods to migrate default content to Dexterity.


`custom_dx_migration.py <https://github.com/collective/collective.migrationhelpers/blob/master/src/collective/migrationhelpers/custom_dx_migration.py>`_
----------------------

A example that migrated PloneHelpCenter to default Dexterity content.

migrate_helpcenter_to_dx
    Run the whole miration

change_phc_layouts
    Remove custom layout.

appending_richtext_migrator
    Example custom field-migrator that appends text to a existing richtext-field.

appending_text_migrator
    Example custom field-migrator that appends text to a existing text-field.

migrate_helpcenter_xxx
    Some Methods that migrate the various types in PHC


`archetypes.py <https://github.com/collective/collective.migrationhelpers/blob/master/src/collective/migrationhelpers/archetypes.py>`_
-------------

remove_archetypes
    Uninstall Archetypes and remove all of its traces.



`patches.py <https://github.com/collective/collective.migrationhelpers/blob/master/src/collective/migrationhelpers/patches.py>`_
----------

Multilple examples of patches using alias_module to deal with migration-problems.


`images.py <https://github.com/collective/collective.migrationhelpers/blob/master/src/collective/migrationhelpers/images.py>`_
---------

fix_at_image_scales
    Fix/Migrate custom images/scales and broken links to AT-based images.



`post_python3_fixes.py <https://github.com/collective/collective.migrationhelpers/blob/master/src/collective/migrationhelpers/post_python3_fixes.py>`_
---------------------

fix_event_indexes
    Metadata on brains is still old DateTime

fix_searchable_text
    Fix bytes in opkapiindex

fix_portlets
    Fix portlets that use a ComputedValue for path-storage instead of a UUID

rebuild_relations
    Exports all valid reations from the relation-catalog, purges the relation-catalog
    (and the intid-catalog) and restores all valid relations.
    Uses `collective.relationhelpers  <https://github.com/collective/collective.relationhelpers>`_

export_relations
    Export all relations as a json file all_relations.json in you buildout directory.
    Uses `collective.relationhelpers  <https://github.com/collective/collective.relationhelpers>`_

restore_relations
    Recreate relations from a annotation on the portal or a list of dicts
    (e.g. restored from the json-file created by export_relations).
    This works fine for all kinds of relations, RelationList- or RelationChoice-fields
    (including the default field "Related Items") as well as for linkintegrity-relations
    and relations between working-copies.
    Uses `collective.relationhelpers  <https://github.com/collective/collective.relationhelpers>`_

cleanup_intids
    Purge all RelationValues and all references to broken objects from the IntId catalog.
    Uses `collective.relationhelpers  <https://github.com/collective/collective.relationhelpers>`_


`finalize.py <https://github.com/collective/collective.migrationhelpers/blob/master/src/collective/migrationhelpers/finalize.py>`_
-----------

Example method for final touces after migrating to 5.2 with py3


`utils.py <https://github.com/collective/collective.migrationhelpers/blob/master/src/collective/migrationhelpers/utils.py>`_
--------

disable_subscriber
    Disable a subscriber

enable_subscriber
    Re-enable a subscriber

example_with_disabled_subscriber
    Example to use the above

rebuild_catalog_without_indexing_blobs
    Rebuild the whole catalog but skip reindexing blobs since that takes a long time.

pack_database
    Pack the database


profiles/migration
------------------

Example of a profile that removes all kinds of stuff that was added with Generic Setup.

Bonus: Fixes modal for login.


profiles/default/registry.xml
-----------------------------

Example for some maybe sensible registry-settings for migrated sites.


Installation
------------

This is mostly meant to copy&paste the code from here to your own packages.

Installation is still possible: To install it add it to your buildout::

    [buildout]

    ...

    eggs =
        collective.migrationhelpers


and then running ``bin/buildout``


Contribute
----------

- Issue Tracker: https://github.com/collective/collective.migrationhelpers/issues
- Source Code: https://github.com/collective/collective.migrationhelpers


License
-------

The project is licensed under the GPLv2.
