import streamlit as st
import pandas as pd
import math
from pathlib import Path
import matplotlib.pyplot as plt

# Set the title and favicon that appear in the Browser's tab bar.
st.set_page_config(
    page_title='Tulies GDP dashboard',
    page_icon=':earth_americas:', # This is an emoji shortcode. Could be a URL too.
)

# -----------------------------------------------------------------------------
# Declare some useful functions.

@st.cache_data
def get_gdp_data():
    """Grab GDP data from a CSV file.

    This uses caching to avoid having to read the file every time. If we were
    reading from an HTTP endpoint instead of a file, it's a good idea to set
    a maximum age to the cache with the TTL argument: @st.cache_data(ttl='1d')
    """

    # Instead of a CSV on disk, you could read from an HTTP endpoint here too.
    DATA_FILENAME = Path(__file__).parent/'data/gdp_data.csv'
    raw_gdp_df = pd.read_csv(DATA_FILENAME)

    MIN_YEAR = 1960
    MAX_YEAR = 2022

    # The data above has columns like:
    # - Country Name
    # - Country Code
    # - [Stuff I don't care about]
    # - GDP for 1960
    # - GDP for 1961
    # - GDP for 1962
    # - ...
    # - GDP for 2022
    #
    # ...but I want this instead:
    # - Country Name
    # - Country Code
    # - Year
    # - GDP
    #
    # So let's pivot all those year-columns into two: Year and GDP
    gdp_df = raw_gdp_df.melt(
        ['Country Code'],
        [str(x) for x in range(MIN_YEAR, MAX_YEAR + 1)],
        'Year',
        'GDP',
    )

    # Convert years from string to integers
    gdp_df['Year'] = pd.to_numeric(gdp_df['Year'])

    return gdp_df

gdp_df = get_gdp_data()

# -----------------------------------------------------------------------------
# Draw the actual page

# Set the title that appears at the top of the page.
'''
# :earth_americas: Tulies GDP dashboard

Browse GDP data from the [World Bank Open Data](https://data.worldbank.org/) website. As you'll
notice, the data only goes to 2022 right now, and datapoints for certain years are often missing.
But it's otherwise a great (and did I mention _free_?) source of data.
'''

# Add some spacing
''
''

min_value = gdp_df['Year'].min()
max_value = gdp_df['Year'].max()

from_year, to_year = st.slider(
    'Which years are you interested in?',
    min_value=min_value,
    max_value=max_value,
    value=[min_value, max_value])

countries = gdp_df['Country Code'].unique()

selected_countries = st.multiselect(
    'Which countries would you like to view?',
    countries,
    ['DEU', 'FRA', 'GBR', 'BRA', 'MEX', 'JPN'])

if not selected_countries:
    st.warning("Select at least one country")

''
''
''

# Filter the data
filtered_gdp_df = gdp_df[
    (gdp_df['Country Code'].isin(selected_countries))
    & (gdp_df['Year'] <= to_year)
    & (from_year <= gdp_df['Year'])
]

st.header('GDP over time', divider='gray')

''

st.line_chart(
    filtered_gdp_df,
    x='Year',
    y='GDP',
    color='Country Code',
)

st.header('GDP distribution by country', divider='gray')

boxplot_data = [
    filtered_gdp_df[filtered_gdp_df['Country Code'] == c]['GDP'].dropna()
    for c in selected_countries
]
fig, ax = plt.subplots()
ax.boxplot(boxplot_data, labels=selected_countries)
ax.set_xlabel('Country')
ax.set_ylabel('GDP')
st.pyplot(fig)
plt.close(fig)

st.header('GDP distribution by year', divider='gray')

years = list(range(from_year, to_year + 1))
year_boxplot_data = [
    filtered_gdp_df[filtered_gdp_df['Year'] == y]['GDP'].dropna()
    for y in years
]
fig2, ax2 = plt.subplots(figsize=(max(6, len(years) * 0.3), 4))
ax2.boxplot(year_boxplot_data, labels=years)
ax2.set_xlabel('Year')
ax2.set_ylabel('GDP')
st.pyplot(fig2)
plt.close(fig2)

''
''


first_year = gdp_df[gdp_df['Year'] == from_year]
last_year = gdp_df[gdp_df['Year'] == to_year]

st.header(f'GDP in {to_year}', divider='gray')

''

cols = st.columns(4)

for i, country in enumerate(selected_countries):
    col = cols[i % len(cols)]

    with col:
        first_year_country = first_year[first_year['Country Code'] == country]['GDP']
        last_year_country = last_year[last_year['Country Code'] == country]['GDP']

        if first_year_country.dropna().empty:
            first_gdp = float('nan')
        else:
            first_gdp = first_year_country.dropna().iloc[0] / 1_000_000_000

        if last_year_country.dropna().empty:
            last_gdp = float('nan')
        else:
            last_gdp = last_year_country.dropna().iloc[0] / 1_000_000_000

        if math.isnan(first_gdp):
            growth = 'n/a'
            delta_color = 'off'
        else:
            growth = f'{last_gdp / first_gdp:,.2f}x'
            delta_color = 'normal'

        st.metric(
            label=f'{country} GDP',
            value=f'{last_gdp:,.0f}B',
            delta=growth,
            delta_color=delta_color
        )

