import asyncio
from functions import retrieve_tello_instructions, wait_for_time_to_start, start_db
from credentials import tello


async def main_program_loop():

    pool = await start_db()
    await wait_for_time_to_start(pool, tello)
    list_ = await retrieve_tello_instructions(pool, tello)
    print(list_)


loop = asyncio.get_event_loop()
loop.run_until_complete(main_program_loop())
