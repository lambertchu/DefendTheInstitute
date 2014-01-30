#!/usr/bin/env python
import pygame, sys, math
from pygame.locals import *
from random import randint

### Global Variables
SPRITE_WIDTH = 40
BOARD_WIDTH = SPRITE_WIDTH*12
BOARD_HEIGHT = SPRITE_WIDTH*18
QUIT_STATE = -1
START_MENU_STATE = 0
HIGH_SCORES_STATE = 1
GAME_STATE = 2
UPGRADE_STATE = 3

timDamage=1
timSpeed=10

# RGB Color definitions
black = (0, 0, 0)
white = (255, 255, 255)
reds = [(255, 0, 0), (205, 0, 0), (155, 0, 0), (105, 0, 0), (55, 0, 0), (0, 0, 0)]
greens = [(0, 255, 0), (0, 205, 0), (0, 155, 0), (0, 105, 0), (0, 55, 0), (0, 0, 0)]
blues = [(0, 0, 255), (0, 0, 205), (0, 0, 155), (0, 0, 105), (0, 0, 55), (0, 0, 0)]

def draw_text(screen, message, position, textSize, textColor, backgroundColor):
    font = pygame.font.Font(None, textSize)
    text = font.render(message, True, textColor, backgroundColor)
    textRect = text.get_rect()
    textRect.centerx = position[0]
    textRect.centery = position[1]
    screen.blit(text, textRect)

##### Background stuff #####
class Background:
    def __init__(self):
        self.things = []
        self.count = 0
        for i in range(BOARD_HEIGHT):
            self.update()
    def update(self):
        for thing in self.things:
            if not thing.update():
                self.things.remove(thing)
        if self.count == 10:
            self.count = 0
            self.things.append(BackgroundThing())
        self.count += 1
    def draw(self, screen):
        screen.fill(black)
        for thing in self.things:
            thing.draw(screen)

class BackgroundThing:
    def __init__(self):
        self.x = randint(0, BOARD_WIDTH-10)
        self.y = 0

        self.width = 3
        rand = randint(0,2)
        if rand == 0:
            self.colors = reds
        elif rand == 1:
            self.colors = greens
        elif rand == 2:
            self.colors = blues
    def update(self):
        if self.y <= BOARD_HEIGHT:
            self.y += 1
            return True
        else:
            return False
    def draw(self, screen):
        for i in range(len(self.colors)):
            rect=(self.x,self.y-self.width*i,self.width,self.width)
            pygame.draw.rect(screen,self.colors[i],rect)

##### High Scores #####
class HighScores:
    def __init__(self):
        self.filename = "highScores.txt"
        content = []
        with open(self.filename) as f:
            content = f.readlines()
        self.content = [line.strip().split(',') for line in content]
    def saveToFile(self):
        with open(self.filename, 'w') as f:
            for thing in self.content:
                f.write(thing.join(','))
                f.write('\n')
            f.truncate()
    def addScore(self, name, level, score):
        self.content.append([name,level,score])
        firstItem = self.content.pop(0)
        self.content.sort(lambda x,y:cmp(x[2],y[2]))
        self.content.insert(0,firstItem)
        while len(self.content>11):
            self.content.pop()
        self.saveToFile()

