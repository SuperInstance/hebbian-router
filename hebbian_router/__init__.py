"""Hebbian Router — Self-optimizing routes between services and agents.

Routes grow stronger with use and successful outcomes. Weak routes are pruned.
Chaos (stochastic exploration) prevents local optima. Channels form between
co-activated nodes — neurons that fire together wire together.
"""

__version__ = "0.1.0"

from hebbian_router.core import HebbianChannel, Route, RoutingLayer

__all__ = ["RoutingLayer", "Route", "HebbianChannel", "__version__"]
