import pandas as pd
import numpy as np
import sklearn
from collections import defaultdict
from sklearn.feature_selection import SelectKBest
from sklearn.feature_selection import chi2

class Data():
    def __init__(self,data_path='/home/saturn/research/petpen/datasets/label_insert_air_2015_data.csv',**kwargs):
        self.df_data = pd.read_csv(data_path)
        self.df_data = self.df_data.iloc[18*24:].reset_index(drop=True) # discard first day data
        self.siteNames = self.df_data['SiteEngName'].unique()
        self.df_data['time'] = pd.to_datetime(self.df_data['time'])
        self.df_data['PM25_1hour'] = self.shiftFeature(shift=-18)
        self.df_data['PM25_6hour'] = self.shiftFeature(shift=-18*6)
        self.df_data['PM25_12hour'] = self.shiftFeature(shift=-18*12)
        self.df_data['PM25_24hour'] = self.shiftFeature(shift=-18*24)
        self.addTemporal()
        self.dict_dataByStation = self.separateStation()
        self.meteoFeatures = ['RH', 'dew_point', 'globlrad', 'grid_index',
                'precp', 'precp_hour', 'sn_press', 'sun_shine_hour',
                'temerature', 'visb', 'wd', 'wd_gust', 'ws', 'ws_gust', ]
        self.trafficFeatures = ['AvgSpd','TotalVol','num_intersection','rd_len','hw_len']
        self.temporalFeatures = ['season', 'weekday']
        self.pollutantFeatures = ['SO2', 'CO', 'NO2', 'PM25', 'PM10', 'FPMI', 'PSI']
        self.train_data, self.test_data = self.splitTrainTestByDatetime()

    def separateStation(self, list_siteNames = None):
        dict_site_data = {}
        if not list_siteNames:
            list_siteNames = self.siteNames
        for siteName in list_siteNames:
            dict_site_data[siteName] = self.df_data[self.df_data['SiteEngName']==siteName]\
            .reset_index(drop=True)
        return dict_site_data
    
    def shiftFeature(self,feature='PM25',shift=0):
        return self.df_data[feature].shift(shift)

    def _toSeason(self,datetime):
        return np.cos((datetime.dayofyear-15)/365*2*np.pi)

    def addTemporal(self):
        self.df_data['weekday'] = self.df_data['time'].apply(lambda x:x.weekday())
        self.df_data['season'] = self.df_data['time'].apply(lambda x: self._toSeason(x))

    def getTrainDataframe(self,feature=None,datetime=pd.to_datetime('2015-08-31 23')):
        if feature:
            return self.df_data.iloc[self.df_data['time']<=datetime][feature]
        return self.df_data.iloc[self.df_data['time']<=datetime]
    
    def getTestDataframe(self,feature=None,datetime=pd.to_datetime('2015-08-31 23')):
        if feature:
            return self.df_data.iloc[self.df_data['time']>datetime][feature]
        return self.df_data.iloc[self.df_data['time']>datetime]
    
    def splitTrainTestByDatetime(self,datetime=pd.to_datetime('2015-08-31 23'),feature=None, dropna=True):
        if type(datetime)==str:
            datetime = pd.to_datetime(datetime)
        if dropna:
            data = self.df_data.dropna()
        else:
            data = self.df_data
        time_index = data['time']
        if feature:
            data = data[feature]
        return data[time_index<=datetime], data[time_index>datetime]
    
    def waveDecompose(self,site='all',feature='PM25',level=8,wname='db5',split=None):
        from pywt import dwt,wavedec,upcoef
        if site=='all':
            data = self.df_data
        elif site in self.df_data_of_station.keys():
            data = self.df_data_of_station[site]
        else:
            raise NameError('Wrong site name!')
        if split=='train':
            data = data.iloc[:-3000*18]
        elif split=='test':
            data = data.iloc[-3000*18:]
        featureData = data[feature].dropna()
        data_size = len(featureData)
        coeffs = wavedec(featureData,wname,level=level)
        decData = []
        for i in range(level):
            if i==0:
                line = upcoef('a',coeffs[i],wname,level=level,take=data_size)
            else:
                line = upcoef('d',coeffs[i],wname,level=level-i+1,take=data_size)
            decData.append(line)
        return decData


