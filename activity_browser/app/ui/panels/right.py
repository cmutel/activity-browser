# -*- coding: utf-8 -*-
from .panel import ABTab
from ..web.graphnav import GraphNavigatorWidget
from ...signals import signals
from .. import activity_cache
from ..tabs import (
    LCASetupTab,
    LCAResultsTab,
    CharacterizationFactorsTab,
    ActivitiesTab
)


class RightPanel(ABTab):
    side = "right"

    def __init__(self, *args):
        super(RightPanel, self).__init__(*args)

        self.tabs = {
            "Characterization Factors": CharacterizationFactorsTab(self),
            "Activities": ActivitiesTab(self),
            "LCA Setup": LCASetupTab(self),
            "Graph Explorer": GraphNavigatorWidget(),
            "LCA results": LCAResultsTab(self),
        }

        for tab_name, tab in self.tabs.items():
            self.addTab(tab, tab_name)

        # tabs hidden at start
        for tab_name in ["Activities", "Characterization Factors", "Graph Explorer", ]:
            self.hide_tab(tab_name)

    #     # Signals
        self.connect_signals()
    #
    def connect_signals(self):
        signals.activity_tabs_changed.connect(self.update_activity_panel)
        signals.method_tabs_changed.connect(self.update_method_panel)
        signals.lca_calculation.connect(self.update_LCA_results_panel)

    def update_method_panel(self):
        """Show or hide Characterization Factors."""
        if "Characterization Factors" in self.tabs:
            tab = self.tabs["Characterization Factors"]
            if tab.tab_dict:
                self.show_tab("Characterization Factors")
            else:
                self.hide_tab("Characterization Factors")

    def update_activity_panel(self):
        """Show or hide Activity Panel."""
        if activity_cache:
            self.show_tab("Activities")
        else:
            self.hide_tab("Activities")

    def update_LCA_results_panel(self):
        """Show or hide LCA Results Panel"""
        if "LCA Results" in self.tabs:
            tab = self.tabs["LCA results"]
            if tab.calculation_setups:
                self.show_tab("LCA Results")
            else:
                self.hide_tab("LCA Results")



# Delete once Sankey stuff has been resolved

        # signals.lca_calculation.connect(self.add_Sankey_Widget)
        # self.currentChanged.connect(self.calculate_first_sankey)

    # def add_Sankey_Widget(self, cs_name):
    #     print("Adding Sankey Tab")
    #     # if not hasattr(self, "sankey_navigator_tab"):
    #     self.sankey_navigator_tab = SankeyNavigatorWidget(cs_name)
    #     self.addTab(self.sankey_navigator_tab, 'LCA Sankey')

    # def calculate_first_sankey(self):
    #     if hasattr(self, "sankey_navigator_tab"):
    #         if self.currentIndex() == self.indexOf(self.sankey_navigator_tab):
    #             print("Changed to Sankey Tab")
    #             if not self.sankey_navigator_tab.graph.json_data:
    #                 print("Calculated first Sankey")
    #                 self.sankey_navigator_tab.new_sankey()