from mesa.visualization.ModularVisualization import VisualizationElement

from Boids import BaseAgent


class VerySimpleCanvas(VisualizationElement):
    local_includes = ['Graphics.js']

    def __init__(self, portrayal_method, canvas_width=500, canvas_height=500):
        super().__init__()
        self.portrayal_method = portrayal_method
        self.canvas_width = canvas_width
        self.canvas_height = canvas_height

        new_elements = 'new VerySimpleContinuousModule(%s, %s)' % (self.canvas_width, self.canvas_height)
        self.js_code = 'elements.push(%s);' % new_elements

    def render(self, model):
        space_state = []
        for obj in model.schedule.agents:
            space_width = obj.space.x_max - obj.space.x_min

            portrayal = obj.draw()
            x, y, = obj.pos
            x, y = x/space_width, y/space_width
            portrayal['x'] = x
            portrayal['y'] = y
            if obj.heading is not None and obj.max_speed is not None:
                vx, vy = obj.pos + obj.heading * obj.max_speed * 10
                vx, vy = vx/space_width, vy/space_width
            else:
                vx, vy = x, y
            portrayal['vx'] = vx
            portrayal['vy'] = vy
            if 'rs' in portrayal:
                portrayal['rs'] = portrayal['rs'] / space_width
            space_state.append(portrayal)
        return space_state
