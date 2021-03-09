import re
from itertools import tee, islice, zip_longest

def lookahead(iterable):
    """Pass through all values from the given iterable, augmented by the
    information if there are more values to come after the current one
    (True), or if it is the last value (False).
    """
    # Get an iterator and pull the first value.
    it = iter(iterable)
    last = next(it)
    # Run the iterator to exhaustion (starting from the second value).
    for val in it:
        # Report the *previous* value (more to come).
        yield last, True
        last = val
    # Report the last value.
    yield last, False

def get_next(some_iterable, window=2):
    items, nexts = tee(some_iterable, 2)
    nexts = islice(nexts, window, None)
    return zip_longest(items, nexts)

def joins_cleans_text(text):
    """cleans text before it stores to pandas df or sqlite db"""
    # joins list elements that are strings

    text = ''.join(text)
    # removes whitespace duplicates
    text = re.sub(' +', ' ', text)
    # removes whitespaces at the beginning and end
    text = text.strip()
    return text

def cleans_line(line):
    """Cleans line from unwanted characters too many spaces"""
    return re.sub(r'-\s+$', '', line + ' ')

def cleans_line_bb(line):
    """Cleans line from unwanted characters too many spaces"""
    return re.sub(r'-(?:\s+)?$',  ' ', line)

def cleans_line_by(line):
    """Cleans line from unwanted characters too many spaces"""
    line = line + ' '
    line = re.sub(r'-(?:\s+)?$',  '', line)
    return line

def cleans_line_hh(line):
    """Cleans line from unwanted characters too many spaces"""
    return re.sub(r'-(?:\s+)?$',  ' ', line)

def cleans_line_sn(line):
    """Cleans line from unwanted characters too many spaces"""
    return re.sub(r'-(?:\s+)?$',  '', line)

