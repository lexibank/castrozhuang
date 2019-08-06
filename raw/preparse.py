from lingpy import *
from pyclts.transcriptionsystem import TranscriptionSystem
from segments.tokenizer import Tokenizer

from collections import defaultdict

bipa = TranscriptionSystem('bipa')

data = csv2list('data-b.tsv', strip_lines=False)

def clean(form):
    form = form.replace(' ː', 'ː')
    form = form.replace(' ː', 'ː')
    form = form.replace('i̪ ', 'i̪')
    form = form.replace('ɘ̪ ', 'ɘ̪')
    form = form.replace('ʌ̪ ', 'ʌ̪')

    st = [
            ('ɪ̪ ', 'ɪ̪'),
            ('ɛ̪ '[1:], 'ɛ̪ '[1:-1]),
            ('²̙ ¹'[1:-1], ''),
            ('****', ''),
            ('ɔ̪'[1], ''),
            ('??', ''),
            ('²̘+³¹','²¹³'),
            ]
    for s, t in st:
        if s:
            form = form.replace(s, t)


    return form.replace(' ', '+')

tk = Tokenizer('../etc/orthography.tsv')

D = {}
idx = 1
header = []
errors = defaultdict(list)
dips = defaultdict(int)
for line in data:
    if line[0].strip() == '汉义':
        header = line
    else:
        print(line[0])
        lines = line[0].split(' ')
        number, concept = lines[0], ' '.join(lines[1:])
        for doculect, form in zip(header[1:], line[1:]):
            if form.strip():
                for f in clean(form).split(','):
                    if f.replace('-', '').strip():
                        tokens = tk('^'+f+'$', column='IPA').split()
                        classes = tokens2class(tokens, 'cv')
                        prec = ''
                        diphs = []
                        for t, c in zip(tokens, classes):
                            if c == 'V' and not prec:
                                diphs += [t]
                                prec = 'V'
                            elif c == 'V' and prec == 'V':
                                diphs[-1] += t
                            else:
                                prec = ''
                            for dip in diphs:
                                if len(dip) > 1:
                                    dips[dip] += 1
                        for token in tokens:
                            if bipa[token].type == 'unknownsound':
                                errors[token] += [f]

                        D[idx] = [doculect, concept, number, form,
                                f.strip(), tokens]
                        idx += 1
D[0] = ['doculect', 'concept', 'gloss_id', 'value', 'form', 'tokens']
wl = Wordlist(D)
wl.output('tsv', filename='../raw/wordlist', ignore='all', prettify=False)

for d in dips:
    print(d+'\t'+d+'\t'+str(dips[d]))
