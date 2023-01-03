import re

from .node.node_base import Port_Types
from .node import mapping

class Compiler:
    @staticmethod
    def unmark(text):
        return re.sub(r"(#<)([0-9]+)(,-?[0-9]+)(>#)", "", text)
        
    @staticmethod
    def get_ranges(text, id, port=None):
        i = 0
        ranges = []
        last = ""
        open = False

        while True:
            res = re.search(r"(#<)([0-9]+)(,-?[0-9]+)(>#)", text)
            if not res:
                break
                
            g = res.group()
            i += res.start()
            text = text[res.end():]
            
            nid, pid = g.strip("#<>").split(",")
            
            if nid == str(id) and (port is None or pid == str(port)):
                if not open:
                    subtext = re.sub(r"(#<)([0-9]+)(,-?[0-9]+)(>#)", "", text[:text.index(g)])
                    r = (i, i + len(subtext))
                    ranges.append(r)
                    open = True
                    last = g
                elif g == last:
                    open = False
            
        return ranges

    def __init__(self, nodes, card=None):
        self.nodes = nodes
        self.card = card
        
    @property
    def header(self):
        if not self.card:
            return ""
        return (
            f"\nclass {self.card.classname}(card_base.Card):\n"
                f"\tname = \"{self.card.name}\"\n"
                f"\tweight = {self.card.weight}\n"
                f"\ttags = {self.card.tags}\n"
        )
        
    @property
    def missing(self):
        return []
                
    @property
    def funcs(self):
        return [n for n in self.nodes if n.is_func]
                
    def compile(self, ignore_missing=False, mark=False):
        for n in self.nodes:
            n.mark = mark
    
        if self.missing:
            return ""
   
        data = {}
        
        for n in self.funcs:
            data[n.name] = {
                "header": "\t" + n.get_text(),
                "start": n.get_start(),
                "body": "",
                "end": n.get_end()
            }
            self._compile(n, data[n.name])
            
        out = self.header

        for func, info in data.items():
            header = info["header"]
            start = info["start"]
            body = info["body"]
            end = info["end"]
            if not start + body + end:
                body = "\t\tpass\n"
            out += header + start + body + end

        return out.replace("\t", "    ")
            
    def _compile(self, node, data, tabs=2):
        text = ""
        
        if not node.is_func:
            out_text = node.get_text()
            if out_text:
                for line in out_text.splitlines():
                    text += (tabs * "\t") + line + "\n"
                data["body"] += text
        
        process_found = False
        for op in node.get_output_ports():
            if op.is_process:
                if op.connection:
                    self._compile(op.connection, data, tabs=tabs + 1)
                process_found = True
                break
     
        if process_found:
            if data["body"].endswith(text):
                data["body"] += ((tabs + 1) * "\t") + "pass\n"

        for op in node.get_output_ports():
            if op.has_type(Port_Types.FLOW) and not op.is_process:
                if op.connection:
                    self._compile(op.connection, data, tabs=tabs)
