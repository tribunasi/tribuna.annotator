#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The Annotation content type."""

from five import grok
from plone.directives import form
from zope import schema
from zope.interface import Interface


class IAnnotation(form.Schema):
    """Interface for Annotation content type."""

    form.primary('title')
    title = schema.TextLine(
        title=u"Name",
    )

    description = schema.Text(
        title=u"Ddescription",
        required=False,
    )


class View(grok.View):
    grok.context(Interface)
    grok.require('zope2.View')
    grok.name('annotation-view')

import json

class Annotations(grok.View):
    grok.context(Interface)
    grok.require('zope2.View')
    grok.name('annotations')

    def jsonify(self, data):
        json_data = json.dumps(data)
        self.request.response.setHeader("Content-type", "application/json")
        return json_data

    def render(self):
        url = self.context.absolute_url()

        return self.jsonify({
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
