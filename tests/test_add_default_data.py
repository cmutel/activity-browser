# -*- coding: utf-8 -*-
import time

import brightway2 as bw
from PyQt5 import QtCore

from activity_browser import Application
from activity_browser.app.controller import Controller
from activity_browser.app.ui.db_import_wizard import import_signals


def test_add_default_data(qtbot, mock):
    assert bw.projects.current == 'default'
    app = Application()
    qtbot.addWidget(app)
    app.show()
    qtbot.waitForWindowShown(app.main_window)
    time.sleep(1)
    mock.patch.object(Controller, 'get_new_project_name', return_value='test_project2')
    qtbot.mouseClick(
        app.main_window.right_panel.inventory_tab.projects_widget.new_project_button,
        QtCore.Qt.LeftButton
    )
    assert bw.projects.current == 'test_project2'

    with qtbot.waitSignal(import_signals.biosphere_finished, timeout=600000):
        qtbot.mouseClick(
            app.main_window.right_panel.inventory_tab.databases_widget.add_default_data_button,
            QtCore.Qt.LeftButton
        )

    mock.patch.object(Controller, 'confirm_project_deletion', return_value=True)
    qtbot.mouseClick(
        app.main_window.right_panel.inventory_tab.projects_widget.delete_project_button,
        QtCore.Qt.LeftButton
    )
    assert bw.projects.current == 'default'