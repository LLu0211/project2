import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

theses = pd.read_csv("THESES-TOTAL.csv")

maitrises = theses.query("type == 'maîtrise'")

medianesMaitrisesUniv = maitrises.groupby("universite")["nbPages"].median().sort_values(ascending=False)

medianesMaitrisesDiscipline = maitrises.groupby("discipline")["nbPages"].median().sort_values(ascending=False)

# Manually update the values in the grandeDiscipline column
theses['grandeDiscipline'] = theses['grandeDiscipline'].str.replace('1. Sciences exactes et naturelles', 'Sciences exactes et naturelles')
theses['grandeDiscipline'] = theses['grandeDiscipline'].str.replace("2. Sciences de l'ingénieur et technologiques", "Sciences de l'ingénieur et technologiques")
theses['grandeDiscipline'] = theses['grandeDiscipline'].str.replace('3. Sciences médicales et sanitaires', 'Sciences médicales et sanitaires')
theses['grandeDiscipline'] = theses['grandeDiscipline'].str.replace('4. Sciences agricoles', 'Sciences agricoles')
theses['grandeDiscipline'] = theses['grandeDiscipline'].str.replace('5. Sciences sociales', 'Sciences sociales')
theses['grandeDiscipline'] = theses['grandeDiscipline'].str.replace('6. Sciences humaines', 'Sciences humaines')
theses['grandeDiscipline'] = theses['grandeDiscipline'].str.replace('7. Programme personnalisé', 'Programme personnalisé')


# Define your functions for updating the plots
def update_box_plot_by_university(selected_type):
    # Ensure that 'selected_type' is a list even if it contains only one element
    if not isinstance(selected_type, list):
        selected_type = [selected_type]

    # Filter data based on selected type
    filtered_df = theses[theses['type'].isin(selected_type)]

    # Check if the filtered dataframe is empty
    if filtered_df.empty:
        st.error('No data found for the selected type(s): {}'.format(selected_type))
        return go.Figure()

    # Calculate median nbPages for each university
    universite_medians = filtered_df.groupby('universite')['nbPages'].median().sort_values(ascending=True)

    # Check if after grouping the dataframe is empty
    if universite_medians.empty:
        st.error('No median page numbers found for the selected type(s): {}'.format(selected_type))
        return go.Figure()

    # Generate an array of colors for the gradient
    base_hue = 240  # Modify as needed for the correct color
    base_saturation = 100
    min_lightness = 10
    max_lightness = 30
    colors = [f'hsl({base_hue}, {base_saturation}%, {l}%)' for l in np.linspace(max_lightness, min_lightness, len(universite_medians))]

    # Create the box plot data, sorted by median nbPages
    data1 = []
    for i, universite in enumerate(universite_medians.index):
        university_df = filtered_df[filtered_df['universite'] == universite]
        if not university_df.empty:
            box = go.Box(
                y=university_df['nbPages'],
                name=universite,
                marker_color=colors[i],
                boxmean='sd'  # Represents the standard deviation
            )
            data1.append(box)
        else:
            st.error(f'No data found for university: {universite}')

    # If no box plots were added, return an empty figure
    if not data1:
        st.error('No data available to plot.')
        return go.Figure()

    # Create the figure with the data
    fig1 = go.Figure(data=data1)

    # Format the layout
    fig1.update_layout(
        yaxis=dict(
            title="Nombre de pages"
        ),
        xaxis=dict(
            categoryorder='array',
            categoryarray=[univ for univ in universite_medians.index],
            title="Université"
        ),
        plot_bgcolor='lightblue',
        font=dict(size=12),
        height=600
    )

    # Debug: Display the figure's data in the Streamlit app for verification
    st.write(fig1)

    return fig1

def update_box_plot_by_discipline(selected_type, selected_grande_discipline):
    if selected_grande_discipline == 'All':
        filtered_df = theses[theses['type'].isin(selected_type)]
    else:
        filtered_df = theses[(theses['type'].isin(selected_type)) & (theses['grandeDiscipline'] == selected_grande_discipline)]
    discipline_medians = filtered_df.groupby('discipline')['nbPages'].median().sort_values(ascending=True)
    base_hue = 82
    base_saturation = 100
    min_lightness = 10
    max_lightness = 30
    colors = [f'hsl({base_hue}, {base_saturation}%, {l}%)' for l in np.linspace(max_lightness, min_lightness, len(discipline_medians))]
    data = [
        go.Box(
            x=filtered_df[filtered_df['discipline'] == discipline]['nbPages'],
            name=discipline,
            marker_color=colors[i],
            showlegend=False
        )
        for i, discipline in enumerate(discipline_medians.index)
    ]
    fig = go.Figure(data=data)
    fig.update_layout(
        yaxis=dict(
            categoryorder='array',
            categoryarray=discipline_medians.index,
            title="Discipline"
        ),
        xaxis=dict(title="Distribution du nombre de pages", zeroline=False, gridcolor='white'),
        plot_bgcolor='khaki',
        font=dict(size=12),
        height=600
    )
    fig.update_xaxes(range=[0, 800], showgrid=True, gridwidth=1, gridcolor='white')
    return fig

# Main function to create the Streamlit app
def main():
    st.title("A Brief View of Page Numbers by Discipline and University")
    
    # Add widgets to the sidebar
    st.sidebar.title("Select Options")
    selected_type = st.sidebar.multiselect("Select type:", ["Maîtrise", "Doctorat"], default=["Doctorat"])
    selected_grande_discipline = st.sidebar.selectbox("Select a grande discipline:", ["All Disciplines"] + list(theses['grandeDiscipline'].unique()), index=0)

    # Update box plot by university
    st.subheader("Box Plot by University")
    fig1 = update_box_plot_by_university(selected_type)
    st.plotly_chart(fig1)

    # Update box plot by discipline
    st.subheader("Box Plot by Discipline")
    fig2 = update_box_plot_by_discipline(selected_type, selected_grande_discipline)
    st.plotly_chart(fig2)

if __name__ == "__main__":
    main()