def cleans_executive_speaker_bw(new_speaker, mnstr, wp, date):
    if wp==12:
        if 'Wissenschaft, Forschung und Kunst' in new_speaker:
            new_speaker = 'von Trotha'
            mnstr = 'Wissenschaft, Forschung und Kunst'
        elif 'Kultus, Jugend und Sport' in new_speaker:
            new_speaker = 'Annette Schavan'
            mnstr = 'Kultus, Jugend und Sport'
        elif 'Umwelt und Verkehr' in new_speaker:
            new_speaker = 'Ulrich Müller'
            mnstr = 'Umwelt und Verkehr'
        elif 'ländlichen Raum' in new_speaker:
            new_speaker = 'Gerdi Staiblin'
            mnstr = 'Ländlicher Raum'
        elif 'Staatsministerium' in new_speaker:
            new_speaker = 'Dr. Christoph Palmer'
            mnstr = 'Staatsministerium'


    if wp==13:
        if 'Wissenschaft, Forschung und Kunst' in new_speaker:
            new_speaker = 'Dr. Peter Frankenberg'
            mnstr = 'Wissenschaft, Forschung und Kunst'
        elif 'Ländlichen Raum' in new_speaker:
            if date <= '2005-04-26':
                new_speaker = 'Willi Stächele'
            else:
                new_speaker = 'Pater Hauk'
            mnstr = 'Ernährung und Ländlicher Raum'
        elif 'Umwelt und Verkehr' in new_speaker:
            if date <= '2004-07-14':
                new_speaker = 'Ulrich Müller'
            else:
                new_speaker = 'Stefan Mappus'
            mnstr = 'Umwelt und Verkehr'
        elif 'Kultus, Jugend und Sport' in new_speaker:
            if date <= '2005-10-05':
                new_speaker = 'Annette Schavan'
            else:
                new_speaker = 'Helmut Rau'
            mnstr = 'Kultus, Jugend und Sport'
        elif 'europäische' in new_speaker:
            if date <= '2004-10-25':
                new_speaker = 'Dr. Christoph Palmer'
            else:
                new_speaker = 'Ulrich Müller'
            mnstr = 'Staatsministerium und für europäische Angelegenheiten'
        elif 'Bevollmächtigter' in new_speaker:
            if date <= '2005-04-26':
                new_speaker = 'Rudolf Köberle'
            else:
                new_speaker = 'Dr. Wolfgang Reinhart'
            mnstr = 'Bevollmächtigter des Landes beim Bund'
        elif 'Arbeit und Soziales' in new_speaker:
            if date < '2006-02-01':
                new_speaker = 'Andreas Renner'
            else:
                new_speaker = 'Dr. Monika Stolz'
            mnstr = 'Arbeit und Soziales'
    
    if wp==14:
        if 'Wissenschaft, Forschung und Kunst' in new_speaker:
            new_speaker = 'Dr. Peter Frankenberg'
            mnstr = 'Wissenschaft, Forschung und Kunst'
        elif 'Ländlichen Raum' in new_speaker:
            new_speaker = 'Peter Hauk'
            mnstr = 'Ernährung und Ländlicher Raum'
        elif 'Arbeit und Soziales' in new_speaker:
            new_speaker = 'Dr. Monika Stolz'
            mnstr = 'Arbeit und Soziales'
        elif 'Kultus, Jugend und Sport' in new_speaker:
            new_speaker = 'Helmut Rau'
            mnstr = 'Kultus, Jugend und Sport'
        elif 'Staatsministeriums' in new_speaker:
            if date <= '2008-06-03':
                new_speaker = 'Willi Stächele'
            else:
                new_speaker = 'Dr. Wolfgang Reinhart'
            mnstr = 'Staatsministerium und für europäische Angelegenheiten'
        elif 'Bevollmächtigter' in new_speaker:
            new_speaker = 'Dr. Wolfgang Reinhart'
            mnstr = 'Bevollmächtigter des Landes beim Bund'

                
    if wp==15:
        if 'Finanzen und Wirtschaft' in new_speaker:
            new_speaker = 'Nils Schmid'
        elif 'Staatsministerium' in new_speaker:
            new_speaker = 'Silke Krebs'
        elif 'Bundesrat, Europa und internationale' in new_speaker:
            new_speaker = 'Peter Friedrich'
        elif 'Umwelt, Klima und Energiewirtschaft' in new_speaker:
            new_speaker = 'Franz Untersteller'
        elif 'Kultus, Jugend und Sport' in new_speaker:
            if date<='2018-08-01':
                new_speaker = 'Gabriele Warminski-Leitheußer'
            else:
                new_speaker = 'Andreas Stoch'
        elif 'Ländlichen Raum und Verbraucherschutz' in new_speaker:
            new_speaker = 'Alexander Bonde'
        elif 'Wissenschaft, Forschung und Kunst' in new_speaker:
            new_speaker = 'Theresia Bauer'
        elif 'Verkehr und Infrastruktur' in new_speaker:
            new_speaker = 'Winfried Hermann'
        elif 'Arbeit und Sozialordnung, Familie' in new_speaker:
            new_speaker = 'Katrin Altpeter'
        elif 'Integration' in new_speaker:
            new_speaker = 'Bilkay Öney'
    elif wp==16:
        if 'Inneres, Digitalisierung und Migration' in new_speaker:
            new_speaker = 'Thomas Strobl'
        elif 'Finanzen' in new_speaker:
            new_speaker = 'Edith Sitzmann'
        elif 'Kultus, Jugend und Sport' in new_speaker:
            new_speaker = 'Susanne Eisenmann'
        elif 'Wissenschaft, Forschung und Kunst' in new_speaker:
            new_speaker = 'Theresia Bauer'
        elif 'Umwelt, Klima und Energiewirtschaft' in new_speaker:
            new_speaker = 'Franz Untersteller'
        elif 'Wirtschaft, Arbeit und Wohnungsbau' in new_speaker:
            new_speaker = 'Nicole Hoffmeister-Kraut'
        elif 'Soziales und Integration' in new_speaker:
            new_speaker = 'Manfred Lucha'
        elif 'Ländlichen Raum und Verbraucherschutz' in new_speaker:
            new_speaker = 'Peter Hauk'
        elif 'Justiz und für Europa' in new_speaker:
            new_speaker = 'Guido Wolf'
        elif 'Verkehr' in new_speaker:
            new_speaker = 'Winfried Hermann'
    return(new_speaker, mnstr)

