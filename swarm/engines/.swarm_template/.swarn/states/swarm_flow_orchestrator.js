const fs = require('fs');
const path = require('path');

class SwarmOrchestrator {
  constructor() {
    this.statePath = path.join(__dirname, '../states/swarm_state.json');
    this.loadState();
  }

  loadState() {
    if (fs.existsSync(this.statePath)) {
      this.state = JSON.parse(fs.readFileSync(this.statePath, 'utf8'));
    } else {
      this.state = { currentNode: 'M0', status: 'PENDING', history: [] };
    }
  }

  saveState() {
    fs.writeFileSync(this.statePath, JSON.stringify(this.state, null, 2));
  }

  transition(nextNode) {
    this.state.history.push({ from: this.state.currentNode, to: nextNode, timestamp: new Date() });
    this.state.currentNode = nextNode;
    this.state.status = 'PENDING';
    this.saveState();
    console.log(`Transición: ${this.state.history[this.state.history.length-1].from} -> ${nextNode}`);
  }
}

module.exports = SwarmOrchestrator;
