from fastapi import APIRouter, Depends, HTTPException

from app.modules.producto_ingrediente import service
from app.modules.producto_ingrediente.producto_ingrediente_uow import (
    ProductoIngredienteUnitOfWork,
)

router = APIRouter(prefix="/producto-ingrediente", tags=["ProductoIngrediente"])


@router.post("/")
def create(
    producto_id: int,
    ingrediente_id: int,
    es_removible: bool = False,
):
    with ProductoIngredienteUnitOfWork() as uow:
        resultado = service.create_relation(
            uow, producto_id, ingrediente_id, es_removible
        )
        return resultado


@router.delete("/")
def delete(
    producto_id: int,
    ingrediente_id: int,
):
    with ProductoIngredienteUnitOfWork() as uow:
        deleted = service.delete_relation(uow, producto_id, ingrediente_id)

        if not deleted:
            raise HTTPException(status_code=404, detail="Relación no encontrada")

        return {"message": "Relación eliminada"}


@router.get("/producto/{producto_id}")
def by_producto(producto_id: int):
    with ProductoIngredienteUnitOfWork() as uow:
        return service.get_by_producto(uow, producto_id)


@router.get("/ingrediente/{ingrediente_id}")
def by_ingrediente(ingrediente_id: int):
    with ProductoIngredienteUnitOfWork() as uow:
        return service.get_by_ingrediente(uow, ingrediente_id)
