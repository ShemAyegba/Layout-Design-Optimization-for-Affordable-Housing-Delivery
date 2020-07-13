import numpy as np

# Object-oriented programming approach to window design


class Window():
    def __init__(self,window_width,overhang_width=150,total_wall_height = 3000,height_ratios=[0.3333,0.2,0.05,0.41667]):
        self.window_width = window_width
        self.overhang_width = overhang_width
        self.height_ratios = height_ratios
        self.total_wall_height = total_wall_height

    def get_design(self):
        self.lintel_width = self.window_width + 2*(self.overhang_width)
        self.top_panel_width = self.lintel_width
        #bottom to top
        self.sill_height = (self.height_ratios[0] / sum(self.height_ratios))*self.total_wall_height
        self.sill_width = self.window_width
        self.window_height = (self.height_ratios[1] / sum(self.height_ratios))*self.total_wall_height
        self.lintel_height = (self.height_ratios[2] / sum(self.height_ratios))*self.total_wall_height
        self.upper_panel_height = (self.height_ratios[3] / sum(self.height_ratios))*self.total_wall_height
        self.upper_panel_width = self.lintel_width
        self.left_panel_width = self.overhang_width
        self.left_panel_height = self.sill_height + self.window_height

        self.right_panel_width = self.left_panel_width
        self.right_panel_height = self.left_panel_height

        upper_panel = [self.upper_panel_width,self.upper_panel_height]
        lintel = [self.lintel_width,self.lintel_height]
        sill_panel = [self.sill_width,self.sill_height]
        left_panel = [self.left_panel_width,self.right_panel_height]
        right_panel = left_panel
        self.full_window = [upper_panel,lintel,sill_panel,left_panel,right_panel]
                
        return self.full_window

    def print(self):

        print(self.full_window)

