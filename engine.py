import pygame
from eventManager import *

class Engine():
    class Colors():
        WHITE = (255, 255, 255, 255)
        WHITE_TRANSLUCENT = (255, 255, 255, 64)
        LIGHT_GREY = (192, 192, 192, 255)
        DARK_BLUE = (0, 0, 96, 255)
        BRIGHT_RED = (255, 0, 0, 255)
        LAVENDER = (210, 166, 255, 255)
        GREY = (128, 128, 128, 255)
        BLACK = (0, 0, 0, 255)

    class Options():
        def __init__(self):
            self.name = "Baller" #"Defeat the oppressive war machine of the evil Quadratic invaders!"
            self.backstory = '''
    From the depths of Outer Space comes the vile army of the extraterrestrial race known only as the Quadrilaterians.

    Freshly resupplied from the war-torn planet of Buttercracker IV, the Quadrilaterians are hellbent on conquest and will not stop until they have crushed our military, overthrown our government, quelled all rebellions, completely subjugated our planet and have captured all of our cheese and the means of production for such.

    It is up to you, our Champion, to defeat the oppressive war machine of the evil Quadratic invaders!

    Your planet needs you!
            '''

            #clock
            self.tickSpeed = 60

            #difficulty
            self.availableDifficulties = [("Easy", 0), ("Normal", 1), ("Hard", 2), ("Brutal", 3)]
            self.defaultDifficultyValue = 1
            self.difficultyValue = self.defaultDifficultyValue
            self.difficulty = {
                0: {
                    "paddleWidth": 150,
                    "brickHitsRemaining": 0,
                    "ballRadius": 25,
                    "ballSpeed": 2
                    },
                1: {
                    "paddleWidth": 100,
                    "brickHitsRemaining": 1,
                    "ballRadius": 12.5,
                    "ballSpeed": 4
                },
                2: {
                    "paddleWidth": 50,
                    "brickHitsRemaining": 2,
                    "ballRadius": 6.75,
                    "ballSpeed": 8
                },
                3: {
                    "paddleWidth": 10,
                    "brickHitsRemaining": 3,
                    "ballRadius": 3.375,
                    "ballSpeed": 16
                }}

            #Mouse / Keyboard(?) sensitivity
            sensitivities = []
            for s in range(10, 0, -1):
                text = "Every {0} ticks"
                sensitivities.append((text.format(s), s))

            sensitivities[0] = ("MIN (not recommended)", len(sensitivities))
            sensitivities[len(sensitivities) - 1] = ("MAX (recommended)", 1)

            self.availableSensitivities = sensitivities
            self.defaultSensitivityValue = 1
            self.sensitivityValue = self.defaultSensitivityValue

            #window properties
            self.windowWidth = 800
            self.windowHeight = 600
            self.windowSize = (self.windowWidth, self.windowHeight)
            self.windowFillColor = Engine.Colors.WHITE

            #paddle properties
            self.paddleWidth = self.difficulty[self.difficultyValue]["paddleWidth"]
            self.paddleHeight = 25
            self.paddleLeftBound = 10
            self.paddleRightBound = self.paddleLeftBound
            self.paddleColor = Engine.Colors.DARK_BLUE
            self.paddleX = (self.windowWidth / 2) - (self.paddleWidth / 2)
            self.paddleY = 550

            #brick properties
            self.brickWidthHeightRatio = {"width": 2, "height": 1} # only ever used in this class to determine width and height
            self.brickSize = 25 # only ever used in this class to determine width and height

            self.brickWidth = self.brickSize * self.brickWidthHeightRatio["width"]
            self.brickHeight = self.brickSize * self.brickWidthHeightRatio["height"]
            self.brickBorderWidth = 2
            self.brickHitsRemaining = self.difficulty[self.difficultyValue]["brickHitsRemaining"]

            #brick wall properties
            self.brickWallWidth = self.windowWidth
            self.brickWallHeight = self.windowHeight - 200
            self.brickWallMortarGap = 2

            #ball properties
            self.ballSpeed = self.difficulty[self.difficultyValue]["ballSpeed"]
            self.ballRadius = self.difficulty[self.difficultyValue]["ballRadius"]
            self.ballVectorInitial = -45
            self.ballGyreDirection = 180
            self.ballColor = Engine.Colors.BRIGHT_RED
            self.ballInitialPosition = (self.windowWidth / 2, self.windowHeight - 100)

            #Base GUI widget properties
            self.widgetPadding = 40
            self.widgetFontSize = 56

            #Slider GUI widget
            self.sliderFontSize = 24
            self.sliderWidth = 200
            self.sliderHeight = 72
            self.sliderBarHeight = 10
            self.sliderBarOffsetX = 0
            self.sliderBarOffsetY = 15
            self.sliderSlideWidth = 10
            self.sliderSlideHeight = 40
            self.sliderTextOffsetY = 8
            self.sliderDragPaddingX = 100

    class GUI():
        def __init__(self):
            pass

        class Widget(pygame.sprite.Sprite):
            def __init__(self, eventManager, container = None):
                pygame.sprite.Sprite.__init__(self)

                self.eventManager = eventManager
                self.container = container
                self.isCollidable = False
                self.focused = False
                self.dirty = True
                self.options = self.eventManager.game.options #alias

            def setPosition(self, x = None, y = None):
                if x or y:
                    self.dirty = True

                    if x:
                        self.rect.x = x

                    if y:
                        self.rect.y = y

                    self.update()

            def centerOn(self, surf):
                surfRect = surf.get_rect()
                onX = surfRect.x + (surfRect.width / 2) - (self.rect.width / 2)
                onY = surfRect.y + (surfRect.height / 2) - (self.rect.height / 2)
                self.setPosition(onX, onY)

            def leftEdge(self):
                return self.rect.x

            def rightEdge(self):
                return self.rect.x + self.rect.width

            def topEdge(self):
                return self.rect.y

            def bottomEdge(self):
                return self.rect.y + self.rect.height

            def centerZone(self, width = 12): # allow for a wider zone, if desired
                rect = self.image.get_rect() # get a new rect based on the image
                rect.y = self.rect.y

                if self.width % 2 == 0: #even width
                    rect.x = self.rect.width / 2
                    rect.width = width

                else: # odd width
                    rect.x = (self.rect.width + 1) / 2
                    rect.width = 1

                return rect

            def leftNearZone(self):
                centerZone = self.centerZone() # get the center zone
                rect = self.image.get_rect() # get a new rect based on the image
                rect.y = self.rect.y

                width = (centerZone.x - self.rect.x)

                if width % 2 == 0: #even width
                    rect.x = width / 2
                    rect.width = (width / 2) - 1

                else: # odd width
                    rect.x = (width + 1) / 2
                    rect.width = ((width + 1) / 2) - 1

                return rect

            def leftFarZone(self):
                leftNearZone = self.leftNearZone() # get the leftNear zone
                rect = self.image.get_rect() # get a new rect based on the image
                rect.y = self.rect.y

                width = (leftNearZone.x - self.rect.x)

                rect.x = self.rect.x
                rect.width = width - 1

                return rect

            def rightNearZone(self):
                centerZone = self.centerZone() # get the center zone
                rect = self.image.get_rect() # get a new rect based on the image
                rect.y = self.rect.y
                rect.x = centerZone.x + centerZone.width

                width = self.rightEdge() - (centerZone.x + centerZone.width)

                if width % 2 == 0: #even width
                    rect.width = (width / 2) - 1

                else: # odd width
                    rect.width = ((width + 1) / 2) - 1

                return rect

            def rightFarZone(self):
                rightNearZone = self.rightNearZone() # get the rightNear zone
                rect = self.image.get_rect() # get a new rect based on the image

                rect.y = self.rect.y
                rect.x = rightNearZone.x + rightNearZone.width
                rect.width = self.rightEdge() - (rightNearZone.x + rightNearZone.width)

                return rect

            def setFocus(self, val):
                self.focused = val
                self.dirty = True

            def kill(self):
                self.removeListeners()
                self.container = None
                del self.container
                pygame.sprite.Sprite.kill(self)

            def removeListeners(self):
                listeners = self.eventManager.getListeners()
                if self in listeners.keys():
                    for event in listeners[self]:
                        e = Events.getEvent(event)
                        self.eventManager.removeListener(e, self)

            def notify(self, event):
                print("Abstract Class not implemented. Triggering event:", event.name)

    class Layer():
        def __init__(self, fillColor = None, mouseVisible = True):
            self.mouseVisible = mouseVisible
            self.fillColor = fillColor if fillColor != None else Engine.Colors.WHITE
            self.widgets = pygame.sprite.Group()
            self.activate = self.addListeners
            self.deactivate = self.removeListeners
            self.widgetValues = {}

        def addWidget(self, widget):
            self.widgets.add(widget)#append

        def addListeners(self):
            for widget in self.widgets:
                widget.addListeners()

        def removeListeners(self):
            for widget in self.widgets:
                widget.removeListeners()

        def removeWidget(self, widget):
            if widget in self.widgets:
                widget.removeListeners()
                self.widgets.remove(widget)

        def getWidgets(self, ofType = None):
            widgets = self.widgets

            if ofType != None:
                widgets = [widget for widget in self.widgets if type(widget) == ofType]

            return widgets

        def redrawWidgets(self, window):
            self.widgets.update()
            self.widgets.draw(window)

    class Ticker():
        def __init__(self, eventManager, engine):
            self.eventManager = eventManager
            self.engine = engine

            event = Events.TickEvent()
            self.eventManager.addListener(event, self)

            event = Events.QuitEvent()
            self.eventManager.addListener(event, self)

        def notify(self, event):
            if isinstance(event, Events.QuitEvent):
                self.eventManager.running = False

            if isinstance(event, Events.TickEvent):
                self.engine.clock.tick(self.engine.options.tickSpeed)
                self.engine.redrawWindow() #redraw sprites
                pygame.time.wait(0) # CRITICAL: sleep for the minimum amount of time. DO NOT REMOVE THIS LINE
                pygame.display.update() #redraw screen

    def applyOptions(self, newSensitivity, newDifficulty):
        from ball import Ball
        from paddle import Paddle
        from brick import Brick
        from widgets import SliderWidget

        # grab old difficulty
        oldDifficulty = self.options.difficultyValue

        # store new setting
        self.options.sensitivityValue = newSensitivity
        self.options.difficultyValue = newDifficulty

        # apply difficulty
        self.options.paddleWidth = self.options.difficulty[self.options.difficultyValue]["paddleWidth"]
        self.options.brickHitsRemaining = self.options.difficulty[self.options.difficultyValue]["brickHitsRemaining"]
        self.options.ballSpeed = self.options.difficulty[self.options.difficultyValue]["ballSpeed"]
        self.options.ballRadius = self.options.difficulty[self.options.difficultyValue]["ballRadius"]

        if self.screens:
            if self.screens["level"]:
                screen = self.screens["level"]

            balls = screen.getWidgets(Ball)
            for ball in balls:
                ball.speed = self.options.ballSpeed
                ball.radius = self.options.ballRadius

            paddles = screen.getWidgets(Paddle)
            for paddle in paddles:
                paddle.sensitivity = self.options.sensitivityValue
                paddle.width = self.options.paddleWidth

            oldBrickHitsRemaining = self.options.difficulty[oldDifficulty]["brickHitsRemaining"]
            bricks = screen.getWidgets(Brick)
            for brick in bricks:
                # update hitsRemaining as needed
                differenceInHitsRemaining = oldBrickHitsRemaining - brick.hitsRemaining
                if differenceInHitsRemaining == 0:
                    # hits remaining should be new max hits remaining
                    brick.hitsRemaining = self.options.brickHitsRemaining
                elif brick.hitsRemaining < 0:
                    # brick should already be eliminated so...
                    pass
                else:
                    # difference is non-zero and brick has hits remaining. adjust for new hits remaining.
                    brick.hitsRemaining = self.options.brickHitsRemaining - differenceInHitsRemaining

                brick.animate()

            #ensure parity between both options screen and pause screen
            screens = ("options", "pause")
            for s in screens:
                if self.screens[s]:
                    screen = self.screens[s]

                    sliders = screen.getWidgets(SliderWidget)
                    for slider in sliders:
                        if slider.valueKey == "sensitivity":
                            slider.setValue(self.options.sensitivityValue)

                        if slider.valueKey == "difficulty":
                            slider.setValue(self.options.difficultyValue)

    def redrawWindow(self):
        screen = self.screens[self.activeScreen]
        self.window.fill(self.options.windowFillColor)
        screen.redrawWidgets(self.window)

    def end(self):
        self.eventManager.running = False
        pygame.display.quit()
        pygame.quit()

    def __init__(self):
        #Initial module setup
        #make an instance of GUI and Options classes so the interpreter won't kvetch
        self.GUI = Engine.GUI()
        self.defaults = Engine.Options() # first instance is read-only
        self.options = Engine.Options() # second is changeable
        #self.GUI.Widget = Engine.GUI.Widget() #interpreter doesn't kvetch on not having an instance of Widget, so commenting out for now

        self.sprites = pygame.sprite.Group()
        self.screens = {}
        self.activeScreen = ""

        #Create a window and start a clock
        pygame.init()
        self.window = pygame.display.set_mode(self.options.windowSize, pygame.SRCALPHA, 32)
        pygame.display.set_caption(self.options.name)
        self.clock = pygame.time.Clock()
