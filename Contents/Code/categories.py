# Reddit Video Categories
# with subreddit discovery the categories are no longer used
# the only thin being used now is the domain_list which could
# obviously just be included in __init__.py instead.

from utilities import list_to_string,  create_list

gaming = ['games',  'gaming',  'tf2',  'starcraft',
          'leagueoflegends', 'minecraft', 'guildwars2',
          'masseffect', 'runescape', 'blackops2',
          'indiegaming', 'wow', 'planetside', 'dayz', 'skyrim']
music = ['blues', 'bluegrass', 'jazz', 'music',
         'electronicmusic', 'ska', 'classicalmusic',
         'listentothis', 'metal', 'hiphopheads']
technology = ['linux', 'technology']
sports = ['sports', 'soccer', 'formula1', 'nba']
educational = ['diy', 'howto', 'learnuselesstalents', 'ted', 'todayilearned']
politics = ['politics', 'atheistvids']
generic = ['videos', 'bestofstreamingvideo']

# Master Dictionary

reddit_categories = {'gaming': {'c_list': gaming,
                                'summary': list_to_string(gaming)},
                     'generic': {'c_list': generic,
                                 'summary': list_to_string(generic)},
                     'music': {'c_list': music,
                               'summary': list_to_string(music)},
                     'technology': {'c_list': technology,
                                    'summary': list_to_string(technology)},
                     'sports': {'c_list': sports,
                                'summary': list_to_string(sports)},
                     'educational': {'c_list': educational,
                                     'summary': list_to_string(educational)},
                     'politics': {'c_list': politics,
                                  'summary': list_to_string(politics)}
                     }
# Master List

master_list = create_list(reddit_categories)

# Domain list

domain_list = ['youtube.com', 'vimeo.com', 'ted.com']
