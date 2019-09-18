import lib as lib3d

class World(lib3d.Model):
    def _initialize(self):
        """ Initialize the world by placing all the blocks.

        """
        n = 80  # 1/2 width and height of world
        s = 1  # step size
        y = 0  # initial y height
        for x in range(-n, n + 1, s):
            for z in range(-n, n + 1, s):
                # create a layer stone an grass everywhere.
                self.add_block((x, y - 2, z), GRASS, immediate=False)
                self.add_block((x, y - 3, z), GRASS, immediate=False)
                self.add_block((x, y - 4, z), GRASS, immediate=False)
                self.add_block((x, y - 5, z), GRASS, immediate=False)
                self.add_block((x, y - 6, z), GRASS, immediate=False)
                self.add_block((x, y - 7, z), GRASS, immediate=False)
                self.add_block((x, y - 8, z), STONE, immediate=False)
                if x in (-n, n) or z in (-n, n):
                    # create outer walls.
                    for dy in range(-2, 3):
                        self.add_block((x, y + dy, z), STONE, immediate=False)

        # generate the hills randomly
        o = n - 10
        for _ in range(120):
            a = random.randint(-o, o)  # x position of the hill
            b = random.randint(-o, o)  # z position of the hill
            c = -1  # base of the hill
            h = random.randint(1, 6)  # height of the hill
            s = random.randint(4, 8)  # 2 * s is the side length of the hill
            d = 1  # how quickly to taper off the hills
            t = random.choice([GRASS, STONE, BRICK])
            for y in range(c, c + h):
                for x in range(a - s, a + s + 1):
                    for z in range(b - s, b + s + 1):
                        if (x - a) ** 2 + (z - b) ** 2 > (s + 1) ** 2:
                            continue
                        if (x - 0) ** 2 + (z - 0) ** 2 < 5 ** 2:
                            continue
                        self.add_block((x, y, z), t, immediate=False)
                s -= d  # decrement side lenth so hills taper off

class Window(lib3d.Window):
    def __init__(width=800, height=600, caption='Game', resizable=True):
        super.__init__(width=width, height=height, caption=caption, resizable=resizable, model=World())

    def on_mouse_press(self, x, y, button, modifiers):
        """ Called when a mouse button is pressed. See pyglet docs for button
        amd modifier mappings.

        Parameters
        ----------
        x, y : int
            The coordinates of the mouse click. Always center of the screen if
            the mouse is captured.
        button : int
            Number representing mouse button that was clicked. 1 = left button,
            4 = right button.
        modifiers : int
            Number representing any modifying keys that were pressed when the
            mouse button was clicked.

        """
        if self.exclusive:
            vector = self.get_sight_vector()
            block, previous = self.model.hit_test(self.position, vector)
            if (button == mouse.RIGHT) or \
                    ((button == mouse.LEFT) and (modifiers & key.MOD_CTRL)):
                # ON OSX, control + left click = right click.
                if previous:
                    self.model.add_block(previous, self.block)
            elif button == pyglet.window.mouse.LEFT and block:
                texture = self.model.world[block]
                if texture != STONE:
                    self.model.remove_block(block)
        else:
            self.set_exclusive_mouse(True)

    def on_key_press(self, symbol, modifiers):
        """ Called when the player presses a key. See pyglet docs for key
        mappings.

        Parameters
        ----------
        symbol : int
            Number representing the key that was pressed.
        modifiers : int
            Number representing any modifying keys that were pressed.

        """
        if symbol == key.W:
            self.strafe[0] -= 1
        elif symbol == key.S:
            self.strafe[0] += 1
        elif symbol == key.A:
            self.strafe[1] -= 1
        elif symbol == key.D:
            self.strafe[1] += 1
        elif symbol == key.SPACE:
            if self.dy == 0:
                self.dy = JUMP_SPEED
        elif symbol == key.ESCAPE:
            self.set_exclusive_mouse(False)
        elif symbol == key.TAB:
            self.flying = not self.flying
        elif symbol in self.num_keys:
            index = (symbol - self.num_keys[0]) % len(self.inventory)
            self.block = self.inventory[index]
        elif symbol == key.M:
            vector = self.get_sight_vector()
            block = self.model.hit_test(self.position, vector)[0]
            if block:
                self.model.move_block(block)

    def on_key_release(self, symbol, modifiers):
        """ Called when the player releases a key. See pyglet docs for key
        mappings.

        Parameters
        ----------
        symbol : int
            Number representing the key that was pressed.
        modifiers : int
            Number representing any modifying keys that were pressed.

        """
        if symbol == key.W:
            self.strafe[0] += 1
        elif symbol == key.S:
            self.strafe[0] -= 1
        elif symbol == key.A:
            self.strafe[1] += 1
        elif symbol == key.D:
            self.strafe[1] -= 1

            
lib3d.main(Window())
