from datetime import date, datetime, time
from decimal import Decimal

import ctds

from .base import TestExternalDatabase
from .compat import long_, PY3, unicode_

class TestCursorDescription(TestExternalDatabase):
    '''Unit tests related to the Cursor.desciption attribute.
    '''
    def test___doc__(self):
        self.assertEqual(
            ctds.Cursor.description.__doc__,
            '''\
A description of the current result set columns.
The description is a sequence of tuples, one tuple per column in the
result set. The tuple describes the column data as follows:

+---------------+--------------------------------------+
| name          | The name of the column, if provided. |
+---------------+--------------------------------------+
| type_code     | The specific type of the column.     |
+---------------+--------------------------------------+
| display_size  | The SQL type size of the column.     |
+---------------+--------------------------------------+
| internal_size | The client size of the column.       |
+---------------+--------------------------------------+
| precision     | The precision of NUMERIC and DECIMAL |
|               | columns.                             |
+---------------+--------------------------------------+
| scale         | The scale of NUMERIC and DECIMAL     |
|               | columns.                             |
+---------------+--------------------------------------+
| null_ok       | Whether the column allows NULL.      |
+---------------+--------------------------------------+

:pep:`0249#description`

:return: A sequence of tuples or None if no results are available.
:rtype: tuple
'''
        )

    def test_before_results(self):
        with self.connect() as connection:
            with connection.cursor() as cursor:
                self.assertEqual(cursor.description, None)

    def test_no_results(self):
        with self.connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute("PRINT('no results here')")
                self.assertEqual(cursor.description, None)

    def test_types(self):
        with self.connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    '''
                    SELECT
                        :0 AS none,
                        :1 AS int,
                        CONVERT(BIGINT, :2) AS bigint,
                        :3 AS bytes,
                        CONVERT(BINARY(10), :3) AS binary10,
                        CONVERT(VARBINARY(10), :3) AS varbinary10,
                        :4 AS bytearray,
                        :5 AS string,
                        CONVERT(CHAR(10), :5) AS char10,
                        CONVERT(VARCHAR(10), :5) AS varchar10,
                        CONVERT(DATETIME, :6) AS datetime,
                        CONVERT(DATE, :7) AS date,
                        CONVERT(TIME, :8) as time,
                        :9 AS decimal,
                        CONVERT(MONEY, :10) AS money
                    ''',
                    (
                        None,
                        -1234567890,
                        2 ** 45,
                        b'1234',
                        bytearray('1234', 'ascii'),
                        unicode_('hello \'world\' ') + unicode_(b'\xc4\x80', encoding='utf-8'),
                        datetime(2001, 1, 1, 12, 13, 14, 150 * 1000),
                        date(2010, 2, 14),
                        time(11, 12, 13, 140 * 1000),
                        Decimal('123.4567890'),
                        Decimal('1000000.0001')
                    )
                )
                self.assertEqual(
                    cursor.description,
                    (
                        ('none', ctds.CHAR, long_(4), long_(4), long_(0), long_(0), True),
                        ('int', ctds.INT, long_(4), long_(4), long_(0), long_(0), True),
                        ('bigint', ctds.BIGINT, long_(8), long_(8), long_(0), long_(0), True),
                        ('bytes', ctds.BINARY, long_(4), long_(4), long_(0), long_(0), True),
                        ('binary10', ctds.BINARY, long_(10), long_(10), long_(0), long_(0), True),
                        ('varbinary10', ctds.BINARY, long_(10), long_(10), long_(0), long_(0), True),
                        ('bytearray', ctds.BINARY, long_(4), long_(4), long_(0), long_(0), True),
                        ('string', ctds.CHAR, long_(64), long_(64), long_(0), long_(0), True),
                        ('char10', ctds.CHAR, long_(40), long_(40), long_(0), long_(0), True),
                        ('varchar10', ctds.CHAR, long_(40), long_(40), long_(0), long_(0), True),
                        ('datetime', ctds.DATETIME, long_(8), long_(8), long_(0), long_(0), True),
                        (
                            ('date', ctds.CHAR, long_(40), long_(40), long_(0), long_(0), True)
                            if connection.tds_version < '7.3'
                            else
                            ('date', ctds.DATE, long_(16), long_(16), long_(0), long_(0), True)
                        ),
                        (
                            ('time', ctds.CHAR, long_(64), long_(64), long_(0), long_(0), True)
                            if connection.tds_version < '7.3'
                            else
                            ('time', ctds.TIME, long_(16), long_(16), long_(7), long_(7), True)
                        ),
                        ('decimal', ctds.DECIMAL, long_(17), long_(17), long_(10), long_(7), True),
                        ('money', ctds.MONEY, long_(8), long_(8), long_(0), long_(0), True)
                    )
                )
                if PY3:
                    self.assertEqual(cursor.description[0].name, 'none')
                    self.assertEqual(cursor.description[0].type_code, ctds.CHAR)
                    self.assertEqual(cursor.description[0].display_size, 4)
                    self.assertEqual(cursor.description[0].internal_size, 4)
                    self.assertEqual(cursor.description[0].scale, 0)
                    self.assertEqual(cursor.description[0].precision, 0)
                    self.assertEqual(cursor.description[0].null_ok, True)
                else: # pragma: nocover
                    pass

    def test_closed(self):
        with self.connect() as connection:
            cursor = connection.cursor()
            try:
                cursor.execute("SELECT 'hi there' as string")
                self.assertNotEqual(cursor.description, None)
            finally:
                cursor.close()

            self.assertEqual(cursor.description, None)
