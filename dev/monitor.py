#!/usr/bin/env python3
from pprint import pprint
import copy
import os
import sys

class Monitor(object):
    def __init__(self) -> None:
        self.is_primary=False
        self.name=""
        self.width:int=0
        self.height:int=0
        self.x:int=0
        self.y:int=0
        self.range_x:list[int]=[]
        self.range_y:list[int]=[]
        # taskbar attribute
        self.tb_width:int=0
        self.tb_height:int=0
        self.tb_x:int=0
        self.tb_y:int=0
        self.tb_range_x:list[int]=[]
        self.tb_range_y:list[int]=[]

        self.index:int=0

    def info(self):
        return f"{self.name} {self.width}x{self.height}+{self.x}+{self.y} primary:{str(self.is_primary).lower()}"

    def print(self):
        pprint(vars(self))

    def contains(self, x:int, y:int):
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

    def get_tiles(self, xdivs:int, ydivs:int, cover_taskbar:bool, tile_nums:list[int]|None=None):
        if tile_nums is None:
            tile_nums=[]

        num_tiles= xdivs * ydivs
        tmp_tile_nums=copy.deepcopy(tile_nums)
        tile_width:int
        tile_height:int

        if cover_taskbar is True:
            tile_width=int(self.width/xdivs)
            tile_height=int(self.height/ydivs)
        else:
            tile_width=int(self.tb_width/xdivs)
            tile_height=int(self.tb_height/ydivs)

        tiles=[]
        index=1
        for h_div in range(ydivs):
            for v_div in range(xdivs):
                tile=Tile()
                tile.x=self.x+(v_div*tile_width)
                tile.y=self.y+(h_div*tile_height)
                tile.width=tile_width
                tile.height=tile_height
                tile.index=index
                tile.range_x=[
                    tile.x,
                    tile.x+tile.width
                ]
                tile.range_y=[
                    tile.y,
                    tile.y+tile.height
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
    def __init__(self) -> None:
        self.x:int=0
        self.y:int=0
        self.width:int=0
        self.height:int=0
        self.nums:int=0
        self.index:int=0
        self.range_x:list[int]=[]
        self.range_y:list[int]=[]

    def print(self):
        pprint(vars(self))

    def contains(self, x:int, y:int):
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