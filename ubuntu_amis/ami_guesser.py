import os
import requests
import time
import json


class Finder(object):
    '''
    Based on the region, release, root device storage provided, load data
    from http://uec-images.ubuntu.com/query/<release>/server/released.current.txt
    and return the relevant ami id.
    '''

    def __init__(self, cache_directory='/tmp', cache_time=3600):
        self.cache_directory = cache_directory
        self.cache_time = cache_time
        self.parsed_data = {}
        self.field_map = {
            'release': 0,
            'root_store': 4,
            'cpu_arch': 5,
            'region': 6,
            'ami_id': 7,
            'instance_arch': 10,
        }

    # def _get_origin_url(self, release=self.release):
    def _get_origin_url(self, release):
        return "http://uec-images.ubuntu.com/query/%s/server/released.current.txt" % release

    def _check_data_cache_time(self, release):
        if release in self.parsed_data.keys() \
            and 'cachetime' in self.parsed_data[release] \
                and (self.parsed_data[release]['cachetime'] - time.time()) < 3600:
                return True
        else:
            return False

    def get_ami(self, release='trusty', region='us-east-1', cpu_arch='amd64', root_store='ebs', instance_arch='hvm'):
        # print "getting ami for: %s %s %s %s" % (release, region, root_store, cpu_arch)
        if not self._check_data_cache_time(release):
            # print "no data"
            self.parsed_data[release] = self._parse_data_file(self._get_cached_file(release))
            self.parsed_data[release]['cachetime'] = time.time()
            # print json.dumps(self.parsed_data, sort_keys=True, indent=2)
        else:
            print json.dumps(self.parsed_data[release][region])
        return self.parsed_data[release][region][root_store][cpu_arch][instance_arch]

    def _get_cached_file(self, release):
        cached_file = "%s/ubuntu-images-%s.txt" % (self.cache_directory, release)
        fresh_file = False
        if os.path.isfile(cached_file):
            mtime = os.path.getmtime(cached_file)
            if (mtime - time.time()) < self.cache_time:
                fresh_file = True
        if not fresh_file:
            self._get_file_from_origin(self._get_origin_url(release), cached_file)
        # print "returning %s as the cached file, which was fresh: %s" % (cached_file, fresh_file)
        return cached_file

    def _get_file_from_origin(self, origin_url, cache_location):
        download = requests.get(origin_url)
        if download.status_code != 200:
            raise ValueError("bad response (%s) for resolver URL %s" % (download.status_code, origin_url))
        cached_file_h = open(cache_location, 'w')
        cached_file_h.write(download.content)
        cached_file_h.close()

    def _parse_data_file(self, file_path):
        # print "parsing file %s" % file_path
        data_file_h = open(file_path, 'r')
        # release
        #     region
        #         root_store
        #             cpu_arch
        #                 instance_arch
        lines = data_file_h.read()
        with open(file_path) as f:
            raw_data = f.readlines()
        # print len(raw_data)
        field_keys = self.field_map.keys()
        release_data = {}
        for line in raw_data:
            clean_line = line.strip()
            field_values = clean_line.split("\t")
            region = field_values[self.field_map['region']]
            root_store = field_values[self.field_map['root_store']]
            cpu_arch = field_values[self.field_map['cpu_arch']]
            instance_arch = field_values[self.field_map['instance_arch']]
            ami_id = field_values[self.field_map['ami_id']]

            if region not in release_data.keys():
                release_data[region] = {}
            if root_store not in release_data[region].keys():
                release_data[region][root_store] = {}
            if cpu_arch not in release_data[region][root_store].keys():
                release_data[region][root_store][cpu_arch] = {}
            if instance_arch not in release_data[region][root_store][cpu_arch].keys():
                release_data[region][root_store][cpu_arch][instance_arch] = ami_id
        return release_data
