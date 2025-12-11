import pytest
from bustapi.safe import Array, Boolean, Const, Float, Integer, String, Struct


def test_basic_struct():
    class User(Struct):
        name: String
        age: Integer

    # Valid
    u = User(name="Test", age=25)
    assert u.name == "Test"
    assert u.age == 25

    # Invalid Type
    with pytest.raises(TypeError):
        User(name="Test", age="25")  # Str passed for Int

    # Missing Field
    with pytest.raises(ValueError):
        User(name="Test")


def test_float_validator():
    class Item(Struct):
        weight: Float

    assert Item(weight=10.5).weight == 10.5
    assert Item(weight=10).weight == 10.0  # Int conversion

    with pytest.raises(TypeError):
        Item(weight="heavy")


def test_boolean_validator():
    class Flag(Struct):
        active: Boolean

    assert Flag(active=True).active is True
    assert Flag(active=False).active is False

    with pytest.raises(TypeError):
        Flag(active=1)  # No implicit casting for bool in this strict mode


def test_array_validator():
    class TagList(Struct):
        tags: Array(String)

    t = TagList(tags=["a", "b", "c"])
    assert t.tags == ["a", "b", "c"]

    # Invalid list item
    with pytest.raises(TypeError):
        TagList(tags=["a", 1, "c"])

    # Not a list
    with pytest.raises(TypeError):
        TagList(tags="not a list")


def test_nested_struct_and_array():
    class Point(Struct):
        x: Integer
        y: Integer

    class Polygon(Struct):
        points: Array(Point)

    data = {"points": [{"x": 1, "y": 2}, {"x": 3, "y": 4}]}

    poly = Polygon(**data)
    assert len(poly.points) == 2
    assert isinstance(poly.points[0], Point)
    assert poly.points[0].x == 1
    assert poly.points[1].y == 4


def test_const_validator():
    class Admin(Struct):
        role: Const("admin")

    assert Admin(role="admin").role == "admin"

    with pytest.raises(ValueError):
        Admin(role="user")
