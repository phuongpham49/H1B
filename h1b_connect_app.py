import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import urllib.parse

st.set_page_config(page_title="H1B Connect", layout="wide")
st.title("📄 H1B Connect")
st.subheader("Find H1B-sponsored firms & LinkedIn contacts")

sector = st.text_input("🔍 Enter sector (e.g., 'Data Science', 'Finance', 'Consulting')", "")
job_title = st.text_input("🎯 Desired position/title (optional)", "")

if sector:
    st.markdown("### Step 1: Searching MyVisaJobs")
    search_url = f"https://www.myvisajobs.com/Reports/2024-H1B-Visa-Sponsor.aspx?T=LC&C={urllib.parse.quote(sector)}&Y=2024"
    st.write(f"🔗 [Raw data on MyVisaJobs]({search_url})")

    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(search_url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")

        # Warning: Table is loaded dynamically via JavaScript, this may not return real data
        table = soup.find("table", {"class": "tbl"})
        rows = table.find_all("tr")[1:11] if table else []

        data = []
        for row in rows:
            cols = [col.get_text(strip=True) for col in row.find_all("td")]
            if cols:
                data.append(cols[:4])

        if not data:
            st.warning("⚠️ Could not retrieve real data (page content is likely loaded by JavaScript). Showing example data instead.")
            data = [
                ["Amazon.com Services LLC", "Data Scientist", "Seattle, WA", "120"],
                ["Google LLC", "Machine Learning Engineer", "Mountain View, CA", "75"],
                ["Meta Platforms Inc", "Quantitative Analyst", "Menlo Park, CA", "50"],
                ["Deloitte Consulting LLP", "Consultant", "New York, NY", "85"],
                ["Goldman Sachs & Co", "Quant Analyst", "New York, NY", "60"]
            ]

        df = pd.DataFrame(data, columns=["Employer", "Job Title", "Location", "Hires"])
        st.dataframe(df)

        st.markdown("### Step 2: LinkedIn Contacts")
        for _, row in df.iterrows():
            title = job_title or row["Job Title"]
            q = f'site:linkedin.com/in "{row["Employer"]}" "{title}"'
            url = f"https://www.google.com/search?q={urllib.parse.quote(q)}"
            st.markdown(f"- 🔗 [Search: {row['Employer']} – {title}]({url})")

    except Exception as e:
        st.error(f"Error: {e}")
else:
    st.info("Enter a sector to begin.")
