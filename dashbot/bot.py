"""
Nanobot Dashboard Bot
=====================
A Discord bot for status monitoring and task management.

Commands:
  /status  - Show Nanobot config and system info
  /tasks   - List all tasks
  /add     - Add a new task
  /done    - Mark a task as completed
  /delete  - Delete a task
"""

import os
import asyncio
from datetime import datetime

import discord
from discord import app_commands
import aiosqlite
import httpx

# Configuration from environment
DISCORD_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
NANOBOT_URL = os.getenv("NANOBOT_URL", "http://nanobot:8080")
DATABASE_PATH = "/app/data/tasks.db"
NANOBOT_CONFIG_PATH = "/app/nanobot-config.yaml"


# Discord bot setup
intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)


# ============================================================
# Database Functions
# ============================================================

async def init_database():
    """Initialize the SQLite database with tasks table."""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                status TEXT DEFAULT 'pending',
                priority TEXT DEFAULT 'normal',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP
            )
        """)
        await db.commit()
    print("Database initialized.")


async def get_all_tasks():
    """Fetch all tasks from the database."""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM tasks ORDER BY status ASC, created_at DESC"
        ) as cursor:
            return await cursor.fetchall()


async def add_task(title: str, priority: str = "normal"):
    """Add a new task to the database."""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.execute(
            "INSERT INTO tasks (title, priority) VALUES (?, ?)",
            (title, priority)
        )
        await db.commit()
        return cursor.lastrowid


async def complete_task(task_id: int):
    """Mark a task as completed."""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute(
            "UPDATE tasks SET status = 'done', completed_at = ? WHERE id = ?",
            (datetime.now(), task_id)
        )
        await db.commit()


async def delete_task(task_id: int):
    """Delete a task from the database."""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        await db.commit()


# ============================================================
# Health Check Functions
# ============================================================

async def check_nanobot_health():
    """Check Nanobot API health."""
    try:
        async with httpx.AsyncClient(timeout=5.0) as http:
            response = await http.get(f"{NANOBOT_URL}/health")
            if response.status_code == 200:
                return {"status": "online"}
            return {"status": "error", "code": response.status_code}
    except Exception as e:
        return {"status": "offline", "error": str(e)}


def read_nanobot_config():
    """Read Nanobot config file."""
    try:
        with open(NANOBOT_CONFIG_PATH, "r") as f:
            content = f.read()
        # Simple parsing for display (YAML)
        config = {}
        for line in content.split("\n"):
            if ":" in line and not line.strip().startswith("#"):
                parts = line.split(":", 1)
                if len(parts) == 2:
                    key = parts[0].strip()
                    value = parts[1].strip().strip('"').strip("'")
                    if key and value:
                        config[key] = value
        return config
    except Exception as e:
        return {"error": str(e)}


# ============================================================
# Discord Commands
# ============================================================

@tree.command(name="status", description="Show system status and health")
async def status_command(interaction: discord.Interaction):
    """Display system status including Nanobot info."""
    await interaction.response.defer()

    # Check Nanobot
    nb_health = await check_nanobot_health()

    # Read Nanobot config
    nb_config = read_nanobot_config()

    # Build embed
    is_healthy = nb_health["status"] == "online"
    embed = discord.Embed(
        title="System Status",
        color=discord.Color.green() if is_healthy else discord.Color.red(),
        timestamp=datetime.now()
    )

    # Nanobot status
    nb_status = "Online" if is_healthy else "Offline"
    if "error" not in nb_config:
        provider = nb_config.get("provider", "unknown")
        model = nb_config.get("model", "unknown")
        embed.add_field(
            name="Nanobot",
            value=f"Status: {nb_status}\nProvider: `{provider}`\nModel: `{model}`",
            inline=False
        )
    else:
        embed.add_field(
            name="Nanobot",
            value=f"Status: {nb_status}\nConfig error: {nb_config['error']}",
            inline=False
        )

    # Task summary
    tasks = await get_all_tasks()
    pending = len([t for t in tasks if t["status"] == "pending"])
    done = len([t for t in tasks if t["status"] == "done"])
    embed.add_field(
        name="Tasks",
        value=f"Pending: {pending} | Completed: {done}",
        inline=False
    )

    await interaction.followup.send(embed=embed)


@tree.command(name="tasks", description="List all tasks")
async def tasks_command(interaction: discord.Interaction):
    """Display all tasks."""
    tasks = await get_all_tasks()

    if not tasks:
        await interaction.response.send_message("No tasks yet. Use `/add` to create one.")
        return

    embed = discord.Embed(
        title="Task List",
        color=discord.Color.blue(),
        timestamp=datetime.now()
    )

    pending_tasks = []
    done_tasks = []

    for task in tasks:
        task_line = f"`{task['id']}` — {task['title']}"
        if task["status"] == "pending":
            pending_tasks.append(task_line)
        else:
            done_tasks.append(f"~~{task_line}~~")

    if pending_tasks:
        embed.add_field(
            name="Pending",
            value="\n".join(pending_tasks[:10]) or "None",
            inline=False
        )

    if done_tasks:
        embed.add_field(
            name="Completed",
            value="\n".join(done_tasks[:10]) or "None",
            inline=False
        )

    await interaction.response.send_message(embed=embed)


@tree.command(name="add", description="Add a new task")
@app_commands.describe(task="The task description")
async def add_command(interaction: discord.Interaction, task: str):
    """Add a new task."""
    task_id = await add_task(task)
    await interaction.response.send_message(
        f"Task added with ID `{task_id}`: {task}"
    )


@tree.command(name="done", description="Mark a task as completed")
@app_commands.describe(task_id="The ID of the task to complete")
async def done_command(interaction: discord.Interaction, task_id: int):
    """Mark a task as done."""
    await complete_task(task_id)
    await interaction.response.send_message(
        f"Task `{task_id}` marked as completed!"
    )


@tree.command(name="delete", description="Delete a task")
@app_commands.describe(task_id="The ID of the task to delete")
async def delete_command(interaction: discord.Interaction, task_id: int):
    """Delete a task."""
    await delete_task(task_id)
    await interaction.response.send_message(
        f"Task `{task_id}` deleted."
    )


# ============================================================
# Bot Events
# ============================================================

@client.event
async def on_ready():
    """Called when the bot is ready."""
    await init_database()
    await tree.sync()
    print(f"Dashboard Bot logged in as {client.user}")
    print(f"Connected to {len(client.guilds)} guild(s)")


# ============================================================
# Main
# ============================================================

if __name__ == "__main__":
    if not DISCORD_TOKEN:
        print("ERROR: DISCORD_BOT_TOKEN environment variable not set")
        exit(1)

    client.run(DISCORD_TOKEN)
