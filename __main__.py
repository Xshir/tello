import asyncio
from functions import retrieve_tello_instructions, wait_for_time_to_start


async def main_program_loop():
    
    config = "tello0"
    await wait_for_time_to_start()
    list_ = await retrieve_tello_instructions(config)
    print(list_)


loop = asyncio.get_event_loop()
loop.run_until_complete(main_program_loop())
