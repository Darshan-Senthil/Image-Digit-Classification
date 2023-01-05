# dataClassifier.py
# -----------------
# Licensing Information: Please do not distribute or publish solutions to this
# project. You are free to use and extend these projects for educational
# purposes. The Pacman AI projects were developed at UC Berkeley, primarily by
# John DeNero (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# For more info, see http://inst.eecs.berkeley.edu/~cs188/sp09/pacman.html

# This file contains feature extraction methods and harness 
# code for data classification

#import mostFrequent
import naiveBayes
import perceptron
import kNearestNeighbors
#import mira
import samples
import sys
import util
import time
import numpy as np

TEST_SET_SIZE = 100
DIGIT_DATUM_WIDTH=28
DIGIT_DATUM_HEIGHT=28
FACE_DATUM_WIDTH=60
FACE_DATUM_HEIGHT=70


def basicFeatureExtractorDigit(datum):
  """
  Returns a set of pixel features indicating whether
  each pixel in the provided datum is white (0) or gray/black (1)
  """
  a = datum.getPixels()

  features = util.Counter()
  for x in range(DIGIT_DATUM_WIDTH):
    for y in range(DIGIT_DATUM_HEIGHT):
      if datum.getPixel(x, y) > 0:
        features[(x,y)] = 1
      else:
        features[(x,y)] = 0
  return features

def basicFeatureExtractorFace(datum):
  """
  Returns a set of pixel features indicating whether
  each pixel in the provided datum is an edge (1) or no edge (0)
  """
  a = datum.getPixels()

  features = util.Counter()
  for x in range(FACE_DATUM_WIDTH):
    for y in range(FACE_DATUM_HEIGHT):
      if datum.getPixel(x, y) > 0:
        features[(x,y)] = 1
      else:
        features[(x,y)] = 0
  return features

def enhancedFeatureExtractorDigit(datum):
  """
  Your feature extraction playground.
  
  You should return a util.Counter() of features
  for this datum (datum is of type samples.Datum).
  
  ## DESCRIBE YOUR ENHANCED FEATURES HERE...
  
  ##
  """
  features =  basicFeatureExtractorDigit(datum)

  "*** YOUR CODE HERE ***"
  
  return features


def contestFeatureExtractorDigit(datum):
  """
  Specify features to use for the minicontest
  """
  features =  basicFeatureExtractorDigit(datum)
  return features

def enhancedFeatureExtractorFace(datum):
  """
  Your feature extraction playground for faces.
  It is your choice to modify this.
  """
  features =  basicFeatureExtractorFace(datum)
  return features

def analysis(classifier, guesses, testLabels, testData, rawTestData, printImage):
  """
  This function is called after learning.
  Include any code that you want here to help you analyze your results.
  
  Use the printImage(<list of pixels>) function to visualize features.
  
  An example of use has been given to you.
  
  - classifier is the trained classifier
  - guesses is the list of labels predicted by your classifier on the test set
  - testLabels is the list of true labels
  - testData is the list of training datapoints (as util.Counter of features)
  - rawTestData is the list of training datapoints (as samples.Datum)
  - printImage is a method to visualize the features 
  (see its use in the odds ratio part in runClassifier method)
  
  This code won't be evaluated. It is for your own optional use
  (and you can modify the signature if you want).
  """
  
  # Put any code here...
  # Example of use:
  for i in range(len(guesses)):
      prediction = guesses[i]
      truth = testLabels[i]
      if (prediction != truth):
          # print("===================================")
          # print("Mistake on example %d" % i) 
          # print("Predicted %d; truth is %d" % (prediction, truth))
          # print("Image: ")
          # print(rawTestData[i])
          break


## =====================
## You don't have to modify any code below.
## =====================


class ImagePrinter:
    def __init__(self, width, height):
      self.width = width
      self.height = height

    def printImage(self, pixels):
      """
      Prints a Datum object that contains all pixels in the 
      provided list of pixels.  This will serve as a helper function
      to the analysis function you write.
      
      Pixels should take the form 
      [(2,2), (2, 3), ...] 
      where each tuple represents a pixel.
      """
      image = samples.Datum(None,self.width,self.height)
      for pix in pixels:
        try:
            # This is so that new features that you could define which 
            # which are not of the form of (x,y) will not break
            # this image printer...
            x,y = pix
            image.pixels[x][y] = 2
        except:
            print("new features:", pix)
            continue
      print(image)  

def default(str):
  return str + ' [Default: %default]'

