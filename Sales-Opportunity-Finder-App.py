import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Function to clean and process the data
def process_data(file):
    try:
        df = pd.read_csv(file)
        st.write("CSV file successfully loaded.")
    except Exception as e:
        st.error(f"Error reading the file: {e}")
        return None
    
    # Convert numeric columns; remove commas and percentage signs if necessary.
    cols_to_clean = ['Quantity available', 'Total impressions on eBay site', 'Quantity sold', 
                     'Top 20 search slot impressions from promoted listings', 'Top 20 search slot organic impressions', 
                     'Rest of search slot impressions', 'Non-search promoted listings impressions', 
                     'Non-search organic impressions', 'Total promoted listings impressions (applies to eBay site only)', 
                     'Total organic impressions on eBay site', 'Total page views']
    
    for col in cols_to_clean:
        if col in df.columns:
            df[col] = (df[col].astype(str)
                       .str.replace(',', '', regex=False)
                       .str.replace('%', '', regex=False))
            df[col] = pd.to_numeric(df[col], errors='coerce')
        else:
            st.warning(f"Column {col} not found in the dataset.")
    
    return df

# Function to generate top opportunities and visualization
def identify_opportunities(df):
    try:
        median_page_views = df['Total page views'].median()
    except KeyError:
        st.error("Error: 'Total page views' column is missing from the dataset.")
        return None
    
    # Filter listings with no sales but high page views
    opp_df = df[(df['Quantity sold'] == 0) & (df['Total page views'] > median_page_views)]
    opp_df_sorted = opp_df.sort_values('Total page views', ascending=False)

    # Create the Opportunity Score
    df['Opportunity Score'] = (df['Total impressions on eBay site'] * df['Total page views']) / (df['Quantity sold'] + 1)
    top_opportunities = df.sort_values('Opportunity Score', ascending=False).head(15)

    # Generate the chart for the top opportunities
    top_10 = top_opportunities.head(10)
    top_10_sorted = top_10.sort_values('Opportunity Score', ascending=True)

    # Create a figure and axis for plotting
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Plot the bar chart on the axis
    ax.barh(top_10_sorted['Listing title'].str[:40], top_10_sorted['Opportunity Score'])
    ax.set_xlabel('Opportunity Score')
    ax.set_ylabel('Listing Title')
    ax.set_title('Top 10 Opportunity Listings')
    plt.tight_layout()

    # Display the chart in Streamlit
    st.pyplot(fig)

    # Return the top opportunities data for download
    return top_opportunities[['Listing title', 'eBay item ID', 'Total impressions on eBay site', 
                              'Total page views', 'Quantity sold', 'Opportunity Score']]

# Streamlit UI
st.title('eBay Traffic Report Opportunity Finder')

st.markdown("""
Upload your eBay traffic report CSV file, and we will analyze it to identify your biggest opportunities to optimize your listings!
""")

# File uploader widget
uploaded_file = st.file_uploader("Choose your eBay traffic report CSV", type='csv')

if uploaded_file is not None:
    # Process the data
    df = process_data(uploaded_file)
    
    if df is not None:
        # Identify the top opportunities
        opportunities = identify_opportunities(df)
        
        if opportunities is not None:
            # Display the results as a table
            st.subheader("Top 15 Opportunity Listings")
            st.dataframe(opportunities)
            
            # Provide download link for CSV
            opportunities_csv = opportunities.to_csv(index=False)
            st.download_button(label="Download Top Opportunities CSV", data=opportunities_csv, file_name="Top_Opportunities.csv", mime="text/csv")
