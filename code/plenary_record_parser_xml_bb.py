# coding: utf-8
import os
import locale
import re
import logging
#import requests
import dataset
from lxml import html
#from urlparse import urljoin
import pandas as pd
from datetime import datetime

#os.chdir('/Volumes/Datahouse/Users/Stipe/Documents/Studium/Master VWL/Masterarbeit/plenarprotokolle/code')
os.chdir('../code')
pd.options.display.max_rows = 500
pd.options.display.max_colwidth = 150

from lib import helper

log = logging.getLogger(__name__)

locale.setlocale(locale.LC_TIME, "de_DE")

DATA_PATH = os.environ.get('DATA_PATH', '../data/BB')

MINISTERS_WP5 = ['Platzeck', 'Markov', 'Speer', 'Woidke', 'Schöneburg', 'Christoffers', 'Görke',
                 'Baaske', 'Tack', 'Rupprecht', 'Münch', 'Kunst', 'Lieske', 'Vogelsänger', 'Holzschuher']

MINISTERS_WP6 = ['Woidke', 'Görke', 'Schröter', 'Markov', 'Ludwig', 'Golze', 'Karawanskij', 
                 'Gerber', 'Steinbach', 'Baaske', 'Ernst', 'Vogelsänger', 'Schneider', 'Kunst', 'Münch']

# regular expressions to capture speeches of one session
BEGIN_STRING = r'^(<poi_begin>)?s*?(?:Beginn\s+der\s+Sitzung|\(Fortsetzung\s+der\s+Sitzung|Beginn\s+der\s+[0-9]{1,2}\.\s+Sitzung)(?::\s+(?:[0-9]{1,2}[.:][0-9]{1,2}|[0-9]{1,2})\s+Uhr|\s+am\s+[0-9]{1,2}\.)'
END_STRING = r'^(<poi_begin>)?s*?\(?(?:Ende|Schluss)\s+(?:der\s+)?(?:[0-9]{1,2}\.\s+)?Sitzung(?:\s+am\s+[0-9]{1,2}\.\s+.+?(?:\s+[0-9]{4})?)?:?\s+(?:[0-9]{1,2}[.:][0-9]{1,2}|[0-9]{1,2})\s+Uhr'
CHAIR_STRING = r'^(<poi_begin>)?s*?(Alterspräsident(?:in)?|Präsident(?:in)?|Vizepräsident(?:in)?)\s+(.+):'
SPEAKER_STRING = r'^(<poi_begin>)?s*?(.+?)\s+(?:<poi_end>)?(?:<poi_begin>)?\((.+?)\)(?:<poi_end>)?:'
COMMITTEE_STRING = r'^(.+?)\s+\((Vorsitzender?\s+(?:des|der)\s+(Haupt|Untersuchungs|Petitions)?(?:[Aa]usschusses|Enquetekommission).+)'
EXECUTIVE_STRING_SHORT = r'^(<poi_begin>)?s*?(Ministerpräsident(?:in)?|Minister(?:in)?)\s+(.+?):'
EXECUTIVE_STRING_LONG = r'^(<poi_begin>)?s*?(Minister(?:in)?)\s+((?:für|der|des\s+Innern)\s+.+)'
EXECUTIVE_STOP_CHARACTERS_STRING = r'[,]'
OFFICIALS_STRING = r'^(<poi_begin>)?s*?(Staatssekretär(?:in)?)\s+(?:(.+?):|(im.+))'
LAKD_STRING = r'^(<poi_begin>)?s*?(.+?)\s+\(LAkD'
DATA_PROTECTION_STRING = r'^(<poi_begin>)?s*?(.+?)\s+\(Landesbeauftragter?\s+für'
LRH_STRING = r'^(<poi_begin>)?s*?(?:Herr\s+)?Weiser\s+\(Präsident\s+des\s+Landesrechnungshofes|Präsident\s+des\s+Landesrechnungshofe?s\s+Weiser'
SORBEN_STRING = r'^(<poi_begin>)?s*?(.+?)\s+\(Rat\s+für\s+sorbische/wendische Angelegenheiten'
SPEECH_CONTINUTATION_STRING = re.compile(r'^(<poi_begin>)?\(.*?\)\s?(<poi_end>)?')
POI_ONE_LINER = re.compile(r'(.+?)?<poi_end>(?:.+)?')



