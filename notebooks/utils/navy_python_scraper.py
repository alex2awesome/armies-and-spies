import re
import spacy
from spacy.matcher import Matcher
import numpy as np 

# setup 
nlp = spacy.load('en_core_web_sm')
matcher = Matcher(nlp.vocab)
matcher.add('court-martial', None,
            [{}, {'LOWER': 'court'}, {'IS_PUNCT': True}, {'LOWER': 'martial'}],
            [{}, {'LOWER': 'court'}, {'LOWER': 'martial'}])

states =['Alaska', 'Alabama', 'Arkansas', 'American Samoa', 'Arizona', 'California', 'Colorado', 'Connecticut',
         'District of Columbia', 'Delaware', 'Florida', 'Georgia', 'Guam', 'Hawaii', 'Iowa', 'Idaho',
        'Illinois', 'Indiana', 'Kansas', 'Kentucky', 'Louisiana', 'Massachusetts', 'Maryland', 'Maine',
         'Michigan', 'Minnesota', 'Missouri', 'Northern Mariana Islands', 'Mississippi', 'Montana', 'National',
         'North Carolina', 'North Dakota', 'Nebraska', 'New Hampshire', 'New Jersey', 'New Mexico', 'Nevada',
         'New York', 'Ohio', 'Oklahoma', 'Oregon', 'Pennsylvania', 'Puerto Rico', 'Rhode Island', 'South Carolina',
         'South Dakota', 'Tennessee', 'Texas', 'Utah', 'Virginia', 'Virgin Islands', 'Vermont', 'Washington',
         'Wisconsin', 'West Virginia', 'Wyoming']

matcher.add('state', None,
            *[[{'LOWER': state.lower()}] for state in states])

rank_re = (
    "\,\s[A-Z]{2,5}[0-9]{0,2}\s|"
    "E[0-9]{1}|"
    "E\-[0-9]|"
    "O\-[0-9]|"
    "Lieutenant|"
    "Seaman|"
    "Major|"
    "Midshipman|"
    "Cpl|"
    "Lieutenant |"
    "Seaman |"
    "Major |"
    "Navy Midshipman |"
    "ENS |"
    "GySgt |"
    "Private |"
    "Sergeant |"
    "Lieutenant Junior Grade|"
    "1stSgt|"
    "CWO2|"
    "\sLCDR\s|"
    "FC2|"
    "Sgt|"
    "Lance|"
    "ET3|"
    "MA3|"
    "ATAN|"
    "Lance\sCpl\.\s|"
    "FT1"
)

date_re = ('([0-3]{0,1}'
           '[0-9]\s('
               'January|'
               'February|'
               'March|'
               'April|'
               'Apr |'
               'May|'
               'June|'
               'July|'
               'August|'
               'September|'
               'October|'
               'November|'
               'December'
           ')\s201[3-7])'
)

sentence_re = "sentenced him|sentenced her|sentenced the|sentenced|ruled that"

def clean_paragraph(paragraph):
    paragraph = (paragraph.replace('\n','')
                        .replace('onboard','in')
                        .replace('pleaded  guilty','pleaded guilty')
                        .replace('at the','in the')
                        .replace('pled                                guilty','pled guilty')
                        .replace('pledguilty','pled guilty')
                        .replace('USNpled','USN pled')
                        .replace(u"\xa02 \x0c", '')
                        .replace('On ','On ')
                        .replace('PS1Bobby', 'PS1 Bobby')
                        .replace('was found guilty','was tried')
                        .replace('was found not guilty','was tried'))
    paragraph= paragraph.split('***')[0]

    return paragraph

def get_date(paragraph, output=None, date_re=date_re):
    if output == None:
        output = {}

    date = re.search(date_re, paragraph)
    if date:
        output['Date'] = date.group()
    return output

def get_gender(paragraph, output=None):
    if output == None:
        output = {}

    # Get gender
    if re.search('\shis\s|\shim\s|\she\s', paragraph.lower()) > 1:
        output['Gender'] = 'male'
    if re.search('\shers\s|\sshe\s|\sher\s', paragraph.lower()) > 1:
        output['Gender'] = 'female'
    return output

def get_name(paragraph, output=None, rank_re=rank_re):
    if output == None:
        output = {}
    ##### Get Person
    after_name_re = "USMC|USN| pleaded guilty | was tried | pled guilty "
    chunks = re.split(after_name_re, paragraph)
    if len(chunks) >= 2:
        chunks = re.split(rank_re, chunks[0].replace(', III', ''))
        if len(chunks) >= 2:
            output['Name'] = (chunks[-1].replace(',', '').strip() or np.nan)
    if 'Name' not in output:
        print paragraph
    return output

def get_described_offense(row, output=None):
    if output == None:
        output = {}
        
    after_name_re = "pleaded guilty | was tried | pled guilty |were tried\, jointly\, | pled guilty pursuant"
    chunks = re.split(after_name_re, row)
    if len(chunks) >= 2:
        end = chunks[1]
        output['Offense'] = end.split('.')[0]
    if 'Offense' not in output:
        print row
    return output

def get_rank(paragraph, output=None, rank_re=rank_re):
    if output == None:
        output = {}
    # Get Rank
    rank = re.findall(rank_re, paragraph)
    rank = filter(lambda x: 'USN' not in x, map(lambda x: x.replace(',','').strip(), rank))
    if len(rank) == 0:
        print ('no rank..')
        print (paragraph)
    else:
        output['Rank'] = rank[0]
    return output

def get_location(paragraph, output=None, rank_re=rank_re):
    if output==None:
        output = {}

    par_split = re.split('\sin\s|\son\sboard\s|\sat\s|\son\s', paragraph)
    if len(par_split) < 2:
        print paragraph
        return

    location_str = re.split(rank_re, par_split[1])[0]
    chunks = map(lambda x: x.strip(), location_str.strip().split(','))
    if len(chunks) >=1:
        output['city'] = chunks[0]
        if 'Washington' in output['city']:
            output['city'] = 'Washington, D.C.'
        if len(chunks) >= 2:
            if chunks[1] in states:
                output['state'] = chunks[1]
                output['country'] = 'U.S.A.'
            if  chunks[1] == 'D.C.':
                output['country'] = 'U.S.A.'
            else:
                output['country'] = chunks[1]
            if len(chunks) >= 3:
                output['country'] = chunks[2]
    return output

def get_conviction(paragraph, output=None):
    if output==None:
        output = {}

    ## conviction
    if (('acquitted' in paragraph) 
        or ('not guilty' in paragraph)
        or ('innocent' in paragraph)
       ):
        output['Conclusion'] = 'not guilty'
        
    elif (
        ('pleaded guilty' in paragraph) 
        or ('pled guilty' in paragraph) 
        or ('guilty' in paragraph)  
       or ('sentenced' in paragraph)
    ):
        output['Conclusion'] = 'guilty'

    elif ('convicted' in paragraph):
        output['Conclusion'] = 'guilty'
        
    if 'Conclusion' not in output:
        print paragraph
        
    return output

def get_sentence(paragraph, output=None, sentence_re=sentence_re):
    if output == None:
        output = {}

    sentence_chunks = re.split(sentence_re, paragraph)
    if len(sentence_chunks) >=2:
        output['Sentence'] = sentence_chunks[1].split('.')[0]

    if ('Sentence' not in output) and (output.get('Conclusion') == 'guilty'):
        print paragraph
    return output


def cleanup(paragraph, output):
    for k, v in output.items():
        if isinstance(v, str):
            output[k] = v.strip()

    # clean up state/country
    if output.get('Country') in states:
        output['Country'] = 'USA'

    return output