def readCommand( argv ):
  "Processes the command used to run from the command line."
  from optparse import OptionParser  
  parser = OptionParser(USAGE_STRING)
  
  parser.add_option('-c', '--classifier', help=default('The type of classifier'), choices=['mostFrequent', 'nb', 'naiveBayes', 'perceptron', 'kNN', 'kNearestNeighbors', 'mira', 'minicontest'], default='mostFrequent')
  parser.add_option('-d', '--data', help=default('Dataset to use'), choices=['digits', 'faces'], default='digits')
  parser.add_option('-t', '--training', help=default('The size of the training set'), default=100, type="int")
  parser.add_option('-f', '--features', help=default('Whether to use enhanced features'), default=False, action="store_true")
  parser.add_option('-o', '--odds', help=default('Whether to compute odds ratios'), default=False, action="store_true")
  parser.add_option('-1', '--label1', help=default("First label in an odds ratio comparison"), default=0, type="int")
  parser.add_option('-2', '--label2', help=default("Second label in an odds ratio comparison"), default=1, type="int")
  parser.add_option('-w', '--weights', help=default('Whether to print weights'), default=False, action="store_true")
  parser.add_option('-k', '--smoothing', help=default("Smoothing parameter (ignored when using --autotune)"), type="float", default=1.0)
  parser.add_option('-a', '--autotune', help=default("Whether to automatically tune hyperparameters"), default=False, action="store_true")
  parser.add_option('-i', '--iterations', help=default("Maximum iterations to run training"), default=2, type="int")
  parser.add_option('-s', '--test', help=default("Amount of test data to use"), default=TEST_SET_SIZE, type="int")

  options, otherjunk = parser.parse_args(argv)
  if len(otherjunk) != 0: raise Exception('Command line input not understood: ' + str(otherjunk))
  args = {}
  
  # Set up variables according to the command line input.
  '''print("Doing classification")
  print("--------------------")
  print("data:\t\t" + options.data)
  print("classifier:\t\t" + options.classifier)
  if not options.classifier == 'minicontest':
    print("using enhanced features?:\t" + str(options.features))
  else:
    print("using minicontest feature extractor")
  print("training set size:\t" + str(options.training))'''
  if(options.data=="digits"):
    printImage = ImagePrinter(DIGIT_DATUM_WIDTH, DIGIT_DATUM_HEIGHT).printImage
    if (options.features):
      featureFunction = enhancedFeatureExtractorDigit
    else:
      featureFunction = basicFeatureExtractorDigit
    if (options.classifier == 'minicontest'):
      featureFunction = contestFeatureExtractorDigit
  elif(options.data=="faces"):
    printImage = ImagePrinter(FACE_DATUM_WIDTH, FACE_DATUM_HEIGHT).printImage
    if (options.features):
      featureFunction = enhancedFeatureExtractorFace
    else:
      featureFunction = basicFeatureExtractorFace      
  else:
    print("Unknown dataset", options.data)
    print(USAGE_STRING)
    sys.exit(2)
    
  if(options.data=="digits"):
    legalLabels = list(range(10))
  else:
    legalLabels = list(range(2))
    
  if options.training <= 0:
    print("Training set size should be a positive integer (you provided: %d)" % options.training)
    print(USAGE_STRING)
    sys.exit(2)
    
  if options.smoothing <= 0:
    print("Please provide a positive number for smoothing (you provided: %f)" % options.smoothing)
    print(USAGE_STRING)
    sys.exit(2)
    
  if options.odds:
    if options.label1 not in legalLabels or options.label2 not in legalLabels:
      print("Didn't provide a legal labels for the odds ratio: (%d,%d)" % (options.label1, options.label2))
      print(USAGE_STRING)
      sys.exit(2)

  if(options.classifier == "mostFrequent"):
    classifier = mostFrequent.MostFrequentClassifier(legalLabels)
  elif(options.classifier == "kNN" or options.classifier == "kNearestNeighbors"):
    classifier = kNearestNeighbors.kNearestNeighborsClassifier(legalLabels)
  elif(options.classifier == "naiveBayes" or options.classifier == "nb"):
    classifier = naiveBayes.NaiveBayesClassifier(legalLabels)
    classifier.setSmoothing(options.smoothing)
    if (options.autotune):
        print("using automatic tuning for naivebayes")
        classifier.automaticTuning = True
    else:
        #print("using smoothing parameter k=%f for naivebayes" %  options.smoothing)
        a = '....'
  elif(options.classifier == "perceptron"):
    classifier = perceptron.PerceptronClassifier(legalLabels,options.iterations)
  elif(options.classifier == "mira"):
    classifier = mira.MiraClassifier(legalLabels, options.iterations)
    if (options.autotune):
        print("using automatic tuning for MIRA")
        classifier.automaticTuning = True
    else:
        print("using default C=0.001 for MIRA")
  elif(options.classifier == 'minicontest'):
    import minicontest
    classifier = minicontest.contestClassifier(legalLabels)
  else:
    print("Unknown classifier:", options.classifier)
    print(USAGE_STRING)
    
    sys.exit(2)

  args['classifier'] = classifier
  args['featureFunction'] = featureFunction
  args['printImage'] = printImage
  
  return args, options

