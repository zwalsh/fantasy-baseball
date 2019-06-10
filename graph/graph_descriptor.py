from plotly import offline as plotly
from plotly import graph_objs as go


class GraphDescriptor:

    def __init__(self, x_data, lines, title, x_name, y_name):
        """
        Describes a graph of data that can be plotted with plotly. The x_data is a list of common,
        x data points shared by each of the lines. The lines is a list of GraphLine objects to
        plot on this graph. The title is the graph's title, and x/y_name are the names of the
        x and y axes.
        :param list x_data: shared points on the x-axis (with a corresponding y-value for each point in each line)
        :param list lines: list of GraphLines in this graph
        :param str title: the title of the graph, to display on the top
        :param str x_name: name of the x-axis
        :param str y_name: name of the y-axis
        """
        self.x_data = x_data
        self.lines = lines
        self.title = title
        self.x_name = x_name
        self.y_name = y_name

    def plot(self):
        data = [l.trace(self.x_data) for l in self.lines]
        layout = {
            "title": self.title,
            "xaxis": {
                "title": self.x_name
            },
            "yaxis": {
                "title": self.y_name
            }
        }
        figure = {
            "data": data,
            "layout": layout
        }
        plotly.plot(figure)


class GraphLine:

    def __init__(self, data, name):
        """
        Represents one line on a graph. Data is a list of the y-values of the data points.
        Name is the name of this line.
        :param list data: the y-values to plot
        :param str name: the name of this line
        """
        self.data = data
        self.name = name

    def trace(self, x_data):
        """
        Generates a plotly trace graph object for this GraphLine
        :param list x_data: the x points for each corresponding y point in this line
        :return :
        """
        return go.Scatter(
            x = x_data,
            y = self.data,
            mode = 'lines',
            name = self.name
        )