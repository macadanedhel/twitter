#!/usr/bin/python
# -*- coding: utf-8 -*-
# encoding=utf8
import os
from langdetect import detect
import json, csv
import ConfigParser

import psycopg2

import argparse
from mongodata import mongodata

#-----------------------------------------------------------------------------------------------------------------------
parser = argparse.ArgumentParser(
    description ='To test different options',
    epilog      = 'comments > /dev/null'
)
#-----------------------------------------------------------------------------------------------------------------------
parser.add_argument('--print_',  "-p", action='store_true', help='print')
parser.add_argument('--show',  "-s", action='store_true', help='print')
parser.add_argument('--updatefrommongo',  "-um", action='store_true', help='update data from mongo')
#parser.add_argument('--show',  "-s", type=str, help='show data ina a csv file')
#-----------------------------------------------------------------------------------------------------------------------
args = parser.parse_args()

#-----------------------------------------------------------------------------------------------------------------------
class pssqldata:
    ENVCONFIG = "config/env.ini"
    EnvConfig = ConfigParser.ConfigParser()
    Config = ConfigParser.ConfigParser()
    EnvConfig.read(ENVCONFIG)
    fields = []

    def __init__(self):
        host_ = self.EnvConfig.get('pssql', 'ip')
        port_ = self.EnvConfig.get('pssql', 'port')
        dbname_ = self.EnvConfig.get('pssql', 'database')
        user_= self.EnvConfig.get('pssql', 'user')
        password_ = self.EnvConfig.get('pssql', 'password')
        self.fields = (self.EnvConfig.get('pssql', 'fields').split(","))
        cadena="host={0} port={1} user={2}  password={3}".format(host_, port_, user_ , password_)

        try:
            self.conn = psycopg2.connect(cadena)
        except:
            print "Connection failed"

    def readcsv(self, file):
        mngdb = mongodata()
        myself = mngdb.list_users()
        for row in myself:
            print ("_id:{0} name:{1} screen_name:{2} created_at:{3} lang:{4} verified:{5}\n\tdescription:{6} location:{7} utc_offset:{8}".format(row['_id'],
                                        row['name'].encode('utf-8'),row['screen_name'].encode('utf-8'),row['created_at'],
                                        row['lang'],row['verified'],row['description'].encode('utf-8'),row['location'].encode('utf-8'),row['utc_offset']))
    def insertfrommongo(self):
        mngdb = mongodata()
        myself = mngdb.list_users()
        alldata=[]
        for row in myself:
            rowaux = {}
            tmp=[]
            for w in row.keys():
                if type(row[w]) is unicode:
                    rowaux[w] = row[w].encode('utf-8')
                    rowaux[w] = rowaux[w].replace("\r\n", " ")
                    rowaux[w] = rowaux[w].replace("\n", " ")
                    rowaux[w] = rowaux[w].replace("'", "''")
                    rowaux[w] = "'" + rowaux[w] + "'"
                elif str(row[w]).isdigit():
                    rowaux[w] = row[w]
                else:
                    rowaux[w] = row[w]
            alldata.append(rowaux)
        cur=self.conn.cursor()
        for rd in alldata:
            print "#",
            cadena= """INSERT INTO twitter.tusers(_id,name,screen_name,created_at,lang,verified,description,location,utc_offset)
            VALUES({},{},{},{},{},{},{},{},{}) """.format(
                rd['_id'],rd['name'],rd['screen_name'],rd['created_at'],rd['lang'],rd['verified'],rd['description'],rd['location'],rd['utc_offset']
                )
            #print (cadena)
            try:
                cur.execute(cadena)
                self.conn.commit
            except psycopg2.DatabaseError as error:
                print ("ERROR:{}".format(error))
                print ("CADENA:{}".format(cadena))
                break

pssqlitem=pssqldata()
if args.show :
    pssqlitem.readcsv(args.show)
elif args.updatefrommongo:
    pssqlitem.insertfrommongo()