#Ziel (Vorsitzender des Ausschusses für Haushaltskontrolle): *

#Herr  Weiser  (Präsident  des  Landesrechnungshofes  Bran-
#denburg):
# compilation of regular expressions
# advantage combination of strings is possible
BEGIN_MARK = re.compile(BEGIN_STRING)
END_MARK = re.compile(END_STRING)
CHAIR_MARK = re.compile(CHAIR_STRING)
SPEAKER_MARK = re.compile(SPEAKER_STRING)
COMMITTEE_MARK = re.compile(COMMITTEE_STRING)
EXECUTIVE_MARK = re.compile(EXECUTIVE_STRING_SHORT)
EXECUTIVE_MARK_SHORT = re.compile(EXECUTIVE_STRING_SHORT)
EXECUTIVE_MARK_LONG = re.compile(EXECUTIVE_STRING_LONG)
EXECUTIVE_STOP_CHARACTERS = re.compile(EXECUTIVE_STOP_CHARACTERS_STRING)
OFFICIALS_MARK = re.compile(OFFICIALS_STRING)
LRH_MARK = re.compile(LRH_STRING)
LAKD_MARK = re.compile(LAKD_STRING)
DATA_PROTECTION_MARK = re.compile(DATA_PROTECTION_STRING)
SORBEN_MARK = re.compile(SORBEN_STRING)
#SPEECH_ENDS = re.compile("|".join([CHAIR_STRING, SPEAKER_STRING, EXECUTIVE_STRING, OFFICIALS_STRING]))
INTERJECTION_MARK = re.compile(r'^<interjection_begin>\(')
INTERJECTION_END = re.compile(r'.+\)<interjection_end>$')
NO_INTERJECTION = re.compile(r'\){2,10}')
HEADER_MARK = re.compile(r'^Landtag\s+Brandenburg\s+-\s+[0-9](?:\s+|\.)\s+Wahlperiode')
HEADER_SPEAKER_MARK = re.compile(r'\((?:Abg\.)|\(Alterspräsident(?:in)?|\(Präsident(?:in)?|\(Vizepräsident(?:in)?|\(Staatssekretär(?:in)?|\(Minister(?:in)?|\(Justizminister(?:in)?:|\(Finanzminister(?:in):|\(Innenminister(?:in)?|\(Ministerpräsident(?:in)?')
DATE_CAPTURE = re.compile(r'([0-9]{1,2}\.\s+(?:.+?)\s+[0-9]{4})')

STATE = 'BB'
ls_speeches = []
files = sorted([os.path.join(dp, f) for dp, dn, fn in os.walk(os.path.expanduser(DATA_PATH)) for f in fn if f.endswith(".txt")])

#db = os.environ.get('DATABASE_URI', 'sqlite:///../data/data.sqlite')
#eng = dataset.connect(db)
#table = eng['de_landesparlamente_plpr']

