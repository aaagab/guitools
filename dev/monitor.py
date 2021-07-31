#!/usr/bin/env python3
from pprint import pprint
import copy
import os
import re
import sys

class Monitor(object):
    def __init__(self):
        self.name=""
        self.width=""
        self.height=""
        self.upper_left_x=""
        self.upper_left_y=""
        self.range_x=""
        self.range_y=""
        # taskbar attribute
        self.tb_width=""
        self.tb_height=""
        self.tb_upper_left_x=""
        self.tb_upper_left_y=""
        self.tb_range_x=""
        self.tb_range_y=""

        self.index=""

    def print(self):
        pprint(vars(self))

    def contains(self, x, y):
        x_found=False
        y_found=False
        if x >= self.range_x[0] and x <= self.range_x[1]:
            x_found=True

        if y >= self.range_y[0] and y <= self.range_y[1]:
            y_found=True
        
        if x_found and y_found:
            return True
        else:
            return False

    def get_tiles(self, int_v_divs, int_h_divs, bool_taskbar, tile_nums=[]):
        if tile_nums:
            if not isinstance(tile_nums, list):
                tile_nums=[tile_nums]

        num_tiles= int_v_divs * int_h_divs
        tmp_tile_nums=copy.deepcopy(tile_nums)
        tile_width=""
        tile_height=""

        if bool_taskbar:
            tile_width=int(self.tb_width/int_v_divs)
            tile_height=int(self.tb_height/int_h_divs)
        else:
            tile_width=int(self.width/int_v_divs)
            tile_height=int(self.height/int_h_divs)

        tiles=[]
        index=1
        for h_div in range(int_h_divs):
            for v_div in range(int_v_divs):
                tile=Tile()
                tile.upper_left_x=self.upper_left_x+(v_div*tile_width)
                tile.upper_left_y=self.upper_left_y+(h_div*tile_height)
                tile.width=tile_width
                tile.height=tile_height
                tile.index=index
                tile.range_x=[
                    tile.upper_left_x,
                    tile.upper_left_x+tile.width
                ]
                tile.range_y=[
                    tile.upper_left_y,
                    tile.upper_left_y+tile.height
                ]
                tile.nums=num_tiles

                if tile_nums:
                    for value in tmp_tile_nums:
                        if value == index:
                            tiles.append(tile)
                            tmp_tile_nums.remove(value)
                            break
                else:
                    tiles.append(tile)

                index+=1
            
            if tile_nums:
                if len(tiles) == len(tile_nums):
                    break

        return tiles

class Tile(object):
    def __init__(self):
        self.upper_left_x=""
        self.upper_left_y=""
        self.width=""
        self.height=""
        self.nums=""
        self.index=""
        self.range_x=[]
        self.range_y=[]

    def print(self):
        pprint(vars(self))

    def contains(self, x, y):
        x_found=False
        y_found=False
        if x >= self.range_x[0] and x < self.range_x[1]:
            x_found=True

        if y >= self.range_y[0] and y < self.range_y[1]:
            y_found=True
        
        if x_found and y_found:
            return True
        else:
            return False