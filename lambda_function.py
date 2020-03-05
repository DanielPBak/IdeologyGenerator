import random
import csv
from urllib import request
import json
import io
url = r"https://docs.google.com/spreadsheets/d/e/2PACX-1vR1woWAU1ClzNJBUElMoxLstPYmhq0JfdajTjBABMM3TqpLE5wevkO6SHeoz2a6NS0pDielm9Zx2bWB/pub?gid=0&single=true&output=csv"


class Generator:

    desc_adjs = []
    desc_adjs_weights = []
    desc_adjs_hasp_weights = []
    desc_nouns = []
    desc_nouns_weights = []
    desc_nouns_hasp_weights = []
    prefixes = []
    prefix_weights = []
    prefix_hasp_weights = []
    nouns = []
    nouns_weights = []
    nouns_hasp_weights = []
    adverbs = []
    adverbs_weights = []
    endings = []
    endings_weights = []


    all_descs = []
    all_descs_weights = []
    all_descs_hasp_weights = []
    rows = []
    
    def __init__(self, html):
        self.html = html.decode('utf-8')

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


                i += 1
                print(i)

                words = words.split(',')
                words = [word.capitalize().replace(';', ',').title() for word in words]

                type = row[1]

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
                elif type == 'DESCNOUN':
                    self.desc_nouns.append(words)
                    self.desc_nouns_weights.append(weight)
                    self.desc_nouns_hasp_weights.append(hasp_weight)
                elif type == 'PREFIX':
                    self.prefixes.append(words)
                    self.prefix_weights.append(weight)
                    self.prefix_hasp_weights.append(hasp_weight)
                elif type == 'ENDING':
                    self.endings.append(words)
                    self.endings_weights.append(weight)
                elif type == 'NOUN':
                    self.nouns.append(words)
                    self.nouns_weights.append(weight)
                    self.nouns_hasp_weights.append(hasp_weight)
                elif type == 'ADVERB':
                    self.adverbs.append(words)
                    self.adverbs_weights.append(weight)
                else:
                    import pdb
                    pdb.set_trace()
                    print(type)
                    raise NotImplementedError(type)


        self.all_descs = self.desc_adjs + self.desc_nouns
        self.all_descs_weights = self.desc_adjs_weights + self.desc_nouns_weights
        self.all_descs_hasp_weights = self.desc_adjs_hasp_weights + self.desc_nouns_hasp_weights

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

        for i in range(0, n_ideologies):
            ideologies.append(self.generate_ideology())
        return ideologies

    def get_noun(self, p_adj=0.5, p_prefix=0.5, p_double=0.25):

        noun = random.choice(self.nouns[self.weighted_choice(self.nouns_weights)])

        if random.random() < p_prefix:
            new_p_prefix = min(p_prefix * p_prefix, p_prefix * .33)
            prefix = self.get_prefix(new_p_prefix)
            noun = prefix + noun

        noun = noun

        if random.random() < p_adj:
            new_p_adj = min(p_adj * p_adj, p_adj * .33)
            noun = self.get_desc(new_p_adj) + ' ' + noun

        if random.random() < p_double:
            noun = noun + '-' + self.get_noun(p_adj=0, p_prefix=0.25, p_double=0)

        return noun

    def get_desc(self, p_prefix=0.5, p_adj=0.33, p_double=0.4, p_adverb=0.2):

        desc_idx = self.weighted_choice(self.all_descs_weights)

        adjs = self.all_descs[desc_idx]

        add_adverb = False

        if adjs in self.desc_adjs and random.random() < p_adverb:
            add_adverb = True

        adj = random.choice(adjs)


        prefix_weight = self.all_descs_hasp_weights[desc_idx]

        adj = adj.replace('{Adj1}', '{adj1}')
        adj = adj.replace('{Adj2}', '{adj2}')
        adj = adj.replace('{Adj}', '{adj}')
        adj = adj.replace('{Noun}', '{noun}')

        if '{adj1}' in adj or '{adj2}' in adj:
            adj = adj.format(adj1=self.get_desc(p_adj=p_adj * p_adj * p_adj, p_double=0),
                             adj2=self.get_desc(p_adj=p_adj * p_adj * p_adj, p_double=0))

            return adj



        if random.random() < p_double:
            adj = adj + '-' + self.get_desc(p_adj=0, p_double=0, p_prefix=0.1, p_adverb=0)

        if random.random() < p_prefix * prefix_weight:
            adj = self.get_prefix() + adj

        if add_adverb:
            adj = self.get_adverb() + ' ' + adj

        if random.random() < p_adj:
            adj = '{} {}'.format(self.get_desc(p_prefix * .8, p_adj * p_adj * p_adj), adj)
        return adj

    def get_prefix(self, p_prefix=0.15, p_hyphen=0.5):
        prefix_idx = self.weighted_choice(self.prefix_weights)
        prefix_weight = self.prefix_hasp_weights[prefix_idx]

        pref = random.choice(self.prefixes[prefix_idx])

        if pref.endswith('-'):
            p_next_hyphen = 1
        else:
            if random.random() < p_hyphen:
                pref = pref + '-'
                p_next_hyphen = p_hyphen
            else:
                p_next_hyphen = 1

        if random.random() < p_prefix * prefix_weight:
            pref = self.get_prefix(p_hyphen=p_next_hyphen, p_prefix=p_prefix*.6) + pref

        return pref

    def get_ending(self):

        ending = random.choice(self.endings[self.weighted_choice(self.endings_weights)])

        ending = ending.replace('{Adj}', '{adj}')
        ending = ending.replace('{Noun}', '{noun}')
        ending = ending.format(adj=self.get_desc(p_double=0.5),
                               noun=self.get_noun(p_adj=0.1))


        return ending

    def get_adverb(self):
        # adverb can have adj?

        adverb = random.choice(self.adverbs[self.weighted_choice(self.adverbs_weights)])

        return adverb


    def generate_ideology(self, p_ending=0.33, p_start=0.5):
        force_prefix = random.choice([False, True])

        if force_prefix:
            p_prefix = 1
            p_adj = .75
        else:
            p_prefix = .75
            p_adj = 1
        ideo = '{}'.format(self.get_noun(p_prefix=p_prefix, p_adj=p_adj))

        with_ending = random.random() < p_ending

        if with_ending:

            ending = self.get_ending()

            ending = ending.strip()

            if ending.startswith(','):
                ending = ending
            else:
                ending = ' ' + ending

            ideo = ideo + '{}'.format(ending).title()

            # characteristics = self.get_desc(p_double=.40)
            #
            # ideo = ideo + ' With {} Characteristics'.format(characteristics)

        return ideo

response = request.urlopen(url)
html = response.read()

gen = Generator(html)
gen.get_words()

def generate_one_ideo():

    ideologies = gen.get_ideologies(1)

    return ideologies[0]
                

def lambda_handler(event, context):
    
    try:
        ideology = generate_one_ideo()
    except Exception as e:
        ideology = str(e)
        raise e
    return {
        'statusCode': 200,
        'body': json.dumps(ideology)
    }
