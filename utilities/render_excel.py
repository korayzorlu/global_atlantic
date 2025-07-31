import io

# from django.http import HttpResponse
# from past.builtins import xrange
# from xlsxwriter import Workbook


def render_to_excel(sheet_name, styles, columns, data, attributes, sum_attributes=None):
    output = io.BytesIO()
    book = Workbook(output)
    sheet = book.add_worksheet(sheet_name)

    headers_only = [k for k, v in columns.items()]
    column_widths = {k: 0 for k, v in columns.items()}

    for col, header in enumerate(headers_only):
        width = len(header) + 6
        sheet.write(0, col, header, book.add_format(styles.get('header', None)))
        sheet.set_column(col, col + 1, width)
        column_widths[col] = width

    for row, obj in enumerate(data, start=1):
        width = len(str(row)) + 6
        sheet.write(row, 0, row, book.add_format(columns[headers_only[0]]))
        if column_widths[0] < width:
            sheet.set_column(row, row + 1, width)
            column_widths[0] = width
        for col, item in enumerate([igetattr(obj, attr) for attr in attributes], start=1):
            width = len(str(item)) + 6
            sheet.write(row, col, item, book.add_format(columns[headers_only[col]]))
            if column_widths[col] < width:
                sheet.set_column(col, col + 1, width)
                column_widths[col] = width

    box(book, sheet, len(data) + 1, 0, len(data) + 1, len(headers_only) - 1, default_format=styles.get('border'))

    if sum_attributes:
        for attribute in sum_attributes:
            column_char = chr(headers_only.index(attribute) + 1 + 96).upper()
            last_row = len(data) + 2
            sheet.write_formula(f'{column_char}{last_row}', f'=SUM({column_char}1:{column_char}{last_row - 1})')

    book.close()

    # construct response
    output.seek(0)

    return HttpResponse(output.read())


def add_to_format(existing_format, dict_of_properties, workbook):
    """Give a format you want to extend and a dict of the properties you want to
    extend it with, and you get them returned in a single format"""
    new_dict = {}
    for key, value in existing_format.__dict__.items():
        if (value != 0) and (value != {}) and (value is not None):
            new_dict[key] = value
    del new_dict['escapes']
    new_dict.update(dict_of_properties)
    return workbook.add_format(new_dict)


# https://stackoverflow.com/a/26429246/14506165
def box(workbook, sheet_name, row_start, col_start, row_stop, col_stop, default_format=None):
    """Makes an RxC box. Use integers, not the 'A1' format"""

    rows = row_stop - row_start + 1
    cols = col_stop - col_start + 1

    for x in xrange((rows) * (cols)):  # Total number of cells in the rectangle

        box_form = workbook.add_format(default_format)  # The format resets each loop
        row = row_start + (x // cols)
        column = col_start + (x % cols)

        if x < (cols):  # If it's on the top row
            box_form = add_to_format(box_form, {'top': 1}, workbook)
        if x >= ((rows * cols) - cols):  # If it's on the bottom row
            box_form = add_to_format(box_form, {'bottom': 1}, workbook)
        if x % cols == 0:  # If it's on the left column
            box_form = add_to_format(box_form, {'left': 1}, workbook)
        if x % cols == (cols - 1):  # If it's on the right column
            box_form = add_to_format(box_form, {'right': 1}, workbook)
        sheet_name.write(row, column, "", box_form)


def igetattr(obj, attr):
    attrs = attr.split('__')
    if len(attrs) > 1:
        r_attr = getattr(obj, attrs[0]) if hasattr(obj, attrs[0]) else None
        return igetattr(r_attr, '__'.join(attrs[1:])) if r_attr else r_attr
    else:
        r_attr = getattr(obj, attrs[0]) if hasattr(obj, attrs[0]) else None
        if callable(r_attr):
            return r_attr()
        return r_attr