def ministerium_secretary(new_speaker, mnstr, wp, date):
    if wp == 12:
        if 'Sieber' in new_speaker:
            mnstr = 'Wissenschaft, Forschung und Kunst'
        elif 'Mappus' in new_speaker: 
            mnstr = 'Umwelt und Verkehr'
        elif 'Köberle' in new_speaker:
            mnstr = 'Kultus, Jugend und Sport'
        elif 'Dr. Mehrländer' in new_speaker:
            mnstr = 'Wirtschaftsministerium'
        elif 'Johanna Lichy' in new_speaker:
            mnstr = 'Sozialministerium'
        elif 'Rückert' in new_speaker:
            mnstr = 'Finanzministerium'
        elif 'Stächele' in new_speaker:
            mnstr = 'Vertretung des Landes beim Bund'
        elif 'Dr. Beyreuther' in new_speaker:
            mnstr = 'Lebenswissenschaften'
            
    elif wp == 13:
        if 'Sieber' in new_speaker:
            mnstr = 'Wissenschaft, Forschung und Kunst'
        elif 'Dr. Beyreuther' in new_speaker:
            mnstr = 'Lebenswissenschaften'
        elif 'Dr. Mehrländer' in new_speaker:
            mnstr = 'Wirtschaftsministerium'
        elif 'Rau' in new_speaker:
            mnstr = 'Kultus, Jugend und Sport'
        elif 'Wacker' in new_speaker:
            mnstr = 'Kultus, Jugend und Sport'
        elif 'Dr. Monika Stolz' in new_speaker:
            mnstr = 'Kultus, Jugend und Sport'
        elif 'Rech' in new_speaker:
            mnstr = 'Innenministerium'
        elif 'Hillebrand' in new_speaker:
            mnstr = 'Umwelt und Verkehr'
        elif 'Mappus' in new_speaker:
            mnstr = 'Umwelt und Verkehr'            
        elif 'Friedlinde Gurr-Hirsch' in new_speaker:
            mnstr = 'Ernährung und Ländlicher Raum'
        elif 'Johanna Lichy' in new_speaker:
            mnstr = 'Sozialministerium'
        elif 'Rückert' in new_speaker:
            mnstr = 'Finanzministerium'            
        elif 'Dr. Reinhart' in new_speaker:
            mnstr = 'Finanzministerium'
        elif 'Köberle' in new_speaker:
            mnstr = 'Bevollmächtigter des Landes beim Bund'
            
    elif wp == 14:
        if 'Richard Drautz' in new_speaker:
            mnstr = 'Wirtschaftsministerium'
        elif 'Rudolf Köberle' in new_speaker:
            mnstr = 'Innenministerium'
        elif 'Dieter Hillebrand' in new_speaker:
            mnstr = 'Arbeit und Soziales'
        elif 'Wacker' in new_speaker:
            mnstr = 'Kultus, Jugend und Sport'
        elif 'Gundolf Fleischer' in new_speaker:
            mnstr = 'Finanzministerium'
        elif 'Dr. Dietrich Birk' in new_speaker:
            mnstr = 'Wissenschaft, Forschung und Kunst'
        elif 'Friedlinde Gurr-Hirsch' in new_speaker:
            mnstr = 'Ernährung und Ländlicher Raum'        
    return mnstr
            
