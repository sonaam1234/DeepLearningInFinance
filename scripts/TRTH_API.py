from suds.client import Client
from suds import WebFault

import logging
import getpass
import datetime
import time
import base64, os
from pandas import *
from datetime import datetime, timedelta
#Begin test gzip format
import gzip, zlib, csv
from io import StringIO
import binascii
import urllib.request, urllib.error, urllib.parse
#End test gzip format


    
class TRTH:
    dateString = ''    
    def __init__(self, dir = '.'):
        self.initialized = False
        try:
            self.WSDL_URL = "https://trth-api.thomsonreuters.com/TRTHApi-5.8/wsdl/TRTHApi.wsdl"
            self.client = Client( self.WSDL_URL, faults=False )
            logging.basicConfig()
            #logging.getLogger('suds.self.client').setLevel(lcogging.DEBUG)
        
            # get username
            username = 'Hrishabh.Sanghvi@edelweissfin.com'
            password = 'EventHorizon123'            
            # create credentials object
            credentials = self.client.factory.create( 'ns0:CredentialsHeader' )
            credentials.username = username
            credentials.password = password
            
            # add credentials to header
            self.client.set_options( soapheaders = credentials )
        
            # add tokenID to credentials and add to header
            credentials.tokenId = self.getTokenId( self.client.last_received() )
            self.client.set_options( soapheaders = credentials )
            #print self.client
            self.dir = dir
            self.initialized = True
            
        except Exception as e:
            print('TRTH API not initialized as Exception Occured', e)
    #===============================================================================
    def createDataObject( self, type, field, value, longName = "" ):
        data = self.client.factory.create( 'ns0:Data' )
        data.type.value = type
        data.field.value = field
        data.value = value
        data.longName = longName
        return data
    
    #===============================================================================
    def getTokenId(self,  message ):
        startIndex = str( message ).find( "<typens:tokenId>" )
        endIndex   = str( message ).find( "</typens:tokenId>" )
        return str( message )[startIndex+16:endIndex]
    
    #===============================================================================
    # Based on the SEARCHRICS example on page 37 of the TRTH API User Guide 5.7.2
    #===============================================================================
    def searchRICs(self):
        if not self.initialized: 
            print('TRTH API not initialized')
            return
        print("---------------------")
        print("SearchRICs()")
        print("---------------------")
    
        # set date range
        dateRange = self.client.factory.create( 'ns0:DateRange' )
        dateRange.start = "2000-01-01"
        dateRange.end = "2006-12-31"
    
        # create data objects
        domain   = createDataObject( "Text", "Domain", "EQU" )
        exchange = createDataObject( "Text", "Exchange", "NSEI" )
        ric      = createDataObject( "Text", "RICRegex", "^MSFT" )
    
        # create criteria and add data objects
        criteria = self.client.factory.create( 'ns0:ArrayOfData' )
        criteria.data.append( domain )
        criteria.data.append( exchange )
        criteria.data.append( ric )
    
        # search RICs
        try:
            result = self.client.service.SearchRICs( dateRange, criteria, False )
            #print "Result length:", len(result['instrument'])
            #for res in result['instrument']:
             #   print res.code
            print("result:", result)
            
        except WebFault as f:
            print("f:", f)
            print("f.fault:", f.fault)    
    
    #===============================================================================
    # Based on the EXPANDCHAIN example on page 39 of the TRTH API User Guide 5.7.2
    #===============================================================================
    def expandChain(self):
        if not self.initialized: 
            print('TRTH API not initialized')
            return
        print("---------------------")
        print("ExpandChain()")
        print("---------------------")
    
        # create an instrument
        instrument = self.client.factory.create( 'ns0:Instrument' )
        instrument.code = "0#.DJI"
        instrument.status = None
    
        # create a date range
        dateRange = self.client.factory.create( 'ns0:DateRange' )
        dateRange.start = "2006-07-01"
        dateRange.end = "2006-07-31"
    
        # create a time range
        timeRange = self.client.factory.create( 'ns0:TimeRange' )
        timeRange.start = "0:00"
        timeRange.end = "23:59:59.999"
    
        # expand chain
        try:
            result = self.client.service.ExpandChain( instrument,
                                                 dateRange,
                                                 timeRange,
                                                 True )
            print("result:", result)
        except WebFault as f:
            print("f:", f)
            print("f.fault:", f.fault)
    
    #===============================================================================
    # Get the Look Back Period Information
    #===============================================================================
    def GetLookBackPeriod(self):
        if not self.initialized: 
            print('TRTH API not initialized')
            return        
        print("---------------------")
        print("GetLookBackPeriod()")
        print("---------------------")
    
        # expand chain
        try:
            result = self.client.service.GetLookBackPeriod()
            print("result:", result)
        except WebFault as f:
            print("f:", f)
            print("f.fault:", f.fault)
    
    def GetMessageType(self):
        if not self.initialized: 
            print('TRTH API not initialized')
            return        
        print("---------------------")
        print("GetMessageType()")
        print("---------------------")
        
        domainList = self.client.factory.create( 'ns0:ArrayOfData')
        #domainList.data = self.client.factory.create( 'ns0:Data')
        #domainList.data.value = 'EQU'
        
        requestType = (self.client.factory.create("ns0:RequestType")).EndOfDay

        try:
            print(self.client.service.GetMessageTypes(domainList, requestType))
            #print "Request:", self.client.service.GetCountries()
           
    
        except WebFault as f:
            print("f:", f)
            print("f.fault:", f.fault)
       
    
    def intraday10minBar(self, scrip, start_date, end_date):
        if not self.initialized: 
            print('TRTH API not initialized')
            return        
        print("---------------------")
        print("submitFTPRequest()", scrip, start_date, end_date)
        print("---------------------")
    
        # create an instrument
        instrument = self.client.factory.create( 'ns0:Instrument' )
        instrument.code = scrip
        instrument.status = None
    
        instrumentList = self.client.factory.create("ns0:ArrayOfInstrument")
        instrumentList.instrument = [instrument]
    
        # create a date range
        dateRange = self.client.factory.create( 'ns0:DateRange' )
        dateRange.start = start_date
        dateRange.end = end_date
    
        # create a time range
        timeRange = self.client.factory.create( 'ns0:TimeRange' )
        timeRange.start = "00:000:00.000"
        timeRange.end = "16:00:00.000"
    
        # create message type
        fields = ["Open","High", "Low", "Last","Volume"]
        messageType = self.client.factory.create("ns0:MessageType")
        messageType.name = "Intraday 10Min"
        fieldArray = self.client.factory.create("ns0:ArrayOfString")
        fieldArray.string = fields
        messageType.fieldList = fieldArray
    
        typesArray = self.client.factory.create("ns0:ArrayOfMessageType")
        typesArray.messageType = [messageType]
        
    
        # create a LargeRequestSpec
        request = self.client.factory.create("ns0:LargeRequestSpec")
        request.friendlyName = "BulkRequest"
        request.requestType = (self.client.factory.create("ns0:RequestType")).Intraday
        request.instrumentList = instrumentList
        request.dateRange = dateRange
        request.timeRange = timeRange
        request.messageTypeList = typesArray
        request.requestInGMT = False
        request.displayInGMT = False
        request.marketDepth = 0
        request.splitSize = 500
        request.delivery = (self.client.factory.create("ns0:RequestDelivery")).Pull
        request.sortType = (self.client.factory.create("ns0:RequestSortType")).RICSequence
        request.fileFormat = (self.client.factory.create("ns0:RequestFileFormat")).Single
        request.dateFormat = (self.client.factory.create("ns0:RequestDateFormat")).DDMMYYYY
        request.applyCorrections = False
        request.displayMicroseconds = False
        request.disableDataPersistence = True
        request.includeCurrentRIC= True        
        fname =''
        
        try:
            reqID = self.client.service.SubmitFTPRequest(request)
            print("Request:", reqID[1])
            fname = reqID[1]
    
        except WebFault as f:
            print("f:", f)
            print("f.fault:", f.fault)
        complete = False
        while(True):
            res = self.client.service.GetRequestResult(reqID[1]);
            print("======Status: ", res[1]['status'])
            if(res[1]['status'] == (self.client.factory.create("ns0:RequestStatusCode")).Complete or res[1]['status'] == (self.client.factory.create("ns0:RequestStatusCode")).Aborted):
                if(res[1]['status'] == (self.client.factory.create("ns0:RequestStatusCode")).Complete):
                    complete = True
                    break;
            time.sleep(5)
        url = 'https://tickhistory.thomsonreuters.com/HttpPull/Download?user=Hrishabh.Sanghvi@edelweissfin.com&pass=EventHorizon123&file=/api-results/'+fname+'.csv.gz'
        local = fname+'.csv.gz'
        
        u = urllib.request.urlopen(url)
        h = u.info()
        totalSize = int(h["Content-Length"])
        
        print("Downloading %s bytes..." % totalSize, end=' ')
        fp = open(local, 'wb')
        
        blockSize = 100000 # urllib.urlretrieve uses 8192
        count = 0
        while True:
            chunk = u.read(blockSize)
            if not chunk: break
            fp.write(chunk)
            count += 1
            if totalSize > 0:
                percent = int(count * blockSize * 100 / totalSize)
                if percent > 100: percent = 100
                print("%2d%%" % percent, end=' ')
                if percent < 100:
                    print("\b\b\b\b\b", end=' ')  # Erase "NN% "
                else:
                    print("Done.")
        
        fp.flush()
        fp.close()
        if not totalSize:
            print()
        f = open(scrip +'_10MinBar.csv','w')
        for i in self.csvreader(local):
            str1 = ''
            for j in i:
                str1 += j.replace('Settle', 'Close').replace('[L]', '') 
                str1 += ','
            #print str1
            str1 += '\n'
            f.write(str1)
        f.close()
    def intraday15minBar(self, scrips, start_date, end_date):
        if not self.initialized: 
            print('TRTH API not initialized')
            return        
