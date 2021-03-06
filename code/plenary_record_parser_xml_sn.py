# coding: utf-8
import os
import locale
import re
import logging
# import requests
import dataset
from lxml import html
# from urlparse import urljoin
import pandas as pd
from datetime import datetime

log = logging.getLogger(__name__)

#os.chdir('/Volumes/Datahouse/Users/Stipe/Documents/Studium/Master VWL/Masterarbeit/plenarprotokolle/code')
# os.chdir('/home/felix/privat/plenarprotokolle/code')
os.chdir('../code')

from lib import helper

locale.setlocale(locale.LC_TIME, "de_DE")

STATE = 'SN'

DATA_PATH = os.environ.get('DATA_PATH', '../data/' + STATE)


# regular expressions to capture speeches of one session
BEGIN_STRING = r'^(?:<interjection_begin>)?\(Beginn(\s+der\s+Sitzung)?:?\s+[0-9]{1,2}[.:][0-9]{1,2}'
END_STRING = r'^(?:<interjection_begin>)?\((?:Schluss|Unterbrechung)\s+(?:des\s+ersten\s+Teils\s+)?der\s+Sitzung(?::?\s+)?[0-9]{1,2}[.:][0-9]{1,2}|^\(Schluss\s+.+?der\s+Sitzung:'
CHAIR_STRING = r'^<poi_begin>(Alterspräsident(?:in)?|Präsident(?:in)?|(?:[0-9]\.)?(?:\s+)?Vizepräsident(?:in)?)\s+(.+?):'
SPEAKER_STRING = r'^<poi_begin>(.+?)\,\s+(CDU|SPD|PDS|GRÜNE|Linksfraktion|(?:Die\s+)?Linke|DIE(?:\s+)?LINKE|FDP|NPD|AfD|fraktionslos):'
EXECUTIVE_STRING = r'^<poi_begin>(.+?),\s+(Staatsminister(?:in)?(\s+de[sr]\s+\w+|\s+für\s+\w+)?|Ministerpräsident(?:in)?).+$'
OFFICIALS_STRING = r'^<poi_begin>(.+?),\s+(Staatssekretär(?:in)?)'
COMISSIONER_STRING = r'^<poi_begin>(.+?),\s+(Sächsischer\s+(?:Ausländer|Datenschutz).*$)'
DATE_STRING = r'^[0-9]\.'

# compilation of regular expressions
# advantage combination of strings is possible
BEGIN_MARK = re.compile(BEGIN_STRING)
END_MARK = re.compile(END_STRING)
CHAIR_MARK = re.compile(CHAIR_STRING)
SPEAKER_MARK = re.compile(SPEAKER_STRING)
EXECUTIVE_MARK = re.compile(EXECUTIVE_STRING)
OFFICIALS_MARK = re.compile(OFFICIALS_STRING)
COMISSIONER_MARK = re.compile(COMISSIONER_STRING)
#SPEECH_ENDS = re.compile("|".join([CHAIR_STRING, SPEAKER_STRING, EXECUTIVE_STRING, OFFICIALS_STRING]))
INTERJECTION_MARK = re.compile(r'^<interjection_begin>\(')
INTERJECTION_END = re.compile(r'\)$')
HEADER_MARK = re.compile(r'^Sächsischer\s+Landtag|^[0-9]\.\s+Wahlperiode\s+–\s+[0-9]|^[0-9]{1,2}\.\s+.+[0-9]{4}\s+$')
#HEADER_SPEAKER_MARK = re.compile(r'\((?:Abg\.)|\(Alterspräsident(?:in)?|\(Präsident(?:in)?|\(Vizepräsident(?:in)?|\(Staatssekretär(?:in)?|\(Minister(?:in)?|\(Justizminister(?:in)?:|\(Finanzminister(?:in):|\(Innenminister(?:in)?|\(Ministerpräsident(?:in)?')
DATE_CAPTURE = re.compile(r'([0-9]{1,2}\.(?:\s+)?.+[0-9]{4})')
NO_INTERJECTION = re.compile(r'^.{1,6}[\)]')
DATE_CHECK = re.compile(DATE_STRING)
POI_ONE_LINER = re.compile(r'(.+?)?<poi_end>(?:.+)?')

files = sorted([os.path.join(dp, f) for dp, dn, fn in os.walk(os.path.expanduser(DATA_PATH)) for f in fn if f.endswith("xml.txt")])

#db = os.environ.get('DATABASE_URI', 'sqlite:///../data/data.sqlite')
#eng = dataset.connect(db)
#table = eng['de_landesparlamente_plpr']
#table.delete(state=STATE)

ls_speeches = []
ls_interjection_length = []
ls_text_length = []
ls_interjection_length = []
log_sessions = []


