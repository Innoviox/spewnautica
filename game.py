from direct.showbase.ShowBase import ShowBase
from direct.actor.Actor import Actor

base = ShowBase()

panda = Actor('panda.egg', {'walk': 'panda-walk.egg'})
panda.loop('walk')

circle_center = render.attach_new_node('circle_center')
circle_center.hprInterval(10, (-360, 0, 0)).loop()
panda.reparent_to(circle_center)
panda.set_x(20)

base.camera.set_pos_hpr(50, -50, 30, 45, -22.5, 0)

base.run()
