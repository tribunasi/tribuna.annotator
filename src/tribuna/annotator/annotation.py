#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The Annotation content type."""

from five import grok
from plone import api
from plone.directives import form
from zope import schema
from zope.interface import Interface

import json


class IAnnotation(form.Schema):
    """Interface for Annotation content type."""

    form.primary('title')
    title = schema.TextLine(
        title=u"Name",
    )

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


class View(grok.View):
    grok.context(Interface)
    grok.require('zope2.View')
    grok.name('annotation-view')


class Annotations(grok.View):
    grok.context(Interface)
    grok.require('zope2.View')
    grok.name('annotations')

    def render(self):
        #request_type = self.request.get('verb', 'Not available')
        request_type = self.request.method

        # dispatch based on the request type - note that we always get
        # GET or POST request, since other verbs are unsupported by Plone atm
        # We rewrite PUT/DELETE requests in nginx and pass in the original
        # request type as a query arg.
        if request_type == 'GET':
            response = self._handle_GET()
        elif request_type == 'POST':
            response = self._handle_POST()
        if request_type == 'PUT':
            response = self._handle_PUT()
        if request_type == 'DELETE':
            response = self._handle_DELETE()

        return response

    def _jsonify(self, data):
        json_data = json.dumps(data)
        self.request.response.setHeader("Content-type", "application/json")
        return json_data

    def _get_data(self):
        """Parse data from the request body."""
        return json.loads(self.request.get('BODY'))

    def _get_obj_from_url(self, url):
        portal_url = api.portal.get().absolute_url()
        obj_path = url.replace(portal_url, '')
        return api.content.get(path=obj_path)

    def _get_article(self, url=None):
        if not url:
            url = "/".join(self.request['HTTP_REFERER'].split("/")[:-1])
        return self._get_obj_from_url(url)

    def _get_annotations(self):
        """Return a list of annotations."""

        article = self._get_article()
        path = '/'.join(article.getPhysicalPath())
        catalog = api.portal.get_tool('portal_catalog')

        brains = catalog(
            portal_type='tribuna.annotator.annotation',
            path={"query": path, "depth": 1}
        )
        annotations = []
        for brain in brains:
            annotation = brain.getObject()
            annotations.append({
                'created': annotation.created().ISO8601(),
                'id': annotation.id,
                'quote': annotation.quote,
                'ranges': annotation.ranges,
                'tags': annotation.Subject,
                'text': '',
                'updated': annotation.modified().ISO8601()
            })
        return annotations

    def _handle_GET(self):
        """Handle GET requests - return API description in JSON format."""
        return self._jsonify(self._get_annotations())

    def _api(self):
        """Return API description in JSON format."""
        url = self.context.absolute_url()
        return self._jsonify({
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

    def _handle_POST(self):
        """Handle POST request - create a new annotation."""
        data = self._get_data()

        if not data:
            return self._jsonify('No JSON sent. Annotation not created.')

        article = self._get_article(data.get('url'))
        user_id = api.user.get_current().id
        annotation = api.content.create(
            title=u'Annotation',
            container=article,
            type='tribuna.annotator.annotation',
            user=data.get('user', u''),
            plone_user_id=user_id,
            consumer=data.get('consumer', u''),
            ranges=data['ranges'],
            Subject=data['tags']
        )
        data.update({
            'created': annotation.created().ISO8601(),
            'updated': annotation.modified().ISO8601(),
            'id': annotation.id
        })
        return self._jsonify(data)

    def _handle_PUT(self):
        """Handle PUT request - update an annotation."""

    def _handle_DELETE(self):
        """Handle DELETE request - delete an annotation."""
