"""
Excel generator core.
"""
import io
from xlsxwriter import Workbook


class WorkbookTemplate(object):
    PAPER_PRINTER_DEFAULT = 0
    PAPER_A4 = 9
    PAPER_A4_SMALL = 10

    def create(self):
        pass


class WorksheetTemplate(object):
    @classmethod
    def set_worksheet_settings(cls, xlsx, worksheet_dict, column_count):
        pass


class Cell(object):
    def __init__(self, content, position, cell_format=None):
        self.position = position
        self.content = content
        self.cell_format = cell_format


class BaseXlsx(object):
    workbook: Workbook
    output: io.BytesIO
    worksheets: dict

    def generate(self):
        for title, ws_dict in self.worksheets.items():
            for c in ws_dict['cells']:
                worksheet = ws_dict['worksheet']
                worksheet.write(c.position[0], c.position[1], c.content, c.cell_format)
        self.workbook.close()
        self.output.seek(0)
        return self.output

    def add_worksheet(self, title, worksheet_class):
        worksheet = self.workbook.add_worksheet(name=title)
        assert isinstance(worksheet_class(), WorksheetTemplate)

        self.worksheets[title] = {
            'title': title,
            'worksheet': worksheet,
            'worksheet_class': worksheet_class,
            'cells': []
        }

        return self.worksheets[title]

    def set_worksheet_margins(self, worksheet_dict,
                              left=0.7,
                              right=0.7,
                              top=0.75,
                              bottom=0.75):
        worksheet_dict['worksheet'].set_margins(left=left, right=right, top=top, bottom=bottom)

    def set_worksheet_header(self, worksheet_dict, header, options=None):
        worksheet_dict['worksheet'].set_header(header=header, options=options)

    def set_worksheet_footer(self, worksheet_dict, footer, options=None):
        worksheet_dict['worksheet'].set_footer(footer=footer, options=options)

    def set_worksheet_landscape(self, worksheet_dict):
        worksheet_dict['worksheet'].set_landscape()

    def set_worksheet_page_view(self, worksheet_dict):
        worksheet_dict['worksheet'].set_page_view()

    def set_worksheet_set_paper(self, worksheet_dict, paper_type):
        worksheet_dict['worksheet'].set_paper(paper_type)

    def set_worksheet_set_print_scale(self, worksheet_dict, scale):
        assert isinstance(scale, int)
        worksheet_dict['worksheet'].set_print_scale(scale)

    def set_worksheet_set_default_row(self, worksheet_dict, height):
        assert isinstance(height, float)
        worksheet_dict['worksheet'].set_default_row(height)

    def set_worksheet_set_row(self, worksheet_dict, row_num, height):
        assert isinstance(row_num, int)
        assert isinstance(height, float)
        worksheet_dict['worksheet'].set_row(row_num, height)

    def set_worksheet_set_column(self, worksheet_dict, first_col, last_col, width):
        assert isinstance(first_col, int)
        assert isinstance(last_col, int)
        assert isinstance(width, float)
        worksheet_dict['worksheet'].set_column(first_col, last_col, width)

    def set_worksheet_settings(self, worksheet_dict, column_count):
        worksheet_dict['worksheet_class'].set_worksheet_settings(self, worksheet_dict, column_count)

    def add_cell(self, worksheet_dict, content, position, cell_format=None):
        if cell_format:
            worksheet_dict['cells'].append(Cell(content, position, cell_format))
        else:
            worksheet_dict['cells'].append(Cell(content, position))

    def add_cell_format(self, cell_format):
        if cell_format:
            cf = self.workbook.add_format(cell_format)
            return cf

    def add_batch_horizontally(self, worksheet_dict, start_position, cells, cell_format=None):
        for idx, c in enumerate(cells):
            self.add_cell(worksheet_dict=worksheet_dict, content=c,
                          position=(start_position[0], start_position[1] + idx),
                          cell_format=cell_format)

    def add_batch_vertically(self, worksheet_dict, start_position, cells, cell_format=None):
        for idx, c in enumerate(cells):
            self.add_cell(worksheet_dict=worksheet_dict, content=c,
                          position=(start_position[0] + idx, start_position[1]),
                          cell_format=cell_format)