##### Start Menu Loop #####
def start_menu_loop(screen, background, clock):
    PLAY_BUTTON = 1
    HIGH_SCORES_BUTTON = 2
    QUIT_BUTTON = 3
    selection = PLAY_BUTTON
    while True:
        background.update()
        background.draw(screen)
        draw_text(screen,"Defend The Institute",(BOARD_WIDTH/2,150),60,white,black)
        textColor = black if selection==PLAY_BUTTON else white
        backgroundColor = white if selection == PLAY_BUTTON else black
        draw_text(screen,"Play",(BOARD_WIDTH/2,300),35,textColor,backgroundColor)
        textColor = black if selection==HIGH_SCORES_BUTTON else white
        backgroundColor = white if selection == HIGH_SCORES_BUTTON else black
        draw_text(screen,"High Scores",(BOARD_WIDTH/2,425),35,textColor,backgroundColor)
        textColor = black if selection == QUIT_BUTTON else white
        backgroundColor = white if selection == QUIT_BUTTON else black
        draw_text(screen,"Quit",(BOARD_WIDTH/2,550),35,textColor,backgroundColor)
        for event in pygame.event.get():
            if event.type == KEYDOWN:
                if event.key==K_DOWN:
                    selection+=1
                    if selection == 4:
                        selection = 1
                elif event.key==K_UP:
                    selection-=1
                    if selection == 0:
                        selection = 3
                elif event.key==K_RETURN:
                    if selection==PLAY_BUTTON:
                        return GAME_STATE
                    elif selection==HIGH_SCORES_BUTTON:
                        return HIGH_SCORES_STATE
                    elif selection==QUIT_BUTTON:
                        return QUIT_STATE
            elif event.type == QUIT:
                return QUIT_STATE
        pygame.display.update()
        clock.tick(30)

##### High Scores Loop #####
def high_scores_loop(screen, background, clock, highScores):
    while True:
        background.update()
        background.draw(screen)
        draw_text(screen,"High Scores",(BOARD_WIDTH/2,100),50,white,black)
        for i in range(len(highScores.content)):
            position = (BOARD_WIDTH/4,200+(BOARD_HEIGHT-300)/11*i)
            draw_text(screen,highScores.content[i][0],position,30,white,black)
            position = (BOARD_WIDTH/2,position[1])
            draw_text(screen,highScores.content[i][1],position,30,white,black)
            position = (3*BOARD_WIDTH/4,position[1])
            draw_text(screen,highScores.content[i][2],position,30,white,black)
        for event in pygame.event.get():
            if event.type == KEYDOWN:
                if event.key==K_RETURN:
                    return START_MENU_STATE
            elif event.type == QUIT:
                return QUIT_STATE
        pygame.display.update()
        clock.tick(30)

##### Game Loop #####
class Projectile(pygame.sprite.Sprite):
    def __init__(self, projImage, direction, position, damage):
        super(Projectile,self).__init__()
        self.direction = direction
        self.damage = damage
        self.image = pygame.image.load(projImage).convert_alpha()
        self.rect = self.image.get_rect()
        self.rect[0] = position[0]
        self.rect[1] = position[1]
    def move(self): # returns a boolean that says whether or not the move worked
        if self.direction == "up" and self.rect[1]>=0:
            self.rect[1]-=10
            return True
        elif self.direction == "up" and self.rect[1]<0:
            return False
        elif self.direction == "down" and self.rect[1]<=BOARD_HEIGHT:
            self.rect[1]+=10
            return True
        elif self.direction == "down" and self.rect[1]>BOARD_HEIGHT:
            return False
    def draw(self, screen):
        screen.blit(self.image, self.rect)

class HealthMeter:
    def __init__(self, maxHealth, rect):
        self.maxHealth = maxHealth
        self.currentHealth = maxHealth
        self.rect = rect
    def setHealth(self, health):
        self.currentHealth = health if health >= 0 else 0
    def draw(self, screen):
        pygame.draw.rect(screen, reds[0],self.rect,2)
        filledRect = self.rect[:]
        filledRect[2] = filledRect[2]*self.currentHealth/self.maxHealth
        pygame.draw.rect(screen,reds[0],filledRect)

