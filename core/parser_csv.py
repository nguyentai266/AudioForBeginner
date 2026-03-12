import glob
import os
import re
from concurrent.futures import ThreadPoolExecutor

import pandas as pd

from core.load_config import load_yaml


class ParserLog(object):
	def __init__(self):
		super().__init__()
		self.config=load_yaml()
		self.select_phases=self.config["select_phase"]

	def load_limit(self,filepath,mode=""):
		col_use=self.config["column_use"]
		df=pd.read_csv(filepath,header=1,usecols=col_use)
		if mode=="audio_sort" or mode == "audio_full" or mode =="":
			sorted_df=df[df["phase"].isin(self.select_phases)].copy()
			df_copy=sorted_df.drop(columns="phase").copy()
			idx = df_copy.columns.get_loc("measurement")
			phase = df_copy["measurement"].str.extract(r'^(.*?)(?=_[\d]+\.?\d*$)')
			freq= df_copy['measurement'].str.extract(r'(\d+\.?\d*)$').astype(float) # lay ra tan so
			df_copy.insert(idx+1,'phase',phase)
			df_copy.insert(idx+2,"freq",freq)
			final=df_copy.drop(columns="measurement")
		elif mode == "rf":
			final=df.copy()
		return final

	def __load_data(self,filepath,mode):
		col_use=["phase","measurement","value"]
		info_log=pd.read_csv(filepath,nrows=0).to_string() #lay dong dau tien cua log
		info_dict={}
		if "dut_id:" in info_log:
			pattern = r'(\w+):\s*([\w\.\-]+)'
			matches=re.findall(pattern,info_log)
			info_dict=dict(matches)
			
		if info_dict:
			dut_id=info_dict.get("dut_id")
			result=info_dict.get("result")
			station_id=info_dict.get("station_id")
			log_id=(re.search(r'(\d{10,15})\.csv$', filepath)).group(1)
			info_df=pd.DataFrame({
				"measurement":["dut_id","result","station_id","log_id"],
				"value":[dut_id,result,station_id,(dut_id+"_"+log_id)]
				})
			df=pd.read_csv(filepath,header=1,usecols=col_use)
			if mode == "" or mode == "audio_sort":
				sort_df=df[df["phase"].isin(self.select_phases)].copy()
				sort_df=sort_df.drop(columns="phase")
				df_combined=pd.concat([info_df,sort_df],ignore_index=True)
				df_transpose=df_combined.set_index("measurement").T
			elif mode == "audio_full" or mode == "rf":
				df_full=df.drop(columns="phase").copy()
				df_combined=pd.concat([info_df,df_full],ignore_index=True)
				df_transpose=df_combined.set_index('measurement').T
				
			else:
				return "error"
			
			return df_transpose

	def __process_data(self,filepath,mode):
		try:
			return self.__load_data(filepath,mode)

		except Exception as e:
			print(f"Error: {e}")
			return None

	def summary_data(self,path_dir,mode=""):
		list_file=glob.glob(os.path.join(path_dir,"*.csv"))
		
		if list_file: df_limit=self.load_limit(filepath=list_file[0],mode=mode)
		with ThreadPoolExecutor(max_workers=8) as executor:
			results = list(executor.map(lambda f:self.__process_data(f,mode), list_file))
		li = [df for df in results if df is not None]
		if li: 
			li_cleaned = [df.loc[:, ~df.columns.duplicated()].copy() for df in li]
			df_summary = pd.concat(li_cleaned, axis=0, ignore_index=True)
		else:  df_summary = pd.DataFrame()
		return df_limit,df_summary		
	
	
			
	def df_phase_freq(self,dataframe):
		if "measurement" in dataframe.columns:
			idx = dataframe.columns.get_loc("measurement")
			phase_data = dataframe["measurement"].str.extract(r'^(.*?)(?=_[\d]+\.?\d*$)')[0]
			freq_data = dataframe["measurement"].str.extract(r'(\d+\.?\d*)$')[0].astype(float)
			dataframe.insert(idx + 1,"phase",phase_data)
			dataframe.insert(idx + 2,"freq",freq_data)
			dataframe["phase"] = phase_data.fillna(dataframe["measurement"])	
		df_copy=dataframe.drop(columns=["measurement"]).copy()
		
		return df_copy
	
	def group_data(self,dataFrame,groupBy):
		if groupBy == "dut_id":
			groups = [(key, g) for key, g in dataFrame.groupby(groupBy)]			
		elif groupBy == "station_id":
			groups = [(key, g) for key, g in dataFrame.groupby(groupBy)]
		else:
			return
		return groups


	
	
	

	



			
		
			
	
	


if __name__=="__main__":\
	
	#file="C:/Users/V1531673/Desktop/RFMS/Audio Basic/data_source/MT5_FVN-E1F3-G01_FATP-AUDIO_BJ25A-01_56100DLCQ00016_GRR_PASS_0-0_1766543317781.csv"
	parser=ParserLog()

	#limit=parser.load_limit(filepath=file)
	#pd.DataFrame.to_csv(limit,"limit.csv")
	'''
	app_path=os.getcwd()
	log_dir=os.path.join(app_path,"data/")
	mode="full"
	df_limit,df_summary=parser.summary_data(log_dir,mode=mode)

	df_summary_transpose=df_summary.T
	df_limit.to_csv("limit.csv",index=False	)
	df_summary_transpose.to_csv("summary.csv",index=True)'''
	#parser.update_log_files("summary.csv","log")
	path="C:/Users/nguye/Desktop/AudioForBeginner/sum.csv"
	dataFrame=pd.read_csv(path)
	phase='mic-1_fr'
	sort=dataFrame.filter(regex=rf"^({re.escape(phase)}_\d+(\.\d+)?|station_id)$").copy()
	groups=parser.group_data(sort,'mic-1_fr','station_id')
	for dut,group in groups:
		group.to_csv(f"C:/Users/nguye/Desktop/AudioForBeginner/dut/{dut}.csv")
	print("ok")
	
	


	#df=parser.df_phase_freq(data,select_phase=['dut_id','station_id',"spk-1_rb"])
	##df.to_csv("test.csv",index=False)
	


	
	













		


