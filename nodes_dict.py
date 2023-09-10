import seaborn as sns

# Working on the nodes_dict

all_events = list(data.event_name.unique())

# Create a set of colors that you'd like to use in your plot.
palette = ['50BE97', 'E4655C', 'FCC865',
           'BFD6DE', '3E5066', '353A3E', 'E6E6E6']
#  Here, I passed the colors as HEX, but we need to pass it as RGB. This loop will convert from HEX to RGB:
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
for rank_event in data.rank_event.unique(): # For each rank of event...
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
