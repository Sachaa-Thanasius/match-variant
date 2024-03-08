import pytest

from match_variant import Variant


class SampleVariant(Variant):
    option0: ()  # type: ignore
    option1: (str,)  # type: ignore
    option2: (str, int)  # type: ignore
    option_list: (list[str],)  # type: ignore


def test_too_many_args():
    with pytest.raises(TypeError) as ex:
        b = SampleVariant.option1("Too", "many", "args")

    ex_str = str(ex.value)
    assert "1" in ex_str
    assert "3" in ex_str


def test_adt():
    assert SampleVariant.option1.__qualname__ == "SampleVariant.option1"


def test_match_args():
    assert SampleVariant.option0().__match_args__ == ()
    assert SampleVariant.option1("one").__match_args__ == ("_0",)
    assert SampleVariant.option2("one", 2).__match_args__ == ("_0", "_1")


def test_match_no_args():
    match SampleVariant.option0():
        case SampleVariant.option0():
            pass
        case _:
            pytest.fail("Should be option0")


def test_match_one_arg():
    match SampleVariant.option1("boo"):
        case SampleVariant.option1(val):
            assert val == "boo"
        case _:
            pytest.fail("Should be option1")


def test_match_two_args():
    match SampleVariant.option2("boo", 2):
        case SampleVariant.option2(val, val2):
            assert val == "boo"
            assert val2 == 2
        case _:
            pytest.fail("Should be option2")


def test_repr():
    o = SampleVariant.option0()
    assert repr(o) == "SampleVariant.option0()"
    o = SampleVariant.option1("one")
    assert repr(o) == "SampleVariant.option1('one')"
    o = SampleVariant.option2("one", 2)
    assert repr(o) == "SampleVariant.option2('one', 2)"


@pytest.mark.parametrize(
    ["self", "other", "expected"],
    [
        pytest.param(
            SampleVariant.option_list([]),
            SampleVariant.option_list([]),
            True,
            id="equal options",
        ),
        pytest.param(
            SampleVariant.option0(), SampleVariant.option0(), True, id="equal option0"
        ),
        pytest.param(
            SampleVariant.option_list([]),
            SampleVariant.option_list(["something"]),
            False,
            id="equal variant, unequal value",
        ),
        pytest.param(
            SampleVariant.option_list([]),
            SampleVariant.option0(),
            False,
            id="left option_list right option0",
        ),
        pytest.param(
            SampleVariant.option0(),
            SampleVariant.option_list([]),
            False,
            id="right option_list left option0",
        ),
        pytest.param(
            SampleVariant.option_list([]), "a string", False, id="different type"
        ),
    ],
)
def test_is_eq(self, other, expected):
    assert (self == other) is expected


def test_hash_identical_val_hashable():
    val = "something"
    assert hash(SampleVariant.option1(val)) == hash(SampleVariant.option1(val))


def test_hash_different_equal_object_values():
    assert hash(SampleVariant.option1(("one",))) == hash(SampleVariant.option1(("one",)))


def test_hashed_same_variant_different_value():
    assert hash(SampleVariant.option1("one")) != hash(SampleVariant.option1("two"))


def test_hash_no_args_is_hashable():
    assert hash(SampleVariant.option0()) == hash(SampleVariant.option0())


def test_hash_multi_args_is_hashable():
    assert hash(SampleVariant.option2("one", 2)) == hash(SampleVariant.option2("one", 2))


def test_hash_unhashable_value_fails():
    with pytest.raises(TypeError) as ex:
        hash(SampleVariant.option1([]))

    assert "unhashable" in str(ex.value)


def test_can_add_hashable_to_set():
    assert {SampleVariant.option1("one"), SampleVariant.option1("one")} == {
        SampleVariant.option1("one")
    }
    assert {SampleVariant.option0(), SampleVariant.option0()} == {SampleVariant.option0()}


@pytest.mark.parametrize(
    ["self", "cls", "expected"],
    [
        pytest.param(
            SampleVariant.option0(), SampleVariant.option0, True, id="noargs is class"
        ),
        pytest.param(
            SampleVariant.option1("blah"),
            SampleVariant.option1,
            True,
            id="withargs is class",
        ),
        pytest.param(
            SampleVariant.option0(),
            SampleVariant.option1,
            False,
            id="noargs is not with args",
        ),
        pytest.param(SampleVariant.option0(), SampleVariant, True, id="noargs is class"),
    ],
)
def test_instance_check(self, cls, expected):
    assert isinstance(self, cls) == expected


def test_exhaust():
    with pytest.raises(ValueError) as ex:
        match SampleVariant.option1("Value"):
            case SampleVariant.option0:
                pytest.fail("Should not match nothing on a value")
            case _ as x:
                SampleVariant.exhaust(x)

    ex_str = str(ex.value)
    assert "SampleVariant.option1" in ex_str
    assert "Value" in ex_str
