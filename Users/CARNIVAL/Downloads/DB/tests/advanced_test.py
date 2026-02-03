from kvstore.client import KVClient

# Initialize connection
client = KVClient("127.0.0.1", 9000)

print("--- Testing Full Text Search ---")
# Indexing a document
client.set("doc", "hello world")
# Searching for a term
results = client.search_text("hello")
print(f"Search results for 'hello': {results}")

print("\n--- Testing Vector Search ---")
# Adding a vector
client.add_vector("v1", [1.0, 0.0])
# Searching by vector
vector_results = client.vector_search([1.0, 0.0], top_k=1)
print(f"Vector search results: {vector_results}")