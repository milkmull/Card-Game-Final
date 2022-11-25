
def analyze(scores, pid):
    player_score = scores[pid]
    score = sum([player_score - score for score in scores]) / (len(scores) - 1)
    return score

class Tree:
    log_types = (
        'p', 
        's', 
        'rand', 
        'randres'
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
        
        with open('other/tree.json', 'w') as f:
            json.dump(self.remap_to_string(), f, indent=4)
        
    def log_to_key(self, log):
        match log['t']:
            
            case 'p':
                pid = log['u']
                deck = log['d']
                cid = log['c']
                x, y = log['pos']
                return (pid, deck, cid, x, y)
            
            case 's':
                pid = log['u']
                cid = log['c']
                return (pid, cid)
                
            case 'rand':
                pid = log['u']
                len = log['len']
                id = log['id']
                return (pid, len, id)
                
            case 'randres':
                pid = log['u']
                res = log['res']
                return (pid, res)
        
    def trim(self, log):
        key = self.log_to_key(log)
        new_tree = self.tree.get(key)
        if isinstance(new_tree, list) or new_tree is None:
            new_tree = {}
        self.tree = new_tree

    def simulate(self, num=20, max_deapth=4):
        for _ in range(num):
        
            g = self.game.copy()
            turn = 0
            while not g.done and turn < max_deapth and g.public_deck:
                g.main()
                turn += 1

            scores = [p.score for p in sorted(g.players, key=lambda p: p.pid)]
            logs = [log for log in g.log if log['t'] in Tree.log_types]

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

        if key not in branch:
            branch[key] = self.update_tree(scores, logs)
            
        else:
            if isinstance(branch[key], list) and logs:
                branch[key] = {}
                
            self.update_tree(scores, logs, branch=branch[key])
            
        return branch
        
    def get_scores(self, pid, branch=None, deapth=0, data=None):
        if branch is None:
            branch = self.tree

        decider = pid
     
        scores = {}
        for key, subbranch in branch.items():
            
            decider = key[0]

            if isinstance(subbranch, list):
                scores[key] = analyze(subbranch, pid)
            else:
                scores[key] = self.get_scores(pid, branch=subbranch, deapth=deapth + 1, data=key)

        if deapth == 0:
            self.save_tree()
            return scores
        if not scores:
            return 0
            
        if data is not None:
            if len(data) == 3:
                return sum(scores.values()) / data[1]

        if decider == pid:
            return max(scores.values())
        return min(scores.values())
        
    def print_tree(self, branch=None, deapth=0, indent=1):
        if branch is None:
            branch = self.tree
            
        if isinstance(branch, list):
            print((' ' * deapth) + str(branch))
            
        else:
            for choice, subbranch in branch.items():
                print((' ' * deapth) + str(choice) + ': {')
                self.print_tree(branch=subbranch, deapth=deapth + indent)
                print((' ' * deapth) + '}')
 