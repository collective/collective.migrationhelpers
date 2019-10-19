.. This README is meant for consumption by humans and pypi. Pypi can render rst files so please do not use Sphinx features.
   If you want to learn more about writing documentation, please check out: http://docs.plone.org/about/documentation_styleguide.html
   This text does not appear on pypi or github. It is a comment.

===========================
collective.migrationhelpers
===========================

Some helpers and examples to use during migrations


statistics.py
-------------

Browser-Views to get information about the portal:


`migrations_stats`
    Get info about the content is in the portal.

`migrations_contentsize`
    How many MB of which content is there really?

`migrations_obsoleteinfo`
    Get info about content-types that may needs to be replaced

`migrations_localroles`
    Export info about local roles. A alternative would be zopyx.plone.cassandra



prepare.py
----------

Prepare the portal for a migration

`disable_solr`
    Disable solr

`disable_ldap`
    Disable ldap/ad-plugins

`remove_overrides`
    Remove any portal_skin an portal_view_customization overrides.



cleanup.py
----------

Fremove obsolete content and settings

delete_items_larger_than_1mb
    Deletes heavy content

remove_all_revisions
    Clear out portal_historiesstorage

disable_theme
    Disable diazo theme, enable suburst (useful for Plone 4)



addons.py
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

`_unregisterUtility`
    Example that removes p4a.subtyper utilities (used in collective.easyslideshow)

`remove_vocabularies`
    Example that removes p4a.subtyper utilities


persistent_utilities_adapaters_and_subscribers.py
-------------------------------------------------

Some examples that remove various adapters, subscriber and utilities.

See also:

* Use alias_module (see `patches.py`)
* profiles/migration/componentregistry.xml
* wildcard.fixpersistentutilities


import_steps.py
---------------

Remove broken and outdated import/export steps


linguaplone.py
--------------

Examples that can help migrating from LinguaPlone to plone.app.multilingual

cleanup_content_for_pam
    Crazy method that sets languages, adds and links translations so that we can migrate to pam.

install_pam
    Install pam and setup site

migrate_to_pam
    Migrate LinguaPlone to plone.app.multilingual
    This mostly uses the migration that is builtin in plone.app.multilingual


dexterity.py
------------

Methods to migrate default content to Dexterity.


custom_at_to_dx_migration.py
----------------------------

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


archetypes.py
-------------

remove_archetypes
    Uninstall Archetypes and remove all of its traces.



patches.py
----------

Multilple examples of patches using alias_module to deal with migration-problems.


images.py
---------

fix_at_image_scales
    Fix/Migrate custom images/scales and broken links to AT-based images.



post_python3_fixes.py
---------------------

fix_event_indexes
    Metadata on brains is still old DateTime

fix_searchable_text
    Fix bytes in opkapiindex

fix_portlets
    Fix navigation_portlet (has ComputedValue for portal instead of a UUID)


finalize.py
-----------

Example method for final touces after migrating to 5.2 with py3


utils.py
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

It is not rally tested for installation but might be possible.
Instead you could copy/paste the code from here to your own packages.

Install collective.migrationhelpers by adding it to your buildout::

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
