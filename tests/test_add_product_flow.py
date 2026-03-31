import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import pytest

from app.dao.enums import Priority, ProductAddAttrs, ProductAppend
from app.handlers.common import (
    add_product_attribute,
    process_product_attrs,
    process_product_url,
    start_command,
)
from app.states.states import AddProductState


YANDEX_MARKET_URL_PLACEHOLDER = "https://market.yandex.ru/product/<PRODUCT_PLACEHOLDER>"
PROCESS_PRODUCT_ATTRS_HANDLER = getattr(process_product_attrs, "__wrapped__", process_product_attrs)


class FakeFSMContext:
    def __init__(self) -> None:
        self._state = None
        self._data = {}

    async def set_state(self, value) -> None:
        self._state = value

    async def get_state(self):
        return self._state

    async def set_data(self, value: dict) -> None:
        self._data = dict(value)

    async def get_data(self) -> dict:
        return dict(self._data)

    async def update_data(self, **kwargs) -> None:
        self._data.update(kwargs)

    async def clear(self) -> None:
        self._state = None
        self._data.clear()


class FakeDishkaContainer:
    def __init__(self, session):
        self._session = session

    async def get(self, _type_hint, component=None):
        return self._session


def make_message(text: str, *, message_id: int = 1, chat_id: int = 111):
    msg = SimpleNamespace()
    msg.text = text
    msg.message_id = message_id
    msg.chat = SimpleNamespace(id=chat_id)
    msg.from_user = SimpleNamespace(first_name="Test", username="tester")
    msg.answer = AsyncMock(
        return_value=SimpleNamespace(message_id=258, chat=SimpleNamespace(id=chat_id))
    )
    return msg


def make_callback(data: str, *, message_id: int = 258, chat_id: int = 111):
    cb = SimpleNamespace()
    cb.data = data
    cb.message = SimpleNamespace(message_id=message_id, chat=SimpleNamespace(id=chat_id))
    cb.answer = AsyncMock()
    return cb


def test_pipeline_url_to_confirm_current_behavior():
    async def scenario():
        state = FakeFSMContext()
        bot = SimpleNamespace(edit_message_text=AsyncMock())
        session = object()
        container = FakeDishkaContainer(session)

        # 1. /start
        msg_start = make_message("/start")
        await start_command(msg_start)
        assert msg_start.answer.await_count == 1

        # 2. send URL
        msg_url = make_message(YANDEX_MARKET_URL_PLACEHOLDER)
        await process_product_url(msg_url, state)
        assert await state.get_state() == AddProductState.start_adding
        data = await state.get_data()
        assert data["marketplace"] == "market.yandex"
        assert data["url"] == YANDEX_MARKET_URL_PLACEHOLDER

        # 3. click "Name"
        cb_name = make_callback(ProductAddAttrs.NAME.value, message_id=data["ppu_message_id"])
        await PROCESS_PRODUCT_ATTRS_HANDLER(
            cb_name, state, bot, dishka_container=container
        )
        # NOTE: current product_answer helper moves state back to start_adding.
        assert await state.get_state() == AddProductState.start_adding

        # 4. type name
        await add_product_attribute(make_message("Cowboy Bebop OST"), state)
        assert await state.get_state() == AddProductState.start_adding

        # 5. click "Price"
        data = await state.get_data()
        cb_price = make_callback(ProductAddAttrs.PRICE.value, message_id=data["ppu_message_id"])
        await PROCESS_PRODUCT_ATTRS_HANDLER(
            cb_price, state, bot, dishka_container=container
        )
        assert await state.get_state() == AddProductState.start_adding

        # 6. type price
        await add_product_attribute(make_message("4990"), state)
        assert await state.get_state() == AddProductState.start_adding

        # 7. click "Priority"
        data = await state.get_data()
        cb_priority = make_callback(
            ProductAddAttrs.PRIORITY.value, message_id=data["ppu_message_id"]
        )
        await PROCESS_PRODUCT_ATTRS_HANDLER(
            cb_priority, state, bot, dishka_container=container
        )
        assert await state.get_state() == AddProductState.start_adding

        # 8. current code stores priority from message text, not callback hearts
        await add_product_attribute(make_message(Priority.MEDIUM.value), state)
        assert await state.get_state() == AddProductState.start_adding

        # 9. click "Confirm"
        data = await state.get_data()
        cb_confirm = make_callback(ProductAppend.CONFIRM.value, message_id=data["ppu_message_id"])
        with patch(
            "app.handlers.common.db_utils.create_product_record",
            new=AsyncMock(return_value=True),
        ) as create_record_mock:
            await PROCESS_PRODUCT_ATTRS_HANDLER(
                cb_confirm, state, bot, dishka_container=container
            )
            create_record_mock.assert_awaited_once()

    asyncio.run(scenario())


@pytest.mark.xfail(reason="Priority hearts callback flow is not implemented yet")
def test_priority_heart_callback_expected_future_flow():
    async def scenario():
        state = FakeFSMContext()
        bot = SimpleNamespace(edit_message_text=AsyncMock())
        session = object()
        container = FakeDishkaContainer(session)

        msg_url = make_message(YANDEX_MARKET_URL_PLACEHOLDER)
        await process_product_url(msg_url, state)
        data = await state.get_data()

        # Click "Priority"
        cb_priority = make_callback(
            ProductAddAttrs.PRIORITY.value, message_id=data["ppu_message_id"]
        )
        await PROCESS_PRODUCT_ATTRS_HANDLER(
            cb_priority, state, bot, dishka_container=container
        )
        assert await state.get_state() == AddProductState.add_attribute

        # Desired behavior: click one heart button as callback
        cb_heart = make_callback(Priority.HIGH.value, message_id=data["ppu_message_id"])
        await PROCESS_PRODUCT_ATTRS_HANDLER(
            cb_heart, state, bot, dishka_container=container
        )

        # Expected target behavior (currently absent):
        # state should return to start_adding and product_priority should be saved.
        data_after = await state.get_data()
        assert data_after["product_priority"] == Priority.HIGH.value
        assert await state.get_state() == AddProductState.start_adding

    asyncio.run(scenario())
