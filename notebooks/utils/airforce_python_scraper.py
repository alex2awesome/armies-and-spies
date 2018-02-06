import re
import spacy
from spacy.matcher import Matcher
import numpy as np 

# setup 
# nlp = spacy.load('en_core_web_sm')
# matcher = Matcher(nlp.vocab)
# matcher.add('court-martial', None,
#             [{}, {'LOWER': 'court'}, {'IS_PUNCT': True}, {'LOWER': 'martial'}],
#             [{}, {'LOWER': 'court'}, {'LOWER': 'martial'}])

states =['Alaska', 'Alabama', 'Arkansas', 'American Samoa', 'Arizona', 'California', 'Colorado', 'Connecticut',
         'District of Columbia', 'Delaware', 'Florida', 'Georgia', 'Guam', 'Hawaii', 'Iowa', 'Idaho',
        'Illinois', 'Indiana', 'Kansas', 'Kentucky', 'Louisiana', 'Massachusetts', 'Maryland', 'Maine',
         'Michigan', 'Minnesota', 'Missouri', 'Northern Mariana Islands', 'Mississippi', 'Montana', 'National',
         'North Carolina', 'North Dakota', 'Nebraska', 'New Hampshire', 'New Jersey', 'New Mexico', 'Nevada',
         'New York', 'Ohio', 'Oklahoma', 'Oregon', 'Pennsylvania', 'Puerto Rico', 'Rhode Island', 'South Carolina',
         'South Dakota', 'Tennessee', 'Texas', 'Utah', 'Virginia', 'Virgin Islands', 'Vermont', 'Washington',
         'Wisconsin', 'West Virginia', 'Wyoming']+['WA','WI','WV','FL','WY','NH','NJ','NM','NA','NC','ND','NE',
         'NY','RI','NV','GU','CO','CA','GA','CT','OK','OH','KS','SC','KY','OR','SD','DE','DC','HI','PR',
         'TX','LA','TN','PA','VA','VI','AK','AL','AS','AR','VT','IL','IN','IA','AZ','ID','ME','MD','MA',
         'UT','MO','MN','MI','MT','MP','MS']


# matcher.add('state', None,
#             *[[{'LOWER': state.lower()}] for state in states])

