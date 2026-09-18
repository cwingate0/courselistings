import re
import asyncio
import pandas as pd
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright
from tqdm.asyncio import tqdm_asyncio
import json
from datetime import datetime

SEMESTER = None
SEMESTERCODE = None
semaphore = asyncio.Semaphore(8)

async def scrape_section(context, dept_name, href):
	sec_page = f"https://doc.sis.columbia.edu/{href}"
	match = re.search(rf"subj/[A-Z]+/([A-Z0-9]+)-{SEMESTERCODE}-([0-9]+)/$", href)
	if not match:
		return None
	code, sec_num = match.groups()

	page = await context.new_page()
	try:
		await page.goto(sec_page, wait_until="networkidle")
		await asyncio.sleep(0.5)
		soup = BeautifulSoup(await page.content(), "html.parser", from_encoding="utf-8")
	
		location = None
		days = None
		start_time = None
		end_time = None
		for r in soup.select("tr"):
			th = r.find("th")
			if th and " ".join(th.get_text(" ").split()) == "Day & Time Location":
				td = r.find("td")
				if td:
					time_and_loc = td.get_text("\n").strip()
					line, location = time_and_loc.split("\n", 1)
					days, time_part = line.split(" ", 1)
					start_str, end_str = time_part.split("-")
					start_time = datetime.strptime(start_str.strip(), "%I:%M%p").strftime("%H:%M")
					end_time = datetime.strptime(end_str.strip(), "%I:%M%p").strftime("%H:%M")
				break

		info_dict = {}
		table = soup.find("table")
		if not table:
			return None
		for row in table.find_all("tr"):
			cells = row.find_all(["th", "td"])
			if len(cells) >= 2:
				key = cells[0].get_text(strip=True)
				if key == "Web Site":
					verg_tag = cells[1].find("a")
					value = verg_tag["href"] if verg_tag else ""
				else:
					value = cells[1].get_text(strip=True)
				info_dict[key] = value

		name = soup.find("h1").get_text(strip=True)


		return {
			"title": name,
			"course": info_dict.get("Section key", ""),
			"subject": info_dict.get("Department", ""),
			"school": info_dict.get("Division", ""),
			"term": SEMESTER,
			"section_number": sec_num,
			"instructor": info_dict.get("Instructor", ""),
			"description": info_dict.get("Course Description", ""),
			"enrollment": info_dict.get("Enrollment", ""),
			"credits": info_dict.get("Points", ""),
			"vergil_link": info_dict.get("Web Site", ""),
			"start_time": start_time,
			"end_time": end_time,
			"class_days": days,
			"class_room": location,
		}
	finally:
		await page.close()


async def scrape_term(context, dept_name, term_page):
	page = await context.new_page()
	await page.goto(term_page, wait_until="networkidle")
	await asyncio.sleep(1)
	soup = BeautifulSoup(await page.content(), "html.parser", from_encoding="utf-8")

	section_links = []
	for a in soup.find_all("a", href=True):
		href = a["href"]
		if re.search(rf"subj/[A-Z]+/([A-Z0-9]+)-{SEMESTERCODE}-([0-9]+)/$", href):
			section_links.append(href)

	tasks = [scrape_section(context, dept_name, href) for href in section_links]
	results = await asyncio.gather(*tasks)
	await page.close()
	return [r for r in results if r]


async def scrape_department(context, dept_url):
	page = await context.new_page()
	await page.goto(dept_url, wait_until="networkidle")
	await asyncio.sleep(1)
	soup = BeautifulSoup(await page.content(), "html.parser", from_encoding="utf-8")

	term_links = []
	for a in soup.find_all("a", href=True):
		href = a["href"]
		match = re.search(rf"sel/([A-Za-z]+)_{SEMESTER}\.html$", href)
		if match:
			dept_name = match.group(1)
			term_page = f"https://doc.sis.columbia.edu/#{href}"
			term_links.append((dept_name, term_page))

	all_results = []
	for dept_name, term_page in term_links:
		results = await scrape_term(context, dept_name, term_page)
		all_results.extend(results)

	await page.close()
	return all_results


async def main():
	all_results = []

	async with async_playwright() as p:
		browser = await p.chromium.launch(headless=True)
		context = await browser.new_context()
		page = await context.new_page()

		base_url = "https://doc.sis.columbia.edu/#sel/dept-A.html"
		await page.goto(base_url, wait_until="networkidle")
		await asyncio.sleep(1)
		soup = BeautifulSoup(await page.content(), "html.parser", from_encoding="utf-8")

		dept_links = []
		for a in soup.find_all("a", href=True):
			href = a["href"]
			if re.search(r"dept-[A-Z]\.html$", href):
				dept_links.append(f"https://doc.sis.columbia.edu/{href}")

		print(f"✅ Found {len(dept_links)} department index links")

		# Run up to 5 departments in parallel
		semaphore = asyncio.Semaphore(5)

		async def limited_scrape(dept_url):
			async with semaphore:
				return await scrape_department(context, dept_url)

		tasks = [limited_scrape(url) for url in dept_links]
		results_by_dept = await tqdm_asyncio.gather(*tasks, desc=f"Scraping {SEMESTER}")

		for dept_results in results_by_dept:
			all_results.extend([{k: str(v) for k, v in r.items()} for r in dept_results])

		await browser.close()

	# Convert and save to SQLite database
	
	df = pd.DataFrame(all_results)
	df = df.astype(str)

	with open (f"../database/raws/{SEMESTERCODE}raw.json", "w") as f:
		json.dump(df.to_dict(orient="records"), f, indent=2)


'''if __name__ == "__main__":
	asyncio.run(main())'''

async def term_scrape(semester: str, semester_code: str):
	global SEMESTER
	global SEMESTERCODE
	SEMESTER = semester
	SEMESTERCODE = semester_code
	await(main())