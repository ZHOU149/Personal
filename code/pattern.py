lookiter_pattern_notindb = "%{TIMESTAMP_ISO8601:log_date_time}.*@WifiAps, lookiter, .*, notindb"

lookiter_pattern_unknown = "%{TIMESTAMP_ISO8601:log_date_time}.*@WifiAps, lookiter, .*, unknown"

lookiter_pattern_valid =  "%{TIMESTAMP_ISO8601:log_date_time}.*@WifiAps, lookiter, .*, %{NUMBER:latitude:float}, %{NUMBER:longitude:float}, hacc, %{NUMBER:hacc:float}," \
                " reach, %{NUMBER:reach:float}, altitude, %{NUMBER:altitude:float}, vacc, %{NUMBER:vacc:float}, src, %{WORD:src}, query age, %{NUMBER:query_age:float} days"

ClxWifi_pattern = "%{TIMESTAMP_ISO8601:log_date_time}.*@ClxWifi, Fix, 1, ll, %{NUMBER:latitude:float}, %{NUMBER:longitude:float}, acc, %{NUMBER:acc:float}," \
                " course, %{NUMBER:course:float}, alt, %{NUMBER:alt:float}, altunc, %{NUMBER:altunc:float}, timestamp, %{NUMBER:time:float}"

Gps_pattern = "%{TIMESTAMP_ISO8601:log_date_time}.*@ClxGpsVendor, Fix, 1, ll, %{NUMBER:latitude:float}, %{NUMBER:longitude:float}, acc, %{NUMBER:acc:float}," \
        " speed, %{NUMBER:speed:float}, course, %{NUMBER:course:float}, imag, %{NUMBER:imag:float}, alt, %{NUMBER:alt:float}, altunc, %{NUMBER:altunc:float}," \
        " ellipsoidalAlt, %{NUMBER:ellipsoidalAlt:float}, speedUnc, %{NUMBER:speedUnc:float}, courseUnc, %{NUMBER:courseUnc:float}, timestamp," \
        " %{NUMBER:time:float}, isGnssLocationService, %{NUMBER:isGnssLocationService:float}"