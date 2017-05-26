from mesa.visualization.ModularVisualization import VisualizationElement


class VerySimpleText(VisualizationElement):
    local_includes = ['Text.js']

    def __init__(self):
        super().__init__()

        new_elements = 'new VerySimpleSpan()'
        self.js_code = 'elements.push(%s);' % new_elements

    def render(self, model):
        return model.starved
