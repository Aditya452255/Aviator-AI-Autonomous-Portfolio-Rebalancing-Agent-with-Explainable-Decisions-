"""Batch Processor slicing items into parallel chunks for batch execution."""

from typing import Any, Callable, List, TypeVar

T = TypeVar("T")
R = TypeVar("R")


class BatchProcessor:
    """Enterprise Batch Processor."""

    def process_in_batches(self, items: List[T], batch_size: int, func: Callable[[List[T]], List[R]]) -> List[R]:
        """Process list of items in fixed-size batch chunks.

        Args:
            items: Target item list.
            batch_size: Size per batch chunk.
            func: Function accepting batch chunk list.

        Returns:
            Flattened list of output results.
        """
        results: List[R] = []
        for i in range(0, len(items), batch_size):
            chunk = items[i : i + batch_size]
            res = func(chunk)
            results.extend(res)
        return results