USAGE_STRING = """
  USAGE:      python dataClassifier.py <options>
  EXAMPLES:   (1) python dataClassifier.py
                  - trains the default mostFrequent classifier on the digit dataset
                  using the default 100 training examples and
                  then test the classifier on test data
              (2) python dataClassifier.py -c naiveBayes -d digits -t 1000 -f -o -1 3 -2 6 -k 2.5
                  - would run the naive Bayes classifier on 1000 training examples
                  using the enhancedFeatureExtractorDigits function to get the features
                  on the faces dataset, would use the smoothing parameter equals to 2.5, would
                  test the classifier on the test data and performs an odd ratio analysis
                  with label1=3 vs. label2=6
                 """

# Main harness code

def runClassifier(args, options):
  #print(options)

  featureFunction = args['featureFunction']
  classifier = args['classifier']
  printImage = args['printImage']
      
  # Load data  
  numTraining = options.training
  numTest = options.test

  if(options.data=="faces"):
    rawTrainingData, chosenList = samples.loadDataFile("facedata/facedatatrain", numTraining,FACE_DATUM_WIDTH,FACE_DATUM_HEIGHT,True)
    trainingLabels = samples.loadLabelsFile("facedata/facedatatrainlabels", chosenList)
    rawTestData, chosenList = samples.loadDataFile("facedata/facedatatest", numTest,FACE_DATUM_WIDTH,FACE_DATUM_HEIGHT)
    testLabels = samples.loadLabelsFile("facedata/facedatatestlabels", chosenList)
  else:
    rawTrainingData, chosenList = samples.loadDataFile("digitdata/trainingimages", numTraining,DIGIT_DATUM_WIDTH,DIGIT_DATUM_HEIGHT,True)
    trainingLabels = samples.loadLabelsFile("digitdata/traininglabels", chosenList)
    rawTestData, chosenList = samples.loadDataFile("digitdata/testimages", numTest,DIGIT_DATUM_WIDTH,DIGIT_DATUM_HEIGHT)
    testLabels = samples.loadLabelsFile("digitdata/testlabels", chosenList)
    
  
  # Extract features
  #print("Extracting features...")
  trainingData = list(map(featureFunction, rawTrainingData))
  # validationData = list(map(featureFunction, rawValidationData))
  testData = list(map(featureFunction, rawTestData))
  
  # Conduct training and testing
  #print("Training...")
  validationData, validationLabels = [0], [0]
  start_time = time.time()
  classifier.train(trainingData, trainingLabels, validationData, validationLabels)
  train_time = time.time() - start_time
  #print(train_time, end='')
  #print (" (training time)")
  #exit()
  #print("Testing...")
  guesses = classifier.classify(testData)
  correct = [guesses[i] == testLabels[i] for i in range(len(testLabels))].count(True)
  #print(str(correct), ("correct out of " + str(len(testLabels)) + " (%.1f%%).") % (100.0 * correct / len(testLabels)))
  final_result = (100.0 * correct / len(testLabels))
  #print("Result: ",final_result)

  return final_result, train_time
  
  '''analysis(classifier, guesses, testLabels, testData, rawTestData, printImage)
  
  
  
  # do odds ratio computation if specified at command line
  if((options.odds) & (options.classifier == "naiveBayes" or (options.classifier == "nb")) ):
    label1, label2 = options.label1, options.label2
    features_odds = classifier.findHighOddsFeatures(label1,label2)
    if(options.classifier == "naiveBayes" or options.classifier == "nb"):
      string3 = "=== Features with highest odd ratio of label %d over label %d ===" % (label1, label2)
    else:
      string3 = "=== Features for which weight(label %d)-weight(label %d) is biggest ===" % (label1, label2)    
      
    print(string3)
    printImage(features_odds)

  if((options.weights) & (options.classifier == "perceptron")):
    for l in classifier.legalLabels:
      features_weights = classifier.findHighWeightFeatures(l)
      print(("=== Features with high weight for label %d ==="%l))
      printImage(features_weights)'''
  
def accuracy(input_arr):
  input_array = input_arr
  output_accuracy = []
  training_time = [] 
  for k in range(5):
    #print("Iteration : ", 1)
    args, options = readCommand(input_array) 
    result_accuracy, result_training_time = runClassifier(args, options)
    output_accuracy.append(result_accuracy)
    training_time.append(result_training_time)
  #print(" % of Accuracy : ",output_accuracy)
  #print("Time taken for training : ",training_time)
  mean_accuracy = np.average(output_accuracy)
  #print("Mean of Accuracy :",mean_accuracy)
  std_accuracy = np.std(output_accuracy)
  #print("Standard Deviation :", std_accuracy)
  time_taken = round((np.average(training_time)),3)
  #print("Average Time Taken for Training: ", time_taken)
  #print("")
  #print("**************************************************************************************************************************************")
  #print("")

  return mean_accuracy, std_accuracy, time_taken


