from bmi_compose import union, intersection

def test_union():
  x = [1,2,3]
  y = [3,4,5,6]
  assert union(x, y) == [1,2,3,4,5,6]

def test_intersection():
  x = [1,2,3]
  y = [3,4,5,6]
  assert intersection(x, y) == [3]