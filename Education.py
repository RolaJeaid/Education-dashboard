import streamlit as st
import pandas as pd
import plotly.express as px

# Load datasets (df1 and df2 for data overview and visualization)
@st.cache_data
def load_data():
    # Replace with the correct file paths for df1 and df2
    df1 = pd.read_csv('49b7d46d7d16e8b5c5579646915e4bfc_20240907_143939.csv')
    df2 = pd.read_csv('cdfd6aad1d3ce14e83f6acae86e2459c_20240907_144721.csv')

    # Clean the data: Replace NaN values with 0
    df1.fillna(0, inplace=True)
    df2.fillna(0, inplace=True)

    return df1, df2

# Load the data
df1, df2 = load_data()

# Sidebar for navigation between pages
page = st.sidebar.selectbox("Select a page", ["Data Overview", "Visualizations"], key="page_selectbox")

# Page 1: Data Overview
if page == "Data Overview":
    st.title("Education Statistics and Resources Dashboard")
    st.header("Page 1: Data Overview")
    
    # Description of Dataset 1
    st.subheader("Dataset 1: Education Statistics by Region")
    st.write("""
    This dataset contains education-related statistics for different regions. The key columns include:
    - **refArea**: The geographical area (e.g., governorate or district).
    - **Percentage of Education Level of Residents**: The percentage of residents who achieved various education levels, including illiterate, university, secondary, intermediate, etc.
    - **Percentage of School Dropout**: The percentage of residents who dropped out of school.
    """)
    
    # Display a preview of Dataset 1
    st.write("Here is a preview of the first dataset:")
    st.dataframe(df1.head())
    
    # Description of Dataset 2
    st.subheader("Dataset 2: Educational Resources by Town")
    st.write("""
    This dataset contains information about educational resources in various towns, including public and private schools, and universities. The key columns include:
    - **Town**: The town or city where the data was collected.
    - **Governorate**: The broader geographical region to which the town belongs.
    - **Type and Size of Educational Resources**: Information about the availability and size of educational resources like public schools, private schools, and universities.
    """)
    
    # Display a preview of Dataset 2
    st.write("Here is a preview of the second dataset:")
    st.dataframe(df2.head())

# Page 2: Visualizations
elif page == "Visualizations":
    st.title("Interactive Dashboard: Education Resources and Statistics")

    # Visualization 1: Distribution of Educational Resources
    st.subheader("Public/Private Schools and Universities by Region")

    # Group the data by region (refArea) and sum the number of public and private schools and universities
    df2_region_grouped = df2.groupby('refArea')[['Type and size of educational resources - public schools', 
                                                 'Type and size of educational resources - private schools', 
                                                 'Nb of universities by type - Private universities',
                                                 'Type and size of educational resources - universities']].sum().reset_index()

    # Clean up the region names in refArea (if necessary)
    df2_region_grouped['refArea'] = df2_region_grouped['refArea'].apply(lambda x: x.split('/')[-1].replace('_', ' '))

    # Interactive dropdown to filter regions
    regions = df2_region_grouped['refArea'].unique()
    selected_regions = st.multiselect('Select Regions', regions, default=regions)

    # Filter the dataframe based on selected regions
    filtered_df2 = df2_region_grouped[df2_region_grouped['refArea'].isin(selected_regions)]

    # Create the stacked bar chart for public/private schools and universities by region with custom colors
    fig1 = px.bar(filtered_df2, x='refArea', 
                 y=['Type and size of educational resources - public schools', 
                    'Type and size of educational resources - private schools',
                    'Nb of universities by type - Private universities',
                    'Type and size of educational resources - universities'],
                 title="Distribution of Public/Private Schools and Universities by Region",
                 labels={'value': 'Number of Institutions', 'refArea': 'Region'},
                 barmode='stack',
                 text_auto=True,  # Add labels for the number of institutions
                 color_discrete_map={
                    'Type and size of educational resources - public schools': 'blue',
                    'Type and size of educational resources - private schools': 'red',
                    'Nb of universities by type - Private universities': 'black',
                    'Type and size of educational resources - universities': 'gray'
                 })

    # Update layout to make the figure larger
    fig1.update_layout(xaxis_title="Region", 
                      yaxis_title="Number of Institutions", 
                      xaxis_tickangle=-50, 
                      width=1700,  # Increase the width
                      height=1100)  # Increase the height

    # Display the Plotly figure in Streamlit
    st.plotly_chart(fig1)

    # Visualization 2: Illiteracy vs School Dropout Rates by Town
    st.subheader("Top Towns: Illiteracy vs School Dropout Rates")

    # Sidebar for selecting filters (add unique keys for each widget)
    st.sidebar.title("Filter Options")
    
    # Interactive dropdown to show either Illiteracy or Dropout Rate
    rate_type = st.sidebar.multiselect("Select Rate to Display", ['Illiteracy Rate', 'School Dropout Rate'], key="rate_type_multiselect", default=['Illiteracy Rate', 'School Dropout Rate'])
    
    # Interactive slider for the number of top towns to display
    num_towns = st.sidebar.slider("Number of Top Towns to Display", min_value=5, max_value=50, value=20, step=5, key="num_towns_slider")
    
    # Clean and filter the dataset to include relevant columns
    df1_cleaned = df1[['Town', 'PercentageofEducationlevelofresidents-illeterate', 
                       'PercentageofSchooldropout']].dropna()

    # Sort the data based on both Illiteracy Rate and School Dropout Rate in descending order
    df1_sorted = df1_cleaned.sort_values(by=['PercentageofEducationlevelofresidents-illeterate', 
                                             'PercentageofSchooldropout'], ascending=False)

    # Select the top towns based on the slider input
    df1_top = df1_sorted.head(num_towns)

    # Create the bar chart based on selected filters
    y_columns = []
    if 'Illiteracy Rate' in rate_type:
        y_columns.append('PercentageofEducationlevelofresidents-illeterate')
    if 'School Dropout Rate' in rate_type:
        y_columns.append('PercentageofSchooldropout')

    # Create a grouped bar chart for illiteracy and/or dropout rates by Town
    fig2 = px.bar(df1_top, x='Town', y=y_columns,
                  barmode='group', title=f"Top {num_towns} Towns: Illiteracy vs School Dropout Rates",
                  labels={'value': 'Percentage (%)', 'Town': 'Town'})

    # Update layout for better readability
    fig2.update_layout(xaxis_title="Town", yaxis_title="Percentage (%)", xaxis_tickangle=-45)

    # Display the Plotly figure in Streamlit
    st.plotly_chart(fig2)
