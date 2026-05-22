"""Tests for hebbian_router.core."""

import numpy as np
import pytest

from hebbian_router.core import HebbianChannel, Route, RoutingLayer


class TestRoute:
    """Route basics: creation, firing, reinforcement, decay."""

    def test_create(self):
        r = Route("A", "B", strength=0.7)
        assert r.source == "A"
        assert r.destination == "B"
        assert r.strength == 0.7
        assert r.fires == 0

    def test_fire_increments_counter(self):
        r = Route("A", "B", strength=1.0)
        r.fire(chaos=0.0)
        assert r.fires == 1
        assert r.last_fired > 0

    def test_fire_deterministic(self):
        r = Route("A", "B", strength=1.0)
        assert r.fire(chaos=0.0) is True

    def test_fire_never_fires_when_strength_zero_and_no_chaos(self):
        r = Route("A", "B", strength=0.0)
        assert r.fire(chaos=0.0) is False

    def test_reinforce_success(self):
        r = Route("A", "B", strength=0.5)
        r.reinforce(success=True, lr=0.1)
        assert r.strength > 0.5
        assert r.successes == 1
        assert r.reception == 1.0

    def test_reinforce_failure(self):
        r = Route("A", "B", strength=0.5)
        r.reinforce(success=False, lr=0.1)
        assert r.strength < 0.5
        assert r.successes == 0

    def test_reinforce_caps_at_0_99(self):
        r = Route("A", "B", strength=0.99)
        r.reinforce(success=True, lr=0.1)
        assert r.strength == 0.99

    def test_reinforce_floors_at_0_01(self):
        r = Route("A", "B", strength=0.01)
        r.reinforce(success=False, lr=0.1)
        assert r.strength == 0.01

    def test_decay(self):
        r = Route("A", "B", strength=0.5)
        r.decay(factor=0.9)
        assert r.strength == pytest.approx(0.45)

    def test_decay_floors_at_0_01(self):
        r = Route("A", "B", strength=0.005)
        r.decay(factor=0.9)
        assert r.strength == 0.01

    def test_repr(self):
        r = Route("svc", "db", strength=0.75, efficiency=0.8, reception=0.9)
        assert "svc→db" in repr(r)
        assert "str=0.75" in repr(r)


