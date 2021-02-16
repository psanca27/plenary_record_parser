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
import json
from datetime import datetime

#os.chdir('/Volumes/Datahouse/Users/Stipe/Documents/Studium/Master VWL/Masterarbeit/plenarprotokolle/code')
#os.chdir('/home/felix/privat/plenarprotokolle/code')
os.chdir('../code')
pd.options.display.max_rows = 500
pd.options.display.max_colwidth = 150


from lib import helper

locale.setlocale(locale.LC_TIME, "de_DE")

STATE = 'SH'

DATA_PATH = os.environ.get('DATA_PATH', '../data/' + STATE)


log = logging.getLogger(__name__)


ministers_wp18 = ['Torsten Albig', 'Robert Habeck', 'Monika Heinold', 'Anke Spoorendonk', 'Reinhard Meyer',
                  'Waltraud Wende', 'Andreas Breitner', 'Kristin Alheit']

ministers_wp19 = ['Daniel Günther', 'Sütterlin-Waack', 'Karin Prien', 'Hans-Joachim Grote', 
                  'Robert Habeck', 'Monika Heinold', 'Bernd Buchholz', 'Heiner Garg']

# regular expressions to capture speeches of one session
BEGIN_STRING = r'^(<poi_begin>)?Beginn(.*?)?:?\s+(.*?)?(?:Beginn\s+)?[0-9]{1,2}[.:][0-9]{1,2}'
END_STRING = r'^(<poi_begin>)?Schluss:\s+[0-9]{1,2}[.:][0-9]{1,2}'
CHAIR_STRING = r'^<poi_begin>\s?(Alterspräsident(?:in)?|Präsident(?:in)?|Vizepräsident(?:in)?)\s+(.+?):'
EXECUTIVE_STRING = r'^<poi_begin>(.*?)\,?<poi_end>\,?\s+(Ministerpräsident(?:in)?:|Minister(?:in)?\s+für\s+(\w+)|Justizminister(?:in)?:|Finanzminister(?:in)?:|Innenminister(?:in)?:)'
SPEAKER_STRING = r'^<poi_begin>(.+?)\s*?\[(AfD|CDU|SPD|F\.?D\.?P\.?|SSW|PIRATEN|BÜNDNIS\s+90\/DIE(?:\s+GRÜ(?:\-|NEN|fraktionslos))?)\]?(?:,\s+Berichterstatter(?:in)?)?'
OFFICIALS_STRING = r'^Staatssekretär(?:in)?\s+(?P<speaker1>.+?):|^(?P<speaker2>.+?)\,\s+Staatssekretär(?:in)?'

BEGIN_STRING_14 = r'^(<poi_begin>)?Beginn(.*?)?:?\s+(.*?)?(?:Beginn\s+)?[0-9]{1,2}[.:][0-9]{1,2}'
END_STRING_14 = r'^(<poi_begin>)?Schluss:\s+[0-9]{1,2}[.:][0-9]{1,2}'
CHAIR_STRING_14 = r'^(<poi_begin>)?(Alterspräsident(?:in)?|Präsident(?:in)?|Vizepräsident(?:in)?)\s+(.+?):'
EXECUTIVE_STRING_14 = r'^(?!<interjection_begin>|\(|\[|\_|\.|\"|nicht|und|[Aa]bgeordneten?)(<poi_begin>)?(.*?)\,\s+(Ministerpräsident(?:in)?:|Minister(?:in)?\s(\w+\s\w+)?|Justizminister(?:in)?:|Finanzminister(?:in)?:|Innenminister(?:in)?:)'
SPEAKER_STRING_14 = r'^(?!<interjection_begin>|\(|\[|\_|\.|\"|nicht|und|weil|von|Astmp|Neugebauer|er|schel|[Aa]bgeordneten?)(<poi_begin>)?(.+?)\s*?(\[\s?|l\s?|J\s?|1\s?)(AfD|C\s?D\s?U|S\s?P\s?D|F\.?D\.?P\.?|SSW|PIRATEN|B[Üü]NDNIS\s+90\/DIE(?:\s+GR[Üü](?:\-|NEN|fraktionslos))?)(\s?\]|\s?l|\s?J|\s?1)?(?!\))(?:,\s+Berichterstatter(?:in)?)?'
OFFICIALS_STRING_14= r'^Staatssekretär(?:in)?\s+(?P<speaker1>.+?):|^(?P<speaker2>.+?)\,\s+Staatssekretär(?:in)?'


#SPEECH_ENDS = re.compile("|".join([CHAIR_STRING, SPEAKER_STRING, EXECUTIVE_STRING, OFFICIALS_STRING]))
INTERJECTION_MARK = re.compile(r'^<interjection_begin>\(')
INTERJECTION_END = re.compile(r'.+\)<interjection_end>$')
HEADER_MARK = re.compile(r'^Schleswig\-Holsteinischer\s+Landtag\s+\([0-9]{1,2}\.\s+WP\)')
FOOTER_LASTPAGE_MARK = re.compile(r'Herausgegeben\s+vom\s+Präsidenten\s+des\s+Schleswig\-Holsteinischen\s+Landtags\s+\-\s+Stenografischer\s+Dienst')
#HEADER_SPEAKER_MARK = re.compile(r'\((?:Abg\.)|\(Alterspräsident(?:in)?|\(Präsident(?:in)?|\(Vizepräsident(?:in)?|\(Staatssekretär(?:in)?|\(Minister(?:in)?|\(Justizminister(?:in)?:|\(Finanzminister(?:in):|\(Innenminister(?:in)?|\(Ministerpräsident(?:in)?')
DATE_CAPTURE = re.compile(r'([0-9]{1,2}\.\s+.+\s+[0-9]{4})')
NO_INTERJECTION = re.compile(r'^\([A-Za-z]{1,4}\)')
ZWISCHENFRAGE_ANTWORT = re.compile(r'^-\s')

