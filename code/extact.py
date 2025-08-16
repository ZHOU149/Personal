from pygrok import Grok
import argparse
import json
import pattern
import logging
import pandas as pd
from geopy import distance

# command = '''log show --archive ~/Downloads/system_logs.logarchive --predicate "process == 'locationd'" > ~/Downloads/locationd.log'''
# subprocess.run(command, shell=True, text=True)
def fill_with_empty_value(data):
    all_keys = set()
    for d in data:
        all_keys.update(d.keys())

    for d in data:
        for key in all_keys:
            d.setdefault(key, " ")

    return data

parser = argparse.ArgumentParser(description="input")
parser.add_argument("--input", default="locationd.log", help="raw log archive name")
parser.add_argument("--output", default="location_result.json", help="parsed locationd log name")

stastic = False
stastic_location = ()

args = parser.parse_args()

Wifi_position_list = []
Gps_position_list = []
data_groups = []
result = {}

with open(args.input, 'r', encoding='utf-8') as file:

    data_group = {}
    mac_address_list = []
    wifi_fix_index = 1
    mac_address_index = 1

    for line in file:
        if "@WifiAps, lookiter" in line:

            data = Grok(pattern.lookiter_pattern_valid).match(line)
            if "notindb" in line:
                notindb_data = Grok(pattern.lookiter_pattern_notindb).match(line)
            elif "unknown" in line:
                unknown_data = Grok(pattern.lookiter_pattern_unknown).match(line)

            if data is not None:
                data = {'index': mac_address_index, "type": "valid", **data}
                mac_address_index = mac_address_index + 1

                mac_address_list.append(data)

            elif notindb_data is not None:
                notindb_data = {'index': mac_address_index, "type": "notindb", **notindb_data}
                mac_address_index = mac_address_index + 1
                mac_address_list.append(notindb_data)

            elif unknown_data is not None:
                unknown_data = {'index': mac_address_index, "type": "unknown", **unknown_data}
                mac_address_index = mac_address_index + 1
                mac_address_list.append(unknown_data)

            else:
                logging.warning("Found Lookiter but not match: " + line)

        if "@ClxWifi, Fix, 1, ll" in line:

            grok = Grok(pattern.ClxWifi_pattern)
            data = grok.match(line)
            if data is not None:
                data = {'index': wifi_fix_index, **data}

                # add to position list
                Wifi_position_list.append(data)

                data_group["fix"] = data
                data_group["mac_address"] = fill_with_empty_value(mac_address_list)
                data_groups.append(data_group)
                mac_address_list = []
                data_group = {}
                mac_address_index = 1

                wifi_fix_index = wifi_fix_index + 1
            else:
                logging.warning("Found ClxWifi but not match: " + line)

        if "@ClxGpsVendor, Fix, 1, ll" in line:
            
            grok = Grok(pattern.Gps_pattern)
            data = grok.match(line)
            if data is not None:
                Gps_position_list.append(data)
            else:
                logging.warning("Found GPS but not match: " + line)

distances = []

time = []
hacc = []
hErr = []
hErr_ratio = []

for wifi_location in Wifi_position_list:
    match_time = 999
    ground_truth = (0, 0)

    # if given stastic data, use fix location else match it with GPS location
    if(stastic):
        ground_truth = stastic_location
        match_time = 0
    
    else:
        for gps_location in Gps_position_list:
            time_distance = abs(gps_location["time"] - wifi_location["time"])

            if(time_distance < match_time):
                match_time = time_distance
                ground_truth = (gps_location["latitude"], gps_location["longitude"])

    # when match 
    if(match_time < 1):
        current_location = (wifi_location["latitude"], wifi_location["longitude"])
        dis = distance.distance(ground_truth, current_location).meters
        distances.append(dis)

        # error = {"ground_truth": ground_truth, "distance": dis}
        data_groups[Wifi_position_list.index(wifi_location)]["fix"]["ground_truth"] = ground_truth
        data_groups[Wifi_position_list.index(wifi_location)]["fix"]["distance"] = dis

        # add KPI graph data
        time.append(data_groups[Wifi_position_list.index(wifi_location)]["fix"]["log_date_time"].split(".")[0])

        acc = data_groups[Wifi_position_list.index(wifi_location)]["fix"]["acc"]
        hacc.append(acc)

        hErr.append(dis)

        hErr_ratio.append(dis/acc)

hacc_CDF_x = sorted(hacc)
hacc_CDF_y = [ x /len(hacc) for x in range(1, len(hacc) + 1)]

hErr_CDF_x = sorted(hErr)
hErr_CDF_y = [ x /len(hErr) for x in range(1, len(hErr) + 1)]

hErr_ratio_CDF_x = sorted(hErr_ratio)
hErr_ratio_CDF_y = [ x /len(hErr_ratio) for x in range(1, len(hErr_ratio) + 1)]


graph_data = {
    "time": time,
    "hacc" : hacc,
    "hErr" : hErr,
    "hErr_ratio" : hErr_ratio,
    "hacc_CDF_x": hacc_CDF_x,
    "hacc_CDF_y": hacc_CDF_y,
    "hErr_CDF_x": hErr_CDF_x,
    "hErr_CDF_y": hErr_CDF_y,
    "hErr_ratio_CDF_x": hErr_ratio_CDF_x,
    "hErr_ratio_CDF_y": hErr_ratio_CDF_y,
}

# calculate percentile and convert it to dict
percentiles = [0.5, 0.67, 0.95, 0.97, 1.0]

results = pd.Series(distances).quantile(percentiles)
hErr_kpi_data = {f"{int(p*100)}%": results[p] for p in percentiles}

results = pd.Series(hacc).quantile(percentiles)
hacc_kpi_data = {f"{int(p*100)}%": results[p] for p in percentiles}

results = pd.Series(hErr_ratio).quantile(percentiles)
hErr_ratio_kpi_data = {f"{int(p*100)}%": results[p] for p in percentiles}

kpi_data = {
    "hErr_KPI" : hErr_kpi_data,
    "hacc_KPI": hacc_kpi_data,
    "hErr_ratio_KPI" : hErr_ratio_kpi_data
}

result["KPI"] = kpi_data
result["data_groups"] = data_groups
result["graph_data"] = graph_data

with open(args.output, "w") as f:
    json.dump(result, f, indent=4)