#def to clean  up names; might be useful. originally used for each identified speaker as e.g.:
#new_speaker = strips_line_down_2_speaker(new_speaker, wp, date).replace('Frisch', 'Fritsch')
def strips_line_down_2_speaker(new_speaker, wp, date):
    if wp==5:
        new_speaker = re.sub(r'(?:Prof\.\s+)?(?:Dr\.(?:\s+)?)?(?:-Ing\.\s+Dr\.\s+)?', '', new_speaker)
        new_speaker = re.sub(r'für\s+Wirtschaft\s+und Europaangelegenheiten(?:\s+)?(?:Chris-)?', 'Christoffers', new_speaker)
        new_speaker = re.sub(r'(?:im\s+Ministerium\s+)?(?:der|des)\s+(?:Finanzen|Innern|Justiz)\s+', '', new_speaker)
        new_speaker = re.sub(r'für\s+Arbeit,\s+Soziales,\s+Frauen\s+und\s+Familie.+', 'Baaske', new_speaker)
        new_speaker = re.sub(r'für\s+Umwelt,\s+Gesundheit\s+und\s+Verbraucher(?:schutz|-)(?:.+)?', 'Tack', new_speaker)
        if date<'2011-01-28':
            new_speaker = re.sub(r'für\s+Bildung,\s+Jugend\s+und\s+Sport.+', 'Rupprecht', new_speaker)
        else:
            new_speaker = re.sub(r'für\s+(?:Bildung,\s+Jugend|Jugend,\s+Bildung)\s+und\s+Sport.+', 'Münch', new_speaker)
        if date<'2010-02-25':
            new_speaker = re.sub(r'für\s+Infrastruktur\s+und\s+Landwirtschaft.+', 'Lieske', new_speaker)
        else:
            new_speaker = re.sub(r'für\s+Infrastruktur\s+und\s+Landwirtschaft.+', 'Vogelsänger', new_speaker)
        if date<'2011-02-23':
            new_speaker = re.sub(r'für\s+Wissenschaft,\s+Forschung\s+und\s+Kultur(?:.+)?', 'Münch', new_speaker)
        else:
            new_speaker = re.sub(r'für\s+Wissenschaft,\s+Forschung\s+und\s+Kultur(?:.+)?', 'Kunst', new_speaker)
        # staatssekretäre
        new_speaker = re.sub(r'im\s+Ministerium\s+für\s+Arbeits?,\s+Soziales,\s+Frau(?:en|-)', 'Schroeder', new_speaker)
        new_speaker = re.sub(r'im\s+Ministerium\s+für\s+Bildung,\s+Jugend\s+und', 'Jungkamp', new_speaker)
        new_speaker = re.sub(r'im\s+Ministerium\s+für\s+Infrastruktur\s+und(?:\s+Land-)?', 'Schneider', new_speaker)
        new_speaker = re.sub(r'im\s+Ministerium\s+für\s+Umwelt,\s+Gesundheit\s+und', 'Rühmkorf', new_speaker)
        new_speaker = re.sub(r'im\s+Ministerium\s+für\s+Wirtschaft\s+und(?:\s+Euro-)?', 'Heidemanns', new_speaker)
        new_speaker = re.sub(r'im\s+Ministerium\s+für\s+Wissenschaft,\s+For(?:-|schung)', 'Gorholt', new_speaker)

        new_speaker = re.sub(r'(?:Vogel-|Vogelsän-)', 'Vogelsänger', new_speaker)
        new_speaker = re.sub(r'Dellmann?', 'Dellmann', new_speaker)
        new_speaker = new_speaker.replace('Frau ', '').replace('Herr ', '').replace('*', '').replace(':', '').strip()
        if new_speaker=='Schulz':
            #import pdb; pdb.set_trace()
            new_speaker = 'Schulz-Höpfner'
    elif wp==6:
        new_speaker = re.sub(r'(?:Prof\.\s+)?(?:Dr\s?\.(?:\s+)?)?(?:-Ing\.\s+(?:Dr\.\s+)?)?', '', new_speaker)
        new_speaker = re.sub(r'für\s+Wirtschaft\s+und\s+Energie\s+Stein-?', 'Steinbach', new_speaker)
        new_speaker = re.sub(r'für\s+Wirtschaft\s+und\s+Energie\s+Gerber', 'Gerber', new_speaker)
        new_speaker = re.sub(r'für\s+Infrastruktur\s+und\s+Landesplanung\s+Schnei(?:-|der)\s?', 'Schneider', new_speaker)
        new_speaker = re.sub(r'des\s+Innern\s+und(?:\s+für)?\s+Komm?unales(?:\s+Schröter)?', 'Schröter', new_speaker) 
        new_speaker = re.sub(r'für\s+Inneres\s+und(?:\s+für)?\s+Komm?unales(?:\s+Schröter)?', 'Schröter', new_speaker) 
        new_speaker = re.sub(r'(?:im\s+Ministerium\s+)?(?:der)\s+(?:Finanzen)', '', new_speaker) # Görke
        new_speaker = re.sub(r'für\s+[lL]ändliche\s+Entwicklung,\s+Umwelt\s+und\s+Land(?:-|wirt-)', 'Vogelsänger', new_speaker)
        if date < '2017-09-28':
            new_speaker = re.sub(r'für\s+Bildung,\s+Jugend\s+und\s+Sport.+', 'Baaske', new_speaker)
        else:
            new_speaker = re.sub(r'für\s+Bildung,\s+Jugend\s+und\s+Sport.+', 'Ernst', new_speaker)
        if date < '2016-04-23':
            new_speaker = re.sub(r'der Justiz\s+und\s+für\s+Europa\s+und\s+Verbraucherschutz\s?', 'Markov', new_speaker)
        else:
            new_speaker = re.sub(r'der Justiz\s+und\s+für\s+Europa\s+und\s+Verbraucherschutz\s?', 'Ludwig', new_speaker)
        if date < '2016-03-09':
            new_speaker = re.sub(r'für\s+Wissenschaft,\s+Forschung\s+und\s+Kultur(?:\s+.+)?', 'Kunst', new_speaker)
        else:
            new_speaker = re.sub(r'für\s+Wissenschaft,\s+Forschung\s+und\s+Kultur(?:\s+.+)?', 'Münch', new_speaker)
        if date < '2018-08-28':
            new_speaker = re.sub(r'für\s+Arbeit,\s+Soziales,\s+Gesundheit,\s+Frauen.+', 'Golze', new_speaker)
        elif date >= '2018-08-28' and date < '2018-09-19':
            new_speaker = re.sub(r'für\s+Arbeit,\s+Soziales,\s+Gesundheit,\s+Frauen.+', 'Ludwig', new_speaker)
        else:
            new_speaker = re.sub(r'für\s+Arbeit,\s+Soziales,\s+Gesundheit,\s+Frauen.+', 'Karawanskij', new_speaker)
        # Staatssekretärinnen
        new_speaker = new_speaker.replace('im Ministerium der Justiz und für Europa', 'Pienky')
        new_speaker = new_speaker.replace('im Ministerium des Innern und für Kom-', 'Lange')
        new_speaker = new_speaker.replace('im Ministerium für Arbeit, Soziales, Ge-', 'Hartwig-Tiedt')
        new_speaker = new_speaker.replace('im Ministerium für Bildung, Jugend und' ,'Drescher')
        new_speaker = new_speaker.replace('im Ministerium für Infrastruktur und', 'Lange')
        new_speaker = new_speaker.replace('im Ministerium für Ländliche Entwick-', 'Schilde')
        new_speaker = new_speaker.replace('im Ministerium für Wissenschaft, For-', 'Gutheil')
        # mp 
        new_speaker = new_speaker.replace('Dombrowksi', 'Dombrowski').replace('Redman', 'Redmann')
        new_speaker = new_speaker.replace('Frau ', '').replace('Herr ', '').replace(':', '').replace('*', '').strip()
    return(new_speaker)