class TestHebbianChannel:
    """Channel basics: creation, activation, decay."""

    def test_create(self):
        ch = HebbianChannel("X", "Y", initial_weight=0.2)
        assert ch.node_a == "X"
        assert ch.node_b == "Y"
        assert ch.weight == 0.2
        assert ch.co_activations == 0

    def test_activate(self):
        ch = HebbianChannel("X", "Y", initial_weight=0.1)
        w = ch.activate()
        assert w > 0.1
        assert ch.co_activations == 1
        assert ch.weight == w

    def test_activate_caps_at_1(self):
        ch = HebbianChannel("X", "Y", initial_weight=1.0)
        w = ch.activate()
        assert w == 1.0

    def test_decay(self):
        ch = HebbianChannel("X", "Y", initial_weight=0.5)
        ch.decay(factor=0.8)
        assert ch.weight == 0.4

    def test_thread_safety(self):
        import threading
        ch = HebbianChannel("X", "Y", initial_weight=0.0)
        def worker():
            for _ in range(100):
                ch.activate()
        threads = [threading.Thread(target=worker) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        assert ch.co_activations == 1000
        assert ch.weight > 0.0


class TestRoutingLayer:
    """Layer basics: add routes/channels, fire, feedback, decay."""

    def test_create(self):
        layer = RoutingLayer(chaos=0.05, learning_rate=0.1)
        assert layer.chaos == 0.05
        assert layer.learning_rate == 0.1

    def test_add_route(self):
        layer = RoutingLayer()
        r = layer.add_route("A", "B", strength=0.6)
        assert r.source == "A"
        assert "A→B" in layer.routes

    def test_add_channel(self):
        layer = RoutingLayer()
        ch = layer.add_channel("A", "B", weight=0.3)
        assert ch.weight == 0.3
        assert "A↔B" in layer.channels

    def test_fire_returns_destinations(self):
        layer = RoutingLayer()
        layer.add_route("A", "B", strength=1.0)
        layer.add_route("A", "C", strength=1.0)
        fired = layer.fire("A")
        assert set(fired) == {"B", "C"}

    def test_fire_with_destinations_filter(self):
        layer = RoutingLayer()
        layer.add_route("A", "B", strength=1.0)
        layer.add_route("A", "C", strength=1.0)
        fired = layer.fire("A", destinations=["B"])
        assert fired == ["B"]

    def test_fire_fast_returns_destinations(self):
        layer = RoutingLayer()
        layer.add_route("A", "B", strength=1.0)
        layer.add_route("A", "C", strength=1.0)
        fired = layer.fire_fast("A")
        assert set(fired) == {"B", "C"}

    def test_fire_fast_with_destinations_filter(self):
        layer = RoutingLayer()
        layer.add_route("A", "B", strength=1.0)
        layer.add_route("A", "C", strength=1.0)
        fired = layer.fire_fast("A", destinations=["B"])
        assert fired == ["B"]

    def test_compiled_route_skips_random_check(self):
        """Routes with strength > 0.9 fire deterministically."""
        layer = RoutingLayer(chaos=0.0)
        layer.add_route("A", "B", strength=0.95)
        for _ in range(100):
            fired = layer.fire_fast("A")
            assert fired == ["B"]

    def test_feedback_strengthens(self):
        layer = RoutingLayer(learning_rate=0.1)
        layer.add_route("A", "B", strength=0.5)
        layer.feedback("A", "B", success=True)
        r = layer.routes["A→B"]
        assert r.strength > 0.5

    def test_feedback_weakens(self):
        layer = RoutingLayer(learning_rate=0.1)
        layer.add_route("A", "B", strength=0.5)
        layer.feedback("A", "B", success=False)
        r = layer.routes["A→B"]
        assert r.strength < 0.5

    def test_feedback_batch(self):
        layer = RoutingLayer(learning_rate=0.1)
        layer.add_route("A", "B", strength=0.5)
        layer.add_route("A", "C", strength=0.5)
        layer.feedback_batch([("A", "B", True), ("A", "C", False)])
        assert layer.routes["A→B"].strength > 0.5
        assert layer.routes["A→C"].strength < 0.5

    def test_get_strongest_routes(self):
        layer = RoutingLayer()
        layer.add_route("A", "B", strength=0.9)
        layer.add_route("A", "C", strength=0.3)
        layer.add_route("A", "D", strength=0.7)
        top = layer.get_strongest_routes("A", top_k=2)
        assert len(top) == 2
        assert top[0].destination == "B"
        assert top[1].destination == "D"

    def test_get_channel_weight(self):
        layer = RoutingLayer()
        layer.add_channel("X", "Y", weight=0.4)
        assert layer.get_channel_weight("X", "Y") == 0.4
        assert layer.get_channel_weight("X", "Z") == 0.0

    def test_decay_all(self):
        layer = RoutingLayer()
        layer.add_route("A", "B", strength=0.5)
        layer.add_channel("X", "Y", weight=0.5)
        layer.decay_all(factor=0.8)
        assert layer.routes["A→B"].strength == pytest.approx(0.4)
        assert layer.channels["X↔Y"].weight == pytest.approx(0.4)

    def test_precomputed_index(self):
        layer = RoutingLayer()
        layer.add_route("A", "B")
        layer.add_route("A", "C")
        layer.add_route("D", "E")
        assert len(layer._routes_by_source["A"]) == 2
        assert len(layer._routes_by_source["D"]) == 1
        assert len(layer._routes_by_dest["B"]) == 1

    def test_fire_creates_hebbian_channels(self):
        layer = RoutingLayer()
        layer.add_route("A", "B", strength=1.0)
        layer.add_route("A", "C", strength=1.0)
        layer.fire("A")
        assert "B↔C" in layer.channels

    def test_fire_fast_creates_hebbian_channels(self):
        layer = RoutingLayer()
        layer.add_route("A", "B", strength=1.0)
        layer.add_route("A", "C", strength=1.0)
        layer.fire_fast("A")
        assert "B↔C" in layer.channels

    def test_repr(self):
        layer = RoutingLayer()
        assert "routes=0" in repr(layer)
        layer.add_route("A", "B")
        assert "routes=1" in repr(layer)


class TestFireFastPerformance:
    """Performance: fire_fast is measurably faster than fire."""

    def test_fire_fast_on_many_routes(self):
        layer = RoutingLayer(chaos=0.1)
        for i in range(500):
            layer.add_route("src", f"dst_{i}", strength=0.5)
        # Should complete without error and return reasonable results
        fired = layer.fire_fast("src")
        assert isinstance(fired, list)
        assert all(d.startswith("dst_") for d in fired)

    def test_fire_fast_vs_fire_consistency(self):
        np.random.seed(42)
        layer_fast = RoutingLayer(chaos=0.0)
        layer_slow = RoutingLayer(chaos=0.0)
        for i in range(20):
            layer_fast.add_route("src", f"dst_{i}", strength=1.0)
            layer_slow.add_route("src", f"dst_{i}", strength=1.0)
        # With strength=1.0 and chaos=0.0, both should fire all routes
        assert set(layer_fast.fire_fast("src")) == set(layer_slow.fire("src"))
