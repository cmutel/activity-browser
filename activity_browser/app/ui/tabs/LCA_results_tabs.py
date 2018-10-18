# -*- coding: utf-8 -*-
from activity_browser.app.ui.style import horizontal_line, vertical_line, header
from activity_browser.app.ui.tables import (
    LCAResultsTable,
    ProcessContributionsTable,
    InventoryTable,
    InventoryCharacterisationTable,
    BiosphereTable
)
from activity_browser.app.ui.graphics import (
    LCAResultsPlot,
    ProcessContributionPlot,
    InventoryCharacterisationPlot,
    CorrelationPlot,
    LCAResultsBarChart
)
from activity_browser.app.bwutils.multilca import MLCA
from activity_browser.app.bwutils import commontasks as bc
from activity_browser.app.ui.widgets.log_slider import LogarithmicSlider


from PyQt5.QtWidgets import QWidget, QTabWidget, QVBoxLayout, QHBoxLayout, QScrollArea, QRadioButton, QSlider, \
    QLabel, QLineEdit, QCheckBox, QPushButton, QComboBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIntValidator, QDoubleValidator

# TODO: LOW PRIORITY: add filtering for tables/graphs


class LCAResultsSubTab(QTabWidget):
    def __init__(self, parent, name):
        super(LCAResultsSubTab, self).__init__(parent)
        self.panel = parent
        self.setup_name = name
        self.method_dict = dict()

        self.setVisible(False)
        self.visible = False

        self.setTabShape(1)  # Triangular-shaped Tabs
        self.setTabPosition(1)  # South-facing Tabs

        self.update_calculation()

        self.LCAscoreComparison_tab = LCAScoreComparisonTab(self)
        # self.inventory_tab = InventoryTab(self, custom=True)
        self.inventory_characterisation_tab = CharacterisationTab(self, relativity=True)
        self.lcia_results_tab = LCIAAnalysisTab(self, relativity=True)
        self.process_contributions_tab = ProcessContributionsTab(self, relativity=True)
        self.correlations_tab = CorrelationsTab(self)

        self.update_setup(calculate=False)

    def update_setup(self, calculate=True):
        """ Update the calculation setup. """
        if calculate:
            self.update_calculation()

        self.LCAscoreComparison_tab.update_analysis_tab()
        # self.inventory_tab.update_analysis_tab()
        self.inventory_characterisation_tab.update_analysis_tab()
        self.lcia_results_tab.update_analysis_tab()
        self.process_contributions_tab.update_analysis_tab()
        self.correlations_tab.update_analysis_tab()

        lca_score_comparison_tab_index = self.indexOf(self.LCAscoreComparison_tab)
        lcia_results_tab_index = self.indexOf(self.lcia_results_tab)
        correlations_tab_index = self.indexOf(self.correlations_tab)

        if not self.single_func_unit:
            self.setTabEnabled(lcia_results_tab_index, True)
            self.setTabEnabled(correlations_tab_index, True)
            self.setTabEnabled(lca_score_comparison_tab_index, True)
        else:
            self.setTabEnabled(lcia_results_tab_index, False)
            self.setTabEnabled(correlations_tab_index, False)
            self.setTabEnabled(lca_score_comparison_tab_index, False)

    def update_calculation(self):
        """ Update the mlca calculation. """
        self.mlca = MLCA(self.setup_name)

        self.method_dict = bc.get_LCIA_method_name_dict(self.mlca.methods)

        if len(self.mlca.func_units) != 1:
            self.single_func_unit = False
        else:
            self.single_func_unit = True
        if len(self.mlca.methods) != 1:
            self.single_method = False
        else:
            self.single_method = True