class XlsxMixin(object):
    workbook: Workbook
    output: io.BytesIO
    worksheets: dict

    def generate(self):
        for title, ws_dict in self.worksheets.items():
            for c in ws_dict['cells']:
                worksheet = ws_dict['worksheet']
                worksheet.write(c.position[0], c.position[1], c.content, c.cell_format)
        self.workbook.close()
        self.output.seek(0)
        return self.output

    def add_worksheet(self, title, worksheet_class):
        worksheet = self.workbook.add_worksheet(name=title)
        assert isinstance(worksheet_class(), WorksheetTemplate)

        self.worksheets[title] = {
            'title': title,
            'worksheet': worksheet,
            'worksheet_class': worksheet_class,
            'cells': []
        }

        return self.worksheets[title]

    def set_worksheet_margins(self, worksheet_dict,
                              left=0.7,
                              right=0.7,
                              top=0.75,
                              bottom=0.75):
        worksheet_dict['worksheet'].set_margins(left=left, right=right, top=top, bottom=bottom)

    def set_worksheet_header(self, worksheet_dict, header, options=None):
        worksheet_dict['worksheet'].set_header(header=header, options=options)

    def set_worksheet_footer(self, worksheet_dict, footer, options=None):
        worksheet_dict['worksheet'].set_footer(footer=footer, options=options)

    def set_worksheet_landscape(self, worksheet_dict):
        worksheet_dict['worksheet'].set_landscape()

    def set_worksheet_page_view(self, worksheet_dict):
        worksheet_dict['worksheet'].set_page_view()

    def set_worksheet_set_paper(self, worksheet_dict, paper_type):
        worksheet_dict['worksheet'].set_paper(paper_type)

    def set_worksheet_set_print_scale(self, worksheet_dict, scale):
        assert isinstance(scale, int)
        worksheet_dict['worksheet'].set_print_scale(scale)

    def set_worksheet_set_default_row(self, worksheet_dict, height):
        assert isinstance(height, float)
        worksheet_dict['worksheet'].set_default_row(height)

    def set_worksheet_set_row(self, worksheet_dict, row_num, height):
        assert isinstance(row_num, int)
        assert isinstance(height, float)
        worksheet_dict['worksheet'].set_row(row_num, height)

    def set_worksheet_set_column(self, worksheet_dict, first_col, last_col, width):
        assert isinstance(first_col, int)
        assert isinstance(last_col, int)
        assert isinstance(width, float)
        worksheet_dict['worksheet'].set_column(first_col, last_col, width)

    def set_worksheet_settings(self, worksheet_dict, column_count):
        worksheet_dict['worksheet_class'].set_worksheet_settings(self, worksheet_dict, column_count)

    def add_cell(self, worksheet_dict, content, position, cell_format=None):
        if isinstance(content, int):
            cell_format.set_num_format('# ### ### ###')
        if cell_format:
            worksheet_dict['cells'].append(Cell(content, position, cell_format))
        else:
            worksheet_dict['cells'].append(Cell(content, position))

    def add_cell_format(self, cell_format):
        if cell_format:
            cf = self.workbook.add_format(cell_format)
            return cf

    def add_batch_horizontally(self, worksheet_dict, start_position, cells, cell_format=None):
        for idx, c in enumerate(cells):
            self.add_cell(worksheet_dict=worksheet_dict, content=c,
                          position=(start_position[0], start_position[1] + idx),
                          cell_format=cell_format)

    def add_batch_vertically(self, worksheet_dict, start_position, cells, cell_format=None):
        for idx, c in enumerate(cells):
            self.add_cell(worksheet_dict=worksheet_dict, content=c,
                          position=(start_position[0] + idx, start_position[1]),
                          cell_format=cell_format)


class InMemoryXlsx(XlsxMixin):
    """ Helper class for creating an in-memory XLSX. """

    def __init__(self):
        self.output = io.BytesIO()
        self.workbook = Workbook(self.output, {'in_memory': True,
                                               'default_date_format': 'yyyy-mm-dd',
                                               'strings_to_urls': False})
        self.worksheets = {}


class ConstantMemoryXlsx(XlsxMixin):
    """ A helper class for creating a constant memory XLSX
        which is better for large XLSX files in order to maintain
        a moderate memory footprint.

        @src: https://xlsxwriter.readthedocs.io/working_with_memory.html
    """

    def __init__(self):
        self.output = io.BytesIO()
        self.workbook = Workbook(self.output, {'constant_memory': True,
                                               'default_date_format': 'yyyy-mm-dd',
                                               'strings_to_urls': False})
        self.worksheets = {}
