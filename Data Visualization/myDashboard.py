import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import pandas as pd
from dash import callback, Output, Input
import plotly.express as px

app = dash.Dash()
df_degrees = pd.read_csv('data/degrees-that-pay-back.csv')
df_college = pd.read_csv('data/salaries-by-college-type.csv')
df_region = pd.read_csv('data/salaries-by-region.csv')

degrees_indicators = df_degrees.columns[1:]
degrees_indicators = degrees_indicators.drop('Percent change from Starting to Mid-Career Salary')
# 学校类型
school_types = list(set(df_college['School Type'].values.tolist()))
school_types_count = []
for school_type in school_types:
    rows = df_college.loc[df_college['School Type'] == school_type]
    school_types_count.append(rows.size)
# 学校地区
school_regions = list(set(df_region['Region'].values.tolist()))
school_regions_count = []
for school_region in school_regions:
    rows = df_region.loc[df_region['Region'] == school_region]
    school_regions_count.append(rows.size)


def covert_currency(x):  # 1定义改变货币的函数
    if x == 0:
        return 0
    else:
        return pd.to_numeric(x.replace("$", "").replace(",", ""))


app.layout = html.Div([
    html.H1("Salaries for different majors"),
    html.Div(children=[
        html.Div(children=[
            dcc.Dropdown(
                id='salary-degree-type',
                options=[{'label': i, 'value': i} for i in degrees_indicators],
                value='Starting Median Salary'
            ),
            dcc.Graph(
                id='salary-degree-diagram',
                figure={},
                hoverData={'points': [{'y': 'Accounting'}]}
            ),
        ], style={'width': '49%', 'display': 'inline-block', 'padding': '0 20'}),
        html.Div(children=[
            # 薪资趋势图表
            dcc.Graph(
                id='salary-trend-diagram',
                figure={},
            ),
            # 薪资提升百分比图表
            dcc.Graph(
                id='salary-percent-diagram',
                figure={},
            ),
        ], style={'width': '49%', 'display': 'inline-block', 'padding': '0 20'})
    ]),
    html.H1("Salaries for different college types"),
    html.Div(children=[
        html.Div(children=[
            dcc.Graph(
                id='school-type-diagram',
                figure=go.Figure(
                    data=go.Pie(
                        labels=school_types,
                        values=school_types_count,
                        textinfo='label+percent'
                    ),
                    layout=go.Layout(
                        height=700,
                        hovermode='closest',
                    )
                ),
                hoverData={'points': [{'label': 'Liberal Arts', 'color': '#EF553B'}]}
            ),
        ], style={'width': '49%', 'display': 'inline-block', 'padding': '0 20'}),
        html.Div(children=[
            dcc.Dropdown(
                id='salary-degree-type-1',
                options=[{'label': i, 'value': i} for i in degrees_indicators],
                value='Starting Median Salary'
            ),
            dcc.Graph(
                id='salary-college-diagram',
                figure={},
            )
        ], style={'width': '49%', 'display': 'inline-block', 'padding': '0 20'})
    ]),
    html.H1("Salaries for different regions"),
    html.Div(children=[
        html.Div(children=[
            dcc.Graph(
                id='school-region-diagram',
                figure=go.Figure(
                    data=go.Pie(
                        labels=school_regions,
                        values=school_regions_count,
                        textinfo='label+percent'
                    ),
                    layout=go.Layout(
                        height=700,
                        hovermode='closest',
                    )
                ),
                hoverData={'points': [{'label': 'Southern', 'color': '#EF553B'}]}
            ),
        ], style={'width': '49%', 'display': 'inline-block', 'padding': '0 20'}),
        html.Div(children=[
            dcc.Dropdown(
                id='salary-degree-type-2',
                options=[{'label': i, 'value': i} for i in degrees_indicators],
                value='Starting Median Salary'
            ),
            dcc.Graph(
                id='salary-region-diagram',
                figure={},
            )
        ], style={'width': '49%', 'display': 'inline-block', 'padding': '0 20'})
    ]),
])


@callback(
    Output(component_id='salary-degree-diagram', component_property='figure'),
    Input(component_id='salary-degree-type', component_property='value')
)
def get_salary_degree_diagram(col_chosen):
    x_axis = df_degrees[col_chosen].apply(lambda x: covert_currency(x))
    # 生成颜色列表
    colorscale = px.colors.sequential.Purples

    # 计算数据范围
    data_range = [0, x_axis.max()]
    start = go.Bar(
        y=df_degrees['Undergraduate Major'],
        x=x_axis,
        name="Salary",
        showlegend=True,
        orientation='h',
        marker=dict(
            color=x_axis,
            colorscale=colorscale,
            cmin=data_range[0],
            cmax=data_range[1]
        )
    )
    layout = go.Layout(
        barmode='group',  # 可以分为 ‘stack’(叠加）、‘group’（分组）、‘overlay’（重叠）、‘relative’（相关）， 默认是‘group’
        barnorm='',  # 设置柱形图纵轴或横轴数据的表示形式，可以是fraction（分数），percent（百分数）

        height=900,
        hovermode='closest',
        legend=dict(
            x=0.8,
            y=1.05,
            xanchor="left",
            yanchor="top",
            orientation="h"
        )
    )
    return go.Figure(
        data=start,
        layout=layout
    )


