# Knowledge-Based Dynamic Wumpus Agent 🤖🧠

**Live Demo:** [Play the Web App on Vercel](https://web-app-murex-phi-34.vercel.app/)

A web-based Artificial Intelligence pathfinding agent that navigates a dynamic "Wumpus World" grid. Instead of using standard search algorithms with complete map knowledge, this agent operates under **partial observability**. It builds a Knowledge Base (KB) in real-time and uses **Propositional Logic** and **Resolution Refutation** to mathematically prove the safety of its next moves.

---

## 🔗 Connect with the Author

**Saqib Khizar (Saqib Ali)**
* **LinkedIn (Profile 1):** [saqib-khizar-894a8822a](https://www.linkedin.com/in/saqib-khizar-894a8822a/)
* **LinkedIn (Profile 2):** [saqibkhizar](https://www.linkedin.com/in/saqibkhizar)
* **Live Project URL:** [Wumpus Agent Live](https://web-app-murex-phi-34.vercel.app/)

---

## ✨ Features

* **Dynamic Grid Sizing:** Users can define custom grid dimensions (Rows × Columns) on the fly.
* **Automated Theorem Proving:** The backend python engine uses custom-built `TELL` and `ASK` functions to convert percepts into Conjunctive Normal Form (CNF) and resolve them.
* **Real-time Metrics Dashboard:** Tracks the agent's exact $(x, y)$ position, current percepts (Breeze/Stench), and the number of active logical inference steps it takes to calculate the next move.
* **Responsive GUI:** Clean, decoupled Vanilla JS frontend that visually renders safe zones (green), unknown zones (gray), and hazards (red).

---

## 🛠️ Tech Stack

* **Backend:** Python, Flask
* **Frontend:** HTML5, CSS3, Vanilla JavaScript (Fetch API/AJAX)
* **Logic/Algorithms:** Propositional Logic, Resolution Refutation, Proof by Contradiction

---

## ⚙️ How It Works

1. **Initialization:** The agent starts at `[1, 1]` with an empty Knowledge Base. Hidden Pits and a Wumpus are spawned in the environment.
2. **Perception:** The agent senses its surroundings. If a Pit is adjacent, it feels a `Breeze`. If the Wumpus is adjacent, it smells a `Stench`.
3. **Inference (TELL):** The agent updates its Knowledge Base with these percepts using CNF logic rules.
4. **Resolution (ASK):** Before taking a step, the agent assumes an adjacent cell has a hazard and attempts to prove a contradiction using Resolution Refutation. If a contradiction is found, the cell is mathematically proven safe.
5. **Movement:** The agent moves to a proven safe cell. The frontend updates immediately to reflect this new state.

---

## 🚀 Local Installation & Setup

If you want to run this project locally on your machine, follow these steps:

### Prerequisites
Make sure you have [Python](https://www.python.org/downloads/) installed on your system.

