"""Parallel Executor using ThreadPoolExecutor for concurrent tasks."""

from concurrent.futures import ThreadPoolExecutor
from typing import Any, Callable, List


class ParallelExecutor:
    """Enterprise Parallel Executor managing worker thread pools."""

    def __init__(self, max_workers: int = 4) -> None:
        self.max_workers = max_workers

    def map_parallel(self, func: Callable[[Any], Any], items: List[Any]) -> List[Any]:
        """Map callable across items concurrently using worker thread pool.

        Args:
            func: Target callable.
            items: Item list.

        Returns:
            List of results.
        """
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            return list(executor.map(func, items))
