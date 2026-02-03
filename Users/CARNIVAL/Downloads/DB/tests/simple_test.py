from kvstore.client import KVClient

# Initialize the client connecting to localhost:9000
client = KVClient("127.0.0.1", 9000)

# Set a key
print("Setting 'hello' to 'world'...")
client.set("hello", "world")

# Get the key back
value = client.get("hello")
print(f"Get 'hello': {value}")