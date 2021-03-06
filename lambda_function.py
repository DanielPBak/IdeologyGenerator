import random
import csv
from urllib import request
import json
import io
import string
url = r"https://docs.google.com/spreadsheets/d/e/2PACX-1vR1woWAU1ClzNJBUElMoxLstPYmhq0JfdajTjBABMM3TqpLE5wevkO6SHeoz2a6NS0pDielm9Zx2bWB/pub?gid=0&single=true&output=csv"
from collections import defaultdict


class Generator:

    desc_adjs = []
    desc_adjs_weights = []
    desc_adjs_hasp_weights = []
    desc_adjs_unique_ids = []
    desc_nouns = []
    desc_nouns_weights = []
    desc_nouns_hasp_weights = []
    desc_nouns_unique_ids = []
    prefixes = []
    prefix_weights = []
    prefix_hasp_weights = []
    prefixes_unique_ids = []
    nouns = []
    nouns_weights = []
    nouns_hasp_weights = []
    nouns_unique_ids = []
    adverbs = []
    adverbs_weights = []
    adverbs_unique_ids = []
    endings = []
    endings_weights = []
    endings_unique_ids = []


    all_descs = []
    all_descs_weights = []
    all_descs_hasp_weights = []
    all_descs_unique_ids = []
    rows = []
    
    def __init__(self, html):
        self.html = html.decode('utf-8')
        self.trace = []
        self.debug_mode = False

    def get_words(self):

        with io.StringIO(self.html, newline='\r\n') as file:
            first = True
            csv_reader = csv.reader(file, delimiter=',')

            i = 0
            for row in csv_reader:
                self.rows.append(row)
                if first:
                    first = False
                    continue

                if row[0] == '':
                    continue
                words = row[0]


                words = words.split(',')
                words = [word.replace(';', ',').replace("'", "abcdefgh").title().replace("abcdefgh", "'") for word in words]

                type = row[1]
                unique_id = row[7]

                if row[2] == '':
                    weight = 1
                else:
                    weight = float(row[2])

                if row[3] == '':
                    hasp_weight = 1
                else:
                    hasp_weight = float(row[3])

                if type == 'DESCADJ':
                    self.desc_adjs.append(words)
                    self.desc_adjs_weights.append(weight)
                    self.desc_adjs_hasp_weights.append(hasp_weight)
                    self.desc_adjs_unique_ids.append(unique_id)
                elif type == 'DESCNOUN':
                    self.desc_nouns.append(words)
                    self.desc_nouns_weights.append(weight)
                    self.desc_nouns_hasp_weights.append(hasp_weight)
                    self.desc_nouns_unique_ids.append(unique_id)

                elif type == 'PREFIX':
                    self.prefixes.append(words)
                    self.prefix_weights.append(weight)
                    self.prefix_hasp_weights.append(hasp_weight)
                    self.prefixes_unique_ids.append(unique_id)

                elif type == 'ENDING':
                    self.endings.append(words)
                    self.endings_weights.append(weight)
                    self.endings_unique_ids.append(unique_id)

                elif type == 'NOUN':
                    self.nouns.append(words)
                    self.nouns_weights.append(weight)
                    self.nouns_hasp_weights.append(hasp_weight)
                    self.nouns_unique_ids.append(unique_id)

                elif type == 'ADVERB':
                    self.adverbs.append(words)
                    self.adverbs_weights.append(weight)
                    self.adverbs_unique_ids.append(unique_id)
                else:
                    import pdb
                    pdb.set_trace()
                    print(type)
                    raise NotImplementedError(type)


        self.all_descs = self.desc_adjs + self.desc_nouns
        self.all_descs_weights = self.desc_adjs_weights + self.desc_nouns_weights
        self.all_descs_hasp_weights = self.desc_adjs_hasp_weights + self.desc_nouns_hasp_weights
        self.all_descs_unique_ids = self.desc_adjs_unique_ids + self.desc_nouns_unique_ids

    def weighted_choice(self, weights):
        totals = []
        running_total = 0

        for w in weights:
            running_total += w
            totals.append(running_total)

        rnd = random.random() * running_total
        for i, total in enumerate(totals):
            if rnd < total:
                return i

    def get_ideologies(self, n_ideologies=100):

        ideologies = []
        traces = []

        for i in range(0, n_ideologies):
            self.trace = []
            ideologies.append(self.generate_ideology())
            traces.append(self.trace)
        return ideologies, traces

    def get_noun(self, p_adj=0.5, p_prefix=0.5, p_double=0.25, is_double=False):

        self.trace.append('Noun')
        choice = self.weighted_choice(self.nouns_weights)
        print('choice:')
        print(choice)
        noun = random.choice(self.nouns[choice])
        noun_uid = self.nouns_unique_ids[choice]
        print(noun_uid)

        if self.debug_mode:
            noun = 'noun'
        has_double = random.random() < p_double

        # If we have a double, lower the odds of prefixes and adjs.
        if has_double:
            p_prefix = p_prefix / 2
            p_adj = p_adj / 2

        has_prefix = random.random() < p_prefix
        has_adj = random.random() < p_adj
        new_p_prefix = min(p_prefix * p_prefix, p_prefix * .25)
        new_p_adj = min(p_adj * p_adj, p_adj * .25)

        if has_prefix:
            if is_double:
                prefix_p_hyphen = 0
            else:
                prefix_p_hyphen = .25
            prefix = self.get_prefix(new_p_prefix, p_hyphen=prefix_p_hyphen)
            noun = prefix + noun

        noun = noun

        if has_adj:
            noun = self.get_desc(new_p_adj, new_p_prefix) + ' ' + noun

        if has_double:
            noun = noun + '-' + self.get_noun(p_adj=0, p_prefix=0.25, p_double=0, is_double=True)

        return noun

    def get_desc(self, p_prefix=0.5, p_adj=0.33, p_double=0.4, p_adverb=0.2):
        new_p_prefix = min(p_prefix * p_prefix, p_prefix * .33)
        new_p_adj = min(p_adj * p_adj, p_adj * .33)

        self.trace.append('Desc')
        desc_idx = self.weighted_choice(self.all_descs_weights)

        adjs = self.all_descs[desc_idx]

        add_adverb = False
        if adjs in self.desc_adjs:
            is_desc_adj = True
        else:
            is_desc_adj = False

        if is_desc_adj and random.random() < p_adverb:
            add_adverb = True

        adj = random.choice(adjs)


        prefix_weight = self.all_descs_hasp_weights[desc_idx]

        adj = adj.replace('{Adj1}', '{adj1}')
        adj = adj.replace('{Adj2}', '{adj2}')
        adj = adj.replace('{Adj}', '{adj}')
        adj = adj.replace('{Noun}', '{noun}')

        if '{adj1}' in adj or '{adj2}' in adj:
            adj = adj.format(adj1=self.get_desc(p_adj=new_p_adj, p_prefix=new_p_prefix, p_double=0),
                             adj2=self.get_desc(p_adj=new_p_adj, p_prefix=new_p_prefix, p_double=0))

            return adj

        if self.debug_mode:
            adj = 'adj'

        if is_desc_adj and random.random() < p_double:
            adj = adj + '-' + self.get_desc(p_adj=0, p_double=0, p_prefix=0.1, p_adverb=0)

        if random.random() < p_prefix * prefix_weight:
            adj = self.get_prefix(p_prefix=new_p_prefix) + adj

        if add_adverb:
            adj = self.get_adverb() + ' ' + adj

        if random.random() < p_adj:
            adj = '{} {}'.format(self.get_desc(new_p_prefix, new_p_adj), adj)

        return adj

    def get_prefix(self, p_prefix=0.15, p_hyphen=0.5):
        self.trace.append('prefix')
        new_p_prefix = min(p_prefix * p_prefix, p_prefix * .33)

        prefix_idx = self.weighted_choice(self.prefix_weights)
        prefix_weight = self.prefix_hasp_weights[prefix_idx]

        pref = random.choice(self.prefixes[prefix_idx])

        if self.debug_mode:
            pref = 'pref'


        if pref.endswith('-'):
            p_next_hyphen = 1
        else:
            if random.random() < p_hyphen:
                pref = pref + '-'
                p_next_hyphen = p_hyphen
            else:
                p_next_hyphen = 1

        if random.random() < p_prefix * prefix_weight:
            pref = self.get_prefix(p_hyphen=p_next_hyphen, p_prefix=new_p_prefix) + pref

        return pref

    def get_ending(self):
        self.trace.append('ending')
        ending = random.choice(self.endings[self.weighted_choice(self.endings_weights)])

        ending = ending.replace('{Adj}', '{adj}')
        ending = ending.replace('{Noun}', '{noun}')

        desc = self.get_desc(p_double=0.2, p_prefix=0.2, p_adj=0.1)
        noun = self.get_noun(p_adj=0.1, p_prefix=0.2, p_double=0.2)

        ending = ending.format(adj=desc,
                               noun=noun)


        return ending

    def get_adverb(self):
        self.trace.append('adverb')
        # adverb can have adj?


        adverb = random.choice(self.adverbs[self.weighted_choice(self.adverbs_weights)])

        if self.debug_mode:
            adverb = 'adverb'
        return adverb


    def generate_ideology(self, p_ending=0.33, p_start=0.5):
        force_prefix = random.choice([False, True])
        with_ending = random.random() < p_ending


        if force_prefix:
            p_prefix = 1
            p_adj = .75
        else:
            p_prefix = .75
            p_adj = 1

        # if with_ending:
        #     p_prefix = p_prefix / 2
        #     p_adj = p_adj / 2

        noun = self.get_noun(p_prefix, p_adj)

        ideo = '{}'.format(noun)

        if with_ending:

            ending = self.get_ending()


            ending = ending.strip()

            if ending.startswith(','):
                ending = ending
            else:
                ending = ' ' + ending

            ideo = ideo + '{}'.format(ending)

            # characteristics = self.get_desc(p_double=.40)
            #
            # ideo = ideo + ' With {} Characteristics'.format(characteristics)

        return ideo

