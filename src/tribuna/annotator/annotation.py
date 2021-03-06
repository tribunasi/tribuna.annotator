"""The Annotation content type."""

from collective import dexteritytextindexer
from five import grok
from plone import api
from plone.app.layout.viewlets.interfaces import IBelowContent
from plone.dexterity.content import Item
from plone.directives import form
from tribuna.annotator.interfaces import ITribunaAnnotator
from tribuna.annotator.utils import unrestricted_create
from zExceptions import NotFound
from zope import schema
from zope.interface import Interface
from zope.interface import implements
from zope.publisher.interfaces import IPublishTraverse

import json

from tribuna.annotator.utils import get_annotations

ANNOTATOR_JS = """
<script>
    $(function() {
        var content = $("#annotator").annotator();

        content.annotator('addPlugin', 'Tags');
        content.annotator('addPlugin', 'Store', {
            // The endpoint of the store on your server.
            prefix: '/%s',
         });
    });
</script>"""


def jsonify(request, data):
    json_data = json.dumps(data)
    request.response.setHeader("Content-type", "application/json")
    return json_data


class IAnnotation(form.Schema):
    """Interface for Annotation content type."""

    form.primary('title')
    title = schema.TextLine(
        title=u"Name",
    )

    text = schema.Text(
        title=u"Text",
    )

    dexteritytextindexer.searchable('quote')
    quote = schema.Text(
        title=u"Quote",
    )

    user = schema.TextLine(
        title=u"User",
        description=u"User sent by annotator"
    )

    plone_user_id = schema.TextLine(
        title=u"Plone user",
        description=u"ID of the Plone user that created the annotation"
    )

    consumer = schema.TextLine(
        title=u"Consumer",
    )

    ranges = schema.List(
        title=u"Ranges",
    )


class Annotation(Item):
    implements(IAnnotation)

    def Description(self):
        return self.quote


#class AnnotationJSONView(grok.View):
#    """View for the Annotation content type which returns annotation data
#    in JSON format.
#    """
#    grok.context(IAnnotation)
#    grok.require('zope2.View')
#    grok.name('view')
#
#    def render(self):
#        annotation = self.context
#        annotation_data = {
#            'created': annotation.created().ISO8601(),
#            'id': annotation.id,
#            'quote': annotation.quote,
#            'ranges': annotation.ranges,
#            'tags': annotation.Subject(),
#            'text': '',
#            'updated': annotation.modified().ISO8601()
#        }
#        return jsonify(self.request, annotation_data)


class AnnotationsViewlet(grok.Viewlet):
    """Viewlet which renders the annotator initialization code."""
    grok.context(ITribunaAnnotator)
    grok.require('zope2.View')
    grok.viewletmanager(IBelowContent)

    def render(self):
        return ANNOTATOR_JS % api.portal.get().id