@app.callback(
    dash.dependencies.Output('salary-trend-diagram', 'figure'),
    [dash.dependencies.Input('salary-degree-diagram', 'hoverData')])
def get_salary_trend_diagram(hoverData):
    degree = hoverData['points'][0]['y']
    major_row = df_degrees.loc[df_degrees['Undergraduate Major'] == degree]

    x_axis = ['Starting Median Salary', 'Mid-Career 10th Percentile Salary', 'Mid-Career 25th Percentile Salary',
              'Mid-Career Median Salary', 'Mid-Career 75th Percentile Salary', 'Mid-Career 90th Percentile Salary']
    y_axis = major_row.loc[:, x_axis].values.tolist()[0]
    y_axis = [covert_currency(x) for x in y_axis]

    # 生成颜色列表
    colorscale = px.colors.sequential.Greens

    # 计算数据范围
    data_range = [0, max(y_axis)]

    salaryBar = go.Bar(
        x=x_axis,
        y=y_axis,
        name='Salary',
        marker=dict(
            color=y_axis,
            colorscale=colorscale,
            cmin=data_range[0],
            cmax=data_range[1]
        )
    )
    salaryScatter = go.Scatter(
        x=x_axis,
        y=y_axis,
        name='Salary',
        showlegend=False
    )
    layout = go.Layout(
        yaxis={'range': [0, 220000]},

    )
    fig = go.Figure(
        data=[salaryBar, salaryScatter],
        layout=layout
    )
    fig.add_annotation(x=0, y=1.05, xanchor='left', yanchor='bottom',
                       xref='paper', yref='paper', showarrow=False, align='left',
                       text="Major:{}".format(degree))
    return fig


@app.callback(
    dash.dependencies.Output('salary-percent-diagram', 'figure'),
    [dash.dependencies.Input('salary-degree-diagram', 'hoverData')])
def get_salary_percent_diagram(hoverData):
    # 获取到某一个专业的信息
    degree = hoverData['points'][0]['y']
    major_row = df_degrees.loc[df_degrees['Undergraduate Major'] == degree]

    percentBar = go.Bar(
        x=df_degrees['Undergraduate Major'],
        y=df_degrees['Percent change from Starting to Mid-Career Salary'],
        width=[0.5 for _ in range(df_degrees['Percent change from Starting to Mid-Career Salary'].size)],
        name="Percent change from Starting to Mid-Career Salary",
        showlegend=True,
        marker=dict(
            color=df_degrees['Percent change from Starting to Mid-Career Salary'],
        )
    )
    layout = go.Layout(
        legend=dict(
            x=0.5,
            y=1.2,
            xanchor="left",
            yanchor="top",
            orientation="h"
        )
    )

    percentBar.marker.color[major_row.index] = 0
    lst = list(percentBar.width)
    lst[major_row.index.values[0]] = 1
    percentBar.width = tuple(lst)
    return go.Figure(
        data=percentBar,
        layout=layout
    )


@app.callback(
    dash.dependencies.Output('salary-college-diagram', 'figure'),
    [dash.dependencies.Input('school-type-diagram', 'hoverData'),
     dash.dependencies.Input('salary-degree-type-1', 'value')])
def get_salary_college_diagram(hoverData, col_chosen):
    schoolType = hoverData['points'][0]['label']
    color = hoverData['points'][0]['color']
    new_df_college = df_college.loc[df_college['School Type'] == schoolType]
    collegeBox = go.Bar(
        y=new_df_college['School Name'],
        x=new_df_college[col_chosen],
        name="Salary",
        showlegend=True,
        orientation='h',
        marker=dict(
            color=color
        )
    )
    layout = go.Layout(
        height=700,
        hovermode='closest',
    )
    return go.Figure(
        data=collegeBox,
        layout=layout
    )


@app.callback(
    dash.dependencies.Output('salary-region-diagram', 'figure'),
    [dash.dependencies.Input('school-region-diagram', 'hoverData'),
     dash.dependencies.Input('salary-degree-type-2', 'value')])
def get_salary_region_diagram(hoverData, col_chosen):
    schoolRegion = hoverData['points'][0]['label']
    color = hoverData['points'][0]['color']
    new_df_region = df_region.loc[df_region['Region'] == schoolRegion]
    regionBox = go.Bar(
        y=new_df_region['School Name'],
        x=new_df_region[col_chosen].apply(lambda x: covert_currency(x)),
        name="Salary",
        showlegend=True,
        orientation='h',
        marker=dict(
            color=color
        )
    )
    layout = go.Layout(
        height=700,
        hovermode='closest',
    )
    return go.Figure(
        data=regionBox,
        layout=layout
    )


if __name__ == '__main__':
    app.run_server()
