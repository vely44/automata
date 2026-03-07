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
from datetime import datetime

import discord
from discord import app_commands
import aiosqlite

# Configuration from environment
DISCORD_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
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
# Config Functions
# ============================================================

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

@tree.command(name="status", description="Show dashboard status and task summary")
async def status_command(interaction: discord.Interaction):
    """Display dashboard status and task summary."""
    await interaction.response.defer()

    # Read Nanobot config (for informational display)
    nb_config = read_nanobot_config()

    # Build embed
    embed = discord.Embed(
        title="Dashboard Status",
        color=discord.Color.blue(),
        timestamp=datetime.now()
    )

    # Nanobot config info
    if "error" not in nb_config:
        provider = nb_config.get("provider", "unknown")
        model = nb_config.get("model", "unknown")
        embed.add_field(
            name="Nanobot Config",
            value=f"Provider: `{provider}`\nModel: `{model}`",
            inline=False
        )
    else:
        embed.add_field(
            name="Nanobot Config",
            value=f"Error: {nb_config['error']}",
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
