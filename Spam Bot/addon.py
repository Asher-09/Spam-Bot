import discord
import asyncio

intents = discord.Intents.default()

async def check_token(token):
    client = discord.Client(intents=intents)

    try:
        @client.event
        async def on_ready():
            print(f"✅ Valid token: {token} — Logged in as {client.user}")
            # Save valid token to a file
            with open("valid_tokens.txt", "a") as vf:
                vf.write(token + "\n")
            await client.close()

        await client.start(token)
    except discord.LoginFailure:
        print(f"❌ Invalid token: {token}")
    except Exception as e:
        print(f"⚠️ Error with token {token}: {e}")
    finally:
        if not client.is_closed():
            await client.close()

def main():
    # Clear the file if it exists already
    open("valid_tokens.txt", "w").close()

    with open('tokens.txt', 'r') as f:
        tokens = [line.strip() for line in f if line.strip()]

    for token in tokens:
        asyncio.run(check_token(token))

if __name__ == "__main__":
    main()
