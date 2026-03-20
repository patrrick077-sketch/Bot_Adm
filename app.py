import asyncio
import os
import threading
from flask import Flask, request, render_template_string
from telethon import TelegramClient
from telethon.tl.types import ChatAdminRights
from telethon.tl.functions.channels import EditAdminRequest
from telethon.errors import SessionPasswordNeededError, FloodWaitError, UserNotParticipantError

# --- CONFIGURATION ---
api_id = 29464258
api_hash = '5ca1ad6d6e0aa144a6e407e0af64510f'
phone_number = '+959678096184'
session_name = 'user_admin_session'

# The specific bot the user must add
REQUIRED_ADMIN_BOT = '@Localhost8800'
BOTS_FILE = 'us_only.txt'

app = Flask(__name__)

# --- LOCK for Thread Safety (Fixes Database Locked Error) ---
telethon_lock = threading.Lock()

# --- PROFESSIONAL HACKER UI TEMPLATE ---
TEMPLATE = """
<!doctype html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <title>SYSTEM_ACCESS // ADMIN_PANEL</title>
    <style>
        :root {
            --primary-glow: #00ff41;
            --secondary-glow: #0088cc;
            --bg-color: #0d0d0d;
            --panel-bg: #1a1a1a;
            --text-dim: #a0a0a0;
        }
        
        body { 
            font-family: 'Courier New', Courier, monospace; 
            background-color: var(--bg-color); 
            color: #e0e0e0; 
            margin: 0; 
            padding: 20px; 
            min-height: 100vh;
            background-image: 
                linear-gradient(rgba(0, 255, 65, 0.03) 1px, transparent 1px),
                linear-gradient(90deg, rgba(0, 255, 65, 0.03) 1px, transparent 1px);
            background-size: 20px 20px;
        }
        
        .container { max-width: 800px; margin: 0 auto; }
        
        .header {
            text-align: center;
            margin-bottom: 40px;
            border-bottom: 2px solid var(--primary-glow);
            padding-bottom: 20px;
        }
        
        h1 { 
            color: var(--primary-glow); 
            text-transform: uppercase; 
            letter-spacing: 4px; 
            font-size: 2em;
            text-shadow: 0 0 10px rgba(0, 255, 65, 0.5);
            margin-bottom: 10px;
        }
        
        .status-bar {
            background: var(--panel-bg);
            border: 1px solid #333;
            padding: 15px;
            margin-bottom: 20px;
            display: flex;
            justify-content: space-between;
            font-size: 0.9em;
            color: var(--primary-glow);
        }

        .card { 
            background: var(--panel-bg); 
            padding: 25px; 
            border-radius: 4px; 
            border: 1px solid #333;
            box-shadow: 0 0 15px rgba(0, 0, 0, 0.8);
            margin-bottom: 20px;
        }
        
        .warning-box {
            background: rgba(255, 0, 0, 0.1);
            border-left: 4px solid #ff4d4d;
            padding: 15px;
            margin-bottom: 20px;
            font-size: 0.9em;
        }

        .warning-box strong { color: #ff4d4d; }

        label { 
            display: block; 
            margin-bottom: 8px; 
            color: var(--primary-glow); 
            font-weight: bold;
            text-transform: uppercase;
            font-size: 0.8em;
        }
        
        input[type="text"] { 
            width: 100%; 
            padding: 15px; 
            background: #0d0d0d; 
            border: 1px solid #444; 
            color: #fff; 
            font-family: inherit; 
            font-size: 1em; 
            box-sizing: border-box;
            transition: border-color 0.3s;
        }
        
        input[type="text"]:focus {
            outline: none;
            border-color: var(--primary-glow);
            box-shadow: 0 0 8px rgba(0, 255, 65, 0.2);
        }
        
        .btn { 
            background: linear-gradient(45deg, #0088cc, #00ff41); 
            color: #000; 
            padding: 15px 30px; 
            border: none; 
            font-weight: bold; 
            cursor: pointer; 
            font-family: inherit; 
            text-transform: uppercase; 
            letter-spacing: 2px;
            width: 100%;
            font-size: 1em;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        
        .btn:hover { 
            transform: translateY(-2px); 
            box-shadow: 0 5px 15px rgba(0, 255, 65, 0.3);
        }

        .btn:disabled {
            background: #555;
            cursor: not-allowed;
            transform: none;
            box-shadow: none;
        }
        
        .log-container {
            background: #000;
            border: 1px solid #333;
            padding: 20px;
            height: 400px;
            overflow-y: auto;
            font-size: 0.85em;
            white-space: pre-wrap;
            font-family: 'Courier New', Courier, monospace;
        }

        .log-success { color: var(--primary-glow); }
        .log-error { color: #ff4d4d; }
        .log-warn { color: #ffc107; }
        .log-info { color: #17a2b8; }

        .count-badge {
            background: var(--primary-glow);
            color: #000;
            padding: 2px 8px;
            border-radius: 10px;
            font-weight: bold;
            margin-left: 10px;
        }

        .grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
        
        @media (max-width: 600px) {
            .grid-2 { grid-template-columns: 1fr; }
            h1 { font-size: 1.5em; }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>// TELEGRAM INJECTOR</h1>
            <div style="color: #666; font-size: 0.8em;">SECURE CONNECTION ESTABLISHED</div>
        </div>

        <div class="status-bar">
            <span>USER: {{ phone }}</span>
            <span>FILE: {{ bots_file }} [{{ bot_count }} USERS LOADED]</span>
        </div>

        {% if error %}
        <div class="card" style="border-color: #ff4d4d;">
            <h3 style="color: #ff4d4d; margin-top:0;">CRITICAL ERROR</h3>
            <div class="log-container">{{ error }}</div>
            <a href="/" style="color:#ccc; text-decoration:none; display:block; margin-top:20px;">[ RETRY ]</a>
        </div>
        {% else %}
            {% if result_log %}
            <div class="card">
                <h3 style="color: var(--primary-glow); margin-top:0; border-bottom:1px solid #333; padding-bottom:10px;">
                    EXECUTION LOG
                </h3>
                <div class="log-container">{{ result_log }}</div>
                <a href="/" style="color: var(--primary-glow); text-decoration:none; display:block; margin-top:20px; text-align:center;">
                    [ NEW OPERATION ]
                </a>
            </div>
            {% else %}
            <div class="card">
                <div class="warning-box">
                    <strong>[!] PROTOCOL NOTICE:</strong><br>
                    You MUST set the account <strong>{{ required_bot }}</strong> as an admin in your channel with <strong>"Add Admins"</strong> permission enabled before proceeding. The system will verify this.
                </div>
                
                <form method="post">
                    <label>TARGET CHANNEL LINK</label>
                    <input type="text" name="channel_link" placeholder="e.g., @my_channel or https://t.me/my_channel" required>
                    <br><br>
                    <button type="submit" class="btn">INITIATE PROMOTION</button>
                </form>
            </div>
            {% endif %}
        {% endif %}
        
        <div style="text-align: center; color: #333; margin-top: 20px; font-size: 0.8em;">
            SYSTEM v2.0 // SECURE SHELL
        </div>
    </div>
</body>
</html>
"""

