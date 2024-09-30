.. -*- coding: utf-8; mode: rst -*-
.. include:: refs.txt

.. _`Emacs Table Mode`: https://www.emacswiki.org/emacs/TableMode
.. _`Online Tables Generator`: http://www.tablesgenerator.com/text_tables
.. _`OASIS XML Exchange Table Model`: https://www.oasis-open.org/specs/tm9901.html

.. _xref_table_concerns:

============
About tables
============

.. contents:: Contents
   :depth: 2
   :local:
   :backlinks: entry

.. note::

   The :ref:`rest-flat-table` directive is the most **diff friendly** table
   markup, it is preferred in the Linux kernel tree.


Intro
=====

Internally, the docutils uses a representation according to the `OASIS XML
Exchange Table Model`_ (same as DocBook). The *OASIS Table Model* gives a huge
bandwidth of possibilities to form tables. This often seduce authors to force a
specific layout. The misuse of tables in this manner is not recommended, it
breaks the separation of *presentation from content* which most often ends in
various problems in the range of output formats. Tables (and pre-formated text
like source code listings) should be used advisedly. In a HTML viewer, the
horizontal and vertical expansion is handled by a scrollbar. On print medias
(paper / pdf) there is no scrollbar and automatically page-breaking a table or
line-breaking a pre-formated text in the layout process ends mostly in unwanted
results.

.. hint::

  Tables and pre-formated text in itself violate the separation of *presentation
  from content*, but we will never be able to entirely renounce them. Use them
  with care, if your content should be rendered well, in the wide variation of
  output formats.


ASCII-art tables
================

ASCII-art tables might be comfortable for readers of the text-files, but they
have huge disadvantages in the creation and modifying. First, they are hard to
edit. Think about adding a row or a column to a ASCII-art table or adding a
paragraph in a cell, it is a nightmare on big tables. Second the diff of
modifying ASCII-art tables is not meaningful, e.g. widening a cell generates a
diff in which also changes are included, which are only ascribable to the
ASCII-art (see also :ref:`list-table-directives`).

* `Emacs Table Mode`_
* `Online Tables Generator`_


Simple tables
-------------

simple tables allow *colspan* but not *rowspan*:

..  code-block:: none

  ====== ====== ======
      Inputs    Output
  ------------- ------
  A      B      A or B
  ====== ====== ======
  False
  --------------------
  True
  --------------------
  True   False  True
  ------ ------ ------
  False  True
  ====== =============

Rendered as:

====== ====== ======
    Inputs    Output
------------- ------
A      B      A or B
====== ====== ======
False
--------------------
True
--------------------
True   False  True
------ ------ ------
False  True
====== =============


Grid tables
-----------

grid tables allow colspan *colspan* and *rowspan*:

.. code-block:: rst

   +------------+------------+-----------+
   | Header 1   | Header 2   | Header 3  |
   +============+============+===========+
   | body row 1 | column 2   | column 3  |
   +------------+------------+-----------+
   | body row 2 | Cells may span columns.|
   +------------+------------+-----------+
   | body row 3 | Cells may  | - Cells   |
   +------------+ span rows. | - contain |
   | body row 4 |            | - blocks. |
   +------------+------------+-----------+

Rendered as:

+------------+------------+-----------+
| Header 1   | Header 2   | Header 3  |
+============+============+===========+
| body row 1 | column 2   | column 3  |
+------------+------------+-----------+
| body row 2 | Cells may span columns.|
+------------+------------+-----------+
| body row 3 | Cells may  | - Cells   |
+------------+ span rows. | - contain |
| body row 4 |            | - blocks. |
+------------+------------+-----------+

.. _list-table-directives:

List table directives
=====================

The *list table* formats are double stage list, compared to the ASCII-art they
might not be as comfortable for readers of the text-files. Their advantage is,
that they are easy to create/modify and that the diff of a modification is much
more meaningful, because it is limited to the modified content.

.. _rest-list-table:

list-table
----------

The ``list-tables`` has no ability to *colspan* nor *rowspan*:

.. code-block:: rst

   .. list-table:: list-table example
      :header-rows: 1
      :stub-columns: 1
      :class: my-class
      :name: my-list-table

      * - ..
        - head col 1
        - head col 2

      * - stub col row 1
        - column
        - column

      * - stub col row 2
        - column
        - column

      * - stub col row 3
        - column
        - column


Rendered in :ref:`my-list-table`:

.. list-table:: list-table example
   :header-rows: 1
   :stub-columns: 1
   :class: my-class
   :name: my-list-table

   * - ..
     - head col 1
     - head col 2

   * - stub col row 1
     - column
     - column

   * - stub col row 2
     - column
     - column

   * - stub col row 3
     - column
     - column