class Tim(pygame.sprite.Sprite):
    def __init__(self, health, damage, speed):
        super(Tim,self).__init__()
        self.health = health
        self.damage = damage # damage of projectiles
        self.speed = speed # movement speed
        self.direction = 0
        self.image = pygame.image.load('./Pictures/tim.jpg').convert_alpha()
        self.rect = self.image.get_rect()
        self.rect[0] = BOARD_WIDTH/2
        self.rect[1] = BOARD_HEIGHT-100
        healthRect = pygame.Rect(self.rect[0],self.rect[1]+self.rect[3]*.75,\
            self.rect[2], self.rect[3]*.25)
        self.healthMeter = HealthMeter(self.health, healthRect)
    def update(self):
        # move
        self.rect[0]+=self.direction*self.speed
        if self.rect[0] <= 0:
            self.rect[0] = 0
        elif self.rect[0] >= BOARD_WIDTH-self.rect[2]:
            self.rect[0] = BOARD_WIDTH-self.rect[2]
        # update health meter
        self.healthMeter.rect[0] = self.rect[0]
        self.healthMeter.setHealth(self.health)
    def draw(self, screen):
        screen.blit(self.image, self.rect)
        self.healthMeter.draw(screen)
    def shoot(self): # returns a Projectile object for the main loop to handle
        destPos = (self.rect[0]+self.rect[2]/2,self.rect[1]-50)
        return Projectile('./Pictures/plank.jpg',"up",destPos,self.damage)
    def takeDamage(self,inflictedDamage): # returns a bool saying if Tim is alive
        self.health-=inflictedDamage
        return True if self.health > 0 else False

class LivesMeter:
    def __init__(self, numLives):
        self.lives = numLives
        self.image = pygame.image.load('./Pictures/tim.jpg').convert_alpha()
        self.image = pygame.transform.scale(self.image, (25,25))
    def draw(self, screen):
        draw_text(screen, "Lives:", (30, BOARD_HEIGHT-15), 20, white, black)
        for i in range(self.lives):
            screen.blit(self.image, (60+30*i, BOARD_HEIGHT-27.5))

class Enemy(pygame.sprite.Sprite):
    def __init__(self, health, position, damage):
        super(Enemy,self).__init__()
        self.health= health
        self.damage= damage

        self.image = pygame.image.load('./Pictures/Harvard.png').convert_alpha()
        self.rect = self.image.get_rect()
        self.rect[0] = position[0]
        self.rect[1] = position[1]
    def moveRight(self, speed):
        self.rect[0]+=speed
    def moveLeft(self, speed):
        self.rect[0]-=speed
    def moveUp(self, speed):
        self.rect[1]-=speed
    def moveDown(self, speed):
        self.rect[1]+=speed
    def shoot(self): # returns a Projectile object for the main loop to handle
        destPos = (self.rect[0]+self.rect[2]/2,self.rect[1]+50)
        return Projectile('./Pictures/plank.jpg',"down",destPos,self.damage)
    def draw(self, screen):
        screen.blit(self.image, self.rect)
    def takeDamage(self,inflictedDamage): # returns a bool saying if it is alive
        self.health-=inflictedDamage
        return True if self.health > 0 else False

class EnemyArmy(pygame.sprite.Sprite):
    def __init__(self, level):
        self.number = int(math.ceil(math.sqrt(level)))+5
        health = int(math.ceil(math.sqrt(level)))*3
        self.speed = int(math.ceil(math.sqrt(level)))
        damage = int(math.ceil(math.sqrt(level)))
        self.position = [10,30]
        self.direction = (1,0)
        self.army = []
        self.count = 0
        for i in range(self.number):
            enemyPosition = (self.position[0]+i*40, self.position[1])
            self.army.append(Enemy(health, enemyPosition, damage))
    def moveRight(self):
        for i in range(len(self.army)):
            self.army[i].moveRight(self.speed)
        self.position[0]+=self.speed
    def moveLeft(self):
        for i in range(len(self.army)):
            self.army[i].moveLeft(self.speed)
        self.position[0]-=self.speed
    def moveUp(self):
        for i in range(len(self.army)):
            self.army[i].moveUp(self.speed)
        self.position[1]-=self.speed
    def moveDown(self):
        for i in range(len(self.army)):
            self.army[i].moveDown(self.speed)
        self.position[1]+=self.speed
    def shoot(self): # returns a Projectile object for the main loop to handle
        return self.army[randint(0, len(self.army)-1)].shoot()
    def update(self):
        if self.direction == (1,0):
            self.moveRight()
            if self.number*40+self.position[0] >= BOARD_WIDTH-10:
                self.direction = (0,-1)
        elif self.direction == (0,-1):
            self.moveDown()
            if self.count >= 5:
                self.count = 0
                if self.position[0]+self.number*40 >= BOARD_WIDTH-10:
                    self.direction = (-1,0)
                elif self.position[0] <= 10:
                    self.direction = (1,0)
            else:
                self.count+=1
        elif self.direction == (-1,0):
            self.moveLeft()
            if self.position[0] <= 10:
                self.direction = (0,-1)
    def draw(self, screen):
        for i in range(len(self.army)):
            self.army[i].draw(screen)
    def isEmpty(self):
        return len(self.army)>0

