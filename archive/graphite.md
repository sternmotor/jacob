collectd.cache03_opd_xres_rz1_xtrav_de.disk-vda.disk_io_time.io_time



* Pull graphite data (browser Test> JSON Rohdaten> Einheitlich formatieren) [URL|http://graphite01.app.infra.rz1.xtrav.de/render?&format=json
&maxDataPoints=10000
&from=-1h
&target=collectd.cache03_opd_xres_rz1_xtrav_de.disk-vda.disk_io_time.io_time
]


* [Graphite API funktions|https://graphite.readthedocs.io/en/latest/render_api.html]



Selecting metrics

&target=aggregate(host.cpu-[0-7].cpu-{user,system}.value, "sum")

stdev(seriesList, points, windowTolerance=0.1)
 stddevSeries(*seriesLists) is an alias for aggregate with aggregation stddev.



&target=aggregate(host.cpu-[0-7].cpu-{user,system}.value, "stdev")
&target=aggregate(host.cpu-[0-7].cpu-{user,system}.value, "average")



&format=png: Renders a graph as a 330×250 px png.
&format=svg : Renders a graph as a 330×250 px svg.
&format=raw: Line-delimited output. (target, start timestamp, end timestamp, step, data)
&format=csv: Creates a CSV file to download (metric,date/time,value)
&format=json: Returns a JSON object.

s   Seconds
min     Minutes
h   Hours
d   Days
w   Weeks
mon     Month (30 Days)
y   Year (365 Days)