#        print "---------------------"
#        print "submitFTPRequest()", scrip, start_date, end_date
#        print "---------------------"
    
        # create an instrument
        # create an instrument
        instrumentList = self.client.factory.create("ns0:ArrayOfInstrument")
        instrumentList.instrument = []
        for i in scrips:
            instrument = self.client.factory.create( 'ns0:Instrument' )
            instrument.code = i
            instrument.status = None      
            instrumentList.instrument.append(instrument)
    
        # create a date range
        dateRange = self.client.factory.create( 'ns0:DateRange' )
        dateRange.start = start_date
        dateRange.end = end_date
    
        # create a time range
        timeRange = self.client.factory.create( 'ns0:TimeRange' )
        timeRange.start = "00:000:00.000"
        timeRange.end = "16:00:00.000"
    
        # create message type
        fields = ["Open","High", "Low", "Last","Volume"]
        messageType = self.client.factory.create("ns0:MessageType")
        messageType.name = "Intraday 15Min"
        fieldArray = self.client.factory.create("ns0:ArrayOfString")
        fieldArray.string = fields
        messageType.fieldList = fieldArray
    
        typesArray = self.client.factory.create("ns0:ArrayOfMessageType")
        typesArray.messageType = [messageType]
        
    
        # create a LargeRequestSpec
        request = self.client.factory.create("ns0:LargeRequestSpec")
        request.friendlyName = "BulkRequest"
        request.requestType = (self.client.factory.create("ns0:RequestType")).Intraday
        request.instrumentList = instrumentList
        request.dateRange = dateRange
        request.timeRange = timeRange
        request.messageTypeList = typesArray
        request.requestInGMT = False
        request.displayInGMT = False
        request.marketDepth = 0
        request.splitSize = 500
        request.delivery = (self.client.factory.create("ns0:RequestDelivery")).Pull
        request.sortType = (self.client.factory.create("ns0:RequestSortType")).RICSequence
        request.fileFormat = (self.client.factory.create("ns0:RequestFileFormat")).Single
        request.dateFormat = (self.client.factory.create("ns0:RequestDateFormat")).DDMMYYYY
        request.applyCorrections = False
        request.displayMicroseconds = False
        request.disableDataPersistence = True
        request.includeCurrentRIC= True        
        fname =''
        
        try:
            reqID = self.client.service.SubmitFTPRequest(request)
            print("Request:", reqID[1])
            fname = reqID[1]
    
        except WebFault as f:
            print("f:", f)
            print("f.fault:", f.fault)
        complete = False
        while(True):
            res = self.client.service.GetRequestResult(reqID[1]);
