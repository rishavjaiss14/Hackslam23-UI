from PyPDF2 import PdfReader
import textract
import nltk
import ssl
import re
from pdfminer.high_level import extract_text
import pytesseract
from pdf2image import convert_from_path
import requests

import spacy

NER = spacy.load("en_core_web_sm")

try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

nltk.download('popular')
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
nltk.download('maxent_ne_chunker')
nltk.download('words')
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords


EMAIL_REG = re.compile(r'[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.[a-z]+')

def extract_text_from_pdf(pdf_path):
    txt = extract_text(pdf_path)
    if txt:
        return txt.replace('\t', ' ')
    return None

def extract_names(txt):
    person_names = []

    text1 = NER(txt)


    for word in text1.ents:
        if (hasattr(word,'label_') and word.label_ == 'PERSON'):
            person_names.append(word.text)
 
    # for sent in nltk.sent_tokenize(txt):
        
    #     chunks = nltk.pos_tag(nltk.word_tokenize(sent))
    #     print(chunks, 'chunks')
    #     for chunk in nltk.ne_chunk(chunks):
    #         print(chunk, 'chunk extract')
    #         if hasattr(chunk, 'label') and chunk.label() == 'PERSON':
    #             print(chunk, 'chunk')
    #             person_names.append(
    #                 ' '.join(chunk_leave[0] for chunk_leave in chunk.leaves())
    #             )
 
    return person_names


def list_to_string(s):
 
    # initialize an empty string
    str1 = ""
 
    # traverse in the string
    for ele in s:
        str1 += " " + ele
 
    # return the string
    return str1

def extract_emails(resume_text):
    return re.findall(EMAIL_REG, resume_text)

def skill_exists(skill):

    url = f'https://api.apilayer.com/skills?q={skill}&amp;count=1'
    headers = {'apikey': 'ejsgcl32UdHtODDEHppRjB3dD1bA814L'}
    response = requests.request('GET', url, headers=headers)
    result = response.json()

    if response.status_code == 200:
        return len(result) > 0 and result[0].lower() == skill.lower()
    raise Exception(result.get('message'))

def extract_skills(resume_text):

    stop_words = stopwords.words('english')
    word_tokens = word_tokenize(resume_text)

    filtered_tokens = [w for w in word_tokens if w not in stop_words]


    filtered_tokens = [w for w in filtered_tokens if w.isalpha()]


    # generate bigrams and trigrams (such as artificial intelligence)
    bigrams_trigrams = list(map(' '.join, nltk.everygrams(filtered_tokens, 2, 3)))


    found_skills = set()

    for token in filtered_tokens:
        if (skill_exists(token.lower())):
            found_skills.add(token)

    # for ngram in bigrams_trigrams:
    #     if (skill_exists(ngram.lower())):
    #         found_skills.add(ngram)
    
    return found_skills

#Write a for-loop to open many files (leave a comment if you'd like to learn how).
filename = 'FullStack.pdf' 

images = convert_from_path(filename)
ocr_text = pytesseract.image_to_string(images[0])

# text = extract_text_from_pdf(filename)

#open allows you to read the file.
# pdfFileObj = open(filename,'rb')
#The pdfReader variable is a readable object that will be parsed.
# pdfReader =  PdfReader(pdfFileObj)
# #Discerning the number of pages will allow us to parse through all the pages.
# num_pages = len(pdfReader.pages)
# count = 0
# text = ""
# #The while loop will read each page.
# while count < num_pages:
#     pageObj = pdfReader.pages[count]
#     count +=1
#     text += pageObj.extract_text()
# #This if statement exists to check if the above library returned words. It's done because PyPDF2 cannot read scanned files.
# if text != "":
#    text = text
# #If the above returns as False, we run the OCR library textract to #convert scanned/image based PDF files into text.
# else:
#    text = textract.process(fileurl, method='tesseract', language='eng')
#Now we have a text variable that contains all the text derived from our PDF file. Type print(text) to see what it contains. It likely contains a lot of spaces, possibly junk such as '\n,' etc.
#Now, we will clean our text variable and return it as a list of keywords.

# print(text)

# #The word_tokenize() function will break our text phrases into individual words.
# tokens = word_tokenize(text, 'english', True)

# #We'll create a new list that contains punctuation we wish to clean.
# punctuations = ['(',')',';',':','[',']',',']
# #We initialize the stopwords variable, which is a list of words like "The," "I," "and," etc. that don't hold much value as keywords.
# stop_words = stopwords.words('english')

# #We create a list comprehension that only returns a list of words that are NOT IN stop_words and NOT IN punctuations.
# keywords = [word for word in tokens if word not in stop_words and word not in punctuations]

# keywordsString = list_to_string(tokens)

names = extract_names(ocr_text)

email = extract_emails(ocr_text)

skills = extract_skills(ocr_text)


print(names, 'names')
print(email, 'email')
print(skills, 'skills')
