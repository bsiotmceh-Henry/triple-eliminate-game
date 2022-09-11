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

class Puzzle(pygame.sprite.Sprite):
    def __init__(self, img_path, position, downlen):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load(img_path)
        self.image = pygame.transform.scale(img, (GRIDSIZE, GRIDSIZE))
        self.rect = img.get_rect()
        self.rect.x = position[0]
        self.rect.y = position[1]
        self.downlen = downlen

        # self.image = pygame.Surface(size)
        # self.image.fill((255, 255, 0))
        # self.rect = self.image.get_rect(center = position)


class Application(Thread):
    gem_imgs = {
        'blue': '.\\triple-eliminate-game\\image\\1.png',
        'red': '.\\triple-eliminate-game\\image\\2.png',
        'green': '.\\triple-eliminate-game\\image\\3.png',
        'purple': '.\\triple-eliminate-game\\image\\4.png',
        'yellow': '.\\triple-eliminate-game\\image\\5.png',
        'orange': '.\\triple-eliminate-game\\image\\6.png',
    }
    gem_imgs_list = list(gem_imgs.values())
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
        # while True:
        self.all_gems = []
        self.gems_group = pygame.sprite.Group()
        for x in range(NUMGRID):
            self.all_gems.append([])
            for y in range(NUMGRID):
                # gem = Puzzle(img_path=random.choice(self.gem_imgs), size=(GRIDSIZE, GRIDSIZE), position=[XMARGIN+x*GRIDSIZE, YMARGIN+y*GRIDSIZE-NUMGRID*GRIDSIZE], downlen=NUMGRID*GRIDSIZE)
                gem = Puzzle(img_path=random.choice(self.gem_imgs_list), position=[XMARGIN+x*GRIDSIZE, YMARGIN+y*GRIDSIZE], downlen=NUMGRID*GRIDSIZE)
                self.all_gems[x].append(gem)
                self.gems_group.add(gem)
            # if self.isMatch()[0] == 0:
            #     break

    def run(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption('消消樂')
        
        self.put_puzzle()

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT: sys.exit()

            self.screen.fill((255, 255, 220))
            
            self.drawGrids()
            self.gems_group.draw(self.screen)

            pygame.display.flip()

if __name__ == '__main__':
    mainApp = Application()
    mainApp.daemon = True
    mainApp.name = 'game'

    mainApp.start()

    while True:
        sleep(1)
    