class ManageAnnotationsView(grok.View):
    """View for managing annotations - creating, reading, deleting...

    XXX: Annotator communicates with this view via a REST interface
    (GET, PUT, POST, DELETE). Currently we only support saving and reading
    annotations. If we want to add support for PUT and DELETE we need to get
    around the fact that Plone only supports GET and POST. Easiest solution
    is probably to rewrite PUT/DELETE requests in nginx to POST requests and
    pass in the original request type as a query arg.
    """
    grok.implements(IPublishTraverse)
    grok.context(Interface)
    grok.require('zope2.View')
    grok.name('annotations')

    annotation_uid = None

    def publishTraverse(self, request, name):
        """Custom traverse method which enables us to have urls in format
        ../@@annotations/annotation_uid instead of
        ../@@annotations/?annotation_uid=...
        """
        if self.annotation_uid is None:
            self.annotation_uid = name
            return self
        else:
            raise NotFound()

    def render(self):
        request_type = self.request.method

        # dispatch based on the request type - note that we always get
        # GET or POST request, since other verbs are unsupported by Plone atm

        # XXX: If we want to make it work for PUT/DELETE requests
        #request_type = self.request.get('req_type', 'Not available')
        # elif request_type == 'PUT':
        #    response = self._handle_PUT()
        #elif request_type == 'DELETE':
        #    response = self._handle_DELETE()

        if request_type == 'GET':
            response = self._handle_GET()
        elif request_type == 'POST':
            response = self._handle_POST()

        return response

    def _handle_GET(self):
        """Handle GET requests - return all saved annotations"""
        return jsonify(self.request, self._get_annotations())

    def _handle_POST(self):
        """Handle POST request - create a new annotation."""
        data = self._get_data()

        if not data:
            return jsonify(
                self.request, 'No JSON sent. Annotation not created.')

        # create a container for annotations, if it doesn't exist yet
        article = self._get_article(data.get('url'))
        container = article.get('annotations-folder', None)
        if not container:
            container = unrestricted_create(
                container=article,
                portal_type='Folder',
                title=u'Annotations folder',
                transition='publish'
            )
            container.setLayout('folder_full_view')

        # create an annotation
        user_id = api.user.get_current().getUserName()
        annotation = unrestricted_create(
            container=container,
            portal_type='tribuna.annotator.annotation',
            title=u'Annotation',
            subject=data['tags'],
            transition='publish',
            text=data.get('text', u''),
            quote=data.get('quote', u''),
            user=data.get('user', u''),
            plone_user_id=user_id,
            consumer=data.get('consumer', u''),
            ranges=data['ranges'],
        )
        # XXX: move to tribuna related code
        with api.env.adopt_user(username='tags_user'):
            api.content.rename(
                obj=annotation, new_id=annotation.UID(), safe_id=True)

        data.update({
            'created': annotation.created().ISO8601(),
            'updated': annotation.modified().ISO8601(),
            'id': annotation.UID()
        })
        annotation.reindexObject()

        return jsonify(self.request, data)

    def _handle_PUT(self):
        """Handle PUT request - update an annotation."""
        raise NotImplemented

    def _handle_DELETE(self):
        """Handle DELETE request - delete an annotation."""
        annotation = api.content.get(UID=self.annotation_uid)
        if annotation:
            del annotation.__parent__[annotation.id]
            return ""
        else:
            return False

    def _get_data(self):
        """Parse data from the request body."""
        return json.loads(self.request.get('BODY'))

    def _get_obj_from_url(self, url):
        """Return object for the provided url."""
        portal_url = api.portal.get().absolute_url()
        obj_path = url.replace(portal_url, '')
        # XXX: temp hack since we have "articles-folder" folder for storing
        # the articles and @@articles fancy view for displaying them
        obj_path = obj_path.replace('/articles/', '/articles-folder/')
        return api.content.get(path=obj_path)

    def _get_article(self, url=None):
        if not url:
            url = self.request['HTTP_REFERER']

            # Remove the GET parameters if we have them
            get_position = url.find('?')
            if get_position != -1:
                url = url[:get_position]

            url = url.strip("/").split("/")
            if '@@' in url[-1]:
                url = url[:-1]
            url = "/".join(url)
        return self._get_obj_from_url(url)

    def _get_annotations(self):
        """Return a list of annotations."""

        article = self._get_article()
        path = '/'.join(article.getPhysicalPath())

        return get_annotations(path)

    def _api(self):
        """Return API description in JSON format."""
        url = self.context.absolute_url()
        return jsonify(self.request, {
            'message': "Annotator Store API",
            'links': {
                'annotation': {
                    'create': {
                        'method': 'POST',
                        'url': url,
                        'query': {
                            'refresh': {
                                'type': 'bool',
                                'desc': ("Force an index refresh after create "
                                         "(default: true)")
                            }
                        },
                        'desc': "Create a new annotation"
                    },
                    'read': {
                        'method': 'GET',
                        'url': url,
                        'desc': "Get an existing annotation"
                    },
                    'update': {
                        'method': 'PUT',
                        'url': url,
                        'query': {
                            'refresh': {
                                'type': 'bool',
                                'desc': ("Force an index refresh after update "
                                         "(default: true)")
                            }
                        },
                        'desc': "Update an existing annotation"
                    },
                    'delete': {
                        'method': 'DELETE',
                        'url': url,
                        'desc': "Delete an annotation"
                    }
                },
            }
        })
