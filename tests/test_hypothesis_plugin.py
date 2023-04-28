import typing
from datetime import date

import pytest

import pydantic_v1
from pydantic_v1.networks import import_email_validator

try:
    from hypothesis import HealthCheck, given, settings, strategies as st
except ImportError:
    from unittest import mock

    given = settings = lambda *a, **kw: (lambda f: f)  # pass-through decorator
    HealthCheck = st = mock.Mock()

    pytestmark = pytest.mark.skipif(True, reason='"hypothesis" not installed')


def gen_models():
    class MiscModel(pydantic_v1.BaseModel):
        # Each of these models contains a few related fields; the idea is that
        # if there's a bug we have neither too many fields to dig through nor
        # too many models to read.
        obj: pydantic_v1.PyObject
        color: pydantic_v1.color.Color
        json_any: pydantic_v1.Json

    class StringsModel(pydantic_v1.BaseModel):
        card: pydantic_v1.PaymentCardNumber
        secbytes: pydantic_v1.SecretBytes
        secstr: pydantic_v1.SecretStr

    class UUIDsModel(pydantic_v1.BaseModel):
        uuid1: pydantic_v1.UUID1
        uuid3: pydantic_v1.UUID3
        uuid4: pydantic_v1.UUID4
        uuid5: pydantic_v1.UUID5

    class IPvAnyAddress(pydantic_v1.BaseModel):
        address: pydantic_v1.IPvAnyAddress

    class IPvAnyInterface(pydantic_v1.BaseModel):
        interface: pydantic_v1.IPvAnyInterface

    class IPvAnyNetwork(pydantic_v1.BaseModel):
        network: pydantic_v1.IPvAnyNetwork

    class StrictNumbersModel(pydantic_v1.BaseModel):
        strictbool: pydantic_v1.StrictBool
        strictint: pydantic_v1.StrictInt
        strictfloat: pydantic_v1.StrictFloat
        strictstr: pydantic_v1.StrictStr

    class NumbersModel(pydantic_v1.BaseModel):
        posint: pydantic_v1.PositiveInt
        negint: pydantic_v1.NegativeInt
        posfloat: pydantic_v1.PositiveFloat
        negfloat: pydantic_v1.NegativeFloat
        nonposint: pydantic_v1.NonPositiveInt
        nonnegint: pydantic_v1.NonNegativeInt
        nonposfloat: pydantic_v1.NonPositiveFloat
        nonnegfloat: pydantic_v1.NonNegativeFloat

    class JsonModel(pydantic_v1.BaseModel):
        json_int: pydantic_v1.Json[int]
        json_float: pydantic_v1.Json[float]
        json_str: pydantic_v1.Json[str]
        json_int_or_str: pydantic_v1.Json[typing.Union[int, str]]
        json_list_of_float: pydantic_v1.Json[typing.List[float]]
        json_pydantic_model: pydantic_v1.Json[pydantic_v1.BaseModel]

    class ConstrainedNumbersModel(pydantic_v1.BaseModel):
        conintt: pydantic_v1.conint(gt=10, lt=100)
        coninte: pydantic_v1.conint(ge=10, le=100)
        conintmul: pydantic_v1.conint(ge=10, le=100, multiple_of=7)
        confloatt: pydantic_v1.confloat(gt=10, lt=100)
        confloate: pydantic_v1.confloat(ge=10, le=100)
        confloatemul: pydantic_v1.confloat(ge=10, le=100, multiple_of=4.2)
        confloattmul: pydantic_v1.confloat(gt=10, lt=100, multiple_of=10)
        condecimalt: pydantic_v1.condecimal(gt=10, lt=100)
        condecimale: pydantic_v1.condecimal(ge=10, le=100)
        condecimaltplc: pydantic_v1.condecimal(gt=10, lt=100, decimal_places=5)
        condecimaleplc: pydantic_v1.condecimal(ge=10, le=100, decimal_places=2)

    class ConstrainedDateModel(pydantic_v1.BaseModel):
        condatet: pydantic_v1.condate(gt=date(1980, 1, 1), lt=date(2180, 12, 31))
        condatee: pydantic_v1.condate(ge=date(1980, 1, 1), le=date(2180, 12, 31))

    yield from (
        MiscModel,
        StringsModel,
        UUIDsModel,
        IPvAnyAddress,
        IPvAnyInterface,
        IPvAnyNetwork,
        StrictNumbersModel,
        NumbersModel,
        JsonModel,
        ConstrainedNumbersModel,
        ConstrainedDateModel,
    )

    try:
        import_email_validator()
    except ImportError:
        pass
    else:

        class EmailsModel(pydantic_v1.BaseModel):
            email: pydantic_v1.EmailStr
            name_email: pydantic_v1.NameEmail

        yield EmailsModel


@pytest.mark.parametrize('model', gen_models())
@settings(suppress_health_check={HealthCheck.too_slow}, deadline=None)
@given(data=st.data())
def test_can_construct_models_with_all_fields(data, model):
    # The value of this test is to confirm that Hypothesis knows how to provide
    # valid values for each field - otherwise, this would raise ValidationError.
    instance = data.draw(st.from_type(model))

    # We additionally check that the instance really is of type `model`, because
    # an evil implementation could avoid ValidationError by means of e.g.
    # `st.register_type_strategy(model, st.none())`, skipping the constructor.
    assert isinstance(instance, model)
