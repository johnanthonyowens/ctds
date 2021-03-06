Reading Result Sets
===================

*cTDS* supports reading multiple result sets generated by
:py:meth:`ctds.Cursor.execute()` or :py:meth:`ctds.Cursor.callproc()`.

Due to the design of the TDS protocol, it is recommended to read all rows of
all result set(s) as soon as possible to allow the database server to reclaim
resources associated with the result set(s).


Fetching Rows
-------------
Rows from the current result set can be read using any of
:py:meth:`ctds.Cursor.fetchone()`, :py:meth:`ctds.Cursor.fetchmany()`, or
:py:meth:`ctds.Cursor.fetchall()` methods. *cTDS* will cache all retrieved raw
row data. However, to save memory, it is only converted to Python objects when
first accessed from the Python client. This is done to minimize memory overhead
when processing large result sets. Columns for the current resultset can be
retrieved using the :py:attr:`ctds.Cursor.description` property.

.. code-block:: python

    import ctds
    with ctds.connect(*args, **kwargs) as connection:
        with connection.cursor() as cursor:
            cursor.callproc('GetSomeResults', (1,))
            rows = cursor.fetchall()

            # Get column names.
            columns = [column.name for column in cursor.description]

    # Process the rows after releasing the connection
    print(columns)
    for row in rows:
        # Do stuff with the rows.
        print(tuple(row))


The row list returned from :py:meth:`ctds.Cursor.fetchmany()`, or
:py:meth:`ctds.Cursor.fetchall()` implements the Python sequence protocol and
therefore supports indexing. For example,

.. code-block:: python

    import ctds
    with ctds.connect(*args, **kwargs) as connection:
        with connection.cursor() as cursor:
            cursor.callproc('GetSomeResults', (1,))
            rows = cursor.fetchall()

    if len(rows) > 5:
        # Print the first column of row 5.
        print(rows[5][0])


.. note::

    Unless a result set contains a large number of rows, it is typically
    recommended to use :py:meth:`ctds.Cursor.fetchall()` to retrieve all the
    rows of a result. Only when result sets are sufficiently large as to make
    caching them a large memory burden is it recommended to use
    :py:meth:`ctds.Cursor.fetchone()` or :py:meth:`ctds.Cursor.fetchmany()`.


Reading Columns
^^^^^^^^^^^^^^^
*cTDS* rows support referencing column values multiple ways: you can index
a row by either a column number or a column name, use a column name as an
attribute of the row, or build a dictionary mapping column names to values.

.. code-block:: python

    import ctds
    with ctds.connect(*args, **kwargs) as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                '''
                SELECT
                    'unnamed',
                    2 AS Column2,
                    'Three' AS Column3
                '''
            )
            rows = cursor.fetchall()

    for row in rows:
        # index
        assert row[0] == 'unnamed'

        # attribute
        assert row.Column2 == 2

        # mapping
        assert row['Column3'] == 'Three'

        # dict - note that the column number is used as the key
        # for any unnamed columns
        assert row.dict() == {
            0: 'unnamed',
            'Column1': 1,
            'Column2': '2',
            'Column3': 'Three',
        }

Advancing the Result Set
------------------------

The result set can be advanced using the :py:meth:`ctds.Cursor.nextset()`
method. New operations using :py:meth:`ctds.Cursor.execute()` or
:py:meth:`ctds.Cursor.callproc()` will discard any unread result sets.

.. note::

   Previous result sets cannot be retrieved once the cursor has been advanced
   past them.