async def telegram_worker(channel_link):
    """Handles the async logic safely."""
    logs = []
    client = TelegramClient(session_name, api_id, api_hash)
    
    logs.append(f"> Connecting to Telegram Network...")
    await client.connect()
    
    if not await client.is_user_authorized():
        logs.append("> ERROR: Session not authorized.")
        logs.append("> Please authorize the session via the terminal/console first.")
        await client.disconnect()
        return "\n".join(logs)

    logs.append("> Authorization verified.\n")

    try:
        # 1. Resolve Entities
        logs.append(f"> Resolving target channel: {channel_link}")
        channel = await client.get_entity(channel_link)
        
        logs.append(f"> Resolving controller bot: {REQUIRED_ADMIN_BOT}")
        bot_admin = await client.get_entity(REQUIRED_ADMIN_BOT)
        
        # 2. Check if the required bot is already admin with ADD_ADMINS rights
        logs.append(f"> Verifying permissions for {REQUIRED_ADMIN_BOT}...")
        
        # We try to edit their rights to ensure they have add_admins=True
        # If they aren't admin at all, this usually fails, catching the error allows us to instruct the user.
        required_rights = ChatAdminRights(
            add_admins=True,
            invite_users=True,
            change_info=True,
            post_messages=True,
            edit_messages=True,
            delete_messages=True,
            ban_users=True,
            manage_call=True
        )
        
        try:
            await client(EditAdminRequest(
                channel=channel,
                user_id=bot_admin,
                admin_rights=required_rights,
                rank="Controller"
            ))
            logs.append(f"> SUCCESS: {REQUIRED_ADMIN_BOT} promoted to Admin with 'Add Admins' rights.")
        except UserNotParticipantError:
            logs.append(f"> ERROR: {REQUIRED_ADMIN_BOT} is NOT an admin in the channel.")
            logs.append(f("> ACTION REQUIRED: Go to Channel Settings > Administrators > Add Admin"))
            logs.append(f("> Add {REQUIRED_ADMIN_BOT} and ENABLE 'Add New Admins' permission.")
            await client.disconnect()
            return "\n".join(logs)
        except Exception as e:
            if "CHAT_ADMIN_REQUIRED" in str(e) or "USER_CREATOR" in str(e):
                # This can happen if the bot is creator, or we lack rights to promote it
                logs.append(f"> WARNING: Could not modify permissions for {REQUIRED_ADMIN_BOT}.")
                logs.append(f("> Ensure {REQUIRED_ADMIN_BOT} is admin with ADD_ADMINS right.")
            else:
                logs.append(f"> ERROR: {str(e)}")
                await client.disconnect()
                return "\n".join(logs)

        # 3. Load Bots from File
        if not os.path.exists(BOTS_FILE):
            logs.append(f"> FILE ERROR: {BOTS_FILE} not found.")
            await client.disconnect()
            return "\n".join(logs)
            
        with open(BOTS_FILE, 'r') as f:
            bots = [line.strip() for line in f if line.strip()]
            
        logs.append(f"> Loaded {len(bots)} targets from database.\n")
        logs.append("="*40)
        logs.append("      STARTING MASS PROMOTION")
        logs.append("="*40)

        # 4. Promote Bots
        for bot_username in bots:
            try:
                logs.append(f"> Processing: {bot_username}")
                target_bot = await client.get_entity(bot_username)
                
                bot_rights = ChatAdminRights(
                    post_messages=True,
                    edit_messages=True,
                    delete_messages=True,
                    invite_users=True,
                    change_info=True,
                    add_admins=False, # We keep this false for target bots
                    manage_call=True
                )
                
                await client(EditAdminRequest(
                    channel=channel,
                    user_id=target_bot,
                    admin_rights=bot_rights,
                    rank="Bot Admin"
                ))
                logs.append(f"  [OK] Successfully promoted.")
                
            except FloodWaitError as e:
                logs.append(f"  [HALT] FloodWait detected. Waiting {e.seconds}s...")
                # In a web environment, we usually can't wait that long, so we break or warn
                break
            except Exception as e:
                logs.append(f"  [FAIL] {str(e)}")

    except Exception as e:
        logs.append(f"> CRITICAL ERROR: {str(e)}")
    finally:
        await client.disconnect()
        
    return "\n".join(logs)

@app.route('/', methods=['GET', 'POST'])
def index():
    error = None
    result_log = None
    
    # Count bots in file
    count = 0
    if os.path.exists(BOTS_FILE):
        with open(BOTS_FILE, 'r') as f:
            count = len([line for line in f if line.strip()])

    if request.method == 'POST':
        channel_link = request.form.get('channel_link')
        if not channel_link:
            error = "Channel link cannot be empty."
        else:
            # --- THREAD SAFE EXECUTION ---
            # This prevents the 'database is locked' error by ensuring
            # the async loop runs safely within the Flask thread.
            try:
                with telethon_lock:
                    # Create new loop for this specific request
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    result_log = loop.run_until_complete(telegram_worker(channel_link))
                    loop.close()
            except Exception as e:
                error = f"Server Execution Error: {str(e)}"

    return render_template_string(
        TEMPLATE, 
        phone=phone_number, 
        bot_count=count, 
        bots_file=BOTS_FILE,
        required_bot=REQUIRED_ADMIN_BOT,
        result_log=result_log,
        error=error
    )

if __name__ == '__main__':
    # Create dummy file for testing
    if not os.path.exists(BOTS_FILE):
        with open(BOTS_FILE, 'w') as f:
            f.write("@BotFather\n@Combot\n@ControllerBot")
            
    print("Server running on http://127.0.0.1:5000")
    app.run(debug=True, port=5000)