rank_re = (
    "\,\s[A-Z]{2,5}[0-9]{0,2}\s|"
    "E[0-9]{1}|"
    "E\-[0-9]|"
    "O\-[0-9]|"
    "1stSgt|"
    "ATAN|"
    "enlisted Airman|"
    "Airman First Class|"
    "Airman|"
    "CWO2|"
    "Camp sergeant|"
    "Captain|"
    "Chief Hospital Corpsman|"
    "Chief Warrant Officer [0-9]{0, 1}|"
    "Chief Warrant Officer-[0-9]{0, 1}|"
    "Chief Warrant Officer|"
    "Colonel|"
    "Commander|"
    "Corporal|"
    "Cpl|"
    "ET3|"
    "FC2|"
    "FT1|"
    "Gunnery|"
    "GySgt|"
    "Hospital Corpsman First Class|"
    "Hospital Corpsman Third Class|"
    "Hospitalman 1st Class|"
    "Hospitalman|"
    "Lance Corporal|"
    "Lance\sCpl\.\s|"
    "Lance|"
    "Lieutenant Junior Grade|"
    "Lieutenant|"
    "Lieutenant|"
    "MA3|"
    "Major|"
    "Major|"
    "Master Gunnery|"
    "Master|"
    "Master Sergeant|"
    "Petty 12,   Officer First Class|"
    "Petty Officer 2nd Class|"
    "Petty Officer 3rd Class|"
    "Petty Officer First Class|"
    "Petty Officer Second Class|"
    "Petty Officer Third Class|"
    "Private First Class|"
    "Private|"
    "First Lieutenant|"
    "Religious Program Specialist Second Class|"
    "Seaman|"
    "Senior Airman|"
    "Sergeant |"
    "Sgt|"
    "Staff Sergeant|"
    "\sLCDR\s|"
    "a staff MCB Camp Butler|"
    "captain|"
    "cadet|"
    "chief warrant officer 2|"
    "chief warrant officer [0-9]{0, 1}|"
    "corporal|"
    "gunnery sergeant|"
    "hospitalman|"
    "lance corporal|"
    "lance|"
    "lieutenant colonel|"
    "lieutenant|"
    "major|"
    "master MHG,  III MEF sergeant|"
    "master|"
    "officer|"
    "petty officer first class|"
    "petty officer second class|"
    "petty officer third class|"
    "private MCB Butler first class|"
    "private first class|"
    "private|"
    "sergeant|"
    "Technical Sergeant|"
    "Senior Master Sergeant|"
    "staff sergeant"
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
sentence_re = (
    "sentenced him|"
    "sentenced her|"
    "sentenced the|"
    "sentenced|"
    "ruled that")
after_name_re = (
    "USMC|"
    "pleaded guilty|"
    "was tried|"
    "pled guilty|"
    "convicted|"
    "was found  guilty|"
    "acquitted|"
    "a military judge sentenced|"
    " military judge alone|"
    " acquittal"
)
date_re = ('Jan|'
           'Feb|'
           'Mar|'
           'Apr|'
           'Apr|'
           'May|'
           'Jun|'
           'Jul|'
           'Aug|'
           'Sep|'
           'Oct|'
           'Nov|'
           'Dec'
)

def clean_paragraph(paragraph):
    paragraph = unicode(paragraph, encoding='utf-8')
    chunks = paragraph.split('At a')
    if len(chunks) > 1:
        paragraph = 'At a' + chunks[1]
    nc_re = re.compile('North.+Carolina', re.DOTALL)
    sc_re = re.compile('South.+Carolina', re.DOTALL)
    cal_re = re.compile('\,.*?California', re.DOTALL)
    paragraph = re.sub(nc_re, 'North Carolina', paragraph)
    paragraph = re.sub(sc_re, 'South Carolina', paragraph)
    paragraph = re.sub(cal_re, ', California', paragraph)
    paragraph = (paragraph
                        .replace('Camp Pendleton,\nCamp Pendleton', 'Camp Pendleton, ')
                        .replace(',', ', ')
                        .replace('\n', ' ')
                        .replace('\n', ' ')
                        .replace('onboard','in')
                        .replace('pleaded  guilty','pleaded guilty')
                        .replace('at the','in the')
                        .replace('pled                                guilty','pled guilty')
                        .replace('pledguilty','pled guilty')
                        .replace('. 00', '')
                        .replace('.00','')
                        .replace('USNpled','USN pled')
                        .replace('2d','').replace('MLG', '')
                        .replace('Camp Pendleton ', 'Camp Pendleton, ')
                        .replace('MCB Camp ', 'MCB Camp,')
                        .replace('North Camp Lejeune Carolina', 'Camp Lejeune, North Carolina')
                        .replace('North TrngCmd Carolina', 'TrngCmd, North Carolina')
                        .replace('TrngCom California', 'TrngCom, California')
                        .replace('North MEF Carolina', 'MEF, North Carolina')
                        .replace('MCB Quantico', 'MCB, Quantico')
                        .replace('South Caroline', 'South Carolina')
                        .replace('MCB California', 'MCB, California')
                        .replace('MAW', '').replace('MarDiv', '')
                        .replace('1stMLG', '').replace('- MCBQ', '')
                        .replace('2dMarDiv', '').replace('10th', '')
                        .replace('1st', '').replace('3d', '')
                        .replace('MCB CamPen', '')
                        .replace(u"\xa02 \x0c", '')
                        .replace('On ', 'On ')
                        .replace('PS1Bobby', 'PS1 Bobby')
                        .replace('was found guilty', 'was tried')
                        .replace('was found not guilty', 'was tried'))
    paragraph= paragraph.split('***')[0]

    return paragraph

def get_date(text, output=None, date_re=date_re):
    if output == None:
        output = {}
    date_str = text.split(',')[0].replace('On', '').strip()
    day = re.search('\d{1,2}', date_str)
    if day:
        day = day.group()
    month = re.search(date_re, date_str)
    if month:
        month = month.group()
    date_str = date_str.split(month)[1]
    year = re.search('\d{2,4}', date_str)
    if year:
        year = year.group()
    output['Date'] = (month or '') + '-' + (year or '')
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


def get_name(
    paragraph,
    output=None,
    rank_re=rank_re,
    after_name_re=after_name_re
):
    if output == None:
        output = {}

    # Get Person
    chunks = re.split(after_name_re, paragraph)
    if len(chunks) >= 2:
        name = chunks[0]
        name = (name
                .replace(', III', '')
                .replace(' was', '')
                )
        chunks = re.split(rank_re, name)
        if len(chunks) >= 2:
            output['Name'] = (chunks[-1].replace(',', '').strip() or np.nan)
    if 'Name' not in output:
        print paragraph
    return output

def get_described_offense(row, output=None, after_name_re=after_name_re):
    if output == None:
        output = {}

    term = re.search(after_name_re, row)
    if term:
        chunks = re.split(term.group(), row)
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
    # get rid of leading junk
    if 'At a' in paragraph:
        paragraph = paragraph.split('At a')[1]
    rank = re.findall(rank_re, paragraph)
    rank = filter(lambda x: 'USN' not in x, map(lambda x: x.replace(',', '').strip(), rank))
    if len(rank) == 0:
        print ('no rank..')
        print (paragraph)
    else:
        output['Rank'] = rank[0]
    return output

def get_location(paragraph, output=None, rank_re=rank_re):
    if output == None:
        output = {}

    par_split = paragraph.split('At')
    if len(par_split) < 2:
        print paragraph
        return

    location_str = re.split(rank_re, par_split[1])[0]
    location_str = " ".join(location_str.strip().split())
    chunks = map(lambda x: x.strip(), location_str.strip().split(','))

    if len(chunks) >= 1:
        # city
        output['city'] = chunks[0]
        if 'Washington' in output['city']:
            output['city'] = 'Washington, D.C.'
        # state
        if len(chunks) >= 2:
            state = chunks[1].strip()
            if state in states:
                output['state'] = state
                output['country'] = 'U.S.A.'
            else:
                output['country'] = state
            # country
            if len(chunks) >= 3:
                country = chunks[2].replace('an', '').replace(' ', '').replace(' ', '')
                if (len(country) >= 2) and (output['country'] is not None) and (country != '  '):
                    output['country'] = country
    return output

def get_conviction(paragraph, output=None):
    if output==None:
        output = {}

    ## conviction
    if (('acquitted' in paragraph) 
        or ('not guilty' in paragraph)
        or ('innocent' in paragraph)
        or ('acquittal' in paragraph)
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