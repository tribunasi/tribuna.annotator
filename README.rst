=================
tribuna.annotator
=================

A Plone add-on that (partly) integrates the annotator jQuery plug-in
for adding text annotations. See http://okfnlabs.org/annotator/ for
more info about the plug-in.

This package is part of tribuna.* series, which are used to build
http://www.tribuna.si web page (a student magazine). Note that this
package doesn't implement all annotator functions like delete etc..
It also contains some Tribuna specific code, so it's not generic
enough for all use cases. For a more comprehensive general annotator
integration you should look into eea.annotator instead:
https://github.com/collective/eea.annotator

* `Source code @ GitHub <https://github.com/Tribuna/tribuna.annotator>`_


Installation
============

To install `tribuna.annotator`, add ``tribuna.annotator``
to the list of eggs in your buildout, run buildout and restart Plone.
Then, install `tribuna.annotator` using the Add-ons control panel.

If you want to make your content type annotator aware, you need to do
the following:

* Your content type needs to provide the ITribunaAnnotator interface

* Content type needs to be folderish, because we store annotations as
  normal plone objects inside 'annotations-folder' subfolder.

* You need to have an element with id "annotator" in the content type
  template. Annotator will be initialized on this element.


Copyright and licence
=====================

Copyright Študentska organizacija Slovenije and Termitnjak d.o.o.

tribuna.annotator was funded by the Študentska organizacija
Slovenije and is licensed under the MIT License. More details under
docs/License.rst.

