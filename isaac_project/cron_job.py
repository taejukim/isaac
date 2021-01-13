# Crontab Schedule
jobs =[
    ('*/5 * * * 1-5','apps.dooray.collect_dooray.main', '>> ~/logs/collect_dooray.log'),
]
 