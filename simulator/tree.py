
def analyze(scores, pid):
    player_score = scores[pid]
    return sum([player_score - score for score in scores]) / (len(scores) - 1)

class Tree:
    def __init__(self, game):
        self.tree = {}
        self.game = game
        
    def reset(self):
        self.tree.clear()
        
    def log_to_key(self, log):
        pid = log["u"]
        cid = log["c"].id
        x, y = log["p"]
        return (pid, f"{cid}-{x}-{y}")
        
    def trim(self, log):
        key = self.log_to_key(log)

        for info in self.tree.copy():
            if info != key:
                self.tree.pop(info)

    def simulate(self, num=1, max_deapth=99):
        for _ in range(num):
        
            g = self.game.copy()
            turn = 0
            while not g.done and turn < max_deapth:
                g.main()
                turn += 1

            scores = [p.score for p in sorted(g.players, key=lambda p: p.pid)]
            logs = [log for log in g.log if log["t'] == 'play"]

            if logs:
                self.update_tree(
                    scores,
                    logs,
                    branch=self.tree
                )
        
    def update_tree(self, scores, logs, index=0, branch=None):
        if branch is None:
            branch = {}
  
        if index == len(logs):
            return scores
        if isinstance(branch, list):
            branch = {}
            
        log = logs[index]
        key = self.log_to_key(log)

        if key not in branch:
            branch[key] = self.update_tree(scores, logs, index=index + 1)
        else:
            self.update_tree(scores, logs, index=index + 1, branch=branch[key])
        
        return branch
    
    def get_scores(self, pid, branch=None, top=True):
        if branch is None:
            branch = self.tree
     
        scores = {}
        for key, subbranch in branch.items():
        
            if top and id != pid:
                return scores

            elif isinstance(subbranch, list):
                scores[choice] = analyze(subbranch, pid)

            else:
                scores[choice] = self.get_scores(pid, subbranch, top=False)
            
        if top:
            return scores

        return sum(scores.values()) / len(scores)
        
    def print_tree(self, branch=None, deapth=0, indent=1):
        if branch is None:
            branch = self.tree
            
        for choice, subbranch in branch.items():
        
            if isinstance(subbranch, list):
                print((" " * deapth) + str(subbranch))
        
            else:
                print((" ' * deapth) + str(choice) + ': {")
                self.print_tree(branch=subbranch, deapth=deapth + indent)
                print((" ' * deapth) + '}")
 