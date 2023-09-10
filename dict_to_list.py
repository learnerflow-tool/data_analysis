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
            target_value['avg_time_to_next'] / target_value['unique_users'])).split('.')[0]) # Split to remove the milliseconds information

labels = []
colors = []
for key, value in output['nodes_dict'].items():
    labels = labels + list(output['nodes_dict'][key]['sources'])
    colors = colors + list(output['nodes_dict'][key]['color'])

for idx, color in enumerate(colors):
    colors[idx] = "rgb" + str(color) + ""