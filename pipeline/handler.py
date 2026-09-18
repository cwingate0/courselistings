import asyncio
from scraper import term_scrape
from temp_cleaner import clean_imported
from compiler import concat
from calendar_cleaner import clean_for_calendar
from schedule_cleaner import clean_for_schedule

'''def ctoname(code: str):
	if
'''
async def main():
    # await term_scrape("Fall2025", "20253")
    # await term_scrape("Spring2026", "20261")
    # await term_scrape("Spring2026", "20261")

    # full_json = await concat("raws/20243raw.json","20251raw.json","20251ar.json")

    # print (await clean_imported("imported/2024-Fall.json","raws/20243raw.json"))
    # print (await clean_imported("imported/2025-Spring.json","raws/20251raw.json"))
    # print (await clean_imported("imported/2025-Summer.json","raws/20252raw.json"))

    # print (await clean_for_calendar("raws/20243raw.json")) 
    # print (await clean_for_calendar("raws/20251raw.json"))
    # print (await clean_for_calendar("raws/20252raw.json"))
    # print (await clean_for_calendar("raws/20253raw.json"))
    # print (await clean_for_calendar("raws/20261raw.json"))
    # print (await clean_for_calendar("raws/20262raw.json"))

    # await clean_for_schedule("raws/20253raw.json")
    await clean_for_schedule("raws/20261raw.json")
    return

if __name__ == "__main__":
	asyncio.run(main())
	