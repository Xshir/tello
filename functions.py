from datetime import datetime
import time
from colorama import Fore, Style
import asyncpg
from credentials import db_creds


async def retrieve_tello_instructions(drone: str) -> list:
    # postgres://user:password@host:port/database?option=value
    database_access_url = f"postgres://{db_creds['user']}:{db_creds['password']}@{db_creds['host']}:{db_creds['port']}/{db_creds['database']}"
    list_of_instructions = []

    try:
        pool = await asyncpg.create_pool(
            database_access_url
        )  # creates a pool to acquire and connect to later
        print("POSTGRESQL connected = ", pool)

        async with pool.acquire() as conn:
            records = await conn.fetch("SELECT * FROM tello_table")
            for column in records:
                if column[drone] is not None:
                    list_of_instructions.append(column[drone])
            return list_of_instructions

    except Exception as e:
        print("Something went wrong:", e)

async def wait_for_time_to_start() -> None:
    time_to_start = input("What H:M (Hours: Minutes) Do You Want To Start The Code?\nExample: 13:23\nEnter: ")

    while True:
        current_time = (datetime.now()).strftime("%H:%M")
        try:
            dt_time_to_start = datetime.strptime(time_to_start, "%H:%M")
        except ValueError:
            print(Fore.RED + "---Wrong Format Used--" + Style.RESET_ALL)
            await wait_for_time_to_start()
 

        if time_to_start != current_time:
            time.sleep(1)
            
            print(Fore.RED + f"Waiting for {time_to_start} to run code ({(dt_time_to_start-(datetime.now())).seconds})s left)")
        else:
            print("Starting Program")
            return





















