import time
from settings import *
from SentenceLevel import featureExtractor as sentenceFeatureExtractor, probablityModel as sentenceProbablityModel, classifier as sentenceClassifier, prepare as sentencePrepare ,replaceExpand as sentenceReplaceExpand
from PhraseLevel import featureExtractor as phraseFeatureExtractor, probablityModel as phraseProbablityModel, classifier as phraseClassifier, prepare as phrasePrepare ,replaceExpand as phraseReplaceExpand

encode={'positive': 1.0,'negative': 2.0,'neutral':3.0}
decode={1.0:'positive',2.0:'negative',3.0:'neutral'}

if __name__=='__main__':
	while True:
    		"""sentence level"""
    		rows = db(db.SentTestDetails.PredictedStatus=='0').select()
    		print rows
		trainFile=os.path.join(appPath,'modules','SentenceLevel','trainData.txt')
		emoticonsFile=os.path.join(appPath,'modules','SentenceLevel','emoticonsWithPolarity.txt')
		acronymFile=os.path.join(appPath,'modules','SentenceLevel','acronym_tokenised.txt')
		stopWordsFile=os.path.join(appPath,'modules','SentenceLevel','stopWords.txt')
		uniFile=os.path.join(appPath,'modules','SentenceLevel','unigram.txt')
		biFile=os.path.join(appPath,'modules','SentenceLevel','bigram.txt')
		triFile=os.path.join(appPath,'modules','SentenceLevel','trigram.txt')
		acronymDict,stopWords,emoticonsDict = sentencePrepare.loadDictionary(emoticonsFile, acronymFile, stopWordsFile)

		affinFile=os.path.join(appPath,'modules','SentenceLevel','AFINN-111.txt')
    		priorScore=dict(map(lambda (k,v): (frozenset(reduce( lambda x,y:x+y,[[i] if i not in acronymDict else acronymDict[i][0] for i in k.split()])),int(v)),[ line.split('\t') for line in open(affinFile,'r') ]))

		modelPath=os.path.join(appPath,'modules','SentenceLevel','sentimentAnalysisSVM.model')    
		"""create Unigram Model"""
    		print "Creating Unigram Model......."
    		uniModel=[]
    		f=open(uniFile,'r')
    		for line in f:
    		    if line:
    		        line=line.strip('\r\t\n ')
    		        uniModel.append(line)
    		uniModel.sort()
		print uniModel
	
	    	print "Unigram Model Created"
	
	    	print "Creating Bigram Model......."
	    	biModel=[]
	    	f=open(biFile,'r')
	    	for line in f:
	    	    if line:
	    	        line=line.strip('\r\t\n ')
	    	        biModel.append(line)
	    	biModel.sort()
	    	print "Bigram Model Created"
		
	    	print "Creating Trigram Model......."
	    	triModel=[]
	    	f=open(triFile,'r')
	    	for line in f:
	    	    if line:
	    	        line=line.strip('\r\t\n ')
	    	        triModel.append(line)
	    	triModel.sort()
	    	print "Trigram Model Created"
	    	
	    	""" polarity dictionary combines prior score """
	    	polarityDictionary = sentenceProbablityModel.probTraining(priorScore)
			
	    
	    	"""Create a feature vector of training set """
	    	print "Creating Feature Vectors....."
			
	    	encode={'positive': 1.0,'negative': 2.0,'neutral':3.0}
	    	
	    	for row in rows:
			featureVectorsTest=[]
			tweet=row.Tweet.split()
			actualLabel=row.ActualLabel
			print tweet
			token=row.Token.split()
			if tweet:
		                vector=[]
                		vector,polarityDictionary=sentenceFeatureExtractor.findFeatures(tweet, token, polarityDictionary, stopWords, emoticonsDict, acronymDict)
				print vector
                		uniVector=[0]*len(uniModel)
                		for i in tweet:
                    			word=i.strip(sentenceReplaceExpand.specialChar).lower()
                    			if word:
                        			if word in uniModel:
                            				ind=uniModel.index(word)
                            				uniVector[ind]=1
                		vector=vector+uniVector

                		biVector=[0]*len(biModel)
                		tweet=[i.strip(sentenceReplaceExpand.specialChar).lower() for i in tweet]
                		tweet=[i for i in tweet if i]
                		for i in range(len(tweet)-1):
                    			phrase=tweet[i]+' '+tweet[i+1]
                    			if word in biModel:
                        			ind=biModel.index(phrase)
                        			biVector[ind]=1
                		vector=vector+biVector

                		triVector=[0]*len(triModel)
                		tweet=[i.strip(sentenceReplaceExpand.specialChar).lower() for i in tweet]
                		tweet=[i for i in tweet if i]

                		for i in range(len(tweet)-2):
                    			phrase=tweet[i]+' '+tweet[i+1]+' '+tweet[i+2]
                    			if word in triModel:
                        			ind=triModel.index(phrase)
                        			triVector[ind]=1
                		vector=vector+triVector

                		featureVectorsTest.append(vector)

				"""predict label"""
				print featureVectorsTest
				if not actualLabel:
					actualLabel='positive'
				print actualLabel
				predictedLabel=sentenceClassifier.svmLabelPredicter([encode[actualLabel]],featureVectorsTest,modelPath)[0]
				row.update_record(PredictedLabel=decode[predictedLabel], PredictedStatus='1')
        			db.commit()

    		"""phrase level"""
    		rows = db(db.PhraseTestDetails.PredictedStatus=='0').select()
    		print rows
		trainFile=os.path.join(appPath,'modules','PhraseLevel','trainData.txt')
		emoticonsFile=os.path.join(appPath,'modules','PhraseLevel','emoticonsWithPolarity.txt')
		acronymFile=os.path.join(appPath,'modules','PhraseLevel','acronym_tokenised.txt')
		stopWordsFile=os.path.join(appPath,'modules','PhraseLevel','stopWords.txt')
		uniFile=os.path.join(appPath,'modules','PhraseLevel','unigram.txt')
		biFile=os.path.join(appPath,'modules','PhraseLevel','bigram.txt')
		triFile=os.path.join(appPath,'modules','PhraseLevel','trigram.txt')
		acronymDict,stopWords,emoticonsDict = phrasePrepare.loadDictionary(emoticonsFile, acronymFile, stopWordsFile)

		affinFile=os.path.join(appPath,'modules','PhraseLevel','AFINN-111.txt')
    		priorScore=dict(map(lambda (k,v): (frozenset(reduce( lambda x,y:x+y,[[i] if i not in acronymDict else acronymDict[i][0] for i in k.split()])),int(v)),[ line.split('\t') for line in open(affinFile,'r') ]))

		modelPath=os.path.join(appPath,'modules','PhraseLevel','sentimentAnalysisSVM.model')    
		"""create Unigram Model"""
    		print "Creating Unigram Model......."
    		uniModel=[]
    		f=open(uniFile,'r')
    		for line in f:
    		    if line:
    		        line=line.strip('\r\t\n ')
    		        uniModel.append(line)
    		uniModel.sort()
		print uniModel
	
	    	print "Unigram Model Created"
	
	    	print "Creating Bigram Model......."
	    	biModel=[]
	    	f=open(biFile,'r')
	    	for line in f:
	    	    if line:
	    	        line=line.strip('\r\t\n ')
	    	        biModel.append(line)
	    	biModel.sort()
	    	print "Bigram Model Created"
		
	    	print "Creating Trigram Model......."
	    	triModel=[]
	    	f=open(triFile,'r')
	    	for line in f:
	    	    if line:
	    	        line=line.strip('\r\t\n ')
	    	        triModel.append(line)
	    	triModel.sort()
	    	print "Trigram Model Created"
	    	
	    	""" polarity dictionary combines prior score """
	    	polarityDictionary = phraseProbablityModel.probTraining(priorScore)
			
	    
	    	"""Create a feature vector of training set """
	    	print "Creating Feature Vectors....."
			
	    	encode={'positive': 1.0,'negative': 2.0,'neutral':3.0}

    		for row in rows:
			featureVectorsTest=[]
			tweet=row.Tweet
			phrase=row.Phrase.split()
            		token=row.Token.split()
			tweet=phrase  #treating phrase as tweet

			print token
			print phrase
			actualLabel=row.ActualLabel
			
			if tweet:
		                vector=[]
                		vector,polarityDictionary=phraseFeatureExtractor.findFeatures(tweet, token, polarityDictionary, stopWords, emoticonsDict, acronymDict)
				print vector
                		uniVector=[0]*len(uniModel)
                		for i in tweet:
                    			word=i.strip(phraseReplaceExpand.specialChar).lower()
                    			if word:
                        			if word in uniModel:
                            				ind=uniModel.index(word)
                            				uniVector[ind]=1
                		vector=vector+uniVector

                		biVector=[0]*len(biModel)
                		tweet=[i.strip(phraseReplaceExpand.specialChar).lower() for i in tweet]
                		tweet=[i for i in tweet if i]
                		for i in range(len(tweet)-1):
                    			phrase=tweet[i]+' '+tweet[i+1]
                    			if word in biModel:
                        			ind=biModel.index(phrase)
                        			biVector[ind]=1
                		vector=vector+biVector

                		triVector=[0]*len(triModel)
                		tweet=[i.strip(phraseReplaceExpand.specialChar).lower() for i in tweet]
                		tweet=[i for i in tweet if i]

                		for i in range(len(tweet)-2):
                    			phrase=tweet[i]+' '+tweet[i+1]+' '+tweet[i+2]
                    			if word in triModel:
                        			ind=triModel.index(phrase)
                        			triVector[ind]=1
                		vector=vector+triVector

                		featureVectorsTest.append(vector)

				"""predict label"""
				print featureVectorsTest
				if not actualLabel:
					actualLabel='positive'
				print actualLabel
				predictedLabel=phraseClassifier.svmLabelPredicter([encode[actualLabel]],featureVectorsTest,modelPath)[0]
				row.update_record(PredictedLabel=decode[predictedLabel], PredictedStatus='1')
        			db.commit()
    		time.sleep(60) # check every minute
    		db.commit()
