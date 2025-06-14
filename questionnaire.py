from aiogram.fsm.state import State, StatesGroup

class JobForm(StatesGroup):
    country = State()
    arrival_date = State()
    age = State()
    citizenship = State()
    documents = State()
    contact = State()