#            print "======Status: ", res[1]['status']
            if(res[1]['status'] == (self.client.factory.create("ns0:RequestStatusCode")).Complete or res[1]['status'] == (self.client.factory.create("ns0:RequestStatusCode")).Aborted):
                if(res[1]['status'] == (self.client.factory.create("ns0:RequestStatusCode")).Complete):
                    complete = True
                    break;
            time.sleep(5)
        url = 'https://tickhistory.thomsonreuters.com/HttpPull/Download?user=Hrishabh.Sanghvi@edelweissfin.com&pass=EventHorizon123&file=/api-results/'+fname+'.csv.gz'
        local = fname+'.csv.gz'
        
        u = urllib.request.urlopen(url)
        h = u.info()
        totalSize = int(h["Content-Length"])
        
        print("Downloading %s bytes..." % totalSize, end=' ')
        fp = open(local, 'wb')
        
        blockSize = 100000 # urllib.urlretrieve uses 8192
        count = 0
        while True:
            chunk = u.read(blockSize)
            if not chunk: break
            fp.write(chunk)
            count += 1
            if totalSize > 0:
                percent = int(count * blockSize * 100 / totalSize)
                if percent > 100: percent = 100
                print("%2d%%" % percent, end=' ')
                if percent < 100:
                    print("\b\b\b\b\b", end=' ')  # Erase "NN% "
                else:
                    print("Done.")
        
        fp.flush()
        fp.close()
        if not totalSize:
            print()

        f = open(self.dir+'//AllData.csv','w')
        for i in self.csvreader(local):
            str1 = ''
            for j in i:
                str1 += j
                str1 += ','
            str1 += '\n'
            f.write(str1)
        f.close()
        dstr = '_'+datetime.strptime(start_date, '%Y-%m-%d').strftime('%d%m%y')+'_'+datetime.strptime(end_date, '%Y-%m-%d').strftime('%d%m%y')
        df = read_csv(self.dir+'//AllData.csv')
        for i, j in df.groupby('#RIC'): j.to_csv(self.dir + '//' + i.replace(':','-')+'_Intraday15min'+dstr+'.csv')
        os.remove(local)
        os.remove(self.dir+'//AllData.csv')
        
    def Daily_OHLC_Bar(self, scrips, start_date, end_date):
        if not self.initialized: 
            print('TRTH API not initialized')
            return False   
        
        # create an instrument
        instrumentList = self.client.factory.create("ns0:ArrayOfInstrument")
        instrumentList.instrument = []
        for i in scrips:
            instrument = self.client.factory.create( 'ns0:Instrument' )
            instrument.code = i
            instrument.status = None      
            instrumentList.instrument.append(instrument)

        dateRange = self.client.factory.create( 'ns0:DateRange' )
        dateRange.start = start_date
        dateRange.end = end_date
    
        # create a date range
        dateRange = self.client.factory.create( 'ns0:DateRange' )
        dateRange.start = start_date
        dateRange.end = end_date
        # create a time range
        timeRange = self.client.factory.create( 'ns0:TimeRange' )
        timeRange.start = "09:00:00:00"
        timeRange.end = "16:00:00.000"
    
        # create message type  
        messageType = self.client.factory.create("ns0:MessageType")
        messageType.name = "End Of Day"

        fields = ["Open","High", "Low", "Last", "Volume", "Settlement Price"]
        fieldArray = self.client.factory.create("ns0:ArrayOfString")
        fieldArray.string = fields
        messageType.fieldList = fieldArray
    
        typesArray = self.client.factory.create("ns0:ArrayOfMessageType")
        typesArray.messageType = [messageType]
        
    
        # create a LargeRequestSpec
        request = self.client.factory.create("ns0:LargeRequestSpec")
        request.friendlyName = "BulkRequest"
        request.requestType = (self.client.factory.create("ns0:RequestType")).EndOfDay
        request.instrumentList = instrumentList
        request.dateRange = dateRange
        request.timeRange = timeRange
        request.messageTypeList = typesArray
        request.requestInGMT = False
        request.displayInGMT = False
        request.marketDepth = 0
        request.splitSize = 500
        request.delivery = (self.client.factory.create("ns0:RequestDelivery")).Pull
        request.sortType = (self.client.factory.create("ns0:RequestSortType")).RICSequence
        request.fileFormat = (self.client.factory.create("ns0:RequestFileFormat")).Single
        request.dateFormat = (self.client.factory.create("ns0:RequestDateFormat")).DDMMYYYY
        request.applyCorrections = False
        request.displayMicroseconds = False
        request.disableDataPersistence = True
        request.includeCurrentRIC= True        
        fname =''
        
        try:
            reqID = self.client.service.SubmitFTPRequest(request)