STATE = 'SH'
files = [os.path.join(dp, f) for dp, dn, fn in os.walk(os.path.expanduser(DATA_PATH)) for f in fn if f.endswith(".txt")]

#db = os.environ.get('DATABASE_URI', 'sqlite:///../data/data.sqlite')
#eng = dataset.connect(db)
#table = eng['de_landesparlamente_plpr']

ls_speeches = []
ls_interjection_length = []
ls_text_length = []
ls_interjection_length = []
log_sessions = []


for filename in files:

    # extracts wp, session no. and if possible date of plenary session
    wp, session = int(filename[11:13]), int( filename[14:17])
    date = None
    print(wp, session)
    
    if wp == 14:
        BEGIN_MARK = re.compile(BEGIN_STRING_14)
        END_MARK = re.compile(END_STRING_14)
        CHAIR_MARK = re.compile(CHAIR_STRING_14)
        SPEAKER_MARK = re.compile(SPEAKER_STRING_14)
        EXECUTIVE_MARK = re.compile(EXECUTIVE_STRING_14)
        OFFICIALS_MARK = re.compile(OFFICIALS_STRING_14)
        POI_ONE_LINER = re.compile(r'(.+?)?<poi_end>(?:.+)?')
        SPEECH_CONTINUTATION_STRING = re.compile(r'^(<poi_begin>)?\(.*?\)\s?(<poi_end>)?')
        
    else:
        # compilation of regular expressions
        # advantage combination of strings is possible
        BEGIN_MARK = re.compile(BEGIN_STRING)
        END_MARK = re.compile(END_STRING)
        CHAIR_MARK = re.compile(CHAIR_STRING)
        SPEAKER_MARK = re.compile(SPEAKER_STRING)
        EXECUTIVE_MARK = re.compile(EXECUTIVE_STRING)
        OFFICIALS_MARK = re.compile(OFFICIALS_STRING)
        POI_ONE_LINER = re.compile(r'(.+?)?<poi_end>(?:.+)?')
        SPEECH_CONTINUTATION_STRING = re.compile(r'^<poi_begin>\(.*?\)\s?<poi_end>')

    # table.delete(wp=wp, session=session, state=STATE)

    with open(filename, 'rb') as fh:
        text = fh.read().decode('utf-8')

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
        line = helper.clean_line_sh_14(line)

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
        if '<poi_begin>' in line or wp ==14:
            if CHAIR_MARK.match(line):
                s = CHAIR_MARK.match(line)
                if wp == 14:
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
                if wp == 14:
                    new_speaker = re.sub(' +', ' ', s.group(2))
                    ministerium = re.sub(' +', ' ', s.group(3)).replace(':', '').replace("<poi_end>", '').strip()
                    ministerium = re.sub('[If]\S+r', 'für', ministerium)
                else:
                    new_speaker = re.sub(' +', ' ', s.group(1))
                    ministerium = re.sub(' +', ' ', s.group(2)).replace(':', '').replace("<poi_end>", '').strip()
                role = 'executive'
                party = None
                president = False
                executive = True
                servant = False
                poi_prev = False
            elif OFFICIALS_MARK.match(line):
                s = OFFICIALS_MARK.match(line)
                new_speaker = re.sub(' +', ' ', s.group(1)) +  ' ' + re.sub(' +', ' ', s.group(2))
                party = None
                president = False
                executive = False
                servant = True
                role = 'state secretary'
                poi_prev = False
                ministerium = None
            elif SPEAKER_MARK.match(line):
                s = SPEAKER_MARK.match(line)
                if wp == 14:
                    new_speaker = re.sub(' +', ' ', s.group(2)).rstrip(')').rstrip('*')                    
                else:
                    new_speaker = re.sub(' +', ' ', s.group(1)).rstrip(')').rstrip('*')
                president = False
                executive = False
                servant = False
                if wp == 14:
                    party = s.group(4)
                    party = re.sub(' +', '', party)
                else:
                    party = s.group(2)
                role = 'mp'
                poi_prev = False
                ministerium = None
            else:
                if SPEECH_CONTINUTATION_STRING.match(line):
                    print(line)
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
                new_speaker = new_speaker.replace(':', '').replace('<poi_end>', '').replace('<poi_begin>', '').replace('·', '').strip()
                new_speaker = helper.clean_speaker_sh_14(new_speaker)
                if party:
                    party = party.replace('F.D.P.', 'FDP')
                    if 'BÜNDNIS' in party or 'BüNDNIS' in party:
                        party = 'GRÜNE'
                    party = party.replace(':', '')

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