def deal_with_green_party(line):
    line = (
        line.replace('Bündnis 90/Die Grünen', 'GRÜNE')
        .replace('Bündnis90/DieGrünen', 'GRÜNE')
        .replace('Bündnis90 /DieGrünen', 'GRÜNE')
        .replace('Bündnis90/ DieGrünen', 'GRÜNE')
        .replace('Bündnis90/Die Grünen', 'GRÜNE')
        .replace('Bündnis 90/DieGrünen', 'GRÜNE')
        .replace('Bündnis90/DieGrünen', 'GRÜNE')
        .replace('Bündnis 90/ Die Grünen', 'GRÜNE')
        .replace('Büdnis 90/Die Grünen', 'GRÜNE')
        .replace('Bündis 90/die Grünen', 'GRÜNE')
        .replace('Bündis 90/ die Grünen', 'GRÜNE')
        .replace('Bündis 90 / die Grünen', 'GRÜNE')
        .replace('Bündis90/ die Grünen', 'GRÜNE')
        .replace('Bündis90/ dieGrünen', 'GRÜNE')
        .replace('Bündis90/dieGrünen', 'GRÜNE')
        .replace('Bündis 90/dieGrünen', 'GRÜNE')
        .replace('Bündnis 90/Die','GRÜNE:')
        .replace('Bündnis 90/ Die','GRÜNE:')
        .replace('Bündnis 90 / Die','GRÜNE:')
        .replace('Bündnis 90/die','GRÜNE:')
        .replace('Bündnis 90/ die','GRÜNE:')
        .replace('Bündnis 90 / die','GRÜNE:')
        .replace('Bündnis90 / die','GRÜNE:')
        .replace('Bündnis 90/Die Grü-','GRÜNE:')
        .replace('nen:', '')
        )
    return line
        
    
def replace_unrecognized_chars(line):
    line = (
        line.replace('(cid:252)', 'ü')
        .replace('(cid:246)', 'ö')
        .replace('(cid:237)', 'i')
        .replace('(cid:231)', 'ç')
        .replace('(cid:228)', 'ä')
        .replace('(cid:224)', 'à')
        .replace('(cid:223)', 'ß')
        .replace('(cid:220)', 'Ü')
        .replace('(cid:216)', 'é')
        .replace('(cid:214)', 'Ö')
        .replace('(cid:190)', 'Ä')        
        .replace('(cid:160)', ' ')
        .replace('(cid:159)', '-')
        .replace('(cid:155)', 'è')
        .replace('(cid:150)', '-')
        .replace('(cid:147)', '"')      
        .replace('(cid:146)', "'")
        .replace('(cid:145)', "'")
        .replace('(cid:144)', "'")
        .replace('(cid:143)', "'")
        .replace('(cid:141)', "'")
        .replace('(cid:140)', "'")
        .replace('(cid:132)', '"')
        .replace('(cid:130)', "'")
        .replace('(cid:21)', "-")

        .replace('\xa0', ' ')
        .replace('\xad', '-')
        )
    return line
       

def cleans_speaker_hh(new_speaker):
    """
    removes words that are not part of speaker's name
    """
    new_speaker = (
        re.sub(' +', ' ', new_speaker)
        .replace('Zwischenfrage von ', '')
        .replace('Zwischenbemerkung von ', '')
        .replace(' (fortfahrend)', '')
        .replace(' (unterbrechend)', '')
        .replace('Treuenfels-Frowein', 'Treuenfels')
        .replace('Busch-', 'Buschhütter')
        .replace(' GRÜNE: Im', '')
        .replace('Stapel-', 'Stapelfeldt')
        .replace(' frakti-', '')
        .replace(' DIE', '')
        .replace('Finn Ole', 'Finn-Ole')
        .replace('Nebahat Güclü', 'Nebahat Güçlü')
        .split(':')[0]
        )

    new_speaker = re.sub(r'\s+DIE(?:\s+LIN-)?', '', new_speaker)
    return new_speaker


    

