#!/usr/bin/env python3
# coding: utf8
import os, enum, numpy, random, pyxel
from abc import ABCMeta, abstractmethod

class App:
    def __init__(self):
        self.__window = Window()
        globals()['Window'] = self.__window
        self.__scenes = Scenes()
        pyxel.run(self.update, self.draw)
    def update(self): self.__scenes.update()
    def draw(self): self.__scenes.draw()

class Window:
    def __init__(self):
        pyxel.init(self.Width, self.Height, border_width=self.BorderWidth, caption=self.Caption, fps=60)
        self.load()
    @property
    def Width(self): return 256
    @property
    def Height(self): return 192
    @property
    def Caption(self): return "Life game"
    @property
    def BorderWidth(self): return 0
    def update(self): pass
    def draw(self): pyxel.cls(0)
    def load(self):
        here = os.path.abspath(os.path.dirname(__file__))
        parent = os.path.dirname(here)
        file = os.path.join(parent, 'res', 'snake.pyxres')
        pyxel.load(file)

class Scenes:
    Types = enum.Enum("Types", "Start Play GameOver")
    def __init__(self):
        self.__scenes = { Scenes.Types.Start:    StartScene(), 
                          Scenes.Types.Play :    PlayScene(), 
                          Scenes.Types.GameOver: GameOverScene() }
        self.__now = Scenes.Types.Start
        self.__scenes[self.__now].init()
    def update(self):
        next_scene, args, kwargs = self.__scenes[self.__now].update()
        if next_scene and self.__now != next_scene:
            self.__now = next_scene
            self.__scenes[self.__now].init(*args, **kwargs if kwargs else {})
    def draw(self):
        pyxel.cls(0)
        self.__scenes[self.__now].draw()

class Scene(metaclass=ABCMeta):
    @abstractmethod
    def update(self): return None, (None,), {}
    @abstractmethod
    def draw(self): pass
    @abstractmethod
    def init(self, *args, **kwargs): pass

class StartScene(Scene):
    def init(self, *args, **kwargs):
        self.__world = World()
    def update(self):
        if pyxel.btn(pyxel.KEY_UP):      return Scenes.Types.Play, (self.__world, DirectType.North), {}
        elif pyxel.btn(pyxel.KEY_DOWN):  return Scenes.Types.Play, (self.__world, DirectType.South), {}
        elif pyxel.btn(pyxel.KEY_LEFT):  return Scenes.Types.Play, (self.__world, DirectType.East), {}
        elif pyxel.btn(pyxel.KEY_RIGHT): return Scenes.Types.Play, (self.__world, DirectType.West), {}
        else: return super(self.__class__, self).update()
    def draw(self):
        self.__world.draw()
        pyxel.text(24, 1, 'Press UP,DOWN,LEFT,RIGHT key', 7)

class PlayScene(Scene):
    def init(self, *args, **kwargs):
        self.__world = args[0]
        self.__direct = args[1]
        self.__world.Snake.Direct = args[1]
        self.__point = 0
    def update(self):
        if self.__world.update():
            return Scenes.Types.GameOver, (self.__world, self.__world.Food.Count,), {}
        return super(self.__class__, self).update()
    def draw(self):
        self.__world.draw()

class GameOverScene(Scene):
    def init(self, *args, **kwargs):
        self.__world = args[0]
        self.__point = args[1]
    def update(self):
        if pyxel.btn(pyxel.KEY_SPACE):
            return Scenes.Types.Start, (0,), {}
        return super(self.__class__, self).update()
    def draw(self):
        self.__world.draw()
        self.__world.Snake.death()
        pyxel.text(100, 80, 'GameOver' + \
                         '\n\npoint: ' + str(self.__point) + \
                         '\n\nPress SPACE key', 7)