epoch = 300 #epoch
delay = 4000 
site = 0 #which site

class TrainConfig():
    input_size = 100#number of feature selection
    cell_size = 20 #num of cell
    train_size = 2000
    batch_size = 10 #
    lr = 0.001 #learning rate
    output_size = 1  #output dim
    num_layers = 1 #num layers
    time_steps = 48 #output length
    cover = 0
    window_size = time_steps #sequence length
    decay_rate = 0.9
    momentum_rate = 0.01
    dropout_in = 1
    dropout_out =1
    cell = "LSTM"
    beta = 0.005
    forget_bias = 1

class TestConfig(TrainConfig):
    test_size = 2000
    shift = TrainConfig.batch_size #between train and test 
    beta = 0.03
    
train_config = TrainConfig()
test_config = TestConfig()

class AirData():
    def __init__(self,data_path='/home/saturn/research/petpen/datasets/label_insert_air_2015_data.csv',**kwargs):
        self.rawData = pd.read_csv(data_path)
        # discard first day data
        self.df_data = self.rawData.iloc[18*24:].reset_index(drop=True)
        self.df_data['time'] = pd.to_datetime(self.df_data['time'])
        self.siteNames = self.df_data['SiteEngName'].unique()
        self.meteoFeatures = ['RH', 'dew_point', 'globlrad', 'grid_index',
                'precp', 'precp_hour', 'sn_press', 'sun_shine_hour',
                'temerature', 'visb', 'wd', 'wd_gust', 'ws', 'ws_gust', ]
        self.trafficFeatures = ['AvgSpd','TotalVol','num_intersection','rd_len','hw_len']
        self.temporalFeatures = ['season', 'weekday']
        self.pollutantFeatures = ['SO2', 'CO', 'NO2', 'PM25', 'PM10', 'FPMI', 'PSI']


class Demo1(AirData):
    def __init__(self,file_path='/home/saturn/research/petpen/datasets/label_insert_air_2015_data.csv',**kwargs):
        super().__init__(file_path,**kwargs)
        self.usedFeatures = self.meteoFeatures + self.pollutantFeatures
        # use multi-index to record data of each time
        self.dataByTime = self.df_data[self.usedFeatures+['time','SiteEngName']].set_index(['time','SiteEngName']).unstack()
        data2 = self.dataByTime**2
        data3 = self.dataByTime**3
        self.dataByTime_power = pd.concat([self.dataByTime,data2,data3], axis=1)

        x_data = self.dataByTime_power.values
        y_data = self.dataByTime['PM25'].iloc[:,0]
        # deal with negative values, need another solution
        x_data = abs(x_data)

        # Univariate Selection - chiSquared
        # feature extraction
        test = SelectKBest(score_func=chi2, k=train_config.input_size)
        fit = test.fit(x_data, y_data)
        features = fit.transform(x_data)
        x_data = features

        #train & test data
        ts_datay = []
        ts_datax = []

        tr_datay = []
        tr_datax = []

        x_data = sklearn.preprocessing.scale(x_data,axis=0)

        for k in range(delay,train_config.train_size+delay):
            a = x_data[(x_data.shape[0]-train_config.window_size-k-test_config.shift):
                       (x_data.shape[0]-k-test_config.shift)]
            ts_datax.append(a)
            new_y = y_data[(len(y_data)-train_config.time_steps-test_config.window_size-k+train_config.cover-test_config.shift):
                           (len(y_data)-test_config.window_size-k+train_config.cover-test_config.shift)]
            ts_datay.append(new_y)

        for k in range(delay,train_config.train_size+delay):
            a = x_data[(x_data.shape[0]-train_config.window_size-k):(x_data.shape[0]-k)]
            tr_datax.append(a)
            new_y = y_data[len(y_data)-train_config.time_steps-train_config.window_size-k+train_config.cover:
                           len(y_data)-train_config.window_size-k+train_config.cover]
            tr_datay.append(new_y)
    
    
        tr_attn = np.zeros(shape=[train_config.batch_size,train_config.time_steps, train_config.cell_size])
        ts_attn = np.zeros(shape=[test_config.batch_size,test_config.time_steps, test_config.cell_size])

        tr_datax = np.reshape(a=tr_datax,newshape=[train_config.train_size,train_config.time_steps,train_config.input_size])
        tr_datay = np.reshape(a=tr_datay,newshape=[train_config.train_size,train_config.time_steps,1])

        ts_datax = np.reshape(a=ts_datax,newshape=[test_config.train_size,train_config.time_steps,train_config.input_size])
        ts_datay = np.reshape(a=ts_datay,newshape=[test_config.train_size,train_config.time_steps,1])
        self.x_train, self.y_train = tr_datax, tr_datay
        self.x_test, self.y_test = ts_datax, ts_datay
        self.y_train = self.y_train[:,1,:]
        self.y_test = self.y_test[:,1,:]
    def load_data(self):
        return (self.x_train,self.y_train), (self.x_test,self.y_test)


