from aiogram.dispatcher.filters.state import State, StatesGroup


class EscrowWizard(StatesGroup):
    Role = State()
    Counterparty = State()
    ItemType = State()
    Description = State()
    Amount = State()
    Confirm = State()

