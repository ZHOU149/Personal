
// two table
const location_table = new DataTable('#location_table');
const mac_table = $('#mac_table').DataTable( {
  columnDefs: [
    {
        targets: 1,
        className: 'dt-center'
    }
  ]
} );

// map used
var map = null;

// record current selected row
var marker;
var HighligtRow;

// use to load two data group
var location_count = 1;
var mac_count = 1;
var location_groups = [];

const dotIcon = L.divIcon({
    className: 'custom-black-dot-icon',
    iconSize: [10, 10]
    
});

const redIcon = L.icon({
  iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-red.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41]
});

//initialize
var location_group = [];
fetch('location_result.json')
.then(response => response.json())
.then(datas => {
    
    datas.data_groups.forEach( data_group => {

        location_group = [];

        var fix_data = data_group.fix;
        location_group.push(fix_data);

        // record mac datas
        var mac_datas = data_group.mac_address;
        mac_datas.forEach( mac_data => {
            location_group.push(mac_data);
        })
        location_groups.push(location_group);

        fix_data.index = "▶ " + fix_data.index;
        // console.log(fix_data.ground_truth)
        if(fix_data.ground_truth == null) {
            fix_data.ground_truth = "N/A";
            fix_data.error = "N/A";
        }
        else {
            fix_data.distance = fix_data.distance.toFixed(2);
        }

        // console.log(fix_data);
        fix_data.time = fix_data.time.toFixed(2);

        location_table.row.add(Object.values(fix_data)).draw(false);

        // add marker for first location 
        if (fix_data.index == "▶ 1") {
            var latitude = fix_data.latitude;
            var longitude = fix_data.longitude;
            map = L.map('map').setView([latitude, longitude], 15);
            L.tileLayer(
                'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
                {attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'}
            ).addTo(map);

            marker = add_marker(location_table.row(0).data(), true);
        }
    });
})
.catch(
    error => {}
);

// show all location
var all_marker = [];
var show = false;
function showAll() {

    if (marker != null) {
        remove_marker(marker);
    }

    if (HighligtRow != null) {
        $(HighligtRow).removeClass("highlight");
    }

    if (!show) {
        location_table.rows().every( 
            function(rowIdx, tableLoop, rowLoop) {
                var data = this.data();
                var m = add_marker(data);
                all_marker.push(m);
            }
        );
        show = true;
    } else {
        all_marker.forEach(
            m => { remove_marker(m); }
        );
        show = false;
    }
}

// on click location row
location_table.on('click', 'tr', function () {

    var data = location_table.row(this).data();
    if (data) {
        if(marker != null){
            remove_marker(marker);
        }
        marker = add_marker(data, true);
    }
})

// remove main marker
function remove_marker(marker)
{
    marker["marker"].forEach(
        m => { map.removeLayer(m); }
    );

    marker["circle"].forEach(
        c => { map.removeLayer(c); }
    );
}

var mac_high_light_row;
// on click mac row
mac_table.on('click', 'tr', function () {
    if (mac_high_light_row != null){
        $(mac_high_light_row).removeClass("highlight");
    }
    mac_high_light_row = mac_table.row(this).node();
    $(mac_high_light_row).addClass('highlight');
})

// ad marker and circle to map
function add_marker(row_data, highlight)
{
    var index = parseInt(row_data[0].substring(2, row_data.length)) - 1;
    var data = location_groups[index][0];

    var timestamp = data.log_date_time;
    var latitude = data.latitude;
    var longitude = data.longitude;
    var acc = data.acc;
    var marker_list = [];
    var circle_list = [];
    var mac_address = location_groups[index];

    if (highlight) {
        if (HighligtRow != null){
            $(HighligtRow).removeClass("highlight");
        }
        HighligtRow = location_table.row(index).node();
        // console.log(HighligtRow);
        $(HighligtRow).addClass('highlight');
    }

    var popup_text = "index: " + index + "<br> TimeStamp: " + timestamp;

    // create location marker
    marker_list.push(L.marker([latitude, longitude]).addTo(map).bindPopup(popup_text).openPopup());

    // creat ground truth
    console.log("ground truth", data.ground_truth)
    if(data.ground_truth != "N/A")
    {
        marker_list.push(L.marker([data.ground_truth[0], data.ground_truth[1]], { icon: redIcon }).addTo(map));
        var line = L.polyline([[latitude, longitude], [data.ground_truth[0], data.ground_truth[1]]], {
                color: 'blue',
                weight: 4, 
                opacity: 0.7
        }).addTo(map);
        marker_list.push(line);
    }

    if(highlight)
    {
        circle_list.push(L.circle([latitude, longitude], {radius: acc, color: 'lightblue', fillColor: 'lightblue', fillOpacity: 0.0 }).addTo(map));
    }

    // clear the table
    mac_table.clear().draw(false);
    
    // start from i = 1, index 0 is the data for fix
    for(var i=1; i < mac_address.length; i++)
    {
        var mac = mac_address[i];
        if(mac.type == "valid"){   
            var mac_altitude = mac.latitude;
            var mac_longitude = mac.longitude;
            var mac_acc = mac.hacc;
            mac_table.row.add(Object.values(mac)).draw(false);
            marker_list.push(L.marker([mac_altitude, mac_longitude], { icon: dotIcon }).addTo(map));
            // c.push(L.circle([mac_altitude, mac_longitude], {radius: mac_acc, color: 'lightblue', fillColor: 'lightblue', fillOpacity: 0.0 }).addTo(map));
        }
        else{
            mac_table.row.add(Object.values(mac)).draw(false);
        }
    };
    return {"marker":marker_list, "circle":circle_list};
}