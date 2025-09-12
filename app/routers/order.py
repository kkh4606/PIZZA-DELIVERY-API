from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from .. import database, oauth2
from app.schemas import order as schema_order, user as schema_user
from app.models import user as model_user, order as model_order


router = APIRouter(tags=["orders"])


@router.post("/orders/order")
async def place_an_order(
    order: schema_order.Order,
    db: Session = Depends(database.get_db),
    current_user: model_user.User = Depends(oauth2.get_current_user),
):
    """
    ## Placing an order
    This requires the following
    - quantity: integer
    - pizza_size : string
    """

    new_order = model_order.Order(**order.model_dump(), user_id=current_user.id)
    db.add(new_order)
    db.commit()
    db.refresh(new_order)
    return new_order


@router.get("/orders")
async def get_orders(
    current_user: model_user.User = Depends(oauth2.get_current_user),
    db: Session = Depends(database.get_db),
):
    """
    # List all orders
    This list all orders made.It can be accessed by spuper users.
    """
    if current_user.is_staff:  # type:ignore
        orders = db.query(model_order.Order).all()
        return orders

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, detail="you are not a super user"
    )


@router.get("/orders/{id}")
async def get_order_by_id(
    id: int,
    db: Session = Depends(database.get_db),
    current_user: model_user.User = Depends(oauth2.get_current_user),
):
    """
    # get order with id
    you need the following
    - order_id : integer
    """
    if current_user.is_staff:
        order = db.query(model_order.Order).filter(model_order.Order.id == id).first()

        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="order not found"
            )
        return order
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, detail="you are not a super user"
    )


@router.get("/orders/users/orders")
async def get_user_orders(
    db: Session = Depends(database.get_db),
    current_user: model_user.User = Depends(oauth2.get_current_user),
):
    """
    # get current users's orders
    This returns users' order detail

    """
    user = (
        db.query(model_user.User)
        .filter(model_user.User.username == current_user.username)
        .first()
    )

    return user.orders


@router.get("/orders/user/order/{id}")
async def get_specific_order(
    id: int,
    db: Session = Depends(database.get_db),
    current_user: model_user.User = Depends(oauth2.get_current_user),
):
    """
    # get a order of current users'orders by id
    You need
    - order_id : integer
    """
    orders = current_user.orders

    for order in orders:
        if order.id == id:
            return order
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail=f"order with id : {id} not found"
    )


@router.put("/orders/order/update/{order_id}")
async def update_order(
    update_order: schema_order.Order,
    order_id: int,
    db: Session = Depends(database.get_db),
    current_user: model_user.User = Depends(oauth2.get_current_user),
):
    order_query = db.query(model_order.Order).filter(model_order.Order.id == order_id)
    order = order_query.first()

    if order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"order with id : {order_id} not found",
        )

    if current_user.id != order.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="you are not allowed to perform request action",
        )

    order_query.update(update_order.model_dump(), synchronize_session=False)
    db.commit()
    db.refresh(order)
    return order


@router.put("/orders/order/status/{order_id}")
async def update_order_status(
    order_status: schema_order.UpdateOrderStatus,
    order_id: int,
    db: Session = Depends(database.get_db),
    current_user: model_user.User = Depends(oauth2.get_current_user),
):

    if current_user.is_staff:
        order_query = db.query(model_order.Order).filter(
            model_order.Order.id == order_id
        )
        order = order_query.first()

        if order is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"order with id : {order_id} not found",
            )

        order_query.update(order_status.model_dump(), synchronize_session=False)
        db.commit()
        db.refresh(order)
        return {
            "id": order.id,
            "quantity": order.quantity,
            "pizza_size": order.pizza_size,
            "order_status": order.order_status,
        }

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="you don't have permission to perform request action",
    )


@router.delete(
    "/orders/order/delete/{order_id}", status_code=status.HTTP_204_NO_CONTENT
)
async def delete_order(
    order_id: int,
    db: Session = Depends(database.get_db),
    current_user: model_user.User = Depends(oauth2.get_current_user),
):
    order_query = db.query(model_order.Order).filter(model_order.Order.id == order_id)
    order_to_deltet = order_query.first()

    if not order_to_deltet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"order id with {order_id} not found",
        )
    if order_to_deltet.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="you don't have permission to perform request action",
        )
    order_query.delete(synchronize_session=False)
    db.commit()
    return