def upgrade_menu_loop(screen, background, clock, money, timDamage, timSpeed):
    UPGRADE_DAMAGE_BUTTON = 1
    UPGRADE_SPEED_BUTTON = 2
    NEXT_LEVEL_BUTTON = 3
    selection = UPGRADE_DAMAGE_BUTTON
    upgradeDamageCost=100
    upgradeSpeedCost=75
    while True:
        background.update()
        background.draw(screen)
        draw_text(screen,"UPGRADES",(BOARD_WIDTH/2,100),60,white,black)
        draw_text(screen,"AVAILABLE MONEY: $" + str(money),(BOARD_WIDTH/2,200),50,white,black)
        textColor = black if selection==UPGRADE_DAMAGE_BUTTON else white
        backgroundColor = white if selection == UPGRADE_DAMAGE_BUTTON else black
        draw_text(screen,"UPGRADE BULLET DAMAGE: $" + str(upgradeDamageCost),(BOARD_WIDTH/2,350),25,textColor,backgroundColor)
        textColor = black if selection==UPGRADE_SPEED_BUTTON else white
        backgroundColor = white if selection == UPGRADE_SPEED_BUTTON else black
        draw_text(screen,"UPGRADE MOVEMENT SPEED: $" + str(upgradeSpeedCost),(BOARD_WIDTH/2,400),25,textColor,backgroundColor)

        textColor = black if selection == NEXT_LEVEL_BUTTON else white
        backgroundColor = white if selection == NEXT_LEVEL_BUTTON else black
        draw_text(screen,"PLAY NEXT LEVEL", (BOARD_WIDTH/2,550),50,textColor,backgroundColor)

        for event in pygame.event.get():
            if event.type == KEYDOWN:
                if event.key==K_DOWN:
                    selection+=1
                    if selection == 4:
                        selection = 1
                elif event.key==K_UP:
                    selection-=1
                    if selection == 0:
                        selection = 3
                elif event.key==K_RETURN:
                    if selection==NEXT_LEVEL_BUTTON:
                        state = game_loop(screen, background, clock, highScores, timDamage, timSpeed)
                    elif selection==UPGRADE_DAMAGE_BUTTON:
                        if money>=upgradeDamageCost:
                            money-=upgradeDamageCost
                            timDamage+=.5
                            upgradeDamageCost=(int)(1.5*upgradeDamageCost)

                            draw_text(screen,"BULLET DAMAGE UPGRADED!", (BOARD_WIDTH/2,475),35,reds[0],black)
                            pygame.display.update()
                            clock.tick(1)
                        else:
                            draw_text(screen,"NOT ENOUGH MONEY!", (BOARD_WIDTH/2,475),35,reds[0],black)
                            pygame.display.update()
                            clock.tick(1)

                    elif selection==UPGRADE_SPEED_BUTTON:
                        if money>=upgradeSpeedCost:
                            money-=upgradeSpeedCost
                            timSpeed+=.5
                            upgradeSpeedCost=(int)(1.5*upgradeSpeedCost)
                            draw_text(screen,"MOVEMENT SPEED UPGRADED!", (BOARD_WIDTH/2,475),35,reds[0],black)
                            pygame.display.update()
                            clock.tick(1)
                        else:
                            draw_text(screen,"NOT ENOUGH MONEY!", (BOARD_WIDTH/2,475),35,reds[0],black)
                            pygame.display.update()
                            clock.tick(1)
            elif event.type == QUIT:
                return (QUIT_STATE)
        pygame.display.update()
        clock.tick(30)