def ministerium_senators_hb(new_speaker, mnstr, wp, date):
    if wp == 15:
        if 'Adolf' in new_speaker:
            mnstr = 'Arbeit, Frauen, Gesundheit, Jugend und Soziales'
        elif 'Röpke' in new_speaker:
            mnstr = 'Arbeit, Frauen, Gesundheit, Jugend und Soziales'
        elif 'Perschau' in new_speaker: 
            mnstr = 'Finanzen'
        elif 'Hattig' in new_speaker:
            mnstr = 'Wirtschaft und Häfen'
        elif 'Dr. Schulte' in new_speaker:
            mnstr = 'Inneres, Kultur und Sport'
        elif 'Wischer' in new_speaker:
            mnstr = 'Bau und Umwelt'
        elif 'Dr. Scherf' in new_speaker:
            mnstr = 'Bürgermeister'
        elif 'Lemke' in new_speaker:
            mnstr = 'Bildung und Wissenschaft'
        elif 'Dr. Böse' in new_speaker:
            mnstr = 'Inneres, Kultur und Sport'
            
    elif wp == 16:
        if date < '2005-11-07':
            if 'Dr. Scherf' in new_speaker:
                mnstr = 'Bürgermeister'
            elif 'Röpke' in new_speaker:
                mnstr = 'Arbeit, Frauen, Gesundheit, Jugend und Soziales'
            elif 'Perschau' in new_speaker: 
                mnstr = 'Kultur'       
            elif 'Dr. Gloystein' in new_speaker:
                mnstr = 'Wirtschaft und Häfen'
            elif 'Kastendiek' in new_speaker:
                mnstr = 'Wirtschaft und Häfen' 
            elif 'Röwekamp' in new_speaker:
                mnstr = 'Inneres und Sport'
            elif 'Dr. Nußbaum' in new_speaker:
                mnstr = 'Finanzen'            
            elif 'Eckhoff' in new_speaker:
                mnstr = 'Bau, Umwelt und Verkehr'
            elif 'Lemke' in new_speaker:
                mnstr = 'Bildung und Wissenschaft'
        else: 
            if 'Böhrnsen' in new_speaker:
                mnstr = 'Bürgermeister'
            elif 'Röpke' in new_speaker:
                mnstr = 'Arbeit, Frauen, Gesundheit, Jugend und Soziales'
            elif 'Rosenköter' in new_speaker:
                mnstr = 'Arbeit, Frauen, Gesundheit, Jugend und Soziales'
            elif 'Rosenkötter' in new_speaker:
                mnstr = 'Arbeit, Frauen, Gesundheit, Jugend und Soziales'  
            elif 'Kastendiek' in new_speaker:
                mnstr = 'Wirtschaft und Häfen' 
            elif 'Röwekamp' in new_speaker:
                mnstr = 'Inneres, Kultur und Sport'
            elif 'Dr. Nussbaum' in new_speaker:
                mnstr = 'Finanzen'            
            elif 'Eckhoff' in new_speaker:
                mnstr = 'Bau, Umwelt und Verkehr'
            elif 'Neumeyer' in new_speaker:
                mnstr = 'Bau, Umwelt und Verkehr'
            elif 'Lemke' in new_speaker:
                mnstr = 'Bildung und Wissenschaft'

    elif wp == 17:
        if 'Böhrnsen' in new_speaker:
            mnstr = 'Bürgermeister'
        elif 'Röpke' in new_speaker:
            mnstr = 'Arbeit, Frauen, Gesundheit, Jugend und Soziales'
        elif 'Rosenkötter' in new_speaker:
            mnstr = 'Arbeit, Frauen, Gesundheit, Jugend und Soziales'  
        elif 'Nagel' in new_speaker:
            mnstr = 'Wirtschaft und Häfen' 
        elif 'Lemke' in new_speaker:
            mnstr = 'Inneres und Sport'
        elif 'Mäurer' in new_speaker:
            mnstr = 'Inneres und Sport'
        elif 'Linnert' in new_speaker:
            mnstr = 'Finanzen'            
        elif 'Dr. Loske' in new_speaker:
            mnstr = 'Bau, Umwelt, Verkehr und Europa'
        elif 'Jürgens-Pieper' in new_speaker:
            mnstr = 'Bildung und Wissenschaft'
            
    return mnstr


