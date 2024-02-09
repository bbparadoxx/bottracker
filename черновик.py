from datetime import datetime, timedelta
from pytz import timezone

# fmt = "%Y-%m-%d %H:%M:%S"
#
# # Current time in UTC
# now_utc_1 = datetime.now(timezone('UTC')) + timedelta(hours= 1)
# now_utc = datetime.now(timezone('UTC'))
# print(now_utc.strftime(fmt), now_utc_1.strftime(fmt))

now = int(str(datetime.now().astimezone())[-6:-3])
# local_tzname = local_tz.tzname(local_now)
print(now)
