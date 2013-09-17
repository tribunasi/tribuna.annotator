# -*- coding: utf-8 -*-
"""Module where all interfaces, events and exceptions live."""

from plone.theme.interfaces import IDefaultPloneLayer
from zope.interface import Interface


class ITribunaAnnotatorLayer(IDefaultPloneLayer):
    """Marker interface that defines a Zope 3 browser layer."""


class ITribunaAnnotator(Interface):
    """Support adding annotations to parts of the text. Your content type
    should provide this interface for annotations to work.

    Annotator expects a folderish type, because we store annotations as
    normal plone objects inside 'annotations-folder' folder inside the
    ITribunaAnnotator implementer. We also need a 'text' field on which
    the annotator operates.

    XXX: We should store annotations similar to what plone.app.discussion
    does

    XXX: I tried applying it as a marker interface with a behavior, but
    it didn't seem to work (interface was there, but we'd have to manually
    enable it for each object)
    """
