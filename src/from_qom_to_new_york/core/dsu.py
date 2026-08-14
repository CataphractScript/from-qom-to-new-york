"""Disjoint Set Union (DSU) / Union-Find data structure.

Implements two crucial optimizations:
1. Path Compression: Flattens the tree during `find` so every traversed node points directly to the root.
2. Union by Rank: Attaches the smaller depth tree under the root of the deeper tree.

Theoretical Complexity:
Any sequence of m operations on n elements runs in O(m * alpha(n)) time,
where alpha(n) is the extremely slowly growing Inverse Ackermann function.
For all practical values of n (n <= 10^80), alpha(n) <= 4, making each operation effectively O(1) amortized.
"""

from __future__ import annotations

from typing import Dict, Generic, Iterable, List, Optional, Set, TypeVar

T = TypeVar("T")


class DisjointSetUnion(Generic[T]):
    """Optimized Disjoint-Set / Union-Find data structure with Path Compression and Union by Rank.

    Attributes:
        _parent: Maps each element to its parent representative.
        _rank: Approximate tree height rooted at the element.
        _size: Number of elements in the component rooted at the element.
        _num_components: Total number of disjoint connected components.
    """

    def __init__(self, elements: Optional[Iterable[T]] = None) -> None:
        """Initialize the DSU with an optional collection of elements.

        Args:
            elements: Initial universe of items. Each element starts in its own singleton set.
        """
        self._parent: Dict[T, T] = {}
        self._rank: Dict[T, int] = {}
        self._size: Dict[T, int] = {}
        self._num_components: int = 0

        if elements is not None:
            for elem in elements:
                self.make_set(elem)

    def make_set(self, x: T) -> None:
        """Create a new set containing only element `x` if not already present.

        Complexity: O(1) time and space.
        """
        if x not in self._parent:
            self._parent[x] = x
            self._rank[x] = 0
            self._size[x] = 1
            self._num_components += 1

    def find(self, x: T) -> T:
        """Find the canonical representative of the set containing `x`.

        Applies Path Compression: Every node on the path to the root is updated
        to point directly to the root, speeding up subsequent queries.

        Args:
            x: The element whose representative is sought.

        Returns:
            The canonical root representative of `x`'s partition.

        Complexity: Amortized O(alpha(N)).
        """
        if x not in self._parent:
            self.make_set(x)
            return x

        # Iterative two-pass path compression (avoids deep recursion limits)
        root = x
        while root != self._parent[root]:
            root = self._parent[root]

        curr = x
        while curr != root:
            nxt = self._parent[curr]
            self._parent[curr] = root
            curr = nxt

        return root

    def union(self, x: T, y: T) -> bool:
        """Merge the sets containing `x` and `y`.

        Applies Union by Rank: Attaches the shallower tree to the root of the deeper tree.
        If ranks are equal, one is chosen arbitrarily as parent and its rank is incremented.

        Args:
            x: First element.
            y: Second element.

        Returns:
            True if `x` and `y` were in different sets and got merged; False if already in the same set.

        Complexity: Amortized O(alpha(N)).
        """
        root_x = self.find(x)
        root_y = self.find(y)

        if root_x == root_y:
            return False  # Already connected, adding this edge would create a cycle

        # Union by rank optimization
        if self._rank[root_x] < self._rank[root_y]:
            self._parent[root_x] = root_y
            self._size[root_y] += self._size[root_x]
        elif self._rank[root_x] > self._rank[root_y]:
            self._parent[root_y] = root_x
            self._size[root_x] += self._size[root_y]
        else:
            self._parent[root_y] = root_x
            self._rank[root_x] += 1
            self._size[root_x] += self._size[root_y]

        self._num_components -= 1
        return True

    def connected(self, x: T, y: T) -> bool:
        """Check whether `x` and `y` belong to the same connected component.

        Args:
            x: First element.
            y: Second element.

        Returns:
            True if representative roots match, False otherwise.
        """
        return self.find(x) == self.find(y)

    def component_size(self, x: T) -> int:
        """Get the number of elements in the component containing `x`."""
        return self._size[self.find(x)]

    @property
    def num_components(self) -> int:
        """Return the current number of disjoint components."""
        return self._num_components

    def get_components(self) -> Dict[T, Set[T]]:
        """Return all disjoint sets grouped by their root representative."""
        components: Dict[T, Set[T]] = {}
        for elem in self._parent:
            root = self.find(elem)
            components.setdefault(root, set()).add(elem)
        return components

    def __len__(self) -> int:
        """Total number of tracked elements."""
        return len(self._parent)

    def __repr__(self) -> str:
        return f"DisjointSetUnion(elements={len(self._parent)}, components={self._num_components})"