def ministerium_secretaries_hb(new_speaker, mnstr, wp, date):
    if 'Knigge' in new_speaker:
        mnstr = 'Arbeit, Frauen, Gesundheit, Jugend und Soziales'
    elif 'Hoppensack' in new_speaker:
        mnstr = 'Arbeit, Frauen, Gesundheit, Jugend und Soziales'
    elif 'Weihrauch' in new_speaker:
        mnstr = 'Arbeit, Frauen, Gesundheit, Jugend und Soziales'
    elif 'Schuster' in new_speaker:
        mnstr = 'Arbeit, Frauen, Gesundheit, Jugend und Soziales'
    elif 'Schulte-Sasse' in new_speaker:
        mnstr = 'Arbeit, Frauen, Gesundheit, Jugend und Soziales'
    elif 'Dr. Dannemann' in new_speaker: 
        mnstr = 'Finanzen'
    elif 'Metz' in new_speaker: 
        mnstr = 'Finanzen'
    elif 'Lühr' in new_speaker: 
        mnstr = 'Finanzen'
    elif 'Mützelburg' in new_speaker: 
        mnstr = 'Finanzen'
    elif 'Winther' in new_speaker:
        mnstr = 'Wirtschaft und Häfen'
    elif 'Dr. Färber' in new_speaker:
        mnstr = 'Wirtschaft und Häfen'
    elif 'Heseler' in new_speaker:
        mnstr = 'Wirtschaft und Häfen'
    elif 'Goehler' in new_speaker:
        mnstr = 'Inneres'
    elif 'Wischer' in new_speaker:
        mnstr = 'Bau und Umwelt'
    elif 'Logemann' in new_speaker:
        mnstr = 'Bau und Umwelt'
    elif 'Kramer' in new_speaker:
        mnstr = 'Bau, Umwelt und Verkehr'
    elif 'Dr. Scherf' in new_speaker:
        mnstr = 'Bürgermeister'
    elif 'Köttgen' in new_speaker:
        mnstr = 'Bildung und Wissenschaft'
    elif 'Othmer' in new_speaker:
        mnstr = 'Bildung und Wissenschaft'
    elif 'Wewer' in new_speaker:
        mnstr = 'Inneres und Sport'
    elif 'Buse' in new_speaker:
        mnstr = 'Inneres und Sport'
    elif 'Motschmann' in new_speaker:
        mnstr = 'Inneres, Kultur und Sport'
    elif 'Böse' in new_speaker:
        mnstr = 'Inneres, Kultur und Sport'
    elif 'vom Bruch' in new_speaker:
        mnstr = 'Inneres, Kultur und Sport'
    elif 'Mäurer' in new_speaker:
        mnstr = 'Justiz und Verfassung'
    elif 'Hoffmann' in new_speaker:
        mnstr = 'Senatskanzlei'
    elif 'Schulte' in new_speaker:
        mnstr = 'Senatskanzlei'
    elif 'Bettermann' in new_speaker:
        mnstr = 'Bevollmächtigter beim Bund'   
    elif 'Kießler' in new_speaker:
        mnstr = 'Bevollmächtigter beim Bund'  
    elif 'Golasowski' in new_speaker:
        mnstr = 'Bau, Umwelt, Verkehr und Europa'
    elif 'Emigholz' in new_speaker:
        mnstr = 'Kultur'
    elif 'Ehmigholz' in new_speaker:
        mnstr = 'Kultur'
    elif 'Stauch' in new_speaker:
        mnstr = 'Justiz'
            
    return mnstr


def ministerium_st(ministerium):
    if 'Arbeit' in ministerium:
        ministerium = 'Arbeit, Frauen, Gesundheit und Soziales'
    elif 'Raumordnung' in ministerium:
        ministerium = 'Raumordnung, Landwirtschaft und Umwelt'
    elif 'Wirtschaft' in ministerium:
        ministerium = 'Wirtschaft und Technologie'
    elif 'Wohnungswesen' in ministerium:
        ministerium = 'Wohnungswesen, Städtebau und Verkehr'
    elif 'Landwirtschaft' in ministerium:
        ministerium = 'Landwirtschaft und Umwelt'
    elif 'Landentwicklung' in ministerium:
        ministerium = 'Landentwicklung und Verkehr'
    elif 'Gesundheit' in ministerium:
        ministerium = 'Gesundheit und Soziales'        
            
    return ministerium
