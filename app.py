from flask import Flask, render_template, request, jsonify
import random

app = Flask(__name__)

class WumpusEnvironment:
    def __init__(self, rows, cols):
        self.rows = rows
        self.cols = cols
        self.pits = set()
        self.wumpus = None
        self.agent_pos = (1, 1)
        self.generate_hazards()

    def generate_hazards(self):
        # Randomly place Wumpus and Pits, ensuring (1,1) is safe
        cells = [(r, c) for r in range(1, self.rows + 1) for c in range(1, self.cols + 1) if (r, c) != (1, 1)]
        self.wumpus = random.choice(cells)
        cells.remove(self.wumpus)
        
        # 20% probability of a pit in remaining cells
        for cell in cells:
            if random.random() < 0.2:
                self.pits.add(cell)

    def get_percepts(self, r, c):
        percepts = []
        adjacents = self.get_adjacent(r, c)
        if any(adj in self.pits for adj in adjacents):
            percepts.append('Breeze')
        if any(adj == self.wumpus for adj in adjacents):
            percepts.append('Stench')
        return percepts

    def get_adjacent(self, r, c):
        adj = []
        if r > 1: adj.append((r - 1, c))
        if r < self.rows: adj.append((r + 1, c))
        if c > 1: adj.append((r, c - 1))
        if c < self.cols: adj.append((r, c + 1))
        return adj


class LogicAgent:
    def __init__(self, rows, cols):
        self.kb = set() # Set of frozensets (clauses in CNF)
        self.visited = set()
        self.safe_cells = set([(1, 1)])
        self.hazard_cells = set()
        self.inference_steps = 0
        self.rows = rows
        self.cols = cols
        
        # Initial Knowledge: (1,1) is safe
        self.tell([f"~P_{1}_{1}"])
        self.tell([f"~W_{1}_{1}"])

    def tell(self, clause):
        """Adds a clause to the KB. Clause is a list of literals."""
        self.kb.add(frozenset(clause))

    def ask(self, query_clause):
        """
        Uses Resolution Refutation to prove the query.
        query_clause is a list of literals representing the negated goal.
        """
        clauses = self.kb.copy()
        clauses.add(frozenset(query_clause))
        new = set()
        
        while True:
            n = len(clauses)
            clauses_list = list(clauses)
            for i in range(n):
                for j in range(i + 1, n):
                    resolvents = self.resolve(clauses_list[i], clauses_list[j])
                    self.inference_steps += 1
                    
                    if frozenset() in resolvents: # Empty clause = Contradiction found!
                        return True
                    new = new.union(resolvents)
            
            if new.issubset(clauses):
                return False # No new clauses, cannot prove
            
            clauses = clauses.union(new)
            
            # Safety limit to prevent infinite loops in massive grids
            if self.inference_steps > 2000: 
                return False

    def resolve(self, ci, cj):
        """Resolves two clauses and returns the resulting clauses."""
        resolvents = set()
        for di in ci:
            for dj in cj:
                if di == self.negate(dj) or self.negate(di) == dj:
                    # Resolve by removing the complementary literals
                    res = (set(ci) - {di}).union(set(cj) - {dj})
                    if not self.is_tautology(res):
                        resolvents.add(frozenset(res))
        return resolvents

    def negate(self, literal):
        return literal[1:] if literal.startswith('~') else '~' + literal

    def is_tautology(self, clause):
        return any(self.negate(lit) in clause for lit in clause)


# Global instances
env = None
agent = None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/init', methods=['POST'])
def init_game():
    global env, agent
    data = request.json
    rows = int(data.get('rows', 4))
    cols = int(data.get('cols', 4))
    
    env = WumpusEnvironment(rows, cols)
    agent = LogicAgent(rows, cols)
    
    return jsonify({"status": "initialized", "agent_pos": env.agent_pos})

@app.route('/step', methods=['POST'])
def step():
    global env, agent
    if not env or not agent:
        return jsonify({"error": "Game not initialized"}), 400

    r, c = env.agent_pos
    agent.visited.add((r, c))
    percepts = env.get_percepts(r, c)
    adjacents = env.get_adjacent(r, c)

    # 1. TELL the KB about the percepts (CNF Conversion happens here)
    # If NO Breeze: ~P_adj1 AND ~P_adj2 (Added as unit clauses)
    if 'Breeze' not in percepts:
        for adj in adjacents:
            agent.tell([f"~P_{adj[0]}_{adj[1]}"])
    else:
        # If Breeze: P_adj1 OR P_adj2 OR ...
        agent.tell([f"P_{adj[0]}_{adj[1]}" for adj in adjacents])

    # Same for Wumpus (Stench)
    if 'Stench' not in percepts:
        for adj in adjacents:
            agent.tell([f"~W_{adj[0]}_{adj[1]}"])
    else:
        agent.tell([f"W_{adj[0]}_{adj[1]}" for adj in adjacents])

    # 2. ASK the KB to find safe adjacent cells
    for adj in adjacents:
        if adj not in agent.visited and adj not in agent.safe_cells and adj not in agent.hazard_cells:
            # Prove ~P_adj AND ~W_adj. We do this by proving them individually.
            # To prove ~P, we assume P (negation of goal) and look for contradiction.
            is_pit_safe = agent.ask([f"P_{adj[0]}_{adj[1]}"])
            is_wumpus_safe = agent.ask([f"W_{adj[0]}_{adj[1]}"])
            
            if is_pit_safe and is_wumpus_safe:
                agent.safe_cells.add(adj)

    # 3. Simple movement logic (Move to a known safe, unvisited cell)
    next_moves = list(agent.safe_cells - agent.visited)
    if next_moves:
        env.agent_pos = next_moves[0]
    else:
        # Game over / No safe moves left
        env.agent_pos = None 

    grid_state = []
    for i in range(1, env.rows + 1):
        row = []
        for j in range(1, env.cols + 1):
            cell_state = "unknown"
            if (i, j) in agent.visited or (i, j) in agent.safe_cells: cell_state = "safe"
            if (i, j) in agent.hazard_cells: cell_state = "hazard"
            if env.agent_pos == (i, j): cell_state = "agent"
            row.append(cell_state)
        grid_state.append(row)

    return jsonify({
        "grid": grid_state,
        "percepts": percepts,
        "inference_steps": agent.inference_steps,
        "agent_pos": env.agent_pos,
        "wumpus": env.wumpus, # Sent for debug/verification
        "pits": list(env.pits)
    })

if __name__ == '__main__':
    app.run(debug=True)