#            print "Request:", reqID[1]
            fname = reqID[1]
    
        except WebFault as f:
            print("f:", f)
            print("f.fault:", f.fault)
            return False
            
        complete = False
        while(True):
            res = self.client.service.GetRequestResult(reqID[1]);
#            print "======Status: ", res[1]['status']
            if(res[1]['status'] == (self.client.factory.create("ns0:RequestStatusCode")).Complete or res[1]['status'] == (self.client.factory.create("ns0:RequestStatusCode")).Aborted):
                if(res[1]['status'] == (self.client.factory.create("ns0:RequestStatusCode")).Complete):
                    complete = True
                    break;
            time.sleep(3)

        url = 'https://tickhistory.thomsonreuters.com/HttpPull/Download?user=Hrishabh.Sanghvi@edelweissfin.com&pass=EventHorizon123&file=/api-results/'+fname+'.csv.gz'
        local = fname+'.csv.gz'
        try:
            u = urllib.request.urlopen(url)
        except urllib.error.URLError as e:
            print('URLError ', url, e.reason)
            return False
            
        h = u.info()
        totalSize = int(h["Content-Length"])
        
#        print "Downloading %s bytes..." % totalSize,
        fp = open(local, 'wb')
        
        blockSize = 8192 #100000 # urllib.urlretrieve uses 8192
        count = 0
        while True:
            chunk = u.read(blockSize)
            if not chunk: break
            fp.write(chunk)
            count += 1
            if totalSize > 0:
                percent = int(count * blockSize * 100 / totalSize)
                if percent > 100: percent = 100