for filename in files:

    # extracts wp, session no. and if possible date of plenary session
    wp, session = int(filename[11:12]), int(filename[13:16])
    date = None

    print(wp, session)

    # if wp==18:
    #     abg = abg_wp18
    # elif wp==19:
    #     abg = abg_wp19

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
    topo = 0

    endend_with_interjection = False

    # contains list of dataframes, one df = one speech
    speeches = []

    for line, has_more in helper.lookahead(lines):
        if line and line==line.rstrip():
            line = line + ' '
        #    import pdb; pdb.set_trace()
        #if 'nochmals das Hauptmotiv' in line:
        #    import pdb; pdb.set_trace()
        if 'issue_begin' in line:
            line = line.replace('<issue_begin>', '').replace('<issue_end>', '')
            topo += 1
        #pdb.set_trace()
        # to avoid whitespace before interjections; like ' (Heiterkeit bei SPD)'
        if not line.isspace():
            line = line.lstrip()

        # grabs date, goes to next line until it is captured
        if not date_captured and DATE_CAPTURE.search(line):
            date = DATE_CAPTURE.search(line).group(1)
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
        if '<poi_begin>' in line:
            if CHAIR_MARK.match(line):
                s = CHAIR_MARK.match(line)
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
                new_speaker = re.sub(' +', ' ', s.group(1)).replace('*', '').strip()
                role = 'executive'
                party = None
                president = False
                executive = True
                servant = False
                poi_prev = False
                ministerium = re.sub(' +', ' ', s.group(2))
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
            elif COMISSIONER_MARK.match(line):
                s = COMISSIONER_MARK.match(line)
                new_speaker = re.sub(' +', ' ', s.group(1))
                party = None
                president = False
                executive = False
                servant = False
                role = 'commissioner'
                poi_prev = False
                ministerium = None
            elif SPEAKER_MARK.match(line):
                s = SPEAKER_MARK.match(line)
                new_speaker = re.sub(' +', ' ', s.group(1)).rstrip(')').rstrip('*')
                president = False
                executive = False
                servant = False
                party = s.group(2)
                role = 'mp'
                poi_prev = False
                ministerium = None
            else:
                if POI_ONE_LINER.match(line):
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
                new_speaker = re.sub('[0-9]\.\s*', '', new_speaker)
                new_speaker = new_speaker.replace('\x9b', 'è').replace(', CDU', '')
                new_speaker = new_speaker.replace(':', '').replace('<poi_end>', '').strip()
                if party:
                    party = party.replace('BÜNDNIS 90', 'GRÜNE')
                    party = party.replace('Linksfraktion', 'DIE LINKE')

        # saves speech, if new speaker is detected:
        if s is not None and current_speaker is not None:
            # ensures that new_speaker != current_speaker or matches end of session, document
            if (new_speaker!=current_speaker or END_MARK.search(line) or not has_more) and not interjection:
                
                # joins list elements that are strings
                text_len = len(text)
                #text = [i.replace('-', '').rstrip() if i.rstrip().endswith('-') else i + ' ' for i in text]
                text = ''.join(text)

                # removes whitespace duplicates
                text = re.sub(' +', ' ', text)
                # removes whitespaces at the beginning and end
                text = text.strip()
                # # 
                # text = re.sub('-(?=[a-z])', '', text)
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
                                       'issue': topo}

                    #table.insert(speech_dict)

                ls_text_length.append([text_len, wp, session, seq, sub, current_speaker, interjection_text])
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
                seq += 1
                # resets sub counter (for parts of one speech: speakers' parts and interjections)
                # for next speech
                sub = 0
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
                text_len = len(text)
                #text = [i.replace('-', '').rstrip() if i.rstrip().endswith('-') else i + ' ' for i in text]
                # joins list elements of strings
                text = ''.join(text)

                # removes whitespace duplicates
                text = re.sub(' +', ' ', text)
                # removes whitespaces at the beginning and end
                text = text.strip()
                # text = re.sub('-(?=[a-z])', '', text)
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
                                       'issue': topo}

                    #table.insert(speech_dict)

                    ls_text_length.append([text_len, wp, session, seq, sub, current_speaker, text])

            #
            sub += 1
            interjection = True
            interjection_text = []
    # special case: interjection
        if interjection:
            # either line ends with ')' and opening and closing brackets are equal or we had two empty lines in a row
            if not '<interjection_begin>' in line and line and not line.isspace():
                # to avoid an error, if interjection is at the beginning without anybod have started speaking
                # was only relevant for bavaria so far.
                if current_speaker is not None:
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
                                       'issue': topo}

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
                if line:
                    interjection_text.append(line)
                    interjection_length += 1
                continue
        if current_speaker is not None and not endend_with_interjection:
            if interjection_complete:
                interjection_complete = None
                text = []
                line = helper.cleans_line_sn(line)
                text.append(line)
                continue
            else:
                current_role = current_role.strip()

                line = helper.cleans_line_sn(line)
                text.append(line)
                continue

        if s is not None:
            if ":* " in line:
                line = line.split(':* ', 1)[-1]
            elif ":" in line:
                line = line.split(':', 1)[-1]
            line = helper.cleans_line_sn(line)
            text = []
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

    if speeches == []:
        print('no speeches detected in session %d wp %d' %(session,wp))
        session_descriptives = pd.DataFrame({'date': [date],
                                            'wp': [wp],
                                            'session': [session],
                                            'n_speeches': 0,
                                            'n_interruptions': 0})
        log_sessions.append(session_descriptives)
    else:
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
idx = [i for i, e in enumerate(ls_interjection_length) if e[0] > 8]

#text length
idx_txt = [i for i, e in enumerate(ls_text_length) if e[0] > 15]

pd_speeches.loc[:, ['wp', 'session', 'seq']].groupby(['wp', 'session']).max()