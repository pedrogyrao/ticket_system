from fastapi import APIRouter

from models.ticket import TicketModel

router = APIRouter()

data = {
    'ticket_id': 'str',
    'description': 'str',
    'points': 0,
    'sprint_num': 0,
}


@router.post('/')
def create_ticket(ticket: TicketModel):
    return ticket


@router.get('/')
def get_tickets():
    return [data, data]


@router.get('/{ticket_id}/')
def get_ticket(ticket_id: str):
    return data


@router.put('/{ticket_id}/')
def update_ticket(ticket_id: str, ticket: TicketModel):
    return data


@router.delete('/{ticket_id}/')
def delete_ticket():
    return data


@router.post('/{ticket_id}/start')
def start_ticket(ticket_id: str):
    return data


@router.post('/{ticket_id}/finish')
def finish_ticket(ticket_id: str):
    return data
