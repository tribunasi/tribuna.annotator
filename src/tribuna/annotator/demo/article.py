from five import grok
from plone.directives import form
from tribuna.annotator.interfaces import ITribunaAnnotator
from zope import schema


class IArticle(form.Schema, ITribunaAnnotator):
    """Interface for Article content type."""

    form.primary('title')
    title = schema.TextLine(
        title=u"Name",
    )

    text = schema.Text(
        title=u"Body text",
        required=False,
    )


class AnnotationsView(grok.View):
    """View for annotating text with the Annotator plugin."""
    grok.context(ITribunaAnnotator)
    grok.require('zope2.View')
    grok.name('annotations-view')
