# -*- coding: utf-8 -*-

import sys, getopt
import subprocess
import xmlrpc.client
import argparse

# Initiate the parser
parser = argparse.ArgumentParser() 
 
# Initialize parser
full_cmd_arguments = sys.argv
parser.add_argument("--domain", "-d", help="Odoo URL.conf")
parser.add_argument("--module", "-m", help="Module to be Upgraded.")

#COMMON_AUTH_USERNAME = 'module_upgrade_user'
#COMMON_AUTH_PASSWORD = 'module_upgrade_user'
COMMON_AUTH_USERNAME = 'developer@armsit.com'
COMMON_AUTH_PASSWORD = 'armsit@2022'

class Upgrade():

    def __init__(self):
        """
        Constructor for the script.
        """
        args = parser.parse_args()
        self.url = args.domain
        self.module = args.module
        
        if not self.url or not self.module:
            print("Error - Could not find required arguments.")

        self.databases = self._set_databases()
        self._upgrade_module()

    def _upgrade_module(self):
        """
        Upgrade Module of the particular 
        database.
        """
        for db in self.databases:
            print("Upgrade Attempting on database : {}".format(db))
            common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(self.url))
            common.version()
            try:
                uid = common.authenticate(db, COMMON_AUTH_USERNAME, COMMON_AUTH_PASSWORD, {})
                if not uid:
                    print("Error - Invalid Credentials for database : {}".format(db))
                models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(self.url))
                
                try:
                    module_ids = models.execute_kw(db, uid, COMMON_AUTH_PASSWORD, 'ir.module.module', 'search', [[['name', '=', self.module]]], {'limit': 1})
                    if module_ids:
                        try:
                            models.execute_kw(db, uid, COMMON_AUTH_PASSWORD, 'ir.module.module', 'button_immediate_upgrade', [module_ids])
                            print("Module - {} upgraded successfully.".format(self.module))
                        except Exception as e:
                            print("Error Upgrading Module - {}".format(e))
                    else:
                        print("Error - No Module Found with Name : {} on Database : {}".format(self.module, db))
                except Exception as e:
                    print(e)
            except Exception as e:
                    print(e)
            print("=====================================================================")


    def _set_databases(self):
        """
        List all the databases.
        """
        sock_db = xmlrpc.client.ServerProxy('{}/xmlrpc/db'.format(self.url))
        all_dbs = sock_db.list()
        print("Please select the databases below(Comma Separated). Enter 0(Zero) for all the databases.")
        for index, database in enumerate(all_dbs):
            print("{} : {}".format(index+1, database))
        dbs_selected = input("Enter your choice : ")

        if '0' in dbs_selected.split(','):
            return all_dbs

        result = list()
        for choice in dbs_selected.split(','):
            try:
                result.append(all_dbs[int(choice)-1])
            except:
                print("Invalid Database Choice.")        
        return result

if __name__ == '__main__':
    print("Odoo Module Upgrade Script")
    upgradeObj = Upgrade()
