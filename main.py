import os
import sys
from time import sleep
import pygame
import random
from threading import Thread

WIDTH = 400
HEIGHT = 400
NUMGRID = 8
GRIDSIZE = 36
XMARGIN = (WIDTH - GRIDSIZE * NUMGRID) // 2
YMARGIN = (HEIGHT - GRIDSIZE * NUMGRID) // 2
ROOTDIR = os.getcwd()
FPS = 30

gem_imgs = {
    'blue': (0, 0, 200),
    'red': (255, 0, 0),
    'green': (0, 255, 0),
    'purple': (100, 0, 255),
    'yellow': (100, 255, 0),
    'orange': (255, 100, 0),
}
gem_imgs_list = list(gem_imgs.keys())

class Puzzle(pygame.sprite.Sprite):
    def __init__(self, type, position, downlen):
        pygame.sprite.Sprite.__init__(self)

        self.type = type

        # img = pygame.image.load(img_path)
        # self.image = pygame.transform.scale(img, (GRIDSIZE, GRIDSIZE))
        # self.rect = img.get_rect()
        self.image = pygame.Surface((GRIDSIZE - 4, GRIDSIZE - 4))
        self.image.fill(gem_imgs[type])
        self.rect = self.image.get_rect(center = position)
        self.rect.x = position[0] + 2
        self.rect.y = position[1] + 2
        self.downlen = downlen

