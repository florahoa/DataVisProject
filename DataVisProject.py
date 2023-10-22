import streamlit as st
import pandas as pd
from bokeh.plotting import figure
from bokeh.palettes import viridis
from bokeh.models import ColumnDataSource
from bokeh.transform import cumsum
from math import pi
import plotly.express as px

# Side Bar
with st.sidebar:
    st.image("https://i.pinimg.com/originals/3e/2a/1c/3e2a1c01d2857cfd1194f923957a6b9c.jpg", width=100)

    st.write("## Menu")
    st.write("All interventions by region")
    st.write("All interventions by department")
    st.write("Fires by region")
    st.write("Fires by department")
    st.write("Rescues by region")
    st.write("Rescues by department")
    st.write("## About the author")
    st.write("Flora HOA BIA 1")
    st.write("Supervised by DJALLEL Mohamed")
    st.write("#datavz2023efrei")
    st.write("## Contact")
    st.write("[Linkedin](https://www.linkedin.com/in/flora-hoa)")
    st.write("")
    st.image("https://www.efrei.fr/wp-content/uploads/2022/01/LOGO_EFREI-PRINT_EFREI-WEB.png", width=100)

st.title('Interventions carried out by the fire and rescue services')
st.subheader('What are the most frequent interventions per region and department ?')

@st.cache_data
def cache(file):
    return pd.read_csv(file, sep=';', encoding='ISO-8859-1')

file = st.file_uploader("Choose a CSV file, please : ", type="csv")

