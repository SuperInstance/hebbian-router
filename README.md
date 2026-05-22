# Hebbian Router 🦀

Self-optimizing routes between services and agents. Routes grow stronger with use and successful outcomes. Weak routes fade. Chaos keeps exploration alive.

> *Neurons that fire together, wire together. The water carves channels.*

## Quickstart

```bash
pip install hebbian-router
```

```python
from hebbian_router import RoutingLayer

# Create a routing layer
layer = RoutingLayer(chaos=0.1, learning_rate=0.05)

# Register routes between your services
layer.add_route("microservice-a", "database", strength=0.5)
layer.add_route("microservice-a", "cache", strength=0.5)
layer.add_route("microservice-a", "queue", strength=0.3)

# Fire routes — strong ones fire more often
fired = layer.fire_fast("microservice-a")
print(fired)  # ['database', 'cache']  (or stochastic exploration)

# Provide feedback — success strengthens, failure weakens
layer.feedback("microservice-a", "cache", success=True)   # route strengthens
layer.feedback("microservice-a", "database", success=False)  # route weakens

# After 10 successes, cache route is "compiled" — fires deterministically
# (strength > 0.9 skips random checks entirely)
```

## What Makes This Killer

**Self-optimizing load balancer without a control plane.** Your microservices (or agents, or functions) call each other through routes that learn. No manual tuning, no static weights. A fast path that becomes *faster* the more it's used, while slow paths get explored probabilistically via chaos.

The 60× vectorized `fire_fast()` path with precomputed indexes means this scales to thousands of routes. Compiled routes (strength > 0.9) skip all randomness. Hebbian channels auto-form between co-activated nodes, discovering latent clusters in your topology.

## API

### `RoutingLayer(chaos=0.1, learning_rate=0.05)`

Manages routes and Hebbian channels.

- `add_route(source, destination, strength=0.5)` → `Route`
- `add_channel(node_a, node_b, weight=0.1)` → `HebbianChannel`
- `fire(source, destinations=None)` → `list[str]` — scalar path, simple
- `fire_fast(source, destinations=None, chaos=None)` → `list[str]` — vectorized, 60× faster
- `feedback(source, destination, success)` — strengthen or weaken a route
- `feedback_batch(updates)` — batch feedback: `[(src, dst, success), ...]`
- `get_strongest_routes(source, top_k=5)` → `list[Route]`
- `get_channel_weight(a, b)` → `float`
- `decay_all(factor=0.999)` — time-based decay for all routes and channels

### `Route`

A pathway between nodes.

| Attribute | Description |
|-----------|-------------|
| `source` | Origin node |
| `destination` | Target node |
| `strength` | Firing probability (0.01–0.99) |
| `efficiency` | Latency/throughput score |
| `reception` | Success ratio (successes / fires) |
| `fires` | Total firing attempts |
| `successes` | Successful outcomes |

Methods: `fire(chaos)`, `reinforce(success, lr)`, `decay(factor)`

### `HebbianChannel`

Bidirectional channel between two nodes that strengthens when both fire together.

Methods: `activate()`, `decay(factor)`

## Performance

| Operation | `fire()` | `fire_fast()` |
|-----------|----------|---------------|
| 100 routes | ~2 ms | ~0.03 ms |
| 1,000 routes | ~20 ms | ~0.3 ms |
| 10,000 routes | ~200 ms | ~3 ms |

Compiled routes (strength > 0.9) bypass random checks entirely. Hebbian activation is limited to top-k pairs, not O(n²).

## Install from Source

```bash
git clone https://github.com/SuperInstance/hebbian-router.git
cd hebbian-router
pip install -e ".[dev]"
pytest
```

## License

MIT
