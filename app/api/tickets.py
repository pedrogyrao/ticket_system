import math
from typing import List
from datetime import datetime
from starlette.status import HTTP_201_CREATED
from fastapi import APIRouter, Depends, HTTPException, Query

from db.mongodb import database
from models.ticket import TicketModel, TicketPutModel
from db.mongodb_validators import validate_object_id

router = APIRouter()


def convert_id(ticket):
    if ticket.get('_id', False):
        ticket['_id'] = str(ticket['_id'])
        return ticket
    else:
        raise ValueError(
            f'No `_id` found! Unable to cast ID for ticket: {ticket}'
        )


async def _get_ticket_or_404(ticket_id: str):
    _id = validate_object_id(ticket_id)
    ticket = await database.ticketDB.find_one({'_id': _id})
    if ticket:
        return convert_id(ticket)
    else:
        raise HTTPException(status_code=404, detail='Ticket not found')



@router.post(
    '/',
    status_code=HTTP_201_CREATED,
    response_model_include=['description', 'points', 'sprint_num', 'handler'])
async def create_ticket(ticket: TicketModel):
    ticket = ticket.dict()
    ticket['created_at'] = datetime.now()
    ticket['started_at'] = None
    ticket['finished_at'] = None


    ticket_op = await database.ticketDB.insert_one(ticket)
    if ticket_op.inserted_id:
        ticket = await _get_ticket_or_404(ticket_op.inserted_id)
        return ticket
    return ticket


@router.get('/{ticket_id}/')
async def get_ticket(ticket_id: str)-> TicketModel:
    ticket = await _get_ticket_or_404(ticket_id)
    return ticket


@router.get('/')
async def get_tickets(
    limit: int = 10, skip: int = 0,
    handler: str = None, has_handler: bool=None,
    ongoing: bool = None):

    filtering = {}
    if handler:
        filtering['handler'] = handler

    if has_handler is not None:
        if has_handler:
            filtering['handler'] = {'$ne': None}
        else:
            filtering['handler'] = None

    if ongoing is not None:
        if ongoing:
            filtering['started_at'] ={'$ne': None}
            filtering['finished_at'] = None
        else:
            filtering['finished_at'] ={'$ne': None}

    tickets_cursor = database.ticketDB.find(filtering).skip(skip).limit(limit)
    tickets = await tickets_cursor.to_list(length=limit)
    return list(map(convert_id, tickets))


@router.put('/{ticket_id}/', dependencies=[Depends(_get_ticket_or_404)])
async def update_ticket(ticket_id: str, ticket_data: TicketPutModel):
    ticket_data = ticket_data.dict()
    ticket_data = {k:v for k,v in ticket_data.items() if v is not None}

    ticket_op = await database.ticketDB.update_one(
        {'_id': validate_object_id(ticket_id)}, {'$set': ticket_data}
    )
    if ticket_op.modified_count:
        return await _get_ticket_or_404(ticket_id)
    else:
        raise HTTPException(status_code=304)


@router.delete('/{ticket_id}/')
async def delete_ticket(ticket_id: str):
    await _get_ticket_or_404(ticket_id)
    ticket_op = await database.ticketDB.delete_one(
        {'_id': validate_object_id(ticket_id)})
    if ticket_op.deleted_count:
        return {'status': f'deleted count: {ticket_op.deleted_count}'}



@router.post('/{ticket_id}/start')
async def create_ticket(ticket_id: str):
    ticket = await _get_ticket_or_404(ticket_id)
    if ticket['started_at']:
        raise HTTPException(status_code=304, detail='Ticket already started.')
    ticket_data = {'started_at': datetime.now()}

    ticket_op = await database.ticketDB.update_one(
        {'_id': validate_object_id(ticket_id)}, {'$set': ticket_data}
    )

    if ticket_op.modified_count:
        return await _get_ticket_or_404(ticket_id)
    else:
        raise HTTPException(status_code=304)


@router.post('/{ticket_id}/finish')
async def finish_ticket(ticket_id: str):
    ticket = await _get_ticket_or_404(ticket_id)
    if ticket['started_at'] is None:
        raise HTTPException(status_code=304, detail='Ticket not started.')
    if ticket['finished_at']:
        raise HTTPException(status_code=304, detail='Ticket already finished.')
    ticket_data = {'finished_at': datetime.now()}

    ticket_op = await database.ticketDB.update_one(
        {'_id': validate_object_id(ticket_id)}, {'$set': ticket_data}
    )

    if ticket_op.modified_count:
        return await _get_ticket_or_404(ticket_id)
    else:
        raise HTTPException(status_code=304)


async def get_data_for_history(handler: str = None, sprint_num: int = None):
    filtering = {'finished_at': {'$ne': None}}
    if handler is not None:
        filtering['handler'] = handler
    if sprint_num is not None:
        filtering['sprint_num'] = sprint_num
    return database.ticketDB.find(filtering)


@router.get('/history')
async def get_history(handler: str = None, sprint_num: int = None):
    if (handler is None) and (sprint_num is None):
        raise HTTPException(status_code=400)

    tickets_cursor = await get_data_for_history(handler, sprint_num)

    points = 0
    seconds = 0
    async for ticket in tickets_cursor:
        points += ticket['points']
        seconds += (ticket['finished_at'] - ticket['started_at']).seconds
    hours = seconds // 3600

    points_hour = max(1, points) / max(1, hours)
    return {
        'total_points': points,
        'total_hours': hours,
        'points_hour': points_hour}


@router.get('/handler_capacity')
async def get_handlers_capacity(handler: str):
    history = await get_history(handler)
    return {'capacity': history['points_hour']}


@router.get('/sprint_estimative')
async def get_sprint_estimative(sprint_num: int):
    handlers_capacity = {None: 1}
    sprint_tickets = await get_data_for_history(sprint_num=sprint_num)

    total_hours = 0
    async for ticket in sprint_tickets:
        capacity = 1
        handler = ticket['handler']
        if handler not in handlers_capacity:
            capacity = (await get_handlers_capacity(handler))['capacity']
            handlers_capacity[handler] = capacity
        total_hours += max(1, ticket['points']) / handlers_capacity[handler]
    return {'ETA': math.ceil(total_hours)}