#                print "%2d%%" % percent,
#                if percent < 100:
#                    print "\b\b\b\b\b",  # Erase "NN% "
#                else:
#                    print "Done."
        
        fp.flush()
        fp.close()
        if not totalSize:
            print()

        f = open(self.dir+'//AllData.csv','w')
        for i in self.csvreader(local):
            str1 = ''
            for j in i:
                str1 += j
                str1 += ','
            str1 += '\n'
            f.write(str1)
        f.close()
        dstr = '_'+datetime.strptime(start_date, '%Y-%m-%d').strftime('%d%m%y')+'_'+datetime.strptime(end_date, '%Y-%m-%d').strftime('%d%m%y')
        df = read_csv(self.dir+'//AllData.csv')
        for i, j in df.groupby('#RIC'): j.to_csv(self.dir + '//' + i.replace(':','-')+'_OHLC'+dstr+'.csv')
        os.remove(local)
        os.remove(self.dir+'//AllData.csv')
    #===============================================================================
    # Based on the SUBMITFTPREQUEST example on page 46 of the TRTH API User Guide 5.7.2
    #===============================================================================
    def bulkTradeData(self, scrips, start_date, end_date):
        if not self.initialized: 
            print('TRTH API not initialized')
            return           
        print("---------------------")
        print("bulkTradeData()")
        print("---------------------")
    
        # create an instrument
        #print scrips
        instrumentList = self.client.factory.create("ns0:ArrayOfInstrument")
        instrumentList.instrument = []
        for i in scrips:
            instrument = self.client.factory.create( 'ns0:Instrument' )
            instrument.code = i
            instrument.status = None      
            instrumentList.instrument.append(instrument)

        dateRange = self.client.factory.create( 'ns0:DateRange' )
        dateRange.start = start_date
        dateRange.end = end_date
    
        # create a time range
        timeRange = self.client.factory.create( 'ns0:TimeRange' )
        timeRange.start = "0:00"
        timeRange.end = "15:29:59.999"
    
        # create message type
        fields = ['Bid Price', 'Bid Size', 'Ask Price', 'Ask Size']
        messageType = self.client.factory.create("ns0:MessageType")
        messageType.name = "BulkRequest"
        fieldArray = self.client.factory.create("ns0:ArrayOfString")
        fieldArray.string = fields
        messageType.fieldList = fieldArray
    
        typesArray = self.client.factory.create("ns0:ArrayOfMessageType")
        typesArray.messageType = [messageType]
        
    
        # create a LargeRequestSpec
        request = self.client.factory.create("ns0:LargeRequestSpec")
        request.friendlyName = "BulkRequest"
        request.requestType = (self.client.factory.create("ns0:RequestType")).TimeAndSales
        request.instrumentList = instrumentList
        request.dateRange = dateRange
        request.timeRange = timeRange
        request.messageTypeList = typesArray
        request.requestInGMT = False
        request.displayInGMT = False
        request.marketDepth = 0
        request.splitSize = 500
        request.delivery = (self.client.factory.create("ns0:RequestDelivery")).Pull
        request.sortType = (self.client.factory.create("ns0:RequestSortType")).RICSequence
        request.fileFormat = (self.client.factory.create("ns0:RequestFileFormat")).Single
        request.dateFormat = (self.client.factory.create("ns0:RequestDateFormat")).DDMMYYYY
        request.applyCorrections = False
        request.displayMicroseconds = False
        request.disableDataPersistence = True
        request.includeCurrentRIC= True        
        fname =''
        
        try:
            reqID = self.client.service.SubmitFTPRequest(request)
            print("Request:", reqID[1])
            fname = reqID[1]
    
        except WebFault as f:
            print("f:", f)
            print("f.fault:", f.fault)
        complete = False
        while(True):
            res = self.client.service.GetRequestResult(reqID[1]);
            print("======Status: ", res[1]['status'], datetime.now())
            if(res[1]['status'] == (self.client.factory.create("ns0:RequestStatusCode")).Complete or res[1]['status'] == (self.client.factory.create("ns0:RequestStatusCode")).Aborted):
                if(res[1]['status'] == (self.client.factory.create("ns0:RequestStatusCode")).Complete):
                    complete = True
                    break;
            time.sleep(10)
        url = 'https://tickhistory.thomsonreuters.com/HttpPull/Download?user=Hrishabh.Sanghvi@edelweissfin.com&pass=EventHorizon123&file=/api-results/'+fname+'.csv.gz'
        local = self.dir + '//' + fname+'.csv.gz'
        
        u = urllib.request.urlopen(url)
        h = u.info()
        totalSize = int(h["Content-Length"])
        
        print("Downloading %s bytes..." % totalSize, end=' ')
        fp = open(local, 'wb')
        
        blockSize = 8192 #100000 # urllib.urlretrieve uses 8192
        count = 0
        while True:
            chunk = u.read(blockSize)
            if not chunk: break
            fp.write(chunk)
            count += 1
            if totalSize > 0:
                percent = int(count * blockSize * 100 / totalSize)
                if percent > 100: percent = 100
                if percent%5 == 0:                
                    print("%2d%%" % percent, end=' ')
                    if percent < 100:
                        print("\b\b\b\b\b", end=' ')  # Erase "NN% "
                    else:
                        print("Done.")
        fp.flush()
        fp.close()
        u.close()
        if not totalSize:
            print()
        f = open(self.dir+'//AllData.csv','w')
        for i in self.csvreader(local):
            str1 = ''
            for j in i:
                str1 += j.replace('Settle', 'Close').replace('[L]', '') 
                str1 += ','
            str1 += '\n'
            f.write(str1)
        f.close()
        dstr = '_'+datetime.strptime(start_date, '%Y-%m-%d').strftime('%d%m%y')+'_'+datetime.strptime(end_date, '%Y-%m-%d').strftime('%d%m%y')
        df = read_csv(self.dir+'//AllData.csv')
        for i, j in df.groupby('#RIC'): j.to_csv(self.dir + '//' + i.replace(':','-')+'_Quotes'+dstr+'.csv')
        os.remove(local)
        os.remove(self.dir+'//AllData.csv')

    #===============================================================================
    # 
    #===============================================================================
    def csvreader(self, file):
        with gzip.open(file, 'rb') as csvfile:
            reader = csv.reader(csvfile, delimiter=',',quotechar='"')
            for row in reader:
                yield row
                
    def submitRequest(self):
        if not self.initialized: 
            print('TRTH API not initialized')
            return           
        print("---------------------")
        print("submitRequest()")
        print("---------------------")
    
        # create an instrument
        instrument = self.client.factory.create( 'ns0:Instrument' )
        instrument.code = "ICBK.NS"
        instrument.status = None
    
        # create a date range
        date = self.client.factory.create( 'xsd:date' )
        date = "2014-07-07"
    
        # create a time range
        timeRange = self.client.factory.create( 'ns0:TimeRange' )
        timeRange.start = "09:00:00.000"
        timeRange.end = "09:29:59.999"
    
        # create a LargeRequestSpec
        request = self.client.factory.create("ns0:RequestSpec")
        request.friendlyName = "Single Day Request"
        request.requestType = (self.client.factory.create("ns0:RequestType")).MarketDepth
        request.instrument = instrument
        request.date = date
        request.timeRange = timeRange
        #request.messageTypeList = typesArray
        request.requestInGMT = False
        request.displayInGMT = False
        request.disableHeader = False
        request.marketDepth = 10
        request.dateFormat = (self.client.factory.create("ns0:RequestDateFormat")).DDMMYYYY
        request.applyCorrections = False
        request.displayMicroseconds = False
        request.disableDataPersistence = True
        request.includeCurrentRIC= True
        print(request)
    
        # submit request
        try:
            reqID = self.client.service.SubmitRequest(request)
            print("Request:", reqID[1])
    
        except WebFault as f:
            print("f:", f)
            print("f.fault:", f.fault)
    
        complete = False
        while(True):
            res = self.client.service.GetRequestResult(reqID[1]);
            print("======Status: ", res[1]['status'])
            if(res[1]['status'] == (self.client.factory.create("ns0:RequestStatusCode")).Complete or res[1]['status'] == (self.client.factory.create("ns0:RequestStatusCode")).Aborted):
                if(res[1]['status'] == (self.client.factory.create("ns0:RequestStatusCode")).Complete):
                    complete = True
                    break;
            time.sleep(5)
    
        if(complete == True): 
            data = base64.b64decode(res[1]['data'])
            fileR = open(self.dir + '\\result.csv.gz', 'wb')
            fileR.write(data)
            fileR.close()
            
    def market_depth(self, scrip, date1, start_time, end_time, levels):
        if not self.initialized: 
            print('TRTH API not initialized')
            return           
        self.dateString = datetime.strptime(date1, '%Y-%m-%d').strftime('%Y%m%d')
        # create an instrument
        instrument = self.client.factory.create( 'ns0:Instrument' )
        instrument.code = scrip
        instrument.status = None
    
        # create a date range
        date = self.client.factory.create( 'xsd:date' )
        date = date1
    
        # create a time range
        timeRange = self.client.factory.create( 'ns0:TimeRange' )
        timeRange.start = start_time
        timeRange.end = end_time
    
        # create a LargeRequestSpec
        request = self.client.factory.create("ns0:RequestSpec")
        request.friendlyName = "Single Day Request"
        request.requestType = (self.client.factory.create("ns0:RequestType")).MarketDepth
        request.instrument = instrument
        request.date = date
        request.timeRange = timeRange
        #request.messageTypeList = typesArray
        request.requestInGMT = False
        request.displayInGMT = False
        request.disableHeader = False
        request.marketDepth = levels
        request.dateFormat = (self.client.factory.create("ns0:RequestDateFormat")).DDMMYYYY
        request.applyCorrections = False
        request.displayMicroseconds = False
        request.disableDataPersistence = True
        request.includeCurrentRIC= True
    
        try:
            reqID = self.client.service.SubmitRequest(request)
        except WebFault as f:
            print("f.fault:", f.fault)
    
        complete = False
        while(True):
            res = self.client.service.GetRequestResult(reqID[1]);
            print("======Status: ", res[1]['status'])
            if(res[1]['status'] == (self.client.factory.create("ns0:RequestStatusCode")).Complete or res[1]['status'] == (self.client.factory.create("ns0:RequestStatusCode")).Aborted):
                if(res[1]['status'] == (self.client.factory.create("ns0:RequestStatusCode")).Complete):
                    complete = True
                    break;
            time.sleep(5)
    
        if(complete == True): 
            data = base64.b64decode(res[1]['data'])
            fileR = open(self.dir + '\\result.csv.gz', 'wb')
            fileR.write(data)
            fileR.close()
            columns = []
            quotes = []
            for i in self.csvreader(self.dir+ '\\result.csv.gz'):   
                if i[0] == '#RIC':
                    for j in i:
                        columns.append(j)
                else:
                    if i[4] == 'Market Depth':
                        quotes.append(i)
    
            df =  DataFrame(quotes)
            if len(quotes) < 1: 
                print('depth not found')
                return
            df.columns = columns
            new_cols = ['#RIC', 'Type', 'Date[L]', 'Time[L]']
            for i in range(levels):
                new_cols.append('L'+str(i+1)+'-BidSize')            
                new_cols.append('L'+str(i+1)+'-BidPrice')
                new_cols.append('L'+str(i+1)+'-AskSize')
                new_cols.append('L'+str(i+1)+'-AskPrice')
            
            df = df[new_cols]
            df.to_csv(self.dir + '\\'+scrip.replace(':','')+'_'+self.dateString +'_depth.csv', index = False)
            
    def market_data(self, scrip, date1, start_time, end_time):
        if not self.initialized: 
            print('TRTH API not initialized')
            return           
        self.dateString = datetime.strptime(date1, '%Y-%m-%d').strftime('%Y%m%d')
        # create an instrument
        instrument = self.client.factory.create( 'ns0:Instrument' )
        instrument.code = scrip
        instrument.status = None
    
        # create a date range
        date = self.client.factory.create( 'xsd:date' )
        date = date1
    
        # create a time range
        timeRange = self.client.factory.create( 'ns0:TimeRange' )
        timeRange.start = start_time
        timeRange.end = end_time
    
        # create a LargeRequestSpec
        request = self.client.factory.create("ns0:RequestSpec")
        request.friendlyName = "Single Day Request"
        request.requestType = (self.client.factory.create("ns0:RequestType")).TimeAndSales
        request.instrument = instrument
        request.date = date
        request.timeRange = timeRange
        #request.messageTypeList = typesArray
        request.requestInGMT = False
        request.displayInGMT = False
        request.disableHeader = False
        request.marketDepth = 0
        request.dateFormat = (self.client.factory.create("ns0:RequestDateFormat")).DDMMYYYY
        request.applyCorrections = False
        request.displayMicroseconds = False
        request.disableDataPersistence = True
        request.includeCurrentRIC= True
    
        try:
            reqID = self.client.service.SubmitRequest(request)
        except WebFault as f:
            print("f.fault:", f.fault)
    
        complete = False
        while(True):
            res = self.client.service.GetRequestResult(reqID[1]);
            print("======Status: ", res[1]['status'])
            if(res[1]['status'] == (self.client.factory.create("ns0:RequestStatusCode")).Complete or res[1]['status'] == (self.client.factory.create("ns0:RequestStatusCode")).Aborted):
                if(res[1]['status'] == (self.client.factory.create("ns0:RequestStatusCode")).Complete):
                    complete = True
                break;
            #time.sleep(1)
        if(complete == True): 
            data = base64.b64decode(res[1]['data'])
            fileR = open(self.dir + '\\result.csv.gz', 'wb')
            fileR.write(data)
            fileR.close()
            columns = []
            trades = []
            quotes = []
            for i in self.csvreader(self.dir + '\\result.csv.gz'):   
                if i[0] == '#RIC':
                    #trades.append(i)
                    #quotes.append(i)
                    
                    for j in i:
                        columns.append(j)
                else:
                    if i[4] == 'Trade':
                        trades.append(i)
                    if i[4] == 'Quote':
                        quotes.append(i)
            df =  DataFrame(trades)
            if(len(df) > 0):
                df.columns = columns
                new_cols = ['#RIC', 'Type', 'Date[L]', 'Time[L]', 'Price', 'Volume']
                df = df[new_cols]
                df.to_csv(self.dir + '\\'+scrip.replace(':','')+'_'+self.dateString +'_trades.csv', index = False)
                print(self.dir + '\\'+scrip+'_'+self.dateString +'_trades.csv')
    
            df =  DataFrame(quotes)
            if(len(df) > 0):
                df.columns = columns
                new_cols = ['#RIC', 'Type', 'Date[L]', 'Time[L]', 'Bid Price', 'Bid Size', 'Ask Price', 'Ask Size']
                df = df[new_cols]
                df.to_csv(self.dir + '\\'+scrip.replace(':','')+'_'+self.dateString +'_quotes.csv', index = False)
                print(self.dir + '\\'+scrip+'_'+self.dateString +'_quotes.csv')
   
    def eod_data(self, scrip, date1, start_time, end_time):
        if not self.initialized: 
            print('TRTH API not initialized')
            return           
        self.dateString = datetime.strptime(date1, '%Y-%m-%d').strftime('%Y%m%d')
        # create an instrument
        instrument = self.client.factory.create( 'ns0:Instrument' )
        instrument.code = scrip
        instrument.status = None
    
        # create a date range
        date = self.client.factory.create( 'xsd:date' )
        date = date1
    
        # create a time range
        timeRange = self.client.factory.create( 'ns0:TimeRange' )
        timeRange.start = start_time
        timeRange.end = end_time
    
        # create a LargeRequestSpec
        request = self.client.factory.create("ns0:RequestSpec")
        request.friendlyName = "Single Day Request"
        request.requestType = (self.client.factory.create("ns0:RequestType")).EndOfDay
        request.instrument = instrument
        request.date = date
        request.timeRange = timeRange
        #request.messageTypeList = typesArray
        request.requestInGMT = False
        request.displayInGMT = False
        request.disableHeader = False
        request.marketDepth = 0
        request.dateFormat = (self.client.factory.create("ns0:RequestDateFormat")).DDMMYYYY
        request.applyCorrections = False
        request.displayMicroseconds = False
        request.disableDataPersistence = True
        request.includeCurrentRIC= True
    
        try:
            reqID = self.client.service.SubmitRequest(request)
        except WebFault as f:
            print("f.fault:", f.fault)
    
        complete = False
        while(True):
            res = self.client.service.GetRequestResult(reqID[1]);
            print("======Status: ", res[1]['status'])
            if(res[1]['status'] == (self.client.factory.create("ns0:RequestStatusCode")).Complete or res[1]['status'] == (self.client.factory.create("ns0:RequestStatusCode")).Aborted):
                if(res[1]['status'] == (self.client.factory.create("ns0:RequestStatusCode")).Complete):
                    complete = True
                break;
            #time.sleep(1)
        if(complete == True): 
            data = base64.b64decode(res[1]['data'])
            fileR = open(self.dir + '\\result.csv.gz', 'wb')
            fileR.write(data)
            fileR.close()
            columns = []
            trades = []
            quotes = []
            for i in self.csvreader(self.dir + '\\result.csv.gz'):   
                if i[0] == '#RIC':
                    #trades.append(i)
                    #quotes.append(i)
                    
                    for j in i:
                        columns.append(j)
                else:
                    print(i[4])
                    if i[4] == 'End Of Day':
                        trades.append(i)
            df =  DataFrame(trades)
            if(len(df) > 0):
                df.columns = columns
                new_cols = ['#RIC', 'Type', 'Date[L]', 'Open', 'High', 'Low', 'Alternate Close', 'Volume','Last']
                df = df[new_cols]
                df['Close'] = df['Alternate Close']
                df = df.drop('Alternate Close', 1)
                print(df)
                df.to_csv(self.dir + '\\'+scrip.replace(':','')+'_'+self.dateString +'_eod.csv', index = False)
                print(self.dir + '\\'+scrip+'_'+self.dateString +'_eod.csv') 
                
    def getFileName(self, req_type, scrip, start_date, end_date):
        if not self.initialized: 
            print('TRTH API not initialized')
            return
        dstr = '_'+datetime.strptime(start_date, '%Y-%m-%d').strftime('%d%m%y')+'_'+datetime.strptime(end_date, '%Y-%m-%d').strftime('%d%m%y')
        fname = self.dir + '//' + scrip.replace(':','-') + '_'+req_type+dstr+'.csv'       
