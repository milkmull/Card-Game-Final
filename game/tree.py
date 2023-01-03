
class Node:
    def __init__(self, type, data):
        self.type = type
        self.data = data
        
    def __eq__(self, other):
        if isinstance(other, Node):
            return self.type == other.type and self.data == other.data
        return False
        
    def __hash__(self):
        return hash(self.data)
        
    def __str__(self):
        return str(self.data)
        
    def __repr__(self):
        return f"{self.type}: {str(self.data)}"

def analyze(scores, pid):
    player_score = scores[pid]
    score = sum([player_score - score for score in scores]) / (len(scores) - 1)
    return score

class Tree:
    log_types = (
        "p", 
        "s", 
        "rand", 
        "randres"
    )
    
    def __init__(self, game):
        self.tree = {}
        self.game = game
        self.f = ""
        
        self.sims = 0
        
    def reset(self):
        self.tree.clear()
        self.sims = 0
        
    def remap_to_string(self, branch=None):
        if branch is None:
            branch = self.tree
        elif isinstance(branch, list):
            return branch
            
        return {str(key): self.remap_to_string(branch=subbranch) for key, subbranch in branch.items()}
        
    def save_tree(self):
        import json
        
        with open("other/tree.json", "w") as f:
            json.dump(self.remap_to_string(), f, indent=4)
        
    def log_to_key(self, log):
        match (type := log["t"]):
            
            case "p":
                pid = log["u"]
                deck = log["d"]
                cid = log["c"]
                x, y = log["pos"]
                return Node(type, (pid, deck, cid, x, y))
            
            case "s":
                pid = log["u"]
                cid = log["c"]
                return Node(type, (pid, cid))
                
            case "rand":
                pid = log["u"]
                len = log["len"]
                return Node(type, (pid, len))
                
            case "randres":
                pid = log["u"]
                res = log["res"]
                w = log.get("w", 1)
                return Node(type, (pid, res, w))
        
    def trim(self, log):
        key = self.log_to_key(log)
        new_tree = self.tree.get(key)
        if isinstance(new_tree, list) or new_tree is None:
            new_tree = {}
        self.tree = new_tree

    def simulate(self, num=100, max_deapth=2):
        for _ in range(num):
        
            g = self.game.copy()
            turn = 0
            while not g.done and turn < max_deapth and g.public_deck:
                g.main()
                turn += 1

            scores = [p.score for p in sorted(g.players, key=lambda p: p.pid)]
            logs = [log for log in g.log if log["t"] in Tree.log_types]

            self.update_tree(
                scores,
                logs,
                branch=self.tree
            )
            
            self.sims += 1
            
    def update_tree(self, scores, logs, branch=None):
        if not logs:
            return scores
            
        if branch is None:
            branch = {}
            
        log = logs.pop(0)
        key = self.log_to_key(log)
        
        if isinstance(branch, list):
            branch = {}
            
        if key not in branch:
            branch[key] = self.update_tree(scores, logs)
        else:
            self.update_tree(scores, logs, branch=branch[key])
            
        return branch
        
    def get_scores(self, pid, branch=None, deapth=0, node=None):
        if branch is None:
            branch = self.tree

        decider = pid
     
        scores = {}
        for key, subbranch in branch.items():
            
            decider = key.data[0]

            if isinstance(subbranch, list):
                scores[key] = analyze(subbranch, pid)
            else:
                scores[key] = self.get_scores(pid, branch=subbranch, deapth=deapth + 1, node=key)

        if deapth == 0:
            return scores
        if not scores:
            return 0
            
        if node and node.type == "rand":
            return sum(scores.values()) / node.data[1]

        score = 0
        if decider == pid:
            score = max(scores.values())
        score = min(scores.values())
        
        if node.type == "randres":
            score *= node.data[2]
            
        return score
        
    def print_tree(self, branch=None, deapth=0, indent=1):
        if branch is None:
            branch = self.tree
            
        if isinstance(branch, list):
            print((" " * deapth) + str(branch))
            
        else:
            for choice, subbranch in branch.items():
                print((" " * deapth) + str(choice) + ": {")
                self.print_tree(branch=subbranch, deapth=deapth + indent)
                print((" " * deapth) + "}")
 