class AnalysisTab(QWidget):
    def __init__(self, parent, cutoff=None, func=None, combobox=None, table=None,\
                 plot=None, export=None, relativity=None, custom=False, *args, **kwargs):
        super(AnalysisTab, self).__init__(parent)
        self.setup = parent

        self.custom = custom
        self.cutoff_menu = cutoff
        self.cutoff_func = func

        self.combobox_menu_combobox = combobox
        self.table = table
        self.plot = plot
        self.limit_type = "percent"
        self.export_menu = export
        self.relativity = relativity
        self.relative = True

        self.name = str()
        self.header = header(self.name)

        #layout for custom tab (currently only InventoryTab)
        # if self.custom:
        #     self.Second_Space = QScrollArea()
        #     self.SecondWidget = QWidget()
        #     self.Biosphere = header('Biosphere Inventory')
        #     self.SecondTable = BiosphereTable(self.setup)
        #     self.SecondLayout = QVBoxLayout()
        self.layout = QVBoxLayout()

        self.TopStrip = QHBoxLayout()
        self.setLayout(self.layout)
        self.TopStrip.addWidget(self.header)
        self.layout.addLayout(self.TopStrip)
        self.layout.addWidget(horizontal_line())

    def connect_analysis_signals(self):
        # Cut-off
        if self.cutoff_menu:
            # Cut-off types
            self.cutoff_type_topx.clicked.connect(self.cutoff_type_topx_check)
            self.cutoff_type_relative.clicked.connect(self.cutoff_type_relative_check)
            self.cutoff_slider_lft_btn.clicked.connect(self.cutoff_increment_left_check)
            self.cutoff_slider_rght_btn.clicked.connect(self.cutoff_increment_right_check)

            # Cut-off log slider
            self.cutoff_slider_log_slider.valueChanged.connect(
                lambda: self.cutoff_slider_relative_check("sl"))
            self.cutoff_slider_line.textChanged.connect(
                lambda: self.cutoff_slider_relative_check("le"))
            # Cut-off slider
            self.cutoff_slider_slider.valueChanged.connect(
                lambda: self.cutoff_slider_topx_check("sl"))
            self.cutoff_slider_line.textChanged.connect(
                lambda: self.cutoff_slider_topx_check("le"))

        # Combo box signal
        if self.combobox_menu_combobox != None:
            if self.combobox_menu_method_bool and self.combobox_menu_func_bool:
                self.combobox_menu_switch_met.clicked.connect(self.combo_switch_check)
                self.combobox_menu_switch_fun.clicked.connect(self.combo_switch_check)

            if self.plot:
                self.combobox_menu_combobox.currentTextChanged.connect(
                    lambda name: self.update_plot(method=name))

            if self.table:
                self.combobox_menu_combobox.currentTextChanged.connect(
                    lambda name: self.update_table(method=name))

        # Mainspace Checkboxes
        self.main_space_tb_grph_table.stateChanged.connect(
            lambda: self.main_space_check(self.main_space_tb_grph_table, self.main_space_tb_grph_plot))
        self.main_space_tb_grph_plot.stateChanged.connect(
            lambda: self.main_space_check(self.main_space_tb_grph_table, self.main_space_tb_grph_plot))

        # Export Table
        if self.table and self.export_menu:
            self.export_table_buttons_copy.clicked.connect(self.table.to_clipboard)
            self.export_table_buttons_csv.clicked.connect(self.table.to_csv)
            self.export_table_buttons_excel.clicked.connect(self.table.to_excel)

        # Export Plot
        if self.plot and self.export_menu:
            self.export_plot_buttons_png.clicked.connect(self.plot.to_png)
            self.export_plot_buttons_svg.clicked.connect(self.plot.to_svg)

    def combo_switch_check(self):
        """ Show either the functional units or methods combo-box, dependent on button state. """
        if self.combo_box_menu_options == "Compare LCIA Methods":
            self.combo_box_menu_options = "Compare Functional Units"
            self.combobox_menu_label.setText(self.combobox_menu_method_label)
            self.combobox_menu_switch_met.setChecked(False)
            self.combobox_menu_switch_fun.setChecked(True)
        else:
            self.combo_box_menu_options = "Compare LCIA Methods"
            self.combobox_menu_label.setText(self.combobox_menu_func_label)
            self.combobox_menu_switch_met.setChecked(True)
            self.combobox_menu_switch_fun.setChecked(False)
        self.update_combobox()

    def cutoff_increment_left_check(self):
        """ Move the slider 1 increment when left button is clicked. """
        if self.cutoff_type_relative.isChecked():
            num = int(self.cutoff_slider_log_slider.value())
            self.cutoff_slider_log_slider.setValue(num + 1)
        else:
            num = int(self.cutoff_slider_slider.value())
            self.cutoff_slider_slider.setValue(num - 1)

    def cutoff_increment_right_check(self):
        """ Move the slider 1 increment when right button is clicked. """
        if self.cutoff_type_relative.isChecked():
            num = int(self.cutoff_slider_log_slider.value())
            self.cutoff_slider_log_slider.setValue(num - 1)
        else:
            num = int(self.cutoff_slider_slider.value())
            self.cutoff_slider_slider.setValue(num + 1)

    def cutoff_type_relative_check(self):
        """ Set cutoff to process that contribute #% or more. """
        self.cutoff_slider_slider.setVisible(False)
        self.cutoff_slider_log_slider.blockSignals(True)
        self.cutoff_slider_slider.blockSignals(True)
        self.cutoff_slider_line.blockSignals(True)
        self.cutoff_slider_unit.setText("%  of total")
        self.cutoff_slider_min.setText("100%")
        self.cutoff_slider_max.setText("0.001%")
        self.limit_type = "percent"
        self.cutoff_slider_log_slider.blockSignals(False)
        self.cutoff_slider_slider.blockSignals(False)
        self.cutoff_slider_line.blockSignals(False)
        self.cutoff_slider_log_slider.setVisible(True)

    def cutoff_type_topx_check(self):
        """ Set cut-off to the top # of processes. """
        self.cutoff_slider_log_slider.setVisible(False)
        self.cutoff_slider_log_slider.blockSignals(True)
        self.cutoff_slider_slider.blockSignals(True)
        self.cutoff_slider_line.blockSignals(True)
        self.cutoff_slider_unit.setText(" top #")
        self.cutoff_slider_min.setText(str(self.cutoff_slider_slider.minimum()))
        self.cutoff_slider_max.setText(str(self.cutoff_slider_slider.maximum()))
        self.limit_type = "number"
        self.cutoff_slider_log_slider.blockSignals(False)
        self.cutoff_slider_slider.blockSignals(False)
        self.cutoff_slider_line.blockSignals(False)
        self.cutoff_slider_slider.setVisible(True)

    def cutoff_slider_relative_check(self, editor):
        """ With relative selected, change the values for plots and tables to reflect the slider/line-edit. """
        if self.cutoff_type_relative.isChecked():
            self.cutoff_validator = self.cutoff_validator_float
            self.cutoff_slider_line.setValidator(self.cutoff_validator)
            cutoff = float

            # If called by slider
            if editor == "sl":
                self.cutoff_slider_line.blockSignals(True)
                cutoff = abs(self.cutoff_slider_log_slider.logValue())
                self.cutoff_slider_line.setText(str(cutoff))
                self.cutoff_slider_line.blockSignals(False)

            # if called by line edit
            elif editor == "le":
                self.cutoff_slider_log_slider.blockSignals(True)
                if self.cutoff_slider_line.text() == '-':
                    cutoff = 0.001
                    self.cutoff_slider_line.setText("0.001")
                elif self.cutoff_slider_line.text() == '':
                    cutoff = 0.001
                else:
                    cutoff = abs(float(self.cutoff_slider_line.text()))

                if cutoff > 100:
                    cutoff = 100
                    self.cutoff_slider_line.setText(str(cutoff))
                self.cutoff_slider_log_slider.setLogValue(float(cutoff))
                self.cutoff_slider_log_slider.blockSignals(False)

            self.cutoff_value = (cutoff/100)
            if self.plot:
                self.update_plot()
            if self.table:
                self.update_table()

    def cutoff_slider_topx_check(self, editor):
        """ With top # selected, change the values for plots and tables to reflect the slider/line-edit. """
        if self.cutoff_type_topx.isChecked():
            self.cutoff_validator = self.cutoff_validator_int
            self.cutoff_slider_line.setValidator(self.cutoff_validator)
            cutoff = int

            # If called by slider
            if editor == "sl":
                self.cutoff_slider_line.blockSignals(True)
                cutoff = abs(int(self.cutoff_slider_slider.value()))
                self.cutoff_slider_line.setText(str(cutoff))
                self.cutoff_slider_line.blockSignals(False)

            # if called by line edit
            elif editor == "le":
                self.cutoff_slider_slider.blockSignals(True)
                if self.cutoff_slider_line.text() == '-':
                    cutoff = self.cutoff_slider_slider.minimum()
                    self.cutoff_slider_line.setText(str(self.cutoff_slider_slider.minimum()))
                elif self.cutoff_slider_line.text() == '':
                    cutoff = self.cutoff_slider_slider.minimum()
                else:
                    cutoff = abs(int(self.cutoff_slider_line.text()))

                if cutoff > self.cutoff_slider_slider.maximum():
                    cutoff = self.cutoff_slider_slider.maximum()
                    self.cutoff_slider_line.setText(str(cutoff))
                self.cutoff_slider_slider.setValue(int(cutoff))
                self.cutoff_slider_slider.blockSignals(False)

            self.cutoff_value = int(cutoff)
            if self.plot:
                self.update_plot()
            if self.table:
                self.update_table()

    def add_cutoff(self):
        """ Add the cut-off menu to the tab. """
        self.cutoff_menu = QHBoxLayout()

        # Cut-off types
        self.cutoff_type = QVBoxLayout()
        self.cutoff_type_label = QLabel("Cut-off type")
        self.cutoff_type_relative = QRadioButton("Relative")
        self.cutoff_type_relative.setChecked(True)
        self.cutoff_type_topx = QRadioButton("Top #")

        # Cut-off slider
        self.cutoff_slider = QVBoxLayout()
        self.cutoff_slider_set = QVBoxLayout()
        self.cutoff_slider_label = QLabel("Cut-off level")
        self.cutoff_value = 5
        self.cutoff_slider_slider = QSlider(Qt.Horizontal)
        self.cutoff_slider_log_slider = LogarithmicSlider(self)
        self.cutoff_slider_log_slider.setInvertedAppearance(True)
        self.cutoff_slider_slider.setMinimum(1)
        self.cutoff_slider_slider.setMaximum(50)
        self.cutoff_slider_slider.setValue(self.cutoff_value)
        self.cutoff_slider_log_slider.setLogValue(0.01)
        self.cutoff_slider_minmax = QHBoxLayout()
        self.cutoff_slider_min = QLabel("100%")
        self.cutoff_slider_max = QLabel("0.001%")
        self.cutoff_slider_ledit = QHBoxLayout()
        self.cutoff_slider_line = QLineEdit()
        self.cutoff_validator_int = QIntValidator(self.cutoff_slider_line)
        self.cutoff_validator_float = QDoubleValidator(self.cutoff_slider_line)
        self.cutoff_validator = self.cutoff_validator_int
        self.cutoff_slider_line.setValidator(self.cutoff_validator)

        self.cutoff_slider_unit = QLabel("%  of total")

        self.cutoff_slider_lft_btn = QPushButton("<")
        self.cutoff_slider_lft_btn.setMaximumWidth(15)
        self.cutoff_slider_rght_btn = QPushButton(">")
        self.cutoff_slider_rght_btn.setMaximumWidth(15)

        # Assemble types
        self.cutoff_type.addWidget(self.cutoff_type_label)
        self.cutoff_type.addWidget(self.cutoff_type_relative)
        self.cutoff_type.addWidget(self.cutoff_type_topx)

        # Assemble slider set
        self.cutoff_slider_set.addWidget(self.cutoff_slider_label)
        self.cutoff_slider_set.addWidget(self.cutoff_slider_slider)
        self.cutoff_slider_slider.setVisible(False)
        self.cutoff_slider_minmax.addWidget(self.cutoff_slider_min)
        self.cutoff_slider_minmax.addWidget(self.cutoff_slider_log_slider)
        self.cutoff_slider_minmax.addWidget(self.cutoff_slider_max)
        self.cutoff_slider_set.addLayout(self.cutoff_slider_minmax)

        self.cutoff_slider_ledit.addWidget(self.cutoff_slider_line)
        self.cutoff_slider_ledit.addWidget(self.cutoff_slider_lft_btn)
        self.cutoff_slider_ledit.addWidget(self.cutoff_slider_rght_btn)
        self.cutoff_slider_ledit.addWidget(self.cutoff_slider_unit)
        self.cutoff_slider_ledit.addStretch(1)

        self.cutoff_slider.addLayout(self.cutoff_slider_set)
        self.cutoff_slider.addLayout(self.cutoff_slider_ledit)

        # Assemble cut-off menu
        self.cutoff_menu.addLayout(self.cutoff_type)
        self.cutoff_menu.addWidget(vertical_line())
        self.cutoff_menu.addLayout(self.cutoff_slider)
        self.cutoff_menu.addStretch()

        self.layout.addLayout(self.cutoff_menu)
        self.layout.addWidget(horizontal_line())

    def main_space_check(self, table_ch, plot_ch):
        """ Show only table or graph, whichever is selected. """
        table_state = table_ch.isChecked()
        plot_state = plot_ch.isChecked()

        if table_state and plot_state:
            self.main_space_table.setVisible(True)
            self.main_space_plot.setVisible(True)

        elif not table_state and plot_state:
            self.main_space_table.setVisible(False)
            self.main_space_plot.setVisible(True)

        else:
            self.main_space_tb_grph_table.setChecked(True)
            self.main_space_table.setVisible(True)
            self.main_space_plot.setVisible(False)

    def add_main_space(self):
        """ Add the main space to the tab. """
        # Why is this a function and not implemented in the init?;
        # This way, the main space can easily be altered for a specific use if required

        # Generate Table and Plot area
        self.main_space = QScrollArea()
        self.main_space_widget = QWidget()
        self.main_space_widget_layout = QVBoxLayout()
        self.main_space_widget.setLayout(self.main_space_widget_layout)
        self.main_space.setWidget(self.main_space_widget)
        self.main_space.setWidgetResizable(True)

        # Option switches
        self.main_space_tb_grph = QHBoxLayout()
        self.main_space_tb_grph_plot = QCheckBox("Plot")
        self.main_space_tb_grph_plot.setChecked(True)
        self.main_space_tb_grph_table = QCheckBox("Table")
        self.main_space_tb_grph_table.setChecked(True)

        # Plot
        self.main_space_plot = self.plot
        # Table
        self.main_space_table = self.table

        # Assemble option switch
        self.main_space_tb_grph.addWidget(self.main_space_tb_grph_plot)
        self.main_space_tb_grph.addWidget(self.main_space_tb_grph_table)
        self.main_space_tb_grph.addWidget(vertical_line())
        self.relativity_button(self.main_space_tb_grph)
        self.main_space_tb_grph.addStretch()

        # Assemble Table and Plot area
        if self.table and self.plot:
            self.main_space_widget_layout.addLayout(self.main_space_tb_grph)
        if self.plot:
            self.main_space_widget_layout.addWidget(self.main_space_plot, 1)
        if self.table:
            self.main_space_widget_layout.addWidget(self.main_space_table)

        if not self.custom:
            self.main_space_widget_layout.addStretch()

        self.layout.addWidget(self.main_space)

        # if self.custom:
        #     self.main_space.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        #     self.SecondLayout.addWidget(self.Biosphere)
        #     self.SecondLayout.addWidget(self.SecondTable)
        #     self.SecondWidget.setLayout(self.SecondLayout)
        #     self.SecondWidget.setMinimumWidth(718)
        #     self.Second_Space.setWidget(self.SecondWidget)
        #     self.layout.addWidget(self.Second_Space)

    def update_analysis_tab(self):
        if self.combobox_menu_combobox != None:
            self.update_combobox()
        if self.plot:
            self.update_plot()
        if self.table:
            self.update_table()

    def update_table(self, method=None):
        """ Update the table. """
        self.table.sync(self.setup.mlca)

    def relativity_button(self, layout):
        if self.relativity is not None:
            self.button1 = QRadioButton("Relative")
            self.button1.setChecked(True)
            self.button2 = QRadioButton("Absolute")
            layout.addStretch(1)
            layout.addWidget(self.button1)
            layout.addWidget(self.button2)
            self.button1.clicked.connect(self.relativity_check)
            self.button2.clicked.connect(self.relativity_check)

    def relativity_check(self):
        if self.relative == False:
            self.button1.setChecked(True)
            self.button2.setChecked(False)
            self.relative = True
        else:
            self.button1.setChecked(False)
            self.button2.setChecked(True)
            self.relative = False
        if self.plot:
            self.update_plot()
        if self.table:
            self.update_table()

    def add_combobox(self, method=True, func=False):
        """ Add the combobox menu to the tab. """
        self.combobox_menu = QHBoxLayout()

        self.combobox_menu_label = QLabel()

        self.combobox_menu_combobox = None
        self.combobox_menu_switch_met = None
        self.combobox_menu_method_label = None
        self.combobox_menu_method_bool = method
        self.combobox_menu_func_bool = func

        if self.combobox_menu_func_bool:
            self.combobox_menu_func_label = "Choose Functional Unit: "
            self.combobox_menu_combobox_func = QComboBox()
            self.combobox_menu_combobox_func.scroll = False
            self.combobox_menu_combobox = self.combobox_menu_combobox_func
            self.combobox_menu_label.setText(self.combobox_menu_func_label)

        if self.combobox_menu_method_bool:
            self.combobox_menu_method_label = "Choose LCIA Method: "
            self.combobox_menu_combobox_method = QComboBox()
            self.combobox_menu_combobox_method.scroll = False
            self.combobox_menu_combobox = self.combobox_menu_combobox_method
            self.combobox_menu_label.setText(self.combobox_menu_method_label)

        if self.combobox_menu_method_bool and self.combobox_menu_func_bool:
            self.combobox_menu.addStretch(1)
            self.combo_box_menu_options = "Functional Units"
            self.combobox_menu_switch_met = QRadioButton("Compare LCIA Methods")
            self.combobox_menu.addWidget(self.combobox_menu_switch_met)

            self.combobox_menu_switch_fun = QRadioButton("Compare Functional Units")
            self.combobox_menu_switch_fun.setChecked(True)

            self.combobox_menu.addWidget(self.combobox_menu_switch_fun)


        self.combobox_menu.addWidget(vertical_line())

        self.combobox_menu.addWidget(self.combobox_menu_label)
        self.combobox_menu.addWidget(self.combobox_menu_combobox, 1)

        self.combobox_menu_horizontal = horizontal_line()
        self.combobox_menu.addStretch(1)

        self.layout.addLayout(self.combobox_menu)
        self.layout.addWidget(self.combobox_menu_horizontal)

    def update_combobox(self):
        """ Update the combobox menu. """
        self.combobox_menu_combobox.clear()
        visibility = True
        self.combobox_menu_combobox.blockSignals(True)

        if self.combobox_menu_label.text() == self.combobox_menu_method_label: # if is assessment methods
            self.combobox_list = list(self.setup.method_dict.keys())
            if self.setup.single_method:
                visibility = False

        else:
            self.combobox_list = list(self.setup.mlca.func_unit_translation_dict.keys())
            if self.setup.single_func_unit:
                visibility = False

        self.combobox_menu_combobox.insertItems(0, self.combobox_list)
        self.combobox_menu_combobox.blockSignals(False)

        if visibility:
            self.combobox_menu_label.setVisible(True)
            self.combobox_menu_combobox.setVisible(True)
            self.combobox_menu_horizontal.setVisible(True)
            if self.combobox_menu_method_bool and self.combobox_menu_func_bool:
                self.combobox_menu_switch_met.setVisible(True)
        else:
            self.combobox_menu_label.setVisible(False)
            self.combobox_menu_combobox.setVisible(False)
            self.combobox_menu_horizontal.setVisible(False)
            if self.combobox_menu_method_bool and self.combobox_menu_func_bool:
                self.combobox_menu_switch_met.setVisible(False)

    def add_export(self):
        """ Add the export menu to the tab. """
        self.export_menu = QHBoxLayout()

        # Export Plot
        self.export_plot = QVBoxLayout()
        self.export_plot_label = QLabel("Export plot")
        self.export_plot_buttons = QHBoxLayout()
        self.export_plot_buttons_png = QPushButton(".png")
        self.export_plot_buttons_svg = QPushButton(".svg")
        # Export Table
        self.export_table = QVBoxLayout()
        self.export_table_label = QLabel("Export table")
        self.export_table_buttons = QHBoxLayout()
        self.export_table_buttons_copy = QPushButton("Copy")
        self.export_table_buttons_csv = QPushButton(".csv")
        self.export_table_buttons_excel = QPushButton("Excel")

        # Assemble export plot
        self.export_plot.addWidget(self.export_plot_label)
        self.export_plot_buttons.addWidget(self.export_plot_buttons_png)
        self.export_plot_buttons.addWidget(self.export_plot_buttons_svg)
        self.export_plot.addLayout(self.export_plot_buttons)

        # Assemble export table
        self.export_table.addWidget(self.export_table_label)
        self.export_table_buttons.addWidget(self.export_table_buttons_copy)
        self.export_table_buttons.addWidget(self.export_table_buttons_csv)
        self.export_table_buttons.addWidget(self.export_table_buttons_excel)
        self.export_table.addLayout(self.export_table_buttons)

        # Assemble export menu
        if self.plot:
            self.export_menu.addLayout(self.export_plot)
        if self.table and self.plot:
            self.export_menu_vert_line = vertical_line()
            self.export_menu.addWidget(self.export_menu_vert_line)
        if self.table:
            self.export_menu.addLayout(self.export_table)
        self.export_menu.addStretch()

        self.layout.addWidget(horizontal_line())
        self.layout.addLayout(self.export_menu)


