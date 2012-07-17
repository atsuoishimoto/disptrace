"""
Sidecar to disptrace that infers where else statements should be, because
they're not traced by default...and that's wrong.
"""

import ast
from memento import MementoMetaclass
from codemanager import CodeManager

class ImpliedElseFinder(ast.NodeVisitor):
    """
    An ast.NodeVisitor that looks into ast.If nodes to find else
    clauses that Python tracing will not explicitly trace. If the first statement
    of an orelse component is an ast.If it might be an elif. Check for that. 
    """
    __metaclass__ = MementoMetaclass

    def __init__(self, filepath):
        ast.NodeVisitor.__init__(self)
        self.code = CodeManager(filepath)
        self.else_lines = {}
        self.visit(self.code.ast)
        
    def implied_else_line(self, lineno):
        """Main query front-end for this class. Given a line, where is its
        implied else, if any?
        """
        return self.else_lines.get(lineno, None)
    
    def associated_else(self, lineno):
        """Given a lineno where an implied else has been found, return the
        line number on which that implied else resides."""

        while 'else' not in self.code.sourcelines[lineno]:
            lineno -= 1
        return lineno
        
    def visit_If(self, node):
        """
        Called for all ast.If nodes.
        """
        try:
            # if the else doesn't start with another If, record it
            else_start = node.orelse[0]
            lineno = else_start.lineno
            if not isinstance(else_start, ast.If) or \
                not self.code.sourcelines[lineno].strip().startswith('elif'):
            
                assoc_else_line = self.associated_else(lineno)
                if assoc_else_line != lineno:
                    self.else_lines[lineno] = assoc_else_line
                
            # visit its children
            ast.NodeVisitor.generic_visit(self, node)
            
        except IndexError as e:
            pass