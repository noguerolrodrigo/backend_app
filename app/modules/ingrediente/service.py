from sqlmodel import select

from app.modules.ingrediente.model import Ingrediente
from app.modules.ingrediente.ingrediente_uow import IngredienteUnitOfWork


def create(uow: IngredienteUnitOfWork, data):
    ingrediente = Ingrediente(**data.model_dump())
    uow.session.add(ingrediente)
    uow.session.flush()
    uow.session.refresh(ingrediente)
    return ingrediente


def get_all(uow: IngredienteUnitOfWork, limit: int):
    return uow.session.exec(select(Ingrediente).limit(limit)).all()


def get_by_id(uow: IngredienteUnitOfWork, ingrediente_id: int):
    return uow.session.get(Ingrediente, ingrediente_id)


def update(uow: IngredienteUnitOfWork, ingrediente_id: int, data):
    ingrediente = uow.session.get(Ingrediente, ingrediente_id)

    if not ingrediente:
        return None

    for key, value in data.items():
        setattr(ingrediente, key, value)

    uow.session.add(ingrediente)
    uow.session.flush()
    uow.session.refresh(ingrediente)

    return ingrediente


def delete(uow: IngredienteUnitOfWork, ingrediente_id: int):
    ingrediente = uow.session.get(Ingrediente, ingrediente_id)

    if not ingrediente:
        return None

    uow.session.delete(ingrediente)
    uow.session.flush()

    return {"message": "Ingrediente eliminado"}
