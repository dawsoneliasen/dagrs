""" Graph degree progress.
"""

from graphviz import Digraph

class Graph:
    """ A webgraphviz graph representation of a degree program.
    """

    def test(self):
        dot = Digraph(comment='The Round Table')
        dot.node('A', 'King Arthur')
        dot.node('B', 'Sir Bedevere the Wise')
        dot.node('L', 'Sir Lancelot the Brave')
        dot.edges(['AB', 'AL'])
        dot.edge('B', 'L', constraint='false')
        dot.render('output/test.gv', view=True)

    def __init__(self, program):
        dot = Digraph(
            comment=program.desc,
            node_attr={
                'shape': 'box', 
                'style': 'filled, rounded', 
                'fillcolor': 'lightblue', 
                'fontname': 'Verdana'
            }
        )
        flow = []
        for i in range(len(program.reqs)):
            if program.reqs[i].req_type == 'rigid':
                dot.node(str(i), str(program.reqs[i]))
                flow.append(i)
                if i > 0 and (i - 1) in flow:
                    dot.edge(str(i - 1), str(i))
        for i in range(len(program.reqs)):
            if program.reqs[i].req_type == 'choose':
                dot.node(str(i), str(program.reqs[i].count) + ' ' + program.reqs[i].desc)
        dot.graph_attr['rankdir'] = 'LR'
        dot.render('output/program.gv', view=True)
