import sys
import os
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.layout import Layout
from rich import box

# Add current dir to path
sys.path.append(os.getcwd())

from core.services.memory_service import MemoryService
from core.config import settings

console = Console()

class Dashboard:
    def __init__(self):
        self.memory = MemoryService()

    def get_nodes(self):
        conn = self.memory._get_connection()
        with conn.cursor() as cur:
            cur.execute("SELECT node_id, version, last_seen FROM swarm_nodes ORDER BY last_seen DESC;")
            return cur.fetchall()

    def get_recent_traces(self, limit=10):
        conn = self.memory._get_connection()
        with conn.cursor() as cur:
            cur.execute("""
                SELECT project_id, phase, content, created_at, node_id 
                FROM sga_l0_context 
                ORDER BY created_at DESC LIMIT %s;
            """, (limit,))
            return cur.fetchall()

    def get_knowledge_summary(self):
        conn = self.memory._get_connection()
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM sga_l1_swarm_knowledge;")
            count = cur.fetchone()[0]
            cur.execute("SELECT content, created_at FROM sga_l1_swarm_knowledge ORDER BY created_at DESC LIMIT 3;")
            recent = cur.fetchall()
            return count, recent

    def render(self):
        console.clear()
        console.print(Panel(f"[bold cyan]SwarmTeam OS Elite[/bold cyan] - Observability Dashboard (v{settings.version})", box=box.DOUBLE))

        # Nodes Table
        nodes_table = Table(title="Connected Nodes (SGA)", box=box.SIMPLE)
        nodes_table.add_column("Node ID", style="magenta")
        nodes_table.add_column("Version", style="green")
        nodes_table.add_column("Last Seen", style="yellow")

        for node in self.get_nodes():
            nodes_table.add_row(node[0], node[1], node[2].strftime("%Y-%m-%d %H:%M:%S"))

        console.print(nodes_table)

        # Traces Table
        traces_table = Table(title="Recent Execution Traces (L0)", box=box.SIMPLE)
        traces_table.add_column("Project", style="cyan")
        traces_table.add_column("Phase", style="blue")
        traces_table.add_column("Content Preview", style="white", ratio=2)
        traces_table.add_column("Time", style="dim")

        for trace in self.get_recent_traces():
            content = trace[2][:50] + "..." if len(trace[2]) > 50 else trace[2]
            traces_table.add_row(trace[0], trace[1], content, trace[3].strftime("%H:%M:%S"))

        console.print(traces_table)

        # Knowledge Panel
        count, recent = self.get_knowledge_summary()
        knowledge_content = f"Total Indexed Insights: [bold green]{count}[/bold green]\n\n"
        knowledge_content += "[bold cyan]Recent Industry Insights (L1):[/bold cyan]\n"
        for r in recent:
            knowledge_content += f"- {r[0][:80]}... ([dim]{r[1].strftime('%m-%d')}[/dim])\n"

        console.print(Panel(knowledge_content, title="Global Knowledge (SGA L1)", border_style="green"))

if __name__ == "__main__":
    try:
        dash = Dashboard()
        dash.render()
    except Exception as e:
        console.print(f"[bold red]Error loading dashboard:[/bold red] {e}")
