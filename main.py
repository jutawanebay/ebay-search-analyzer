import streamlit as st
import pandas as pd
from scraper import scrape_ebay_results
from text_analyzer import analyze_keywords, suggest_title, calculate_price_stats
import re

def is_valid_ebay_url(url):
    """Check if the URL is a valid eBay search URL"""
    ebay_pattern = r'https?://(www\.)?ebay\.(com|co\.uk|de|fr|au)/.*'
    return bool(re.match(ebay_pattern, url))

def main():
    st.set_page_config(
        page_title="eBay Search Results Analyzer",
        page_icon="📊",
        layout="wide"
    )

    st.title("📊 eBay Search Results Analyzer")
    st.markdown("""
    This tool analyzes eBay search results to show you the most common keywords in product titles.
    Enter an eBay search URL below to get started.
    """)

    # URL input
    url = st.text_input(
        "Enter eBay Search URL",
        value="https://www.ebay.com/sch/i.html?_nkw=dvd+anime+japanese+blu+ray&_sacat=0&_from=R40&_trksid=p4432023.m570.l1311"
    )

    if url:
        if not is_valid_ebay_url(url):
            st.error("Please enter a valid eBay search URL")
            return

        with st.spinner("Scraping eBay results..."):
            try:
                titles, prices = scrape_ebay_results(url)
                if not titles:
                    st.warning("No results found. Please try a different search.")
                    return

                st.success(f"Found {len(titles)} items!")

                # Display raw titles
                with st.expander("Show Raw Titles"):
                    for i, title in enumerate(titles, 1):
                        st.text(f"{i}. {title}")

                # Analyze keywords
                keyword_freq = analyze_keywords(titles)

                # Calculate price statistics
                price_stats = calculate_price_stats(prices)

                # Generate suggested title
                suggested_title = suggest_title(keyword_freq)

                # Create DataFrame for keyword frequency
                df = pd.DataFrame(
                    keyword_freq.items(),
                    columns=['Keyword', 'Frequency']
                ).sort_values('Frequency', ascending=False)

                # Display results in columns
                col1, col2 = st.columns([2, 1])

                with col1:
                    # Display suggested title
                    st.subheader("📝 Suggested Title")
                    st.info(suggested_title)

                    # Display price statistics
                    st.subheader("💰 Price Analysis")
                    price_col1, price_col2 = st.columns(2)

                    with price_col1:
                        st.metric("Average Price", f"${price_stats['average']:.2f}")
                        st.metric("Minimum Price", f"${price_stats['min']:.2f}")

                    with price_col2:
                        st.metric("Median Price", f"${price_stats['median']:.2f}")
                        st.metric("Maximum Price", f"${price_stats['max']:.2f}")

                    # Display keyword frequency table
                    st.subheader("Keyword Frequency Analysis")
                    st.dataframe(
                        df,
                        use_container_width=True,
                        hide_index=True
                    )

                with col2:
                    st.subheader("Top 30 Keywords")
                    chart_data = df.head(30)
                    # Rotate chart for better readability of more keywords
                    chart = st.bar_chart(
                        chart_data,
                        x='Keyword',
                        y='Frequency',
                        height=600  # Increase height to accommodate more bars
                    )

            except Exception as e:
                st.error(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()