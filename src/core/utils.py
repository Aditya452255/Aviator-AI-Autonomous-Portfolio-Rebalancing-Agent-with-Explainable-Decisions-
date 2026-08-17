"""Utility functions for mathematical operations, random seeds, and performance metrics."""

import contextlib
import random
import time
from typing import Any, Dict, Generator, List
import numpy as np
from src.core.logger import get_logger

logger = get_logger(__name__)


def set_random_seed(seed: int) -> None:
    """Set global random seed across python random and numpy for reproducibility.

    Args:
        seed: Integer seed value.
    """
    random.seed(seed)
    np.random.seed(seed)
    logger.debug(f"Global random seed set to: {seed}")


@contextlib.contextmanager
def Timer(operation_name: str) -> Generator[Dict[str, Any], None, None]:
    """Context manager to measure and log execution duration of code blocks.

    Args:
        operation_name: Human readable label for the operation.

    Yields:
        Dictionary containing elapsed execution metrics.
    """
    start_time = time.perf_counter()
    metrics: Dict[str, Any] = {"operation": operation_name, "start_time": start_time}
    logger.info(f"Starting operation: '{operation_name}'...")
    try:
        yield metrics
    finally:
        elapsed = time.perf_counter() - start_time
        metrics["elapsed_seconds"] = round(elapsed, 4)
        logger.info(f"Completed operation: '{operation_name}' in {elapsed:.4f}s")


def normalize_weights(weights: Dict[Any, float]) -> Dict[Any, float]:
    """Normalize a dictionary of weights so they sum precisely to 1.0.

    Args:
        weights: Dictionary mapping keys to numerical weights.

    Returns:
        New dictionary with normalized weights.
    """
    total = sum(weights.values())
    if total <= 0:
        raise ValueError("Cannot normalize weights with zero or negative total sum.")
    return {k: v / total for k, v in weights.items()}


def ensure_positive_definite(matrix: np.ndarray, jitter: float = 1e-6) -> np.ndarray:
    """Ensure a matrix is symmetric positive semi-definite for Cholesky decomposition.

    Args:
        matrix: Input square 2D numpy array.
        jitter: Small positive diagonal offset added if eigenvalues are non-positive.

    Returns:
        Symmetric positive-definite covariance matrix.
    """
    sym_matrix = (matrix + matrix.T) / 2.0
    min_eig = np.min(np.real(np.linalg.eigvals(sym_matrix)))
    if min_eig < 0:
        sym_matrix += (-min_eig + jitter) * np.eye(sym_matrix.shape[0])
    return sym_matrix
