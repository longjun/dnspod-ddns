#!/usr/bin/env python
# -*- coding:utf-8 -*-
import urllib2
import urllib
import json
import logging
import os
import sys
reload(sys)
sys.setdefaultencoding("utf8")

logging.basicConfig(
    filename = os.path.join(os.path.dirname(__file__), 'pypod.log'),
    level = logging.DEBUG,
    format = "%(asctime)s - %(levelname)s: %(message)s")

class PyPod(object):
    def __init__(self):
        self.params = {}
        self.params["login_email"]= ""
        self.params["login_password"]= ""
        self.params["format"] = "json"
        self.params["lang"] = "cn"
        self.dnspod_api = "https://dnsapi.cn"
        self.domain = ""
        self.sub_domain = ""
        self.get_ip = "http://ip.taobao.com/service/getIpInfo.php?ip=myip"

    def get_my_ip(self):
        response = urllib2.urlopen(self.get_ip)
        result = response.read()
        result = json.loads(result)
        return result["data"]["ip"]

    def post_api(self, url, params):
        response = urllib2.Request("%s/%s" % (self.dnspod_api, url), data=urllib.urlencode(params))
        result = urllib2.urlopen(response)
        return json.load(result)

    def get_domain_id(self):
        """
        - url: https://dnsapi.cn/Domain.Info
        - POST
        - params: self.params, domain
        """
        self.params["domain"] = self.domain
        result = self.post_api("Domain.Info", self.params)
        if result["status"]["code"] != "1":
            logging.debug(
                "GET DOMAIN ID! code:{0},message:{1}"
                .format(
                    result["status"]["code"], 
                    result["status"]["message"]))
        else:
            return result["domain"]["id"]

    def get_record(self, domain_id):
        """
        - url: https://dnsapi.cn/Record.List
        - POST
        - params: self.params, domain_id
        """
        record = {}
        self.params["domain_id"] = domain_id
        result = self.post_api("Record.List", self.params)
        if result["status"]["code"] != "1":
            logging.debug(
                "GET RECORD ID! code:{0},message:{1}"
                .format(
                    result["status"]["code"], 
                    result["status"]["message"]))
        else:
            for i in result["records"]:
                if i["name"] == self.sub_domain:
                    record["ip"] = i["value"]
                    record["id"] = i["id"]
            return record

    def set_ddns(self, domain_id, record_id, new_ip):
        self.params["domain_id"] = domain_id
        self.params["record_id"] = record_id
        self.params["sub_domain"] = self.sub_domain
        self.params["record_line"] = "默认"
        self.params["value"] = new_ip
        result = self.post_api("Record.Ddns", self.params)
        if result["status"]["code"] != "1":
            logging.debug(
                "SET DDNS! code:{0},message:{1}"
                .format(
                    result["status"]["code"], 
                    result["status"]["message"]))
        else:
            logging.info(
                "SET DDNS! message:{0},updated:{1},ip:{2}"
                .format(
                    result["status"]["message"],
                    result["status"]["created_at"],
                    result["record"]["value"]))

    def main(self):
        domain_id = self.get_domain_id()
        record = self.get_record(domain_id)
        new_ip = self.get_my_ip()
        if record:
            dns_ip = record["ip"]
            record_id = record["id"]
            if new_ip == dns_ip:
                logging.info("外网IP没有改变，不需要更新dns")
            else:
                result = self.set_ddns(domain_id, record_id, new_ip)
        else:
            logging.debug("没有找到二级域名为'{0}'的记录".format(self.sub_domain))

if __name__ == "__main__":
    pod = PyPod()
    pod.main()