class LCAScoreComparisonTab(AnalysisTab):
    def __init__(self, parent, **kwargs):
        super(LCAScoreComparisonTab, self).__init__(parent, **kwargs)
        self.setup = parent

        self.name = "LCA score comparison"
        self.header.setText(self.name)


        self.plot = LCAResultsBarChart(self.setup)

        self.add_combobox(method=True, func=False)
        self.add_main_space()
        self.add_export()

        self.setup.addTab(self, self.name)

        self.connect_analysis_signals()

    def update_plot(self, method=None):
        if method == None or method == '':
            method = self.setup.mlca.methods[0]
        else:
            method = self.setup.method_dict[method]
        self.plot.plot(self.setup.mlca, method=method)


class InventoryTab(AnalysisTab):
    def __init__(self, parent, **kwargs):
        super(InventoryTab, self).__init__(parent, **kwargs)
        self.setup = parent

        self.name = "Inventory"
        self.header.setText(self.name)

        self.table = InventoryTable(self.setup, maxheight=20)

        self.add_main_space()
        self.add_export()

        self.setup.addTab(self, self.name)

        self.connect_analysis_signals()

    def update_table(self, method=None):
        if method == None:
            method = (list(self.setup.mlca.technosphere_flows))[0]
        else:
            pass
        self.table.sync(self.setup.mlca, method=method)#, limit=self.cutoff_value)
        # self.SecondTable.sync(self.setup.mlca, method=method)