#        print fname
        return fname
        
    def add_timestamp_trth(self, tf):
        tf['dttime'] = datetime.now()
        tf['dttime'] = tf.apply(lambda row: to_datetime(row['Date'] + ' ' + row['Time'], format = '%d/%m/%Y %H:%M:%S.%f'), axis = 1)
#        for i in tf.index:
#            ts = tf['Date'][i] + ' ' + tf['Time'][i]
#            tf['dttime'][i] = datetime.strptime(ts, '%d/%m/%Y %H:%M:%S.%f')
#            tf['dttime'][i] = tf['dttime'][i].replace(microsecond = 0)    
        nf = tf.set_index('dttime')
        nf = nf[nf.Price.notnull()]
        nf = nf.drop('Date', 1)
        nf = nf.drop('Time', 1)
        nf = nf.resample('1S').ffill()
        return nf
        

#===============================================================================
if __name__ == "__main__":
    proxy_support = urllib.request.ProxyHandler({"http":"http://10.250.4.65:8080"})
    opener = urllib.request.build_opener(proxy_support)
    urllib.request.install_opener(opener)
    t = TRTH('.')
    #t.Daily_OHLC_Bar("NIFc1", datetime.strftime(datetime.now() - timedelta(days=7), '%Y-%m-%d'), datetime.strftime(datetime.now(), '%Y-%m-%d'))
    #t.intraday10minBar()
    t.GetMessageType()
    #scrips = ['ICBK.NS', 'HDFC.NS']
    #t.submitFTPRequest(scrips, "2016-01-01", "2016-01-05")
    #t.Daily_OHLC_Bar("NBNc1", "2000-01-01", "2016-06-02")
    #t.Daily_OHLC_Bar("NBPc1", "2016-01-01", "2016-02-02")
    #t.Daily_OHLC_Bar("NIRc1", "2016-01-01", "2016-06-02")
    #t.eod_data('NIRc1', "2016-03-01", "09:15:00.000", "15:29:59.999")
#    t.market_data('SBIN6:NS', '2016-07-01', "15:00:00.000", "15:29:59.999")
#    t.market_data('SBIc1:NS', '2016-07-01', "15:00:00.000", "15:29:59.999")
#    t.market_data('SBIM6:NS', '2016-07-01', "15:00:00.000", "15:29:59.999")
    #t.market_data('BRTI.NS', '2016-06-21', "15:00:00.000", "15:29:59.999")