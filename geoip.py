###############################################################################
## GEOIP2 API                                                                ##
## ----------                                                                ##
## REST API for Maxminds GeoIP2 databases (City and ISP) based on Falcon     ##
## WSGI framework. Run it through a WSGI-server, e.g. Gunicorn.              ##
##                                                                           ##
## Created by Tor Inge Skaar - 2015                                          ##
##                                                                           ##
###############################################################################

# Import core modules
import json
import signal

# Import third-party modules
import falcon
import geoip2.database
from geoip2.errors import AddressNotFoundError


# Get an IP resource with the most used fields
class IpResource:

    def on_get(self, request, response, ip):
        try:
            cdata = db1.city(ip)
            idata = db2.isp(ip)
            data = {}
            data['ip'] = cdata.traits.ip_address
            data['city'] = cdata.city.name
            data['country_code'] = cdata.country.iso_code
            data['location'] = '{},{}'.format(cdata.location.latitude,
                                              cdata.location.longitude)
            data['asn'] = idata.autonomous_system_number
            data['org'] = idata.organization
            response.body = json.dumps(data)

        except AddressNotFoundError:
            response.status = falcon.HTTP_204

        except ValueError:
            response.status = falcon.HTTP_406


# Get a complete IP resource
# In Maxminds docs there are more fields, but they either require additional
# dbs or are very us centric.
class CompleteIpResource:

    def on_get(self, request, response, ip):
        try:
            cdata = db1.city(ip)
            idata = db2.isp(ip)
            data = {}
            data['ip'] = cdata.traits.ip_address
            data['city'] = cdata.city.name
            data['city_gid'] = cdata.city.geoname_id
            data['country_code'] = cdata.country.iso_code
            data['country'] = cdata.country.name
            data['country_gid'] = cdata.country.geoname_id
            data['continent'] = cdata.continent.name
            data['continent_code'] = cdata.continent.code
            data['continent_gid'] = cdata.continent.geoname_id
            data['location'] = '{},{}'.format(cdata.location.latitude,
                                              cdata.location.longitude)
            data['latitude'] = cdata.location.latitude
            data['longitude'] = cdata.location.longitude
            data['tz'] = cdata.location.time_zone
            data['asn'] = idata.autonomous_system_number
            data['org'] = idata.organization
            data['as_org'] = idata.autonomous_system_organization
            data['isp'] = idata.isp
            response.body = json.dumps(data)
        except AddressNotFoundError:
            response.status = falcon.HTTP_204
        except ValueError:
            response.status = falcon.HTTP_406


# Get a single resource based on request
class SingleIpResource:

    def on_get(self, request, response, ip, resource):
        res = resource.lower()
        try:
            data = {}

            if resource == 'asn':
                data['asn'] = db2.isp(ip).autonomous_system_number
            elif resource == 'country_code':
                data['country_code'] = db1.city(ip).country.iso_code
            elif resource == 'location':
                lat = db1.city(ip).location.latitude
                lon = db1.city(ip).location.longitude
                data['location'] = '{},{}'.format(lat, lon)
            elif resource == 'org':
                data['org'] = db2.isp(ip).organization
            elif resource == 'as_org':
                data['as_org'] = db2.isp(ip).autonomous_system_organization
            elif resource == 'country':
                data['country'] = db1.city(ip).country.name
            elif resource == 'country_gid':
                data['country_gid'] = db1.city(ip).country.geoname_id
            elif resource == 'city':
                data['city'] = db1.city(ip).city_name
            elif resource == 'city_gid':
                data['city_gid'] = db1.city(ip).city.geoname_id
            elif resource == 'continent_code':
                data['continent_code'] = db1.city(ip).continent.code
            elif resource == 'continent':
                data['continent'] = db1.city(ip).continent.name
            elif resource == 'continent_gid':
                data['continent_gid'] = db1.city(ip).continent.geoname_id
            elif resource == 'isp':
                data['isp'] = db2.isp(ip).isp
            elif resource == 'latitude':
                data['latitude'] = db1.city(ip).location.latitude
            elif resource == 'longitude':
                data['longitude'] = db1.city(ip).location.longitude
            elif resource == 'tz':
                data['tz'] = db1.city(ip).location.time_zone
            elif resource == 'ip':
                raise NotImplementedError
            else:
                raise ValueError

            if data.itervalues().next() is None:
                raise AttributeError

            response.body = json.dumps(data)

        except AttributeError:
            response.status = falcon.HTTP_204
        except AddressNotFoundError:
            response.status = falcon.HTTP_204
        except ValueError:
            response.status = falcon.HTTP_406
        except NotImplementedError:
            response.status = falcon.HTTP_418


# Create a Falcon API framework
api = application = falcon.API()

# Open GeoIP databases
db1 = geoip2.database.Reader('db/GeoIP2-City.mmdb', locales=['en'])
db2 = geoip2.database.Reader('db/GeoIP2-ISP.mmdb',  locales=['en'])

# Add API routes
api.add_route('/v1/ip/{ip}', IpResource())
api.add_route('/v1/ip/{ip}/{resource}', SingleIpResource())
api.add_route('/v1/ip/{ip}/all', CompleteIpResource())
