from mesa.visualization.ModularVisualization import VisualizationElement

from Boids import BaseAgent


class VerySimpleCanvas(VisualizationElement):
    local_includes = ['graphics.js']

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
            portrayal = BaseAgent.draw(obj)
            x, y, = obj.pos
            x = ((x - obj.space.x_min) /
                 (obj.space.x_max - obj.space.x_min))
            y = ((y - obj.space.y_min) /
                 obj.space.y_max - obj.space.y_min)
            portrayal['x'] = x
            portrayal['y'] = y
            space_state.append(portrayal)
        return space_state
