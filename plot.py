import plotly.graph_objects as go
import chart_studio.plotly as py
import plotly

fig = go.Figure(data=[go.Sankey(
    node=dict(
        thickness=10,  # default is 20
        line=dict(color="black", width=0.5),
        label=labels,
        color=colors
    ),
    link=dict(
        source=sources,
        target=targets,
        value=values,
        label=time_to_next,
        hovertemplate='%{value} unique users went from %{source.label} to %{target.label}.<br />' +
        '<br />It took them %{label} in average.<extra></extra>',
    ))])

fig.update_layout(autosize=True, title_text="Medium app", font=dict(size=15), plot_bgcolor='white')

publish_to_web = True
if publish_to_web:
   py.iplot(fig, filename='user_journey')
else:
   fig.show(renderer='chrome')
