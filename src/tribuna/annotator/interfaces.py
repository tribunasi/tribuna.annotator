# -*- coding: utf-8 -*-
"""Module where all interfaces, events and exceptions live."""

from plone.theme.interfaces import IDefaultPloneLayer
from zope.interface import Interface


class ITribunaAnnotatorLayer(IDefaultPloneLayer):
    """Marker interface that defines a Zope 3 browser layer."""


class ITribunaAnnotator(Interface):
    """Support adding annotations to parts of the text. See
    http://okfnlabs.org/annotator/ for more info.

    To enable the annotation on your content type:

      * Your content type needs to provide this interface

      * Content type needs to be folderish, because we store annotations as
        normal plone objects inside 'annotations-folder' subfolder.

        XXX: We should store annotations similar to what plone.app.discussion
        does

    * You need to have an element with id "annotator" in the content type
      template.

    XXX: I tried applying this interface as a marker interface with a
    behavior, but it didn't seem to work (interface was there, but we'd
    have to manually enable it for each object)
    """
