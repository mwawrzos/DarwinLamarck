import numpy as np

from mesa.visualization.ModularVisualization import VisualizationElement


class HistogramModule(VisualizationElement):
    package_includes = ['Chart.min.js']
    local_includes = ['HistogramModule.js']

    def __init__(self, bins, canvas_height, canvas_width):
        super().__init__()
        self.canvas_height = canvas_height
        self.canvas_width = canvas_width
        self.bins = bins
        new_element = "new HistogramModule({}, {}, {})"
        new_element = new_element.format(bins,
                                         canvas_width,
                                         canvas_height)
        self.js_code = "elements.push(" + new_element + ");"

    def render(self, model):
        wealth_values = [agent.decision for agent in model.schedule.agents if agent.decision >= 0]
        hist = np.histogram(wealth_values, bins=self.bins)[0]
        return [int(x) for x in hist]
