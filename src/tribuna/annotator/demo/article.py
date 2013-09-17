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