class Application(Thread):
    def __init__(self):
        Thread.__init__(self)
        
    # 畫矩形 block 框
    def drawBlock(self, block, color=(255, 0, 0), size=2):
        pygame.draw.rect(self.screen, color, block, size)

    # 遊戲介面的網格繪製
    def drawGrids(self):
        for x in range(NUMGRID):
            for y in range(NUMGRID):
                rect = pygame.Rect((XMARGIN+x*GRIDSIZE, YMARGIN+y*GRIDSIZE, GRIDSIZE, GRIDSIZE))
                self.drawBlock(rect, color=(255, 165, 0), size=1)

    def put_puzzle(self):
        # 所有的拼圖物件都會放在self.all_gems裡面，通常要引用拼圖方法都會呼叫這邊
        self.all_gems = []
        # 這邊我沒有很清楚sprite.Group的方法，看起來是所有遊戲物件的集合
        self.gems_group = pygame.sprite.Group()
        for x in range(NUMGRID):
            self.all_gems.append([])
            for y in range(NUMGRID):
                # gem = Puzzle(img_path=random.choice(gem_imgs), size=(GRIDSIZE, GRIDSIZE), position=[XMARGIN+x*GRIDSIZE, YMARGIN+y*GRIDSIZE-NUMGRID*GRIDSIZE], downlen=NUMGRID*GRIDSIZE)
                gem = Puzzle(type=random.choice(gem_imgs_list), position=[XMARGIN+x*GRIDSIZE, YMARGIN+y*GRIDSIZE], downlen=NUMGRID*GRIDSIZE)
                self.all_gems[x].append(gem)
                self.gems_group.add(gem)
            # if self.isMatch()[0] == 0:
            #     break
    
    def getGemByPos(self, x, y):
        return self.all_gems[x][y]

    def checkSelected(self, position):
        for x in range(NUMGRID):
            for y in range(NUMGRID):
                if self.getGemByPos(x, y).rect.collidepoint(*position):
                    a = self.getGemByPos(x, y)
                    return [x, y]
        return None

    def swapGem(self, gem1_pos, gem2_pos):
        gem1 = self.getGemByPos(*gem1_pos)
        gem2 = self.getGemByPos(*gem2_pos)
        # if gem1_pos[0] - gem2_pos[0] == 1:
        #     gem1.direction = 'left'
        #     gem2.direction = 'right'
        # elif gem1_pos[0] - gem2_pos[0] == -1:
        #     gem2.direction = 'left'
        #     gem1.direction = 'right'
        # elif gem1_pos[1] - gem2_pos[1] == 1:
        #     gem1.direction = 'up'
        #     gem2.direction = 'down'
        # elif gem1_pos[1] - gem2_pos[1] == -1:
        #     gem2.direction = 'up'
        #     gem1.direction = 'down'
        gem1.target_x = gem2.rect.left
        gem1.target_y = gem2.rect.top
        gem2.target_x = gem1.rect.left
        gem2.target_y = gem1.rect.top
        gem1.rect.x = gem1.target_x
        gem1.rect.y = gem1.target_y
        gem2.rect.x = gem2.target_x
        gem2.rect.y = gem2.target_y
        self.all_gems[gem2_pos[0]][gem2_pos[1]] = gem1
        self.all_gems[gem1_pos[0]][gem1_pos[1]] = gem2
        
        return True

    def isMatch(self):
        for x in range(NUMGRID):
            for y in range(NUMGRID):
                if x + 2 < NUMGRID:
                    if self.getGemByPos(x, y).type == self.getGemByPos(x+1, y).type == self.getGemByPos(x+2, y).type:
                        return [1, x, y]
                if y + 2 < NUMGRID:
                    if self.getGemByPos(x, y).type == self.getGemByPos(x, y+1).type == self.getGemByPos(x, y+2).type:
                        return [2, x, y]
        return [0, x, y]

    def removeMatched(self, res_match):
        if res_match[0] > 0:
            self.generateNewGems(res_match)
            self.score += self.reward
            return self.reward
        return 0

    def generateNewGems(self, res_match):
        if res_match[0] == 1:
            start = res_match[2]
            while start > -2:
                for each in [res_match[1], res_match[1]+1, res_match[1]+2]:
                    gem = self.getGemByPos(*[each, start])
                    if start == res_match[2]:
                        self.gems_group.remove(gem)
                        self.all_gems[each][start] = None
                    elif start >= 0:
                        gem.target_y += GRIDSIZE
                        gem.fixed = False
                        gem.direction = 'down'
                        self.all_gems[each][start+1] = gem
                    else:
                        gem = Puzzle(img_path=random.choice(gem_imgs), size=(GRIDSIZE, GRIDSIZE), position=[XMARGIN+each*GRIDSIZE, YMARGIN-GRIDSIZE], downlen=GRIDSIZE)
                        self.gems_group.add(gem)
                        self.all_gems[each][start+1] = gem
                start -= 1
        elif res_match[0] == 2:
            start = res_match[2]
            while start > -4:
                if start == res_match[2]:
                    for each in range(0, 3):
                        gem = self.getGemByPos(*[res_match[1], start+each])
                        self.gems_group.remove(gem)
                        self.all_gems[res_match[1]][start+each] = None
                elif start >= 0:
                    gem = self.getGemByPos(*[res_match[1], start])
                    gem.target_y += GRIDSIZE * 3
                    gem.fixed = False
                    gem.direction = 'down'
                    self.all_gems[res_match[1]][start+3] = gem
                else:
                    gem = Puzzle(img_path=random.choice(gem_imgs), size=(GRIDSIZE, GRIDSIZE), position=[XMARGIN+res_match[1]*GRIDSIZE, YMARGIN+start*GRIDSIZE], downlen=GRIDSIZE*3)
                    self.gems_group.add(gem)
                    self.all_gems[res_match[1]][start+3] = gem
                start -= 1

    def run(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption('消消樂')
        
        self.put_puzzle()

        left_mouse_pressed = False
        gem1_pos = None
        gem2_pos = None

        while True:
            for event in pygame.event.get():
                # 不知為何絕對要有這行才跑得動
                if event.type == pygame.QUIT: sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    # 判斷左鍵按壓
                    if pygame.mouse.get_pressed()[0] == True:
                        press_pos = pygame.mouse.get_pos()
                        left_mouse_pressed = True
                        print(press_pos)
                        gem1_pos = self.checkSelected(press_pos)
                        
                elif event.type == pygame.MOUSEBUTTONUP:
                    # 判斷左鍵釋放
                    if left_mouse_pressed == True:
                        left_mouse_pressed == False
                        release_pos = pygame.mouse.get_pos()
                        print(release_pos)
                        gem2_pos = self.checkSelected(release_pos)
                        if gem1_pos != None and gem2_pos != None:
                            margin = gem1_pos[0] - gem2_pos[0] + gem1_pos[1] - gem2_pos[1]
                            if abs(margin) == 1:
                                self.swapGem(gem1_pos, gem2_pos)
                            

            # 填上滿滿的黃色
            self.screen.fill((255, 255, 220))
            
            self.drawGrids()
            self.gems_group.draw(self.screen)

            # 重複刷新畫面
            pygame.display.flip()


if __name__ == '__main__':
    mainApp = Application()
    mainApp.daemon = True
    mainApp.name = 'game'

    mainApp.start()

    while True:
        sleep(1)
    