import locale
locale.setlocale(locale.LC_ALL, 'en_US')

def Dollar(value):
  return '$' + locale.format('%d', value, grouping=True)

# roof pitch?
installation_cost=34300
kw=9
cents_kwh = 39.6 # was 54.9
kwhpy=1255  # estimate of kw -> kWh/y
kwh_year=kwhpy * kw
increase_home_value=1.03
home_value=550000
increased_home_value=(increase_home_value * home_value) - home_value
net_install_cost=installation_cost - increased_home_value
print '%.1f kw installation' % kw
print '%s install cost' % Dollar(installation_cost)
print 'Increase home value %s (%d%%)' % (Dollar(increased_home_value),
    (increase_home_value-1) * 100)
print 'Net installation cost %s (%.1f%%)' % (Dollar(net_install_cost),
    100 * increased_home_value / installation_cost)
print '%0.f kWh/year' % (kwh_year)
income_year = cents_kwh * kwh_year / 100.0
print '%s income/year' % Dollar(income_year)
print '%s income/month' % Dollar(income_year / 12)
total_years = 20
net_income = (total_years * income_year) - net_install_cost
print 'Pays for self in %.1f years' % (net_install_cost / income_year)
print 'Net income %s in %d years' % (Dollar(net_income), total_years)
print 'Investment profit %.2f%% in %d years' % ((total_years * income_year) /
    net_install_cost, total_years)

# samples from their site http://solardynamics.ca/microfit.php
kwh1=10678/8.5 # per year for 8.5 house
kwh2=15133/11.96
