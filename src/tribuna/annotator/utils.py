from plone import api
from Products.Archetypes.interfaces.base import IBaseObject
from zope.container.interfaces import INameChooser

import random
import transaction


@api.validation.required_parameters('container', 'portal_type')
@api.validation.at_least_one_of('id', 'title')
def unrestricted_create(container=None, portal_type=None,
                        id=None, title=None, transition=None, **kwargs):
    """Create content, bypassing security checks.

    XXX: this would be a bit cleaner if we used api.env.adopt_roles,
    but it doesn't seem to work properly..

    XXX 2: Verbose security needs to be turned on in buildout to make
    this method work. WTF! We need to fix this.

    :param container: container for the created object
    :param portal_type: type of the object to create
    :param id: id of the object to create
    :param title: title of the object to create
    :param transition: name of a workflow transition to perform after
        creation
    :param kwargs: additional parameters which are passed to the
        createContent function (e.g. title, description etc.)
    :returns: object that was created
    """
    portal_types = api.portal.get_tool("portal_types")
    type_info = portal_types.getTypeInfo(portal_type)
    content_id = id or str(random.randint(0, 99999999))
    obj = type_info._constructInstance(
        container, content_id, title=title, **kwargs)

    # Archetypes specific code
    if IBaseObject.providedBy(obj):
        # Will finish Archetypes content item creation process,
        # rename-after-creation and such
        obj.processForm()

    if not id:
        # Create a new id from title
        chooser = INameChooser(container)
        derived_id = id or title
        new_id = chooser.chooseName(derived_id, obj)
        transaction.savepoint(optimistic=True)
        with api.env.adopt_roles(['Manager', 'Member']):
            obj.aq_parent.manage_renameObject(content_id, new_id)

    # perform a workflow transition
    if transition:
        with api.env.adopt_roles(['Manager', 'Member']):
            api.content.transition(obj, transition=transition)

    return obj


def get_annotations(path):
    """Return a list of annotations."""

    catalog = api.portal.get_tool('portal_catalog')

    brains = catalog(
        portal_type='tribuna.annotator.annotation',
        path={"query": path, "depth": 2}
    )
    annotations = []
    for brain in brains:
        annotation = brain.getObject()
        annotations.append({
            'created': annotation.created().ISO8601(),
            'id': annotation.UID(),
            'quote': annotation.quote,
            'ranges': annotation.ranges,
            'tags': annotation.Subject(),
            'text': annotation.text,
            'updated': annotation.modified().ISO8601()
        })

    return annotations
