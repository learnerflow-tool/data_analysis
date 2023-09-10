import seaborn as sns
import pandas as pd
import plotly.graph_objects as go
import chart_studio.plotly as py
import plotly

data = pd.read_csv('your/path/to/the/raw/data.csv')[
    ['user_id', 'session_id', 'event_name', 'time_event']]

# Start with making sure that time_event and time_insrall are Pandas Datetime types:
data['time_event'] = pd.to_datetime(data['time_event'])
data['session_id'] = pd.to_datetime(data['session_id'])

# Make sure that there's no event occurring before session_id
data = data[data.time_event >= data.session_id]


# The initial data Pandas DataFrame must have these 4 columns:
# user_id | session_id | event_name | time_event
# - user_id (string): the unique identifier of a user
# - session_id (Pandas datetime): the time when the user installed the app (there should be 1 session_id per user_id)
# - event_name (string): the name of a specific in-app event (there can be many event_name per user_id)
# - time_event (Pandas datetime): the time of each event (there should be 1 time_event per user_id)

# Edit this dataframe so that installs are passed as events

# Create a new DF from the data DF containing only install data
installs = data[['user_id', 'session_id']].sort_values(
    'session_id').drop_duplicates('user_id')

# Create an install column containing dummy "install" events
installs['event_name'] = 'install'

# Create an event_type column to keep the information of install vs other events
installs['event_type'] = 'install'

# Rename session_id to time_event

installs.rename(columns={'session_id': 'time_event'}, inplace=True)

# In the data DF, keep only events data and create the event_type column
data = data[['user_id', 'event_name',
             'time_event']].drop_duplicates()
data['event_type'] = 'in_app_action'

# Concatenate the two DataFrames
data = pd.concat([data, installs[data.columns]])

# Based on the time of events, we can compute the rank of each action at the user_id level:

# a) Sort ascendingly per user_id and time_event
# sort by event_type to make sure installs come first
data.sort_values(['user_id', 'event_type', 'time_event'],
                 ascending=[True, False, True], inplace=True)

# b) Group by user_id
grouped = data.groupby('user_id')

# c) Define a ranking function based on time_event, using the method = 'first' param to ensure no events have the same rank


def rank(x): return x['time_event'].rank(method='first').astype(int)


# d) Apply the ranking function to the data DF into a new "rank_event" column
data["rank_event"] = grouped.apply(rank).reset_index(0, drop=True)

# Add, each row, the information about the next_event

# a) Regroup by user_id
grouped = data.groupby('user_id')

# b) The shift function allows to access the next row's data. Here, we'll want the event name


def get_next_event(x): return x['event_name'].shift(-1)


# c) Apply the function into a new "next_event" column
data["next_event"] = grouped.apply(
    lambda x: get_next_event(x)).reset_index(0, drop=True)

# Likewise, we can compute time from each event to its next event:

# a) Regroup by user_id
grouped = data.groupby('user_id')

# b) We make use one more time of the shift function:


def get_time_diff(
    x): return x['time_event'].shift(-1) - x['time_event']


# c) Apply the function to the data DF into a new "time_to_next" column
data["time_to_next"] = grouped.apply(
    lambda x: get_time_diff(x)).reset_index(0, drop=True)

# Here we'll plot the journey up to the 10th action. This can be achieved by filtering the dataframe based on the rank_event column that we computed:
data = data[data.rank_event < 10]

# Check that you have only installs at rank 1:
data[data['rank_event'] == 1].event_name.unique()

# Working on the nodes_dict

all_events = list(data.event_name.unique())

# Create a set of colors that you'd like to use in your plot.
palette = ['50BE97', 'E4655C', 'FCC865',
           'BFD6DE', '3E5066', '353A3E', 'E6E6E6']
#  Here, I passed the colors as hex, but we need to pass it as RGB. This loop will do:
for i, col in enumerate(palette):
    palette[i] = tuple(int(col[i:i+2], 16) for i in (0, 2, 4))

# Append a Seaborn complementary palette to your palette in case you did not provide enough colors to style every event
complementary_palette = sns.color_palette(
    "deep", len(all_events) - len(palette))
if len(complementary_palette) > 0:
    palette.extend(complementary_palette)

output = dict()
output.update({'nodes_dict': dict()})

i = 0
for rank_event in data.rank_event.unique():  # For each rank of event...
    # Create a new key equal to the rank...
    output['nodes_dict'].update(
        {rank_event: dict()}
    )

    # Look at all the events that were done at this step of the funnel...
    all_events_at_this_rank = data[data.rank_event ==
                                   rank_event].event_name.unique()

    # Read the colors for these events and store them in a list...
    rank_palette = []
    for event in all_events_at_this_rank:
        rank_palette.append(palette[list(all_events).index(event)])

    # Keep trace of the events' names, colors and indices.
    output['nodes_dict'][rank_event].update(
        {
            'sources': list(all_events_at_this_rank),
            'color': rank_palette,
            'sources_index': list(range(i, i+len(all_events_at_this_rank)))
        }
    )
    # Finally, increment by the length of this rank's available events to make sure next indices will not be chosen from existing ones
    i += len(output['nodes_dict'][rank_event]['sources_index'])

# Working on the links_dict

output.update({'links_dict': dict()})

# Group the DataFrame by user_id and rank_event
grouped = data.groupby(['user_id', 'rank_event'])

# Define a function to read the souces, targets, values and time from event to next_event:


def update_source_target(user):
    try:
        source_index = output['nodes_dict'][user.name[1]]['sources_index'][output['nodes_dict']
                                                                           [user.name[1]]['sources'].index(user['event_name'].values[0])]

        target_index = output['nodes_dict'][user.name[1] + 1]['sources_index'][output['nodes_dict']
                                                                               [user.name[1] + 1]['sources'].index(user['next_event'].values[0])]

        if source_index in output['links_dict']:
            if target_index in output['links_dict'][source_index]:

                output['links_dict'][source_index][target_index]['unique_users'] += 1
                output['links_dict'][source_index][target_index]['avg_time_to_next'] += user['time_to_next'].values[0]
            else:

                output['links_dict'][source_index].update({target_index:
                                                           dict(
                                                               {'unique_users': 1,
                                                                'avg_time_to_next': user['time_to_next'].values[0]}
                                                           )
                                                           })
        else:

            output['links_dict'].update({source_index: dict({target_index: dict(
                {'unique_users': 1, 'avg_time_to_next': user['time_to_next'].values[0]})})})
    except Exception as e:
        pass


# Apply the function to your grouped Pandas object:
grouped.apply(lambda user: update_source_target(user))


targets = []
sources = []
values = []
time_to_next = []

for source_key, source_value in output['links_dict'].items():
    for target_key, target_value in output['links_dict'][source_key].items():
        sources.append(source_key)
        targets.append(target_key)
        values.append(target_value['unique_users'])
        time_to_next.append(str(pd.to_timedelta(
            target_value['avg_time_to_next'] / target_value['unique_users'])).split('.')[0])  # Split to remove the milliseconds information

labels = []
colors = []
for key, value in output['nodes_dict'].items():
    labels = labels + list(output['nodes_dict'][key]['sources'])
    colors = colors + list(output['nodes_dict'][key]['color'])

for idx, color in enumerate(colors):
    colors[idx] = "rgb" + str(color) + ""

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

fig.update_layout(autosize=True, title_text="Module",
                  font=dict(size=15), plot_bgcolor='white')

publish_to_web = True
if publish_to_web:
    py.iplot(fig, filename='user_journey')
else:
    fig.show(renderer='chrome')