response = request.urlopen(url)
html = response.read()

gen = Generator(html)
gen.get_words()

def generate_one_ideo():

    ideologies, traces = gen.get_ideologies(1)

    return ideologies[0]
                

def lambda_handler(event, context):
    client_id = None
    try:
        if 'body' in event and event['body'] is not None:
            body = json.loads(event['body'])
            
            n_ideologies = body['n_ideo']
            client_id = body['g_client_id']
        else:
            n_ideologies = 5
        if random.random() < 0.01 and True:
            ideologies = ["I know who you are.", "I know what you're doing.", "I know where you live.", "Prepare.", "Prepare..", "Prepare...", "Happy Halloween!"]
        else:
            ideologies = gen.get_ideologies(n_ideologies)[0]
    except Exception as e:
        print(e)
        ideologies = [str(e)]

    print('## EVENT')
    print(event)
    print('## IDEOLOGIES')
    print(ideologies)
    if client_id is not None:
        print('## CLIENT_ID: ' + client_id)
    
    return {
        'statusCode': 200,
        'body': json.dumps(ideologies)
    }



if __name__ == '__main__':
    n_ideologies = 10000
    ideologies, traces = gen.get_ideologies(n_ideologies)

    counts = defaultdict(int)
    lens = []
    for idx, ideo in enumerate(ideologies):
        trace = traces[idx]

        counts[len(trace)] += 1

        if len(traces[idx]) != 0:
            print(ideo)
            # print(ideo)
            # print(traces[idx])
        lens.append(len(traces[idx]))
        # print(ideo)

    print(sum(lens) / len(lens))

    for k in counts:
        counts[k] = counts[k] / n_ideologies

    s = sorted(counts.items())

    for k in s:
        print(k)
