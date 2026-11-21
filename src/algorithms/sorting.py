"""
Sorting algorithms and parcel prioritization routines.
Implements Merge Sort, Quick Sort, multi-criteria parcel ranking, and runtime benchmarks.
"""

import time
import random
from typing import List, Callable, Any, Tuple, Dict
from ..models import Parcel


def _default_comparator(a: Any, b: Any) -> int:
    """Returns -1 if a < b, 0 if a == b, 1 if a > b."""
    if a < b:
        return -1
    elif a > b:
        return 1
    return 0


def merge_sort(items: List[Any], key: Callable[[Any], Any] = lambda x: x, reverse: bool = False) -> List[Any]:
    """
    Stable Merge Sort implementation with O(N log N) worst-case time complexity.
    """
    if len(items) <= 1:
        return list(items)

    mid = len(items) // 2
    left = merge_sort(items[:mid], key=key, reverse=reverse)
    right = merge_sort(items[mid:], key=key, reverse=reverse)

    merged = []
    i = j = 0
    while i < len(left) and j < len(right):
        k_left = key(left[i])
        k_right = key(right[j])
        
        # Determine condition based on reverse flag
        condition = (k_left >= k_right) if reverse else (k_left <= k_right)
        if condition:
            merged.append(left[i])
            i += 1
        else:
            merged.append(right[j])
            j += 1

    merged.extend(left[i:])
    merged.extend(right[j:])
    return merged


def quick_sort(items: List[Any], key: Callable[[Any], Any] = lambda x: x, reverse: bool = False) -> List[Any]:
    """
    In-place randomized Quick Sort with O(N log N) average time complexity.
    Uses 3-way partitioning (Dutch National Flag) to efficiently handle duplicate keys.
    """
    arr = list(items)
    if len(arr) <= 1:
        return arr

    def _quick_sort_recurse(low: int, high: int):
        if low >= high:
            return
        
        # Randomized pivot selection to avoid O(N^2) on sorted/reverse-sorted data
        pivot_idx = random.randint(low, high)
        arr[low], arr[pivot_idx] = arr[pivot_idx], arr[low]
        pivot_val = key(arr[low])

        # 3-way partition:
        # elements < pivot: [low .. lt - 1]
        # elements == pivot: [lt .. gt]
        # elements > pivot: [gt + 1 .. high]
        lt = low
        gt = high
        i = low + 1

        while i <= gt:
            curr_val = key(arr[i])
            if curr_val < pivot_val:
                if not reverse:
                    arr[lt], arr[i] = arr[i], arr[lt]
                    lt += 1
                    i += 1
                else:
                    arr[gt], arr[i] = arr[i], arr[gt]
                    gt -= 1
            elif curr_val > pivot_val:
                if not reverse:
                    arr[gt], arr[i] = arr[i], arr[gt]
                    gt -= 1
                else:
                    arr[lt], arr[i] = arr[i], arr[lt]
                    lt += 1
                    i += 1
            else:
                i += 1

        _quick_sort_recurse(low, lt - 1)
        _quick_sort_recurse(gt + 1, high)

    _quick_sort_recurse(0, len(arr) - 1)
    return arr


def parcel_sort_key(criterion: str) -> Callable[[Parcel], Any]:
    """
    Returns a sort key tuple for parcel prioritization.
    Available criteria:
      - 'deadline_priority': (deadline ascending, priority descending, value descending)
      - 'priority_deadline': (priority descending, deadline ascending, value descending)
      - 'value_density': (value/weight ratio descending)
      - 'deadline_only': (deadline ascending)
    """
    if criterion == "deadline_priority":
        # Sort by earliest deadline first; if equal, higher priority first, higher value first
        return lambda p: (p.deadline_min, -p.priority, -p.value, p.weight)
    elif criterion == "priority_deadline":
        # Highest priority first; if equal, earliest deadline first
        return lambda p: (-p.priority, p.deadline_min, -p.value, p.weight)
    elif criterion == "value_density":
        # Highest value per kg first
        return lambda p: (-(p.value / max(1, p.weight)), p.deadline_min)
    elif criterion == "deadline_only":
        return lambda p: (p.deadline_min, p.parcel_id)
    else:
        raise ValueError(f"Unknown sorting criterion: {criterion}")


def sort_parcels(parcels: List[Parcel],
                 criterion: str = "deadline_priority",
                 algorithm: str = "merge_sort") -> List[Parcel]:
    """
    Sorts a collection of parcels according to the specified priority rule and algorithm.
    """
    key_func = parcel_sort_key(criterion)
    if algorithm == "merge_sort":
        return merge_sort(parcels, key=key_func)
    elif algorithm == "quick_sort":
        return quick_sort(parcels, key=key_func)
    elif algorithm == "timsort":
        return sorted(parcels, key=key_func)
    else:
        raise ValueError(f"Unsupported sorting algorithm: {algorithm}")


def compare_sorting_algorithms(parcels: List[Parcel], criterion: str = "deadline_priority") -> Dict[str, Any]:
    """
    Runs Merge Sort, Quick Sort, and Python's built-in Timsort on the same list of parcels,
    verifying correctness and measuring execution times.
    """
    key_fn = parcel_sort_key(criterion)
    results = {}

    # Built-in Timsort (Golden Baseline)
    t0 = time.perf_counter()
    expected = sorted(parcels, key=key_fn)
    timsort_time = (time.perf_counter() - t0) * 1000.0
    results["timsort"] = {
        "time_ms": timsort_time,
        "is_correct": True
    }

    # Merge Sort
    t0 = time.perf_counter()
    m_sorted = merge_sort(parcels, key=key_fn)
    merge_time = (time.perf_counter() - t0) * 1000.0
    # Check correctness (keys match expected)
    is_merge_correct = [key_fn(p) for p in m_sorted] == [key_fn(p) for p in expected]
    results["merge_sort"] = {
        "time_ms": merge_time,
        "is_correct": is_merge_correct,
        "result_count": len(m_sorted)
    }

    # Quick Sort
    t0 = time.perf_counter()
    q_sorted = quick_sort(parcels, key=key_fn)
    quick_time = (time.perf_counter() - t0) * 1000.0
    is_quick_correct = [key_fn(p) for p in q_sorted] == [key_fn(p) for p in expected]
    results["quick_sort"] = {
        "time_ms": quick_time,
        "is_correct": is_quick_correct,
        "result_count": len(q_sorted)
    }

    return results
