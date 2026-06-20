import pytest
from bmi_compose import union, intersection

# Union tests

@pytest.mark.parametrize("x,y,expected", [
  ([1,2,3], [3,4,5,6], [1,2,3,4,5,6]),           # overlapping
  ([], [1,2,3], [1,2,3]),                         # empty first
  ([1,2,3], [], [1,2,3]),                         # empty second
  ([], [], []),                                   # both empty
  ([1,2,3], [1,2,3], [1,2,3]),                   # identical
  ([1,2,3], [4,5,6], [1,2,3,4,5,6]),             # disjoint
  (["a","b","c"], ["c","d","e"], ["a","b","c","d","e"]),  # strings
  ([3,1,2], [5,4,2], [3,1,2,5,4]),               # preserves order
])
def test_union(x, y, expected):
  assert union(x, y) == expected

# Intersection tests

@pytest.mark.parametrize("x,y,expected", [
  ([1,2,3], [3,4,5,6], [3]),                     # overlapping
  ([], [1,2,3], []),                              # empty first
  ([1,2,3], [], []),                              # empty second
  ([], [], []),                                   # both empty
  ([1,2,3], [1,2,3], [1,2,3]),                   # identical
  ([1,2,3], [4,5,6], []),                        # disjoint
  (["a","b","c"], ["c","d","b"], ["b","c"]),     # strings
  ([3,1,2,5], [5,2,7], [2,5]),                   # preserves order from first
  ([1,2,3,4,5], [2,4,6,8], [2,4]),               # multiple common
])
def test_intersection(x, y, expected):
  assert intersection(x, y) == expected