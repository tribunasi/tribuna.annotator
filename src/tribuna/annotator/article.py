from plone.directives import form
from zope import schema


class IArticle(form.Schema):
    """Interface for Article content type."""

    form.primary('title')
    title = schema.TextLine(
        title=u"Name",
    )

    subtitle = schema.TextLine(
        title=u"Article subtitle",
        required=False,
    )

    article_author = schema.TextLine(
        title=u"Article author",
        required=False,
    )

    description = schema.Text(
        title=u"Article description",
        required=False,
    )

    text = schema.Text(
        title=u"Body text",
        required=False,
    )
