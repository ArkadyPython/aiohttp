from aiohttp import web
from models import engine, Session, Advertisement, init_db
import json
from sqlalchemy.exc import IntegrityError

app = web.Application()

@web.middleware
async def session_middleware(request: web.Request, handler):
    async with Session() as session:
        request.session = session
        response = await handler(request)
        return response

async def init_orm(app: web.Application):
    print('START')
    await init_db()
    yield
    await engine.dispose()
    print('FINISH')

app.cleanup_ctx.append(init_orm)
app.middlewares.append(session_middleware)


def get_http_error(error_class, message):
    error = error_class(
        body=json.dumps({'error': message}),
        content_type='application/json'
    )
    return error


async def get_advertisement_by_id(session: Session, advertisement_id: int):
    advertisement = await session.get(Advertisement, advertisement_id)
    if advertisement is None:
        raise get_http_error(web.HTTPNotFound, f'Advertisement with id {advertisement_id} not found')
    return advertisement

async def add_advertisement(session: Session, advertisement: Advertisement):
    try:
        session.add(advertisement)
        await session.commit()
    except IntegrityError as error:
        raise get_http_error(web.HTTPConflict, 'Advertisement already exist')
    return advertisement


class AdvertisementView(web.View):

    @property
    def advertisement_id(self):
        return int(self.request.match_info['advertisement_id'])

    @property
    def session(self) -> Session:
        return self.request.session

    async def get_current_advertisement(self):
        return await get_advertisement_by_id(self.session, self.advertisement_id)
    async def get(self):
        advertisement = await self.get_current_advertisement()
        return web.json_response(advertisement.json)
    async def post(self):
        json_data = await self.request.json()
        advertisement = Advertisement(**json_data)
        advertisement = await add_advertisement(self.session, advertisement)
        return web.json_response({'id': advertisement.id})
    async def delete(self):
        advertisement = await self.get_current_advertisement()
        await self.session.delete(advertisement)
        await self.session.commit()
        return web.json_response({'status': 'deleted'})

app.add_routes(
    [
        web.post('/advertisement', AdvertisementView),
        web.get('/advertisement/{advertisement_id:\d+}', AdvertisementView),
        web.delete('/advertisement/{advertisement_id:\d+}', AdvertisementView)
    ]
)

web.run_app(app)