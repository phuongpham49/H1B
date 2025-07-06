
import streamlit as st
import pandas as pd
import urllib.parse
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time

st.set_page_config(page_title="H1B Connect (Live)", layout="wide")
st.title("📄 H1B Connect")
st.subheader("Scraping real H1B-sponsored firms from MyVisaJobs")

sector = st.text_input("🔍 Enter sector (e.g., 'Data Science', 'Finance', 'Consulting')", "")
job_title = st.text_input("🎯 Desired position/title (optional)", "")

def get_h1b_data(sector):
    url = f"https://www.myvisajobs.com/Reports/2024-H1B-Visa-Sponsor.aspx?T=LC&C={urllib.parse.quote(sector)}&Y=2024"
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=options)
    driver.get(url)
    time.sleep(5)

    data = []
    try:
        rows = driver.find_elements(By.CSS_SELECTOR, "table.tbl tbody tr")[1:11]
        for row in rows:
            cols = row.find_elements(By.TAG_NAME, "td")
            if len(cols) >= 4:
                data.append([col.text for col in cols[:4]])
    finally:
        driver.quit()

    return pd.DataFrame(data, columns=["Employer", "Job Title", "Location", "Hires"])

if sector:
    try:
        df = get_h1b_data(sector)
        if df.empty:
            st.warning("⚠️ No data retrieved.")
        else:
            st.dataframe(df)

            st.markdown("### Step 2: LinkedIn Contact Search")
            for _, row in df.iterrows():
                title = job_title or row["Job Title"]
                query = f'site:linkedin.com/in "{row["Employer"]}" "{title}"'
                url = f"https://www.google.com/search?q={urllib.parse.quote(query)}"
                st.markdown(f"- 🔗 [Search: {row['Employer']} – {title}]({url})")
    except Exception as e:
        st.error(f"❌ Error: {e}")
else:
    st.info("Enter a sector to begin.")
