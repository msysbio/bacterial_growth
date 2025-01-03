μGrowthDB
==================

.. only:: html

   .. image:: https://readthedocs.org/projects/crest/badge/?version=latest
      :target: https://mgrowthdb.readthedocs.io/en/latest/?badge=latest
      :alt: Documentation Status

.. NOTE:
.. Subsequent captions are broken in PDFs: https://github.com/sphinx-doc/sphinx/issues/4977.

.. NOTE:
.. :numbered: has bugs with PDFs: https://github.com/sphinx-doc/sphinx/issues/4318.

.. NOTE:
.. only directive does not work with tocree directive for HTML.

.. .. only:: latex
..
..    .. toctree::
..       :hidden:
..       :caption: User Guide
..
..       about/introduction

.. NOTE:
.. ":numbered: 1" means numbering is only one deep. Needed for the version history.


.. toctree::
   :numbered: 1
   :maxdepth: 2
   :caption: About μGrowthDB

   about/introduction
   about/known-issues
   about/history
..    about/integrations


.. toctree::
   :numbered: 
   :maxdepth: 3
   :caption: Data Submission

   submission/upload


.. toctree::
   :numbered: 
   :maxdepth: 3
   :caption: Data Discovery and Retrieval

   retrieval/discover

.. toctree::
   :numbered: 
   :maxdepth: 3
   :caption: Tips and hints

   faqs/faqs



.. NOTE:
.. Tried to have only the title show in the ToC, but it looks like Sphinx is ignoring toctree options.

.. .. only:: latex
..
..    .. toctree::
..
..       meta/history

.. TODO:
..   user/support

.. only:: html

   .. toctree::
      :maxdepth: 1
      :caption: Developer Guide

      dev/contributing