class Demo2(AirData):
    def __init__(self,file_path='/home/saturn/research/petpen/datasets/label_insert_air_2015_data.csv',**kwargs):
        super().__init__(file_path,**kwargs)
        self.windFeatures = ['wd','ws','wd_gust','ws_gust']
        self.otherFeatures = self.pollutantFeatures + self.trafficFeatures + self.meteoFeatures[:-4]
        self.df_data = self.rawData[self.otherFeatures+self.windFeatures]
        cols = self.df_data.columns.tolist()
        target_index = cols.index('PM25')
        if target_index  == len(cols)-1:
            cols = [cols[target_index]]+cols[:target_index]
        else:
            cols = [cols[target_index]]+cols[:target_index]+cols[target_index+1:]
        self.df_data = self.df_data[cols]
        self.y_train = self.df_data['PM25'].values[:5000]
        self.y_test = self.df_data['PM25'].values[5000:]
        self.x_train_wind = self.df_data[self.windFeatures].values[:5000]
        self.x_test_wind = self.df_data[self.windFeatures][5000:]
        self.x_train_other = self.df_data[self.otherFeatures].values[:5000]
        self.x_test_other = self.df_data[self.otherFeatures].values[5000:]
    def load_data(self):
        return([self.x_train_other,self.x_train_wind],self.y_train),([self.x_test_other,self.x_test_wind],self.y_test)

class Mnist():
    def __init__(self):
        from keras.datasets import mnist
        num_classes=10
        img_rows = img_cols = 28
        (x_train,y_train), (x_test,y_test) = mnist.load_data()
        x_train = x_train.reshape(x_train.shape[0], img_rows, img_cols, 1)
        x_test = x_test.reshape(x_test.shape[0], img_rows, img_cols, 1)
        input_shape = (28, 28, 1)
        self.x_train = x_train.astype('float32')
        self.x_test = x_test.astype('float32')
        self.x_train /= 255
        self.x_test /= 255
        
        # convert class vectors to binary class matrices
        import keras
        self.y_train = keras.utils.to_categorical(y_train, num_classes)
        self.y_test = keras.utils.to_categorical(y_test, num_classes)
        # print('x_train shape:', x_train.shape)
        # print(x_train.shape[0], 'train samples')
        # print(x_test.shape[0], 'test samples')
    def load_data(self):
        return (self.x_train,self.y_train), (self.x_test,self.y_test)

class Cifar():
    def __init__(self):
        from keras.datasets import cifar10
        (self.x_train, self.y_train), (self.x_test, self.y_test) = cifar10.load_data()
    def load_data(self):
        return (self.x_train, self.y_train), (self.x_test, self.y_test)