.. _rest-flat-table:

flat-table
----------

The ``flat-table`` (:py:class:`FlatTable`) is a double-stage list similar
to the ``list-table`` with some additional features:

* *column-span*: with the role ``cspan`` a cell can be extended through
  additional columns

* *row-span*: with the role ``rspan`` a cell can be extended through
  additional rows

* *auto-span* rightmost cell of a table row over the missing cells on the right
  side of that table-row.  With Option ``:fill-cells:`` this behavior can
  changed from *auto span* to *auto fill*, which automatically inserts (empty)
  cells instead of spanning the last cell.

options:
  :header-rows:   [int] count of header rows
  :stub-columns:  [int] count of stub columns
  :widths:        [[int] [int] ... ] widths of columns
  :fill-cells:    instead of auto-span missing cells, insert missing cells

roles:
  :cspan: [int] additional columns (*morecols*)
  :rspan: [int] additional rows (*morerows*)

The example below shows how to use this markup.  The first level of the staged
list is the *table-row*. In the *table-row* there is only one markup allowed,
the list of the cells in this *table-row*. Exception are *comments* ( ``..`` )
and *targets* (e.g. a ref to :ref:`row 2 of table's body <row body 2>`).

.. code-block:: rst

   .. flat-table:: flat-table example
      :header-rows: 2
      :stub-columns: 1
      :widths: 1 1 1 1 2
      :class: my-class
      :name: my-flat-table

      * - :rspan:`1` head / stub
        - :cspan:`3` head 1.1-4

      * - head 2.1
        - head 2.2
        - head 2.3
        - head 2.4

      * .. row body 1 / this is a comment

        - row 1
        - :rspan:`2` cell 1-3.1
        - cell 1.2
        - cell 1.3
        - cell 1.4

      * .. Comments and targets are allowed on *table-row* stage.
        .. _`row body 2`:

        - row 2
        - cell 2.2
        - :rspan:`1` :cspan:`1`
          cell 2.3 with a span over

          * col 3-4 &
          * row 2-3

      * - row 3
        - cell 3.2

      * - row 4
        - cell 4.1
        - cell 4.2
        - cell 4.3
        - cell 4.4

      * - row 5
        - cell 5.1 with automatic span to rigth end

      * - row 6
        - cell 6.1
        - ..


Rendered in :ref:`my-flat-table`:

 .. flat-table:: flat-table example
    :header-rows: 2
    :stub-columns: 1
    :widths: 1 1 1 1 2
    :class: my-class
    :name: my-flat-table

    * - :rspan:`1` head / stub
      - :cspan:`3` head 1.1-4

    * - head 2.1
      - head 2.2
      - head 2.3
      - head 2.4

    * .. row body 1 / this is a comment

      - row 1
      - :rspan:`2` cell 1-3.1
      - cell 1.2
      - cell 1.3
      - cell 1.4

    * .. Comments and targets are allowed on *table-row* stage.
      .. _`row body 2`:

      - row 2
      - cell 2.2
      - :rspan:`1` :cspan:`1`
        cell 2.3 with a span over

        * col 3-4 &
        * row 2-3

    * - row 3
      - cell 3.2

    * - row 4
      - cell 4.1
      - cell 4.2
      - cell 4.3
      - cell 4.4

    * - row 5
      - cell 5.1 with automatic span to rigth end

    * - row 6
      - cell 6.1
      - ..


CSV table
=========

CSV table might be the choice if you want to include CSV-data from a outstanding
(build) process into your documentation.

.. code-block:: rst

   .. csv-table:: csv-table example
      :header: , Header1, Header2
      :widths: 15, 10, 30
      :stub-columns: 1
      :file: csv_table.txt
      :class: my-class
      :name: my-csv-table

Content of file ``csv_table.txt``:

.. literalinclude:: csv_table.txt

Rendered in :ref:`my-csv-table`:

.. csv-table:: csv-table example
   :header: , Header1, Header2
   :widths: 15, 10, 30
   :stub-columns: 1
   :file: csv_table.txt
   :class: my-class
   :name: my-csv-table


Nested Tables
=============

Nested tables are ugly, don't use them! This part here is only to show what you
should never do. They are ugly because they cause huge problems in many output
formats and there is always no need for nested tables.

