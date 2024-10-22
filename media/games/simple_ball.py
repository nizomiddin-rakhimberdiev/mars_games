from panda3d.core import Point3, DirectionalLight, AmbientLight, Vec4
from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from direct.gui.OnscreenText import OnscreenText
import random
import math

class SimpleGame(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)

        # Camera settings
        self.disableMouse()
        self.camera.setPos(0, -20, 10)
        self.camera.lookAt(0, 0, 0)

        # Add lights
        dlight = DirectionalLight('dlight')
        dlight.setColor(Vec4(1.0, 1.0, 1.0, 1))
        dlnp = self.render.attachNewNode(dlight)
        dlnp.setHpr(0, -60, 0)
        self.render.setLight(dlnp)

        alight = AmbientLight('alight')
        alight.setColor(Vec4(0.5, 0.5, 0.5, 1))
        alnp = self.render.attachNewNode(alight)
        self.render.setLight(alnp)

        # Game field - ground
        self.ground = self.loader.loadModel("models/environment")
        self.ground.reparentTo(self.render)
        self.ground.setScale(0.25, 0.25, 0.25)
        self.ground.setPos(-8, 42, 0)

        # Player (ball)
        self.ball = self.loader.loadModel("smiley")
        self.ball.reparentTo(self.render)
        self.ball.setScale(0.5)
        self.ball.setPos(0, 0, 1)

        # Ammo and lives
        self.ammo = 40
        self.lives = 3
        self.reloading = False

        # HUD
        self.ammo_text = OnscreenText(text=f"Ammo: {self.ammo}", pos=(-1.3, 0.8), scale=0.07)
        self.lives_text = OnscreenText(text=f"Lives: {self.lives}", pos=(1.1, 0.8), scale=0.07)
        self.level_text = OnscreenText(text=f"Level: 1", pos=(-1.0, 0.9), scale=0.07)  # Level text

        # Create enemies
        self.enemies = []
        self.current_level = 1  # Start with level 1
        self.max_levels = 20  # Total number of levels
        self.startNewLevel()

        # Key mapping (WASD)
        self.keyMap = {"left": False, "right": False, "forward": False, "backward": False, "space": False}
        self.accept("a", self.setKey, ["left", True])       # A key
        self.accept("a-up", self.setKey, ["left", False])
        self.accept("d", self.setKey, ["right", True])      # D key
        self.accept("d-up", self.setKey, ["right", False])
        self.accept("w", self.setKey, ["forward", True])     # W key
        self.accept("w-up", self.setKey, ["forward", False])
        self.accept("s", self.setKey, ["backward", True])    # S key
        self.accept("s-up", self.setKey, ["backward", False])
        self.accept("space", self.setKey, ["space", True])
        self.accept("space-up", self.setKey, ["space", False])

        # Add tasks
        self.shots = []  # To store bullets
        self.taskMgr.add(self.moveBall, "moveBallTask")
        self.taskMgr.add(self.shootTask, "shootTask")
        self.taskMgr.add(self.checkCollisionTask, "checkCollisionTask")
        self.taskMgr.add(self.moveEnemiesTask, "moveEnemiesTask")  # Task for enemy movement

        # Reload with R
        self.accept("r", self.reload)

        # Mouse controls
        self.accept("mouse1", self.mouseButtonPress)
        self.accept("mouse1-up", self.mouseButtonRelease)

        # Mouse movement tracking
        self.mouseMoveTask = self.taskMgr.add(self.mouseMoveTask, "mouseMoveTask")

    def setKey(self, key, value):
        self.keyMap[key] = value

    def moveBall(self, task):
        # Move player based on key presses
        if self.keyMap["left"]:
            self.ball.setX(self.ball.getX() - 0.1)
        if self.keyMap["right"]:
            self.ball.setX(self.ball.getX() + 0.1)
        if self.keyMap["forward"]:
            self.ball.setY(self.ball.getY() + 0.1)
        if self.keyMap["backward"]:
            self.ball.setY(self.ball.getY() - 0.1)
        return Task.cont

    def shootTask(self, task):
        # Shooting bullets when space is pressed and ammo is available
        if self.keyMap["space"] and self.ammo > 0 and not self.reloading:
            bullet = self.loader.loadModel("smiley")
            bullet.setScale(0.1)  # Small bullet size
            bullet.setPos(self.ball.getPos())  # Set bullet position to player position

            # Bullet moves in the direction player is facing
            bullet.reparentTo(self.render)
            self.shots.append(bullet)  # Store bullet
            self.ammo -= 1  # Decrease ammo count
            self.ammo_text.setText(f"Ammo: {self.ammo}")
            self.keyMap["space"] = False  # Single press per bullet

        for shot in self.shots:
            # Move bullet in Y direction only
            shot.setY(shot.getY() + 0.2)

        return Task.cont

    def moveEnemiesTask(self, task):
        # Move enemies towards the player
        for enemy in self.enemies:
            enemy_pos = enemy.getPos()
            player_pos = self.ball.getPos()

            direction = player_pos - enemy_pos
            distance = direction.length()

            if distance > 0:
                direction.normalize()
                enemy.setX(enemy.getX() + direction.x * 0.02)
                enemy.setY(enemy.getY() + direction.y * 0.02)

            # Check collision between player and enemy
            if self.isCollision(self.ball, enemy):
                self.lives -= 1  # Player loses a life
                self.lives_text.setText(f"Lives: {self.lives}")

                if self.lives == 0:
                    self.gameOver()  # End the game if no lives left

                enemy.removeNode()  # Remove the enemy after collision
                self.enemies.remove(enemy)

        return Task.cont

    def checkCollisionTask(self, task):
        # Check collisions between bullets and enemies
        for enemy in self.enemies:
            for shot in self.shots:
                if self.isCollision(shot, enemy):  # If bullet hits enemy
                    enemy.removeNode()  # Remove enemy
                    self.enemies.remove(enemy)
                    shot.removeNode()  # Remove bullet
                    self.shots.remove(shot)
                    self.checkLevelComplete()  # Check if the level is complete
                    break
        return Task.cont

    def isCollision(self, obj1, obj2):
        # Simple collision check (based on distance)
        pos1 = obj1.getPos()
        pos2 = obj2.getPos()
        distance = (pos1 - pos2).length()
        return distance < 0.5  # Define collision distance

    def checkLevelComplete(self):
        if len(self.enemies) == 0:  # Check if all enemies are defeated
            if self.current_level < self.max_levels:
                self.current_level += 1  # Go to the next level
                self.startNewLevel()     # Start the new level
            else:
                self.showVictoryMessage()  # Show victory message

    def startNewLevel(self):
        # Start a new level
        self.ammo = 40  # Reset ammo
        self.ammo_text.setText(f"Ammo: {self.ammo}")
        self.level_text.setText(f"Level: {self.current_level}")  # Update level text

        num_enemies = 5 + self.current_level  # Increase enemy count with each level
        for i in range(num_enemies):
            enemy = self.loader.loadModel("smiley")
            enemy.setScale(0.5)
            enemy.setColor(1, 0, 0, 1)
            enemy.setPos(random.uniform(-5, 5), random.uniform(-5, 5), 1)
            enemy.reparentTo(self.render)
            self.enemies.append(enemy)

    def mouseButtonPress(self):
        # Fire bullet when mouse button is pressed
        self.keyMap["space"] = True

    def mouseButtonRelease(self):
        # Stop firing bullets when mouse button is released
        self.keyMap["space"] = False

    def reload(self):
        if not self.reloading and self.ammo == 0:
            self.reloading = True
            self.ammo_text.setText("Reloading...")  # Display reloading text
            self.taskMgr.doMethodLater(2, self.finishReload, "reloadTask")  # 2-second delay for reloading

    def finishReload(self, task):
        self.ammo = 40  # Reload ammo
        self.ammo_text.setText(f"Ammo: {self.ammo}")
        self.reloading = False  # Reset reloading flag
        return Task.done

    def gameOver(self):
        self.ammo_text.setText("Game Over! Restarting...")
        self.lives = 3  # Reset lives
        self.lives_text.setText(f"Lives: {self.lives}")
        self.current_level = 1  # Reset level
        self.enemies.clear()  # Clear enemies
        self.startNewLevel()  # Restart the game

    def showVictoryMessage(self):
        self.ammo_text.setText("You Win!")
        self.lives_text.setText("")
        self.level_text.setText("")
        self.taskMgr.doMethodLater(3, self.restartGame, "victoryTask")

    def restartGame(self, task):
        self.ammo_text.setText("Game Restarting...")
        self.lives = 3  # Reset lives
        self.lives_text.setText(f"Lives: {self.lives}")
        self.current_level = 1  # Reset level
        self.enemies.clear()  # Clear enemies
        self.startNewLevel()  # Restart the game
        return Task.done

    def mouseMoveTask(self, task):
        # Track mouse movement
        if self.mouseWatcherNode.hasMouse():
            mouse_x = self.mouseWatcherNode.getMouseX()
            mouse_y = self.mouseWatcherNode.getMouseY()

            # Rotate player based on mouse X position
            angle = mouse_x * 180  # Adjust rotation based on mouse position
            self.ball.setH(angle)  # Update player's heading

        return Task.cont

game = SimpleGame()
game.run()