if __name__ == '__main__':

  # Read input
  input_array_classifier = sys.argv[1:2]
  #print(input_array_classifier)
  input_array_datatype = sys.argv[2:]
  #print(input_array_datatype)

  if (input_array_classifier[0] == 'naiveBayes'):
    if (input_array_datatype[0] == 'digits'):
      mean_accuracy_list = []
      std_accuracy_list = []
      time_taken_list = []
      values = ['500','1000', '1500', '2000', '2500', '3000', '3500', '4000', '4500', '5000']
      for i in values:
        #print("Inside Iterations")
        print("")
        print("Executing naiveBayes for Digits-> Training data : ", i)
        input_array = ['-c', 'naiveBayes', '-d', 'digits', '-t', i, '-f', '-o', '-1', '3', '-2', '6', '-k', '2.5']
        mean_accuracy, std_accuracy, time_taken = accuracy(input_array)
        mean_accuracy_list.append(mean_accuracy)
        std_accuracy_list.append(std_accuracy)
        time_taken_list.append(time_taken)
      print("Accuracy : ",mean_accuracy_list)
      print("Standard Deviation : ", std_accuracy_list)
      print("Time Taken : ", time_taken_list)
      print("")
      print("**************************************************************************************************************************************")
      
    elif (input_array_datatype[0] == 'faces'):
      mean_accuracy_list = []
      std_accuracy_list = []
      time_taken_list = []     
      values = ['45','90','135','180','225','270','315','360','405','450']
      for i in values:
        print("")
        print("Executing naiveBayes for Faces-> Training data : ", i)
        input_array = ['-c' ,'naiveBayes', '-d', 'faces', '-t' , i ,'-f' ,'-o' ,'-k' ,'2.5']
        mean_accuracy, std_accuracy, time_taken = accuracy(input_array)
        mean_accuracy_list.append(mean_accuracy)
        std_accuracy_list.append(std_accuracy)
        time_taken_list.append(time_taken)
      print("Accuracy: ",mean_accuracy_list)
      print("Standard Deviation : ", std_accuracy_list)
      print("Time Taken : ", time_taken_list)  
      print("")
      print("**************************************************************************************************************************************")

    else :
      print("")
      print(" INPUT ERROR : ENTER THE PROPER VALUES !!!")

  elif (input_array_classifier[0] == 'kNearestNeighbors' or input_array_classifier[0] == 'perceptron'):
    if (input_array_datatype[0] == 'digits'):
      mean_accuracy_list = []
      std_accuracy_list = []
      time_taken_list = []
      values = ['500','1000', '1500', '2000', '2500', '3000', '3500', '4000', '4500', '5000']
      for i in values:
        print("")
        print("Executing " + input_array_classifier[0] + " for Digits-> Training data : ", i)
        input_array = ['-c' ,input_array_classifier[0], '-d', 'digits', '-t' , i ,'-f' ,'-o' ,'-1' ,'3' ,'-2' ,'6']
        mean_accuracy, std_accuracy, time_taken = accuracy(input_array)
        mean_accuracy_list.append(mean_accuracy)
        std_accuracy_list.append(std_accuracy)
        time_taken_list.append(time_taken)
      print("Accuracy : ",mean_accuracy_list)
      print("Standard Deviation : ", std_accuracy_list)
      print("Time Taken : ", time_taken_list)
      print("")
      print("**************************************************************************************************************************************")

    elif (input_array_datatype[0] == 'faces'):
      mean_accuracy_list = []
      std_accuracy_list = []
      time_taken_list = []
      values = ['45','90','135','180','225','270','315','360','405','450']
      for i in values:
        print("")
        print("Executing " + input_array_classifier[0] + " for Faces-> Training data :", i)
        input_array = ['-c' ,input_array_classifier[0], '-d', 'faces', '-t' , i ,'-f' ,'-o']
        mean_accuracy, std_accuracy, time_taken = accuracy(input_array)
        mean_accuracy_list.append(mean_accuracy)
        std_accuracy_list.append(std_accuracy)
        time_taken_list.append(time_taken)
      print("Accuracy : ",mean_accuracy_list)
      print("Standard Deviation : ", std_accuracy_list)
      print("Time Taken : ", time_taken_list)
      print("")
      print("**************************************************************************************************************************************")

    else :
      print("")
      print(" INPUT ERROR : ENTER THE PROPER VALUES !!!")

  else :
    print("")
    print(" INPUT ERROR : ENTER THE PROPER VALUES !!!")
