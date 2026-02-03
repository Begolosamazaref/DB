# KVStore - Persistent Distributed Key-Value Store

A high-performance, persistent key-value store with distributed capabilities, advanced indexing, and replication support.

## Features

- **Persistent Storage**: Data persists across server restarts using Write-Ahead Logs (WAL)
- **Distributed Architecture**: Multi-node support with replication and failover capabilities
- **Advanced Indexing**:
  - Secondary indexing for efficient lookups
  - Inverted index for full-text search
  - Vector indexing for similarity searches
- **Replication**: Master-slave replication with configurable failover
- **Bulk Operations**: Efficient batch set/get operations
- **CLI Interface**: Command-line tool for server management

## Installation

```bash
pip install -e .
```

## Quick Start

### Start the Server

```bash
kvstore-server
```

### Using the Client

```python
from kvstore import KVClient

# Connect to server
client = KVClient(host='localhost', port=5000)

# Set a key-value pair
client.set('user:1', {'name': 'John', 'age': 30})

# Get a value
user = client.get('user:1')

# Delete a key
client.delete('user:1')
```

## Project Structure

```
src/kvstore/
├── engine.py         # Core KV engine with indexing
├── storage.py        # Persistent storage with WAL
├── server.py         # Network server
├── client.py         # Client library
├── replication.py    # Replication and failover
├── indexing.py       # Secondary, inverted, and vector indexes
├── protocol.py       # Communication protocol
├── config.py         # Configuration management
└── cli.py            # Command-line interface

tests/                # Comprehensive test suite
scripts/              # Benchmarking and testing utilities
data/                 # Sample data
```

## Testing

Run the test suite:

```bash
pytest tests/
```

## Configuration

Configuration can be set via environment variables or config files. See `src/kvstore/config.py` for available options.

## Performance

See `scripts/benchmark_write.py` for performance benchmarks and testing utilities.

## License

MIT

## Repository

[GitHub Repository](https://github.com/Begolosamazaref/DB)