.. code-block:: rst

   +-----------+----------------------------------------------------+
   | W/NW cell | N/NE cell                                          |
   |           +-------------+--------------------------+-----------+
   |           | W/NW center | N/NE center              | E/SE cell |
   |           |             +------------+-------------+           |
   |           |             | +--------+ | E/SE center |           |
   |           |             | | nested | |             |           |
   |           |             | +--------+ |             |           |
   |           |             | | table  | |             |           |
   |           |             | +--------+ |             |           |
   |           +-------------+------------+             |           |
   |           | S/SE center              |             |           |
   +-----------+--------------------------+-------------+           |
   | S/SW cell                                          |           |
   +----------------------------------------------------+-----------+

Rendered as: Not supported by all sphinx-builders, don't use nested tables!!!


raw HTML tables
===============

If HTML is the only format you want to render, you could use a raw-import of a
HTML table markup. But be aware, this breaks the separation of *presentation from
content*. HTML-Tables are only rendered within a HTML output.

.. code-block:: html

   <div class="wy-table-responsive">
   <table class="docutils">
     <thead>
       <tr style="font-weight: bold;">
	 <td>Owner Module/Drivers</td>
	 <td>Group</td>
	 <td>Property Name</td>
	 <td>Type</td>
	 <td>Property Values</td>
	 <td>Object attached</td>
	 <td>Description/Restrictions</td>
       </tr>
     </thead>
     <tbody>
       <tr>
	 <td rowspan="4">DRM</td>
	 <td>Generic</td>
	 <td>"rotation"</td>
	 <td>BITMASK</td>
	 <td>{ 0, "rotate-0" }, { 1, "rotate-90" }, { 2, "rotate-180" }, { 3,
	   "rotate-270" }, { 4, "reflect-x" }, { 5, "reflect-y" }</td>
	 <td>CRTC, Plane</td>
	 <td>rotate-(degrees) rotates the image by the specified amount in
	  degrees in counter clockwise direction. reflect-x and reflect-y
	  reflects the image along the specified axis prior to rotation</td>
       </tr>

       <tr>
	 <td rowspan="3">Connector</td>
	 <td>"EDID"</td>
	 <td>BLOB | IMMUTABLE</td>
	 <td>0</td>
	 <td>Connector</td>
	 <td>Contains id of edid blob ptr object.</td>
       </tr>

       <tr>
	 <td>"DPMS"</td>
	 <td>ENUM</td>
	 <td>{ "On", "Standby", "Suspend", "Off" }</td>
	 <td>Connector</td>
	 <td>Contains DPMS operation mode value.</td>
       </tr>

       <tr>
	 <td>"PATH"</td>
	 <td>BLOB | IMMUTABLE</td>
	 <td>0</td>
	 <td>Connector</td>
	 <td>Contains topology path to a connector.</td>
       </tr>
     </tbody>
   </table>
   </div>



.. raw:: html

   <div class="wy-table-responsive">
   <table class="docutils">
     <thead>
       <tr style="font-weight: bold;">
	 <td>Owner Module/Drivers</td>
	 <td>Group</td>
	 <td>Property Name</td>
	 <td>Type</td>
	 <td>Property Values</td>
	 <td>Object attached</td>
	 <td>Description/Restrictions</td>
       </tr>
     </thead>
     <tbody>
       <tr>
	 <td rowspan="4">DRM</td>
	 <td>Generic</td>
	 <td>"rotation"</td>
	 <td>BITMASK</td>
	 <td>{ 0, "rotate-0" }, { 1, "rotate-90" }, { 2, "rotate-180" }, { 3,
	   "rotate-270" }, { 4, "reflect-x" }, { 5, "reflect-y" }</td>
	 <td>CRTC, Plane</td>
	 <td>rotate-(degrees) rotates the image by the specified amount in
	  degrees in counter clockwise direction. reflect-x and reflect-y
	  reflects the image along the specified axis prior to rotation</td>
       </tr>

       <tr>
	 <td rowspan="3">Connector</td>
	 <td>"EDID"</td>
	 <td>BLOB | IMMUTABLE</td>
	 <td>0</td>
	 <td>Connector</td>
	 <td>Contains id of edid blob ptr object.</td>
       </tr>

       <tr>
	 <td>"DPMS"</td>
	 <td>ENUM</td>
	 <td>{ "On", "Standby", "Suspend", "Off" }</td>
	 <td>Connector</td>
	 <td>Contains DPMS operation mode value.</td>
       </tr>

       <tr>
	 <td>"PATH"</td>
	 <td>BLOB | IMMUTABLE</td>
	 <td>0</td>
	 <td>Connector</td>
	 <td>Contains topology path to a connector.</td>
       </tr>
     </tbody>
   </table>
   </div>