#def to clean up party names; might be useful. originally used for each identified abg. as e.g.:
#party = cleans_party_names(s.group(2))

def cleans_party_names(party):
    party = re.sub(r'BÜNDNIS\s+90/DIE\s+GRÜNEN|GRÜNE/B?90|B90/G(?:RÜNE|rüne|R0ÜNE)', 'GRÜNE', party)
    # wp6
    party = re.sub(r'BVB(?:/|\s)FREIE\s+WÄHLER\s+GRUPPE', 'BVB/FREIE WÄHLER', party)
    party = party.replace('FPD', 'FDP').replace('Die LINKE', 'DIE LINKE').replace('fraktionlos', 'fraktionslos')
    return(party)




ls_speeches = []
ls_interjection_length = []
ls_text_length = []
ls_interjection_length = []
log_sessions = []

# debug mode
debug = True

for filename in files[:6]:

    wp, session, date = int(filename[11:12]), int(filename[13:16]), None
    print(wp, session)

    with open(filename, 'rb') as fh:
        text = fh.read().decode('utf-8')

    if wp==5:
        MINISTERS=MINISTERS_WP5
    elif wp==6:
        MINISTERS=MINISTERS_WP6
    else:
        print('error: no minister list for this election period')

    print("Loading transcript: %s/%.3d, from %s" % (wp, session, filename))

    lines = text.split('\r\n')

    # trigger to skip lines until date is captured
    date_captured = False
    # trigger to skip lines until in_session mark is matched
    in_session = False

    # poi
    poi = False
    poi_prev = False
    issue = None
    concat_issues = False

    # variable captures contain new speaker if new speaker is detected
    new_speaker = None
    # contains current speaker, to use actual speaker and not speaker that interrupts speech
    current_speaker = None
    s = None

    # trigger to check whether a interjection is found
    interjection = False
    interjection_complete = None
    cnt_brackets_opening = 0
    cnt_brackets_closing = 0
    missing_closing = False

    # identation
    identation = False

    # trigger to find parts where zwischenfragen are continued without labelling current speaker
    zwischenfrage = False
    speaker_cnt = 0

    # dummy variables and categorial variables to characterize speaker
    president = False
    executive = False
    servant = False
    party = None
    role = None
    ministerium = None


    # counts to keep order
    seq = 0
    sub = 0

    endend_with_interjection = False

    # contains list of dataframes, one df = one speech
    speeches = []

    for line, has_more in helper.lookahead(lines):
        #if '<interjection_begin>Beifall im ganzen Hause)<interjection_end>' in line:
        #    import pdb; pdb.set_trace()

        #pdb.set_trace()
        # to avoid whitespace before interjections; like ' (Heiterkeit bei SPD)'
        line = line.lstrip()
        #line = helper.clean_line_sh_14(line)

        # grabs date, goes to next line until it is captured
        if not date_captured and DATE_CAPTURE.search(line):
            date = DATE_CAPTURE.search(line).group(0)
            try:
                date = datetime.strptime(date, '%d. %B %Y').strftime('%Y-%m-%d')
            except ValueError:
                date = datetime.strptime(date, '%d.%m.%Y').strftime('%Y-%m-%d')
            print('date captured ' +  date)
            date_captured = True
            continue
        elif not date_captured:
            continue
        if not in_session and BEGIN_MARK.search(line):
            #import pdb; pdb.set_trace()
            print('now in session')
            in_session = True
            continue
        elif not in_session:
            continue

        #ignores header lines and page numbers e.g. 'Landtag Mecklenburg-Vorpommer - 6. Wahlperiode [...]'
        if line.replace('<interjection_begin>', '').replace('<interjection_end>', '').strip().isdigit():
           continue
        if poi:
            if POI_ONE_LINER.match(line):
                if POI_ONE_LINER.match(line).group(1):
                    issue = issue + ' ' + POI_ONE_LINER.match(line).group(1)
                issue = issue.replace('<poi_begin>', '')
                issue = issue.replace('<poi_end>', '')
                poi = False
                # poi_prev = True
                line = line.replace('<poi_end>', '')
            else:
                issue = issue + ' ' + line

        # detects speaker, if no interjection is found:
        if '<poi_begin>' in line or wp ==3:
            if CHAIR_MARK.match(line):
                s = CHAIR_MARK.match(line)
                if wp == 3:
                    new_speaker = re.sub(' +', ' ', s.group(2)) +  ' ' + re.sub(' +', ' ', s.group(3))
                else:
                    new_speaker = re.sub(' +', ' ', s.group(1)) +  ' ' + re.sub(' +', ' ', s.group(2))
                president = True
                executive = False
                servant = False
                party = None
                role = 'chair'
                poi_prev = False
                ministerium = None
            elif EXECUTIVE_MARK.match(line):
                s = EXECUTIVE_MARK.match(line)
                if wp == 3:
                    new_speaker = re.sub(' +', ' ', s.group(2)) + ' ' + re.sub(' +', ' ', s.group(3))
                    ministerium = 'interstellar affairs'
                    #ministerium = re.sub(' +', ' ', s.group(3)).replace(':', '').replace("<poi_end>", '').strip()
                    #ministerium = re.sub('[If]\S+r', 'für', ministerium)
                else:
                    new_speaker = re.sub(' +', ' ', s.group(1))
                    #ministerium = re.sub(' +', ' ', s.group(3)).replace(':', '').replace("<poi_end>", '').strip()
                role = 'executive'
                party = None
                president = False
                executive = True
                servant = False
                poi_prev = False
            elif OFFICIALS_MARK.match(line):
                s = OFFICIALS_MARK.match(line)
                new_speaker = str(s)
                #new_speaker = re.sub(' +', ' ', s.group(1)) +  ' ' + re.sub(' +', ' ', s.group(2))
                party = None
                president = False
                executive = False
                servant = True
                role = 'state secretary'
                poi_prev = False
                ministerium = None
            elif SPEAKER_MARK.match(line):
                s = SPEAKER_MARK.match(line)
                if wp == 3:
                    new_speaker = re.sub(' +', ' ', s.group(2)).rstrip(')').rstrip('*')                    
                else:
                    new_speaker = re.sub(' +', ' ', s.group(1)).rstrip(')').rstrip('*')
                president = False
                executive = False
                servant = False
                if wp == 3:
                    party = s.group(3)
                    party = re.sub(' +', '', party)
                else:
                    party = s.group(2)
                role = 'mp'
                poi_prev = False
                ministerium = None
            else:
                if SPEECH_CONTINUTATION_STRING.match(line):
                    line = ''
                elif POI_ONE_LINER.match(line):
                    issue = POI_ONE_LINER.match(line).group(1)
                    issue = issue.replace('<poi_begin>', '')
                    issue = issue.replace('<poi_end>', '')
                    # poi_prev = True
                # elif poi_prev:
                 #   issue = issue + ' ' + line
                  #  poi = True
                else:
                    issue = line
                    poi = True

            if new_speaker:
                new_speaker = new_speaker.replace(':', '').replace('<poi_end>', '').replace('<poi_begin>', '').replace('·', '').replace('[CDU]', '').strip()
                new_speaker = helper.clean_speaker_bb(new_speaker, wp)

                if party:
                    party = party.replace('F.D.P.', 'FDP')
                    if 'BÜNDNIS' in party or 'BüNDNIS' in party:
                        party = 'GRÜNE'
                    party = party.replace(':', '')
                    
            if executive:
                new_speaker, ministerium = helper.minister_handler(new_speaker, wp)
                

        # saves speech, if new speaker is detected:
        if s is not None and current_speaker is not None:
            # ensures that new_speaker != current_speaker or matches end of session, document
            if new_speaker!=current_speaker or END_MARK.search(line) or not has_more:
                text_length = len(text)
                # joins list elements that are strings
                text = ''.join(text)
                # removes whitespace duplicates
                text = re.sub(' +', ' ', text)
                # removes whitespaces at the beginning and end
                text = text.strip()
                #text = re.sub('-(?=[a-z])', '', text)
                text = text.replace('<interjection_begin>', '').replace('<interjection_end>', '')
                text = text.replace('<poi_begin>', '').replace('<poi_end>', '')


                if text:
                    speech = pd.DataFrame({'speaker': [current_speaker], 
                                           'party': [current_party], 
                                           'speech': [text], 
                                           'seq': [seq],
                                           'sub': [sub],
                                           'executive': current_executive,
                                           'servant': current_servant,
                                           'wp': wp,
                                           'session': session,
                                           'president': current_president,
                                           'ministerium': [current_ministerium],
                                           'role': [current_role],
                                           'state': [STATE],
                                           'interjection': interjection,
                                           'date': [date],
                                           'issue': issue})
                    speeches.append(speech)
                    speech_dict = {'speaker': current_speaker,
                                       'party': current_party,
                                       'speech': text,
                                       'seq': seq,
                                       'sub': sub,
                                       'executive': current_executive,
                                       'servant': current_servant,
                                       'wp': wp,
                                       'session': session,
                                       'president': current_president,
                                       'ministerium': current_ministerium,
                                       'role': current_role,
                                       'state': STATE,
                                       'interjection': interjection,
                                       'identation': identation,
                                       'date': date,
                                       'issue': issue}

                    #table.insert(speech_dict)
                    ls_text_length.append([text_length, wp, session, seq, sub, current_speaker, text])
                # stops iterating over lines, if end of session is reached e.g. Schluss: 17:16 Uhr
                # to know order of speech within a given plenary session
                seq += 1
                # resets sub counter (for parts of one speech: speakers' parts and interjections)
                # for next speech
                sub = 0
                # resets current_speaker for next speech
                current_speaker = None
            elif (new_speaker!=current_speaker or END_MARK.search(line) or not has_more) and interjection:
                endend_with_interjection = True
                # to know order of speech within a given plenary session
                #seq += 1
                # resets sub counter (for parts of one speech: speakers' parts and interjections)
                # for next speech
                #sub = 0
            if END_MARK.search(line):
                in_session = False
                break
        # adds interjections to the data in such a way that order is maintained
        if INTERJECTION_MARK.match(line) and not interjection and not '<poi_begin>' in line:

        # skips lines that start with brackes for abbreviations at the beginning of line e.g. '(EU) Drucksache [...]'
            # variable contains the number of lines an interjection covers
            interjection_length = 0
            # saves speech of speaker until this very interjection
            if not interjection_complete and current_speaker is not None:
                text_length = len(text)
                # joins list elements of strings
                text = ''.join(text)
                # removes whitespace duplicates
                text = re.sub(' +', ' ', text)
                # removes whitespaces at the beginning and end
                text = text.strip()
                text = re.sub('-(?=[a-z])', '', text)
                text = text.replace('<interjection_begin>', '').replace('<interjection_end>', '')
                text = text.replace('<poi_begin>', '').replace('<poi_end>', '')
                if text:
                    speech = pd.DataFrame({'speaker': [current_speaker], 
                                           'party': [current_party], 
                                           'speech': [text], 
                                           'seq': [seq],
                                           'sub': [sub],
                                           'executive': current_executive,
                                           'servant': current_servant,
                                           'wp': wp,
                                           'session': session,
                                           'president': current_president,
                                           'ministerium': [current_ministerium],
                                           'role': [current_role],
                                           'state': [STATE],
                                           'interjection': interjection,
                                           'date': date,
                                           'issue': issue})
                    speeches.append(speech)
                    speech_dict = {'speaker': current_speaker,
                                       'party': current_party,
                                       'speech': text,
                                       'seq': seq,
                                       'sub': sub,
                                       'executive': current_executive,
                                       'servant': current_servant,
                                       'wp': wp,
                                       'session': session,
                                       'president': current_president,
                                       'ministerium': current_ministerium,
                                       'role': current_role,
                                       'state': STATE,
                                       'interjection': interjection,
                                       'identation': identation,
                                       'date': date,
                                       'issue': issue}

                    #table.insert(speech_dict)
                    ls_text_length.append([text_length, wp, session, seq, sub, current_speaker, text])

            #
            sub += 1
            interjection = True
            interjection_text = []
    # special case: interjection
        if interjection:
            # either line ends with ')' and opening and closing brackets are equal or we had two empty lines in a row
            if not '<interjection_begin>' in line and line and not line.isspace() or INTERJECTION_END.search(line):
                # to avoid an error, if interjection is at the beginning without anybod have started speaking
                # was only relevant for bavaria so far.
                if current_speaker is not None:
                    if INTERJECTION_END.search(line):
                        interjection_text.append(line)
                    # interjection_text.append(line)
                    interjection_text = [i.replace('-', '').rstrip() if i.rstrip().endswith('-') else i + ' ' for i in interjection_text]
                    interjection_text = ''.join(interjection_text)
                    # if 'Das sind aber zwei' in interjection_text:
                       # import pdb; pdb.set_trace()
                    # removes whitespace duplicates
                    interjection_text = re.sub(' +', ' ', interjection_text)
                    # removes whitespaces at the beginning and end
                    interjection_text = interjection_text.strip()
                    interjection_text = re.sub('-(?=[a-z])', '', interjection_text)
                    interjection_text = interjection_text.replace('<interjection_begin>', '').replace('<interjection_end>', '')
                    interjection_text = interjection_text.replace('<poi_begin>', '').replace('<poi_end>', '')
                    if interjection_text:
                        speech = pd.DataFrame({'speaker': [current_speaker], 
                                           'party': [current_party], 
                                           'speech': [interjection_text], 
                                           'seq': [seq],
                                           'sub': [sub],
                                           'executive': current_executive,
                                           'servant': current_servant,
                                           'wp': wp,
                                           'session': session,
                                           'president': current_president,
                                           'ministerium': [current_ministerium],
                                           'role': [current_role],
                                           'state': [STATE],
                                           'interjection': [interjection],
                                           'date': date,
                                           'issue': issue})
                        speeches.append(speech)
                        speech_dict = {'speaker': current_speaker,
                                       'party': current_party,
                                       'speech': interjection_text,
                                       'seq': seq,
                                       'sub': sub,
                                       'executive': current_executive,
                                       'servant': current_servant,
                                       'wp': wp,
                                       'session': session,
                                       'president': current_president,
                                       'ministerium': current_ministerium,
                                       'role': current_role,
                                       'state': STATE,
                                       'interjection': interjection,
                                       'identation': identation,
                                       'date': date,
                                       'issue': issue}

                        #table.insert(speech_dict)
                    sub += 1
                    interjection_length += 1
                    ls_interjection_length.append([interjection_length, wp, session, seq, sub, current_speaker, interjection_text])
                interjection = False
                interjection_complete = True
                interjection_skip = False
                cnt_brackets_opening = 0
                cnt_brackets_closing = 0
            else:
                line = line.replace('<interjection_begin>', '').replace('<interjection_end>', '')
                if line and not line.isspace():
                    interjection_text.append(line)
                    interjection_length += 1
                continue
        if current_speaker is not None and not endend_with_interjection:
            if interjection_complete:
                interjection_complete = None
                text = []
                if line and not line.isspace() and not INTERJECTION_END.search(line):
                    line = helper.cleans_line(line)
                    text.append(line)
                continue
            else:
                current_role = current_role.strip()

                line = helper.cleans_line(line)
                if line and not line.isspace():
                    text.append(line)
                continue

        if s is not None:
            if ":* " in line:
                line = line.split(':* ', 1)[-1]
            elif ":" in line:
                line = line.split(':', 1)[-1]
            line = helper.cleans_line(line)
            text = []
            if line and not line.isspace():
                text.append(line)
            current_speaker = new_speaker
            current_party = party
            current_president = president
            current_executive = executive
            current_servant = servant
            current_role = role
            current_ministerium = ministerium
            endend_with_interjection = False
            interjection_complete = None
        if not has_more and in_session:
            print(str(wp) + ' ' + str(session) + ' : no match for end mark -> error')

    pd_session_speeches = pd.concat(speeches)
    print(str(pd_session_speeches.seq.max()) + ' speeches detected and ' + str(pd_session_speeches.loc[pd_session_speeches.interjection==True].interjection.count()) + ' interjections')
    ls_speeches.append(pd_session_speeches)
    
    session_descriptives = pd.DataFrame({'date': [date],
                                    'wp': [wp],
                                    'session': [session],
                                    'n_speeches': [int(pd_session_speeches.seq.max())],
                                    'n_interruptions': [int(pd_session_speeches.loc[pd_session_speeches.interjection==True].interjection.count())]})
    log_sessions.append(session_descriptives)

pd_speeches = pd.concat(ls_speeches).reset_index()
pd_log_sessions = pd.concat(log_sessions).reset_index()

#pd_speeches.to_csv(os.path.join(DATA_PATH, STATE + '_test.csv'))

# checks
# interjection length
idx = [i for i, e in enumerate(ls_interjection_length) if e[0] > 10]

#text length
idx_txt = [i for i, e in enumerate(ls_text_length) if e[0] > 250]

pd_speeches.loc[:, ['wp', 'session', 'seq']].groupby(['wp', 'session']).max()