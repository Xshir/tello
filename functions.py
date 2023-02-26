from datetime import datetime
import time
from colorama import Fore, Style
import asyncpg
from credentials import db_creds
import asyncio

async def start_db():
    try:
        database_access_url = f"postgres://{db_creds['user']}:{db_creds['password']}@{db_creds['host']}:{db_creds['port']}/{db_creds['database']}"
        pool = await asyncpg.create_pool(
            database_access_url
        )  # creates a pool to acquire and connect to later
        print("POSTGRESQL connected = ", pool)
        return pool
    except Exception as e:
        print("Something went wrong:", e)


async def retrieve_tello_instructions(pool, drone: str) -> list:
    # postgres://user:password@host:port/database?option=value
   
    list_of_instructions = []

    async with pool.acquire() as conn:
            records = await conn.fetch("SELECT * FROM tello_table")
            for column in records:
                if column[drone] is not None:
                    if ":" not in column[drone]:
                        list_of_instructions.append(column[drone])
            return list_of_instructions



async def query_db(pool: asyncpg.Pool, query: str, fetch=False):
    # postgres://user:password@host:port/database?option=value
    database_access_url = f"postgres://{db_creds['user']}:{db_creds['password']}@{db_creds['host']}:{db_creds['port']}/{db_creds['database']}"
    async with pool.acquire() as conn:
            if fetch is False:
             return await conn.execute(query)
            elif fetch is True:
             return await conn.fetch(query)

async def wait_for_time_to_start(pool, tello: str) -> None:
    #time_to_start = input("What H:M (Hours: Minutes) Do You Want To Start The Code?\nExample: 13:23\nEnter: ")
    records = await query_db(pool, f"SELECT {tello} FROM tello_table", fetch=True) # key 500 is the timestamp slot in the format of H:M
   #print(type(time_to_start), time_to_start)
    for element in records:
        if element[0] is not None:
            if ":" in element[0]:
                time_to_start = element[0]
            elif element[0] == "NOT SET":
                print("TIME TO START IS NOT SET. WAITING FOR A TIME TO BE SET.")
                asyncio.sleep(1)
                await wait_for_time_to_start(pool, tello)

        

    while True:
        current_time = (datetime.now()).strftime("%H:%M")
        
        dt_time_to_start = datetime.strptime(time_to_start, "%H:%M")
      

        if time_to_start != current_time:
            time.sleep(1)
            
            print(Fore.RED + f"Waiting for {time_to_start} to run code ({(dt_time_to_start-(datetime.now())).seconds})s left)")
        else:
            print("Starting Program")
            return





















