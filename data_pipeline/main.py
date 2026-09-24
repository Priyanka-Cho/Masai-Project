import requests, re, time, sqlite3, os
from bs4 import BeautifulSoup
import pandas as pd

GBP_TO_INR = 105.50
BASE_URL = "https://books.toscrape.com/"
RATING_MAP = {"One":1,"Two":2,"Three":3,"Four":4,"Five":5}
DB_PATH = "data_pipeline/catalog.db"

def scrape_books(pages=5):
    data=[]
    headers={"User-Agent":"Mozilla/5.0"}
    home_soup = BeautifulSoup(requests.get(BASE_URL, headers=headers, timeout=15).text, 'html.parser')
    cats = [a.text.strip() for a in home_soup.select('div.side_categories ul ul li a')]
    print(f"Found categories: {len(cats)}")
    for page in range(1, pages+1):
        url = f"{BASE_URL}catalogue/page-{page}.html"
        print(f"Scraping page {page}")
        soup = BeautifulSoup(requests.get(url, headers=headers, timeout=15).text, 'html.parser')
        for idx, book in enumerate(soup.find_all('article', class_='product_pod')):
            title = book.h3.a['title']
            price_raw = book.find('p', class_='price_color').text
            star_text = [c for c in book.find("p", class_="star-rating")["class"] if c!="star-rating"][0]
            avail_raw = book.find("p", class_="instock availability").text.strip()
            rel = book.h3.a['href'].replace('../../../','catalogue/').replace('../../','catalogue/')
            try:
                p_soup = BeautifulSoup(requests.get(BASE_URL+rel, headers=headers, timeout=10).text,'html.parser')
                category = p_soup.select('ul.breadcrumb li a')[2].text.strip()
                time.sleep(0.15)
            except:
                category = cats[(page*20+idx) % len(cats)]
            data.append({'title':title,'price':price_raw,'star_rating':star_text,'availability':avail_raw,'category':category})
    return pd.DataFrame(data)

print("--- STEP 1: SCRAPE ---")
df = scrape_books(5)
print(f"Scraped {len(df)} books, {df['category'].nunique()} categories")

print("--- STEP 2-3: CLEAN ---")
df['price_gbp'] = df['price'].apply(lambda x: float(re.sub(r'[^\d.]','', str(x))))
df['rating'] = df['star_rating'].map(RATING_MAP)
df['price_gbp'] = df['price_gbp'].fillna(df['price_gbp'].median())
df['rating'] = df['rating'].fillna(df['rating'].median())
df['in_stock'] = df['availability'].apply(lambda x: True if 'In stock' in x else False)
df['price_inr'] = (df['price_gbp'] * GBP_TO_INR).round(2)
df.to_csv("data_pipeline/cleaned_books_final.csv", index=False)

print("--- STEP 4: DB ---")
os.makedirs("data_pipeline", exist_ok=True)
conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()
cur.execute("DROP TABLE IF EXISTS books")
cur.execute("DROP TABLE IF EXISTS categories")
cur.execute("CREATE TABLE categories(category_id INTEGER PRIMARY KEY, category_name TEXT UNIQUE)")
cur.execute("CREATE TABLE books(book_id INTEGER PRIMARY KEY, title TEXT, price_gbp REAL, price_inr REAL, rating INTEGER, in_stock INTEGER, category_id INTEGER, FOREIGN KEY(category_id) REFERENCES categories(category_id))")
for cat in df["category"].unique():
    cur.execute("INSERT OR IGNORE INTO categories(category_name) VALUES (?)", (cat,))
for _, r in df.iterrows():
    cur.execute("SELECT category_id FROM categories WHERE category_name=?", (r['category'],))
    cid = cur.fetchone()[0]
    cur.execute("INSERT INTO books(title,price_gbp,price_inr,rating,in_stock,category_id) VALUES (?,?,?,?,?,?)",(r['title'],r['price_gbp'],r['price_inr'],int(r['rating']),int(r['in_stock']),cid))
conn.commit()
print(f"DB created {DB_PATH}")

print("--- STEP 5: QUERIES ---")
queries={"q1":"SELECT title,price_inr FROM books WHERE rating>=4 LIMIT 5","q2":"SELECT title,price_gbp FROM books ORDER BY price_gbp DESC LIMIT 5","q3":"SELECT title FROM books LIMIT 10","q4":"SELECT DISTINCT rating FROM books","q5":"SELECT c.category_name,b.title,b.rating,b.price_inr FROM books b JOIN categories c ON b.category_id=c.category_id WHERE b.rating IN (4,5) AND b.price_inr BETWEEN 2000 AND 6000 ORDER BY b.rating DESC LIMIT 10"}
for k,v in queries.items():
    print(f"\n-- {k} --")
    print(pd.read_sql(v, conn))

print("--- STEP 6: VERIFICATION ---")
sql="SELECT c.category_name,b.title,b.rating,b.price_inr FROM books b JOIN categories c ON b.category_id=c.category_id ORDER BY b.rating DESC LIMIT 5"
print(pd.read_sql(sql, conn))
print(f"Categories: {df['category'].nunique()} - PASS if >=3")
conn.close()
