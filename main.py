import lib as lib3d
from lib import key, mouse, pyglet, make_3d_textures, OBJECTS, visualization as obj_draw

GRASS, *_, SAND, BRICK, STONE = make_3d_textures(3, 2, special={0: (2, 1, 0)})

class World(lib3d.Model):
    def _initialize(self):
        super()._initialize()
        obj = OBJECTS["fish"]
        print(obj.meshes)
        print(dir(obj))
        # obj.translate(0, 0, 0)
        # obj.rotate(90, 1, 0, 0)
        # obj.scale(0.1, 0.1, 0.1)
        # obj.add_to(self.batch)
        print(obj)
        # obj.meshes["FISH_Plane"].draw()
        # obj.draw()
        obj_draw.draw(obj)
        # self.batch.draw(obj)

        print(self.batch)

class Window(lib3d.Window):
    def __init__(self, width=800, height=600, caption='Game', resizable=True):
        lib3d.Window.__init__(self, model_cls=World, width=width, height=height, caption=caption, resizable=resizable)

    def on_mouse_press(self, x, y, button, modifiers):
        """ Called when a mouse button is pressed. See pyglet docs for button
        amd modifier mappings.
f
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
                self.dy = self.user_config.JUMP_SPEED
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


if __name__ == "__main__":
    lib3d.main(Window())