def game_loop(screen, background, clock, highScores, timDamage, timSpeed):
    tim = Tim(3, timDamage, timSpeed)
    livesMeter = LivesMeter(3)
    level = 1
    enemies = EnemyArmy(level)
    score = 0
    money = 0
    projectiles = []
    while True:
        # Background stuff
        background.update()
        background.draw(screen)
        # HUD stuff
        levelText = "Level: " + str(level)
        draw_text(screen,levelText,(100,25),25,white,black)
        moneyText = "Money: $" + str(money)
        draw_text(screen,moneyText,(BOARD_WIDTH-200,25),25,white,black)
        scoreText = "Score: " + str(score)
        draw_text(screen,scoreText,(BOARD_WIDTH-100,25),25,white,black)
        livesMeter.draw(screen)
        # Tim stuff
        tim.update()
        tim.draw(screen)
        # Enemy stuff
        enemies.update()
        enemies.draw(screen)
        # Projectile stuff
        newProjectiles = []
        for projectile in projectiles:
            if projectile.move():
                newProjectiles.append(projectile)
            projectile.draw(screen)
        projectiles = newProjectiles
        # Collision stuff
        projectileRects = [projectile.rect for projectile in projectiles]
        index = tim.rect.collidelist(projectileRects)
        if index != -1:
            if tim.takeDamage(projectiles[index].damage):
                projectiles.pop(index)
                projectileRects.pop(index)
            else: # Tim died!
                tim.direction = 0
                tim.update()
                tim.draw(screen)
                pygame.display.update()
                clock.tick(1)
                projectiles = []
                tim = Tim(3, 1, 10)
                livesMeter.lives -= 1
                if livesMeter.lives == -1:
                    # Game Over
                    draw_text(screen, "GAME OVER", (BOARD_WIDTH/2, BOARD_HEIGHT/2),\
                        50, white, black)
                    pygame.display.update()
                    clock.tick(0.2)
                    return START_MENU_STATE
        for enemy in enemies.army:
            index = enemy.rect.collidelist(projectileRects)
            if index != -1:
                isAlive = enemy.takeDamage(projectiles[index].damage)
                projectiles.pop(index)
                projectileRects.pop(index)
                if not isAlive:
                    enemies.army.remove(enemy)
                    score += 10
                    money+=5
        # Enemy Shooting
        if pygame.time.get_ticks() % 20 <= len(enemies.army)-1:
            projectiles.append(enemies.shoot())
        # Input handling
        for event in pygame.event.get():
            if event.type == KEYDOWN:
                if event.key == K_LEFT:
                    tim.direction = -1
                elif event.key == K_RIGHT:
                    tim.direction = 1
                elif event.key == K_SPACE:
                    projectiles.append(tim.shoot())
            elif event.type == KEYUP:
                if event.key == K_LEFT and tim.direction == -1:
                    tim.direction = 0
                elif event.key == K_RIGHT and tim.direction == 1:
                    tim.direction = 0
            if event.type == QUIT:
                return QUIT_STATE
        # Stuff
        if len(enemies.army)==0:
            state=upgrade_menu_loop(screen,background,clock,money,timDamage,timSpeed)
        pygame.display.update()
        clock.tick(30)

##### Main Loop #####
if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((BOARD_WIDTH, BOARD_HEIGHT))
    pygame.display.set_caption("Defend The Institute")
    clock = pygame.time.Clock()
    background = Background()
    highScores = HighScores()
    state = START_MENU_STATE
    while state != QUIT_STATE:
        if state == START_MENU_STATE:
            state = start_menu_loop(screen, background, clock)
        elif state == HIGH_SCORES_STATE:
            state = high_scores_loop(screen, background, clock, highScores)
        elif state == GAME_STATE:
            state = game_loop(screen, background, clock, highScores, timDamage, timSpeed)
        elif state == UPGRADE_STATE:
            state = upgrade_menu_loop(screen,background,clock,500,1,10)
    pygame.quit()
