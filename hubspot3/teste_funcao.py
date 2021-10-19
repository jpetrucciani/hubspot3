from hubspot3 import Hubspot3
import datetime as dt
from datetime import timedelta


hapikey = "d20d1047-9aa7-4050-9ce1-5aa6610256d6"

end_date = dt.datetime.now()
start_date = int((end_date - timedelta(seconds=5*60)).timestamp())*1000
end_date = int(end_date.timestamp())*1000

connection = Hubspot3(api_key=hapikey)

cc = connection.contacts.get_recently_modified(start_date=start_date, end_date=end_date)

cc_list = list(cc)