#mv
def adjust_names_mv(new_speaker):
    if new_speaker == 'R e i n h a r d t T h o m a s':
        new_speaker = 'Reinhardt Thomas'
    elif new_speaker == 'Vizepräsidentin Renate H o l z n a g e l':
        new_speaker = 'Vizepräsidentin Renate Holznagel'
    elif new_speaker == 'Vizepräsidentin Rente Holznagel':
        new_speaker = 'Vizepräsidentin Renate Holznagel'
    elif new_speaker == 'Präsidentin Sylvia B r e t s c h n e i d e r':
        new_speaker = 'Präsidentin Sylvia Bretschneider'
    elif new_speaker == 'J ö r g V i e r k a n t':
        new_speaker =  'Jörg Vierkant'
    elif new_speaker ==  'Lorenz Cafﬁ er':
        new_speaker =  'Lorenz Cafﬁer'
    elif new_speaker == 'Gabriele Mû‰Èan':
        new_speaker = 'Gabriele Mestan'
    
    return new_speaker


#sh
def clean_line_sh_14(line):
    line = line.replace("\'Oll", 'von')
    line = line.replace("\Oll", 'von')
    line = line.replace('Dmck', 'Druck')
    line = line.replace('dmck', 'druck')
    line = line.replace('Bildmtg', 'Bildung')
    line = line.replace('bildmtg', 'bildung')

    return line


def clean_speaker_sh_14(speaker):
    if 'Pr' in speaker:
        speaker = 'Präsident Heinz-Werner Arens'
    elif 'Asta' in speaker:
        speaker = "Vizepräsident Dr. Eberhard Dall' Asta"
    elif 'Köt' in speaker:
        speaker = 'Vizepräsidentin Dr. Gabriete Kötschau'
    elif 'Heinold' in speaker:
        speaker = 'Monika Heinold'
    elif 'Detlef' in speaker:
        speaker = 'Detlef Matthiessen'
    elif 'Puls' in speaker:
        speaker = 'Klaus-Peter Puls'
    elif 'Iaurus' in speaker:
        speaker = 'Heinz Maurus'
    elif 'Hielmcrone' in speaker:
        speaker = 'Dr. Ulf von Hielmcrone'
    elif 'Weber' in speaker:
        speaker = 'Jürgen Weber'
    elif 'Anke' in speaker:
        speaker = 'Anke Spoorendonk'
    elif 'Kayenburg' in speaker:
        speaker = 'Martin Kayenburg'
    elif 'Hentsche' in speaker:
        speaker = 'Karl-Martin Hentshcel'
    elif 'Hentscbel' in speaker:
        speaker = 'Karl-Martin Hentshcel'
    elif 'Friihlich' in speaker:
        speaker = 'Irene Fröhlich'
    elif speaker == 'Ute Erdsiek·Rave':
        speaker = 'Ute Erdsiek-Rave'
    elif 'Zahn' in speaker:
        speaker = 'Peter Zahn'
    elif 'Hunecke' in speaker:
        speaker = 'Gudrun Hunecke'
    elif 'Todsen-Reese' in speaker:
        speaker = 'Herlich Marie Todsen-Reese'
    elif 'Kubicki' in speaker:
        speaker = 'Wolfgang Kubicki'    
    return speaker



