from .xlsx import InMemoryXlsx, WorksheetTemplate, WorkbookTemplate, ConstantMemoryXlsx


class ExperimentWorkbookTemplate(WorkbookTemplate):
    """
    Workbook template. Note! Workbook is different than Worksheet.
    """
    # Workbook style names
    TITLE = "TITLE"
    CELL = "CELL"

    STYLES = {TITLE: {'color': '#000000',
                      'bold': 1,
                      'font_name': 'Franklin Gothic Medium',
                      'font_size': 9,
                      'align': 'left',
                      'valign': 'top',
                      'text_wrap': True,
                      },
              CELL: {'color': '#000000',
                     'font_name': 'Franklin Gothic Medium',
                     'font_size': 9,
                     'align': 'left',
                     'valign': 'top',
                     'text_wrap': True,
                     }
              }

    def __init__(self, queryset, constant_memory=False):
        self.styles = {}
        self.xlsx = None
        self.queryset = queryset
        self.constant_memory = constant_memory

    def create(self):
        if self.constant_memory:
            self.xlsx = ConstantMemoryXlsx()
        else:
            self.xlsx = InMemoryXlsx()

        self.add_styles()

    def add_styles(self):
        for key, style_dict in self.STYLES.items():
            self.styles[key] = self.xlsx.add_cell_format(style_dict)


class ExperimentWorksheetTemplate(WorksheetTemplate):
    margins = {
        'left': 0.43,
        'right': 0,
        'top': 0.71,
        'bottom': 0.51
    }
    print_scale = 40

    row_height = 30.0
    title_row_height = 40.0
    column_width = 22.0

    @classmethod
    def set_worksheet_settings(cls, xlsx, worksheet_dict, column_count):
        xlsx.set_worksheet_margins(worksheet_dict, **cls.margins)
        xlsx.set_worksheet_landscape(worksheet_dict)
        xlsx.set_worksheet_page_view(worksheet_dict)
        xlsx.set_worksheet_set_paper(worksheet_dict, WorkbookTemplate.PAPER_A4)
        xlsx.set_worksheet_set_default_row(worksheet_dict, cls.row_height)
        xlsx.set_worksheet_set_row(worksheet_dict, 0, cls.title_row_height)
        xlsx.set_worksheet_set_column(worksheet_dict, 0, column_count, cls.column_width)
        xlsx.set_worksheet_set_print_scale(worksheet_dict, cls.print_scale)