class CharacterisationTab(AnalysisTab):
    def __init__(self, parent, **kwargs):
        super(CharacterisationTab, self).__init__(parent, **kwargs)
        self.setup = parent

        self.name = "Inventory Characterisation"
        self.header.setText(self.name)

        self.plot = InventoryCharacterisationPlot(self.setup)
        self.table = InventoryCharacterisationTable(self)

        self.add_cutoff()
        self.cutoff_value = 0.01
        self.add_combobox(method=True, func=True)
        self.add_main_space()
        self.add_export()

        self.setup.addTab(self, self.name)

        self.connect_analysis_signals()

    def update_plot(self, method=None):
        if self.combobox_menu_label.text() == self.combobox_menu_method_label:
            if method == None or method == '':
                method = self.setup.mlca.methods[0]
            else:
                method = self.setup.method_dict[method]
            func = None
            per = "method"
        else:
            func = method
            if func == None or func == '':
                func = self.setup.mlca.func_key_list[0]
            method = None
            per = "func"

        self.plot.plot(self.setup.mlca, method=method, func=func, limit=self.cutoff_value,
                       limit_type=self.limit_type, per=per, normalised=self.relative)


class LCIAAnalysisTab(AnalysisTab):
    def __init__(self, parent, **kwargs):
        super(LCIAAnalysisTab, self).__init__(parent, **kwargs)
        self.setup = parent

        self.name = "LCIA Results"
        self.header.setText(self.name)

        if not self.setup.single_func_unit:
            self.plot = LCAResultsPlot(self.setup)
            self.table = LCAResultsTable(self.setup)

        self.add_main_space()
        self.add_export()

        self.setup.addTab(self, self.name)

        self.connect_analysis_signals()
        self.relative = False

    def update_plot(self):
        if not isinstance(self.plot, LCAResultsPlot):
            self.plot = LCAResultsPlot(self.setup)
        self.plot.plot(self.setup.mlca, normalised=self.relative)

    def update_table(self):
        if not isinstance(self.table, LCAResultsTable):
            self.table = LCAResultsTable()
        self.table.sync(self.setup.mlca, relative=self.relative)