#bb
#ministers
def minister_handler_bb(speaker, wp):
    ministerium = ''
    if wp == 3:
        if 'Birthler' in speaker or 'Landwirtschaft' in speaker:
            speaker = 'Minister Birthler'
            ministerium = 'Landwirtschaft, Umweltschutz und Raumordnung'
        elif 'Fürniß' in speaker:
            speaker = 'Minister Dr. Fürniß'
            ministerium = 'Wirtschaft'
        elif 'Hackel' in speaker or 'Wissenschaft' in speaker:
            speaker = 'Minister Dr. Hackel'
            ministerium = 'Wissenschaft, Forschung und Kultur'
        elif 'Meyer' in speaker or 'Stadtentwicklung' in speaker:
            speaker = 'Minister Meyer'           
            ministerium = 'Stadtentwicklung, Wohnen und Verkehr'
        elif 'Reiche' in speaker or 'Bildung' in speaker:
            speaker = 'Minister Reiche'
            ministerium = 'Bildung, Jugend und Sport'
        elif 'Schelter' in speaker or 'Justiz' in speaker:
            speaker = 'Minister Prof. Dr. Schelter'
            ministerium = 'Justiz und für Europaangelegenheiten'
        elif 'Schönbohm' in speaker:
            speaker = 'Minister Schönbohm'
            ministerium = 'Innern'
        elif 'Simon' in speaker:
            speaker = 'Ministerin Dr. Simon'
            ministerium = 'Finanzen'
        elif 'Ziel' in speaker or 'Arbeit' in speaker:
            speaker = 'Minister Ziel'
            ministerium = 'Arbeit, Soziales, Gesundheit und Frauen'
        
    return(speaker, ministerium)


def statesec_handler_bb(speaker, wp):
    ministerium = ''
    if wp == 3:
        if 'somebody' in speaker or 'Landwirtschaft' in speaker:
            speaker = ''
            ministerium = 'Landwirtschaft, Umweltschutz und Raumordnung'
        elif 'somebody' in speaker:
            speaker = ''
            ministerium = 'Wirtschaft'
        elif 'somebody' in speaker or 'Wissenschaft' in speaker:
            speaker = ''
            ministerium = 'Wissenschaft, Forschung und Kultur'
        elif 'Mentrup' in speaker:
            speaker = 'Staatssekretär Dr. Mentrup'           
            ministerium = 'Finanzen'
        elif 'somebody' in speaker or 'Stadtentwicklung' in speaker:
            speaker = ''           
            ministerium = 'Stadtentwicklung, Wohnen und Verkehr'
        elif 'somebody' in speaker or 'Bildung' in speaker:
            speaker = ''
            ministerium = 'Bildung, Jugend und Sport'
        elif 'somebody' in speaker or 'Justiz' in speaker:
            speaker = ''
            ministerium = 'Justiz und für Europaangelegenheiten'
        elif 'somebody' in speaker:
            speaker = ''
            ministerium = 'Innern'
        elif 'somebody' in speaker:
            speaker = ''
            ministerium = 'Finanzen'
        elif 'somebody' in speaker or 'Arbeit' in speaker:
            speaker = ''
            ministerium = 'Arbeit, Soziales, Gesundheit und Frauen'
        
    return(speaker, ministerium)


#
def clean_speaker_bb(speaker, wp):
    if wp == 3:        
        if 'Schippe' in speaker:
            speaker = 'Schippel'
        elif 'Knnblich' in speaker:
            speaker = 'Präsident Dr. Knoblich'
        elif 'ohlich' in speaker:
            speaker = 'Präsident Dr. Knoblich'
        elif 'Kneblich' in speaker:
            speaker = 'Präsident Dr. Knoblich'
        elif 'aber' in speaker:
            speaker = 'Vizepräsident Habermann'
        elif 'Birthier' in speaker:
            speaker = 'Minister Birthler'
        elif 'Schuld' in speaker:
            speaker = 'Schuldt'
        elif 'Schön' in speaker:
            speaker = 'Minister Schönbohm'
        elif 'Scheiter' in speaker:
            speaker = 'Minister Prof. Dr. Schelter'
    return speaker


def clean_line_bb(line):
    if 'Nlinister' in line:
        line = line.replace('Nlinister', 'Minister')
        
    return line