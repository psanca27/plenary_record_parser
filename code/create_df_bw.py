import pandas as pd

no_interrupt = pd_speeches['interjection'] == 0
df = pd_speeches[no_interrupt]
df = df[['date', 'executive', 'ministerium', 'party', 'president', 'seq', 'servant', 'session', 'speaker', 'speech', 'state', 'sub', 'wp', 'role']]
df['deputy'] = df['role']=='mp'
df.rename(columns={'executive': 'minister'}, inplace=True)
df.loc[df['role'] == 'secretary','minister'] = True
df['speech'] = df[['date', 'seq', 'speaker', 'speech']].groupby(['date', 'seq', 'speaker'])['speech'].transform(lambda x: ' '.join(x))
df = df.groupby(['date', 'speaker', 'seq'], as_index=False).first()
df = df.set_index(['date', 'seq']).sort_index().reset_index()
df['speaker'] = df['speaker'].apply(lambda x: x.replace(': ', '').replace('<poi_end>', '').strip())