class ProcessContributionsTab(AnalysisTab):
    def __init__(self, parent, **kwargs):
        super(ProcessContributionsTab, self).__init__(parent, **kwargs)
        self.setup = parent

        self.name = "Process Contributions"
        self.header.setText(self.name)

        self.plot = ProcessContributionPlot(self.setup)
        self.table = ProcessContributionsTable(self)

        self.add_cutoff()
        self.cutoff_value = 0.05
        self.add_combobox(method=True, func=True)
        self.add_main_space()
        self.add_export()

        self.setup.addTab(self, self.name)

        self.connect_analysis_signals()

    def update_plot(self, method=None):
        if self.combobox_menu_label.text() == self.combobox_menu_method_label:
            if method == None or method == '':
                method = self.setup.mlca.methods[0]
            else:
                method = self.setup.method_dict[method]
            func = None
            per = "method"
        else:
            func = method
            if func == None or func == '':
                func = self.setup.mlca.func_key_list[0]
            method = None
            per = "func"

        self.plot.plot(self.setup.mlca, method=method, func=func, limit=self.cutoff_value,
                       limit_type=self.limit_type, per=per, normalised=self.relative)


class CorrelationsTab(AnalysisTab):
    def __init__(self, parent, **kwargs):
        super(CorrelationsTab, self).__init__(parent, **kwargs)
        self.setup = parent

        self.name = "Correlations"
        self.header.setText(self.name)

        if not self.setup.single_func_unit:
            self.plot = CorrelationPlot(self.setup)

        self.add_main_space()
        self.add_export()

        self.setup.addTab(self, self.name)

        self.connect_analysis_signals()

    def update_plot(self):
        if isinstance(self.plot, CorrelationPlot):
            labels = [str(x + 1) for x in range(len(self.setup.mlca.func_units))]
            self.plot.plot(self.setup.mlca, labels)
        else:
            self.plot = CorrelationPlot(self.setup)
            labels = [str(x + 1) for x in range(len(self.setup.mlca.func_units))]
            self.plot.plot(self.setup.mlca, labels)