class World:
    Direct = enum.Enum("Direct", "North South East West")
    def __init__(self):
        self.__w = Window.Width
        self.__h = Window.Height
        self.__box = PlayBox()
        self.__snake = Snake(
            pixel_pos=self.Box.get_pos((self.Box.Width // 2), (self.Box.Height // 2)),
            tile_pos=[(self.Box.Width // 2), (self.Box.Height // 2)])
        self.Snake.PixelPos[0], self.Snake.PixelPos[1] = self.Box.get_pos(self.Snake.TilePos[0], self.Snake.TilePos[1])
        self.Snake.TilePos[0], self.Snake.TilePos[1] = self.Box.get_pos_from_pixel(self.Snake.PixelPos)
        self.__food = Food()
        self.Food.next((self.Box.Width, self.Box.Height))
        self.Food.PixelPos[0], self.Food.PixelPos[1] = self.Box.get_pos(self.Food.TilePos[0], self.Food.TilePos[1])
    @property
    def Width(self): return self.__w
    @property
    def Height(self): return self.__h
    @property
    def Box(self): return self.__box
    @property
    def Snake(self): return self.__snake
    @property
    def Food(self): return self.__food
    def update(self):
        self.Snake.update()
        tileX, tileY = self.Box.get_pos_from_pixel(self.Snake.PixelPos)
        if self.Snake.set_body(tileX, tileY): pyxel.play(0, [1]); return True
        self.__get_food()
        if self.__is_death(): pyxel.play(0, [1]); return True
        else: return False
    def draw(self):
        pyxel.cls(0)
        self.Box.draw()
        pyxel.text(2+10, 1, str(self.Food.Count), 7)
        self.Snake.draw()
        self.Food.draw()
    def __is_death(self):
        if self.__detect_collision_border(): return True
        return False
    def __detect_collision_border(self):
        if self.Snake.PixelPos[0] < self.Box.Border.WeightW: return True
        if self.Snake.PixelPos[1] < self.Box.Menu.Height + self.Box.Border.WeightH: return True
        if self.Snake.PixelPos[0] > self.Width  - self.Box.Border.WeightW - self.Box.TileSize: return True
        if self.Snake.PixelPos[1] > self.Height - self.Box.Border.WeightH - self.Box.TileSize: return True
        return False
    def __get_food(self):
        if self.Food.PixelPos[0] <= self.Snake.CenterPos[0] <= self.Food.PixelPos[0]+16 and \
           self.Food.PixelPos[1] <= self.Snake.CenterPos[1] <= self.Food.PixelPos[1]+16: 
            self.Food.next([self.Box.Width, self.Box.Height])
            self.Snake.grow()
            pyxel.play(0, [0])

class PlayBox:
    def __init__(self):
        self.__tile_size = 16
        self.__colors = (3, 11)
        self.__menu = Menu()
        self.__border = Border(0, self.Menu.Height)
        self.__w = (Window.Width  - self.Border.WeightW) // self.TileSize
        self.__h = (Window.Height - self.Border.WeightH - self.Menu.Height) // self.TileSize
    @property
    def Width(self): return self.__w
    @property
    def Height(self): return self.__h
    @property
    def TileSize(self): return self.__tile_size
    @property
    def Colors(self): return self.__colors
    @property
    def Menu(self): return self.__menu
    @property
    def Border(self): return self.__border
    def draw(self):
        self.Menu.draw()
        # 庭
        for y in range(self.Height):
            for x in range(self.Width):
                pyxel.rect(
                    x*self.TileSize + self.Border.WeightW, 
                    y*self.TileSize + self.Border.WeightH + self.Menu.Height, 
                    self.TileSize, self.TileSize, 
                    self.Colors[0] if (y + x) % 2 == 0 else self.Colors[1])
        self.Border.draw()
    # タイル座標→ピクセル座標
    def get_pos(self, x, y):
        return [x * self.TileSize + self.Border.WeightW,
                y * self.TileSize + self.Border.WeightH + self.Menu.Height]
    # ピクセル座標→タイル座標
    def get_pos_from_pixel(self, pixel_pos):
        return [(pixel_pos[0] - (self.Border.WeightW * 2)) // self.TileSize,
                (pixel_pos[1] - (self.Border.WeightH * 2) - self.Menu.Height) // self.TileSize]

class Menu:
    def __init__(self): # 初期値
        self.__w = Window.Width
        self.__h = 8
        self.__bg_color = 2
        self.__fg_color = 7
    @property
    def Width(self): return self.__w
    @property
    def Height(self): return self.__h
    @property
    def BackgroundColor(self): return self.__bg_color
    @property
    def ForegroundColor(self): return self.__fg_color
    def draw(self):
        pyxel.rect(0, 0, self.Width, self.Height, self.BackgroundColor)
        pyxel.blt(2, 0, 0, 16, (4*16), 8, 8, 0)
#        pyxel.text(2+10, 1, food.Count, self.ForegroundColor)
#        pyxel.text(2+10, 1, '0', self.ForegroundColor)

class Border:
    def __init__(self, x, y, weight_w=8, weight_h=6, color=8): # 初期値
        self.__x = x
        self.__y = y
        self.__w = Window.Width
        self.__h = Window.Height
        self.__weight_w = weight_w
        self.__weight_h = weight_h
        self.__color = color
    @property
    def X(self): return self.__x
    @property
    def Y(self): return self.__y
    @property
    def Width(self): return self.__w
    @property
    def Height(self): return self.__h
    @property
    def WeightW(self): return self.__weight_w
    @property
    def WeightH(self): return self.__weight_h
    @property
    def Color(self): return self.__color
    def draw(self):
        # 横
        for s in range(self.WeightH):
            pyxel.line(self.X, self.Y+s,                              self.X+self.Width, self.Y+s,                              self.Color)
            pyxel.line(self.X, self.Height-s-1, self.X+self.Width, self.Height-s-1, self.Color)
        # 縦
        for s in range(self.WeightW):
            pyxel.line(self.X+s,            self.Y, self.X+s,            self.Y+self.Height, self.Color)
            pyxel.line(self.X-s+self.Width-1, self.Y, self.X-s+self.Width-1, self.Y+self.Height, self.Color)

class WorldObject:
    def __init__(self, tile_size=[16,16], tile_pos=[0,0], pixel_pos=[0,0]): # 初期値
        self.__tile_size = tile_size
        self.__tile_pos = tile_pos
        self.__pixel_pos = pixel_pos
        self.__img_id = 0
        self.__u = 0
        self.__v = 0
        self.__w = tile_size[0]
        self.__h = tile_size[1]
        self.__colkey = 0
    @property
    def TileSize(self): return self.__tile_size
    @property
    def TilePos(self): return self.__tile_pos
    @property
    def PixelPos(self): return self.__pixel_pos
    @property
    def CenterPos(self): return [self.PixelPos[0] + self.TilePos[0], self.PixelPos[1] + self.TilePos[1]]
    @property
    def ImageId(self): return self.__img_id
    @property
    def U(self): return self.__u
    @property
    def V(self): return self.__v
    @property
    def W(self): return self.__w
    @property
    def H(self): return self.__h
    @property
    def ColKey(self): return self.__colkey
    @ImageId.setter
    def ImageId(self, value):
        self.__img_id = value if 0 <= value <=4 else 0
    @U.setter
    def U(self, value): self.__u = value
    @V.setter
    def V(self, value): self.__v = value
    @W.setter
    def W(self, value): self.__w = value
    @H.setter
    def H(self, value): self.__h = value
    @ColKey.setter
    def ColKey(self, value): self.__colkey = value if 0 <= value <= 16 else 0
    def draw(self):
        pyxel.blt(self.PixelPos[0], self.PixelPos[1], self.ImageId, self.U, self.V, self.W, self.H, self.ColKey)

class DirectType(enum.Enum):
    North = 0
    South = 1
    East = 2
    West = 3

class Snake(WorldObject):
    def __init__(self, tile_size=[16,16], tile_pos=[0,0], pixel_pos=[0,0], direct=DirectType.North):
        super(self.__class__, self).__init__(tile_size, tile_pos, pixel_pos)
        self.ImageId = 0
        self.U = 0
        self.V = 0
        self.ColKey = 0
        self.__direct = direct
        self.__history = [[self.PixelPos[0], self.PixelPos[1]], 
                          [self.PixelPos[0], self.PixelPos[1]+16]] 
        self.__history_tile = [[7,5], [7,6]]
        self.__images = {
            'Head': {
                DirectType.North: ( 0,  0),
                DirectType.East:  (16,  0),
            },
            'Body': {
                DirectType.North: ( 0, 16),
                DirectType.East:  (16, 16),
            },
            'Tail': {
                DirectType.North: ( 0, 32),
                DirectType.East:  (16, 32),
            },
        }
        self.__death_frame = -1
    @property
    def Direct(self): return self.__direct
    @Direct.setter
    def Direct(self, value): self.__direct = value
    @property
    def Body(self): return self.__body
    @property
    def History(self): return self.__history
    def update(self):
        self.__change_direct()
        self.next()
    # event driven  OnChangedDirect
    def __change_direct(self):
        if pyxel.btn(pyxel.KEY_UP)    and self.Direct != DirectType.South: self.__direct = DirectType.North; self.__set_image_from_direct();
        if pyxel.btn(pyxel.KEY_DOWN)  and self.Direct != DirectType.North: self.__direct = DirectType.South; self.__set_image_from_direct();
        if pyxel.btn(pyxel.KEY_LEFT)  and self.Direct != DirectType.West:  self.__direct = DirectType.East;  self.__set_image_from_direct();
        if pyxel.btn(pyxel.KEY_RIGHT) and self.Direct != DirectType.East:  self.__direct = DirectType.West;  self.__set_image_from_direct();
    def next(self):
        self.__move_pixel_pos()
    def __move_pixel_pos(self):
        if (pyxel.frame_count % 1) != 0: return
        if   self.Direct == DirectType.North: self.__move_body( 0, -1)
        elif self.Direct == DirectType.South: self.__move_body( 0,  1)
        elif self.Direct == DirectType.East:  self.__move_body(-1,  0)
        elif self.Direct == DirectType.West:  self.__move_body( 1,  0)
        else: pass
    def __move_body(self, mx, my):
        self.PixelPos[0] += mx
        self.PixelPos[1] += my
    def __set_image_from_direct(self):
        if   self.Direct == DirectType.North: self.U = 0 * 16
        elif self.Direct == DirectType.South: self.U = 1 * 16
        elif self.Direct == DirectType.East:  self.U = 2 * 16
        elif self.Direct == DirectType.West:  self.U = 3 * 16
        else: pass
    # Event driven or MVVM
    def set_body(self, tileX, tileY):
        if self.TilePos[0] == tileX and self.TilePos[1] == tileY: return
        self.__set_history(tileX, tileY)
        self.TilePos[0] = tileX
        self.TilePos[1] = tileY
        return self.__detect_collision_body_tile()
    def __detect_collision_body_tile(self):
        self.__history_tile.insert(0, list(self.TilePos))
        self.__history_tile.pop()
        if len(self.__history_tile) < 2: return
        for i in range(1, len(self.__history_tile)):
            if self.__history_tile[0][0] == self.__history_tile[i][0] and \
               self.__history_tile[0][1] == self.__history_tile[i][1]:
                return True
        return False
    def __set_history(self, tileX, tileY):
        self.__history.insert(0, list(self.PixelPos))
        self.__history.pop()

    def grow(self):
        self.__history.append(list(self.__history[-1]))
        self.__history_tile.append(list(self.__history_tile[-1]))
    def draw(self):
        if -1 == self.__death_frame:
            self.__draw_body()
            self.__draw_tail()
            self.__draw_head()
        else:
            self.__draw_body()
            self.__draw_tail()
            self.death()
    def __draw_head(self):
        if -1 == self.__death_frame:
            u, v = self.__get_clip_img_pos('Head', self.Direct)
            w, h = self.__get_clip_img_size_and_direct(self.Direct)
            pyxel.blt(self.PixelPos[0], self.PixelPos[1], self.ImageId, u, v, w, h, 0)
        else: self.death()
    def __draw_tail(self):
        direct = self.__get_body_direct(-1)
        u, v = self.__get_clip_img_pos('Tail', direct)
        w, h = self.__get_clip_img_size_and_direct(direct)
        pyxel.blt(self.History[-1][0], self.History[-1][1], self.ImageId, u, v, w, h, 0)
    def __draw_body(self):
        for i in range(len(self.History)-1):
            direct = self.__get_body_direct(i)
            u, v = self.__get_clip_img_pos('Body', direct)
            w, h = self.__get_clip_img_size_and_direct(direct)
            pyxel.blt(self.History[i][0], self.History[i][1], self.ImageId, u, v, w, h, 0)
    def __get_body_direct(self, now):
        if   self.History[now-1][1] < self.History[now][1]: return DirectType.North
        elif self.History[now-1][1] > self.History[now][1]: return DirectType.South
        elif self.History[now-1][0] < self.History[now][0]: return DirectType.East
        elif self.History[now-1][0] > self.History[now][0]: return DirectType.West
        else: return self.__get_body_direct(now-1)
    def __get_clip_img_pos(self, name, direct):
        imgdir = DirectType.North if 0 == (direct.value // 2) else DirectType.East
        return (self.__images[name][imgdir][0], self.__images[name][imgdir][1])
    def __get_clip_img_size_and_direct(self, direct):
        return (16 * (-1 if direct == DirectType.West  else 1), 
                16 * (-1 if direct == DirectType.South else 1))
    def death(self):
        if 0 == (pyxel.frame_count % 5):
            self.__death_frame += 1
            if 5 < self.__death_frame: self.__death_frame = 0
            self.U = (self.__death_frame -3) * self.TileSize[0] if 2 < self.__death_frame else self.__death_frame * self.TileSize[0]
            self.V = 5*self.TileSize[1]
            self.W = self.TileSize[0] * (-1 if 2 < self.__death_frame else 1)
#            print(self.__death_frame, self.U, self.W)
        super(self.__class__, self).draw()


class Food(WorldObject):
    def __init__(self, tile_size=[16,16], tile_pos=[0,0]):
        super(self.__class__, self).__init__(tile_size, tile_pos)
        self.ImageId = 0
        self.U = 0
        self.V = 4*16
        self.ColKey = 0
        self.__count = -1
    @property
    def Count(self): return self.__count
    def next(self, world_tile_size, snake_tile_pos=(0,0)):
        self.__count += 1
        self.TilePos[0] = random.randint(0, world_tile_size[0]-1)
        self.TilePos[1] = random.randint(0, world_tile_size[1]-1)
        self.PixelPos[0] = (self.TilePos[0] * 16) + 8
        self.PixelPos[1] = (self.TilePos[1] * 16) + 8 + 4


App()