if file:
    df = cache(file)

    new = df.select_dtypes([float, int]).sum(axis=1)
    df['Total interventions'] = new

    # All interventions by region
    st.subheader("All interventions by region")
    reg = df.groupby('Région')['Total interventions'].sum().sort_values(ascending=False)
    st.bar_chart(reg)

    choose_reg = st.selectbox('Choose a region for the analysis :', df['Région'].unique())

    data = df[df['Région'] == choose_reg]

    for i in data.columns[3:]:
        data[i] = pd.to_numeric(data[i], errors='coerce')

    top_int = data.drop(columns=["Total interventions"]).iloc[:, 3:].sum().sort_values(ascending=False).head(10)

    pie = px.pie(data_frame=top_int, values=top_int.values, names=top_int.index,
                 title=f"Top 10 interventions in {choose_reg}")
    st.plotly_chart(pie)


    # All interventions by department
    st.subheader("All interventions by department")
    dep = df.groupby('Département')['Total interventions'].sum().sort_values(ascending=False)
    st.bar_chart(dep)

    choose_dep = st.selectbox('Choose a department for the analysis :', df['Département'].unique())

    data2 = df[df['Département'] == choose_dep]

    for i in data2.columns[3:]:
        data2[i] = pd.to_numeric(data2[i], errors='coerce')

    top_int = data2.drop(columns=["Total interventions"]).iloc[:, 3:].sum().sort_values(ascending=False).head(10)

    pie = px.pie(data_frame=top_int, values=top_int.values, names=top_int.index,
                 title=f"Top interventions in {choose_dep}")
    st.plotly_chart(pie)


    st.subheader('Fires By Region and Department')
    st.subheader('What are the most frequent fires per region and department ?')
    # Total fires by region
    st.subheader('Total of fires by region')

    fire = ['Feux dhabitations-bureaux', 'dont feux de cheminées', 'Feux dERP avec local à sommeil',
            'Feux dERP sans local à sommeil', 'Feux de locaux industriels', 'Feux de locaux artisanaux',
            'Feux de locaux agricoles', 'Feux sur voie publique', 'Feux de véhicules', 'Feux de végétations',
            'Autres feux', 'Incendies']

    for col in fire:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    df['Total Fires'] = df[fire].sum(axis=1)

    fire_reg = df.groupby('Région')['Total Fires'].sum().sort_values(ascending=False)

    source = ColumnDataSource(data=dict(regions=fire_reg.index.tolist(), counts=fire_reg.values))
    plot = figure(x_range=fire_reg.index.tolist(), plot_height=350)
    plot.vbar(x='regions', top='counts', width=0.9, source=source, color='red')
    plot.xaxis.major_label_orientation = 1.2
    st.bokeh_chart(plot)

    # Pie Chart of Types of Fire By Region
    st.subheader('Types fire by region')
    choose_reg = st.selectbox('Please select a region:', df['Région'].unique())
    reg_data = df[df['Région'] == choose_reg]

    reg_fire_sum = reg_data[fire].sum().sort_values(ascending=False)
    reg_fire_sum = pd.DataFrame(reg_fire_sum).reset_index()
    reg_fire_sum.columns = ["fire_types", "value"]

    reg_fire_sum['angle'] = reg_fire_sum['value'] / reg_fire_sum['value'].sum() * 2 * pi
    reg_fire_sum['percentage'] = (reg_fire_sum['value'] / reg_fire_sum['value'].sum() * 100).round()
    reg_fire_sum['fire_types'] = reg_fire_sum['fire_types'] + " (" + reg_fire_sum['percentage'].astype(str) + "%)"
    reg_fire_sum['color'] = viridis(len(reg_fire_sum))

    plot = figure(plot_height=350, title=f"Types of fire in {choose_reg}", toolbar_location=None,
                  tools="hover", tooltips="@fire_types: @value", x_range=(-0.5, 1.0))

    plot.wedge(x=0, y=1, radius=0.4,
               start_angle=cumsum('angle', include_zero=True), end_angle=cumsum('angle'),
               line_color="white", fill_color='color', legend_field='fire_types', source=reg_fire_sum)

    plot.axis.axis_label = None
    plot.axis.visible = False
    plot.grid.grid_line_color = None

    st.bokeh_chart(plot)

    # Treemap Total Fires by Department
    st.write("")
    st.subheader('Total fires by department')
    fire_dep = df.groupby(['Région', 'Département'])['Total Fires'].sum().reset_index()
    fig = px.treemap(fire_dep, path=['Région', 'Département'], values='Total Fires', color='Total Fires', color_continuous_scale='Reds')
    st.plotly_chart(fig)

    # Pie Chart of Types of Fire By Department
    st.subheader('Types of fire by department')
    choose_dep = st.selectbox('Please select a department:', df['Département'].unique())
    dep_data = df[df['Département'] == choose_dep]

    dep_fire_sum = dep_data[fire].sum().sort_values(ascending=False)
    dep_fire_sum = pd.DataFrame(dep_fire_sum).reset_index()
    dep_fire_sum.columns = ["fire_types", "value"]

    dep_fire_sum['angle'] = dep_fire_sum['value'] / dep_fire_sum['value'].sum() * 2 * pi
    dep_fire_sum['percentage'] = (dep_fire_sum['value'] / dep_fire_sum['value'].sum() * 100).round()
    dep_fire_sum['fire_types'] = dep_fire_sum['fire_types'] + " (" + dep_fire_sum['percentage'].astype(str) + "%)"
    dep_fire_sum['color'] = viridis(len(dep_fire_sum))

    plot2 = figure(plot_height=350, title=f"Types of fire in {choose_dep}", toolbar_location=None,
                       tools="hover", tooltips="@fire_types: @value", x_range=(-0.5, 1.0))

    plot2.wedge(x=0, y=1, radius=0.4,
                    start_angle=cumsum('angle', include_zero=True), end_angle=cumsum('angle'),
                    line_color="white", fill_color='color', legend_field='fire_types', source=dep_fire_sum)

    plot2.axis.axis_label = None
    plot2.axis.visible = False
    plot2.grid.grid_line_color = None

    print(df.columns)

    st.bokeh_chart(plot2)


    # Rescues
    st.write("")
    st.subheader('Rescues by Region and Department')
    st.subheader('What are the most frequent fires per region and department ?')

    rescue = ['Accidents sur lieux de travail', 'Accidents à domicile', 'Accidents de sport', 'Accidents sur voie publique',
                      'Secours en montagne', 'Malaises sur lieux de travail', 'Malaises à domicile : urgence vitale',
                      'Malaises à domicile : carence', 'Malaises en sport', 'Malaises sur voie publique', 'Autolyses',
                      'Secours en piscines ou eaux intérieures', 'Secours en mer (FDSM)', 'Intoxications',
                      'dont intoxications au CO', 'Autres SAV', 'Secours à victime', 'Relevage de personnes', 'Aides à personne',
                      'Secours à personne', 'Accidents routiers', 'Accidents ferroviaires', 'Accidents aériens',
                      'Accidents de navigation', 'Accidents de téléportage', 'Accidents de circulation', 'Odeurs - fuites de gaz',
                      'Odeurs (autres que gaz)', 'Pollutions - contaminations', 'Autres risques technologiques',
                      'Risques technologiques']


    for i in rescue :
        df[i] = pd.to_numeric(df[i], errors='coerce')

    df['Total Rescues'] = df[rescue].sum(axis=1)
    rescue_reg = df.groupby('Région')['Total Rescues'].sum().sort_values(ascending=False)

    # Bar chart for total accidents by region
    source_rescue = ColumnDataSource(data=dict(regions=rescue_reg.index.tolist(), counts=rescue_reg.values))
    plot3 = figure(x_range=rescue_reg.index.tolist(), plot_height=350, title="Total Rescues by Region")
    plot3.vbar(x='regions', top='counts', width=0.9, source=source_rescue, color='green')
    plot3.xaxis.major_label_orientation = 1.2
    st.bokeh_chart(plot3)

    # Pie Chart of Types of Rescue By Region
    st.subheader('Types of Rescues by Region')
    choose_reg = st.selectbox('Select a region:', df['Région'].unique())
    data_rescue = df[df['Région'] == choose_reg]
    reg_rescue_sum = data_rescue[rescue].sum().sort_values(ascending=False)
    reg_rescue_sum = pd.DataFrame(reg_rescue_sum).reset_index()
    reg_rescue_sum.columns = ["rescue", "value"]

    reg_rescue_sum['angle'] = reg_rescue_sum['value'] / reg_rescue_sum['value'].sum() * 2 * pi
    reg_rescue_sum['percentage'] = (reg_rescue_sum['value'] / reg_rescue_sum['value'].sum() * 100).round()
    reg_rescue_sum['rescue'] = reg_rescue_sum['rescue'] + " (" + reg_rescue_sum['percentage'].astype(str) + "%)"
    reg_rescue_sum['color'] = viridis(len(reg_rescue_sum))

    plot_rescue = figure(plot_height=350, title=f"Types of Rescues in {choose_reg}", toolbar_location=None,
                         tools="hover", tooltips="@rescue: @value", x_range=(-0.5, 1.0))
    plot_rescue.wedge(x=0, y=1, radius=0.4,
                      start_angle=cumsum('angle', include_zero=True), end_angle=cumsum('angle'),
                      line_color="white", fill_color='color', legend_field='rescue', source=reg_rescue_sum)
    plot_rescue.axis.axis_label = None
    plot_rescue.axis.visible = False
    plot_rescue.grid.grid_line_color = None

    st.bokeh_chart(plot_rescue)

    # Treemap Total Rescues by Department
    st.write("")
    st.subheader('Total rescues by department')
    rescue_dep = df.groupby(['Région', 'Département'])[
        'Total Rescues'].sum().reset_index()
    fig_rescue = px.treemap(rescue_dep, path=['Région', 'Département'], values='Total Rescues', color='Total Rescues',color_continuous_scale='Greens')
    st.plotly_chart(fig_rescue)

    # Pie Chart of Types of Rescue By Department
    st.subheader('Types of rescue by department')
    choose_dep = st.selectbox('Select a department:', df['Département'].unique())
    dep_data = df[df['Département'] == choose_dep]

    dep_rescue_sum = dep_data[rescue].sum().sort_values(ascending=False)
    dep_rescue_sum = pd.DataFrame(dep_rescue_sum).reset_index()
    dep_rescue_sum.columns = ["rescue_types", "value"]

    dep_rescue_sum['angle'] = dep_rescue_sum['value'] / dep_rescue_sum['value'].sum() * 2 * pi
    dep_rescue_sum['percentage'] = (dep_rescue_sum['value'] / dep_rescue_sum['value'].sum() * 100).round()
    dep_rescue_sum['rescue_types'] = dep_rescue_sum['rescue_types'] + " (" + dep_rescue_sum['percentage'].astype(str) + "%)"
    dep_rescue_sum['color'] = viridis(len(dep_rescue_sum))

    plot5 = figure(plot_height=350, title=f"Types of rescues in {choose_dep}", toolbar_location=None,
                              tools="hover", tooltips="@rescue_types: @value", x_range=(-0.5, 1.0))

    plot5.wedge(x=0, y=1, radius=0.4,
                           start_angle=cumsum('angle', include_zero=True), end_angle=cumsum('angle'),
                           line_color="white", fill_color='color', legend_field='rescue_types', source=dep_rescue_sum)

    plot5.axis.axis_label = None
    plot5.axis.visible = False
    plot5.grid.grid_line_color = None

    st.bokeh_chart(plot5)


else:
    st.write("Please upload a CVS dataset to start the analysis")
