infos = {
    '16596200': {
        'name': 'Natalie Bennett',
        'id_str': '16596200',
        'tags': [
            '@natalieben',
            '@TheGreenParty',
            '#greens',
            '#VoteGreen',
            '#GreenManifesto',
            '#ForTheCommonGood',
            '#GreenSurge',
            '#VoteGreen2015',
            '#ChangeTheTune',
        ],
    },
    '103065157': {
        'name': 'David Cameron',
        'id_str': '103065157',
        'tags': [
            '@David_Cameron',
            '@conservatives',
            '#conservatives',
            '#CameronMustGo',
            '#TeamCameron',
            '#VoteConservative',
            '#ConservativeManifesto',
        ],
    },
    '15010349': {
        'name': 'Nick Clegg',
        'id_str': '15010349',
        'tags': [
            '@Nick_Clegg',
            '@LibDems',
            '#libdems',
            '#VoteLibDem',
            '#LibDemManifesto',
        ],
    },
    '19017675': {
        'name': 'Nigel Farage',
        'id_str': '19017675',
        'tags': [
            '@Nigel_Farage',
            '@UKIP',
            '#ukip',
            '#BelieveInBritain',
            '#VoteUKIP',
            '#UKIPManifesto'
        ],
    },
    '61781260': {
        'name': 'Ed Miliband',
        'id_str': '61781260',
        'tags': [
            '@Ed_Miliband',
            '@UKLabour',
            '#labour',
            '#VoteLabour',
            '#LabourManifesto',
        ],
    },
    '160952087': {
        'name': 'Nicola Sturgeon',
        'id_str': '160952087',
        'tags': [
            '@NicolaSturgeon',
            '@theSNP',
            '#snp',
            '#VoteSNP',
            '#SNPManifesto',
            '#SexySocialism',
            '#VoteSNPGetSexy',
        ],
    },
    '14450739': {
        'name': 'Leanne Wood',
        'id_str': '14450739',
        'tags': [
            '@LeanneWood',
            '@Plaid_Cymru',
            '#plaid15',
            '#VotePlaid',
            '#PlaidManifesto',
        ],
    },
}

# add urls using the first tag
for key, v in infos.items():
    infos[key]['url'] = 'https://twitter.com/{0}'.format(v['tags'][0][1:])


# from itertools import chain
# terms = list(chain(*[e['tags'] for e in infos.values()]))