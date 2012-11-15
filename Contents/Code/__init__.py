### Reddit Videos Plex Channel ###

from utilities import good_url
from categories import reddit_categories, master_list, domain_list
import time

VIDEO_PREFIX = "/video/redditvideos"
NAME = "Reddit Videos"
ART = 'art-default.jpg'
ICON = 'icon-default.png'


def Start():
    Plugin.AddPrefixHandler(VIDEO_PREFIX, MainMenu, NAME, ICON, ART)
    Plugin.AddViewGroup("List", viewMode="List", mediaType="items")
    Plugin.AddViewGroup('InfoList', viewMode='InfoList', mediaType='items')
    Plugin.AddViewGroup('PanelStream', viewMode='PanelStream',
                        mediaType='items')
    ObjectContainer.art = R(ART)
    ObjectContainer.title1 = NAME
    DirectoryItem.thumb = R(ICON)


def MainMenu():
    '''
    Creates the following menu:
    enter a manual subreddit
    all subreddits
    all domains
    a list of category subreddits
    '''
    oc = ObjectContainer()
    # Enter Manual Menu
    oc.add(InputDirectoryObject(key=Callback(enter_manual),
                                title='enter a subreddit',
                                summary='Enter the name of a subreddit.' +
                                '\nDo not include "r/".  e.g., "r/videos"' +
                                ' should be entered as "videos"',
                                prompt="enter the name of a subreddit",
                                art=R(ART),
                                thumb=R(ICON)))
    # All Subreddits Menu
    oc.add(DirectoryObject(key=Callback(LiveMenu),
                           title="all subreddits",
                           summary="alphabetical order",
                           art=R(ART),
                           thumb=R(ICON)))
    # All Domains Menu
    oc.add(DirectoryObject(key=Callback(get_domains),
                           title='all domains',
                           art=R(ART),
                           thumb=R(ICON)))
    # Start adding menus for each category
    for element in sorted(reddit_categories.keys()):
        title = element
        c_list = reddit_categories[element]['c_list']
        summary = reddit_categories[element]['summary']
        oc.add(DirectoryObject(key=Callback(LiveMenu, category=c_list),
                               title=title,
                               summary=summary,
                               art=R(ART),
                               thumb=R(ICON)))
    return oc


def LiveMenu(category=None):
    oc = ObjectContainer()
    if not category:
        subreddits = master_list
    else:
        subreddits = category
    for subreddit in sorted(subreddits):
        link = 'http://www.reddit.com/r/' + subreddit + '/.json'
        title = 'r/' + subreddit
        title = title.replace('porn', '')
        oc.add(DirectoryObject(key=Callback(videos,
                                            link=link,
                                            baseurl=link),
                               title=title))
    return oc


def videos(link=None, count=0, baseurl=None, query=None):
    time.sleep(1)
    oc = ObjectContainer()
    user = 'seagullcanfly on reddit Reddit Videos Plex plugin'
    search_page = JSON.ObjectFromURL(link, headers={'user-agent': user})

    # Find next and previous links

    reddit_prefix = link + '?count='
    after = search_page['data'].get('after')
    before = search_page['data'].get('before')
    count += 25

    # Add Previous Menu

    if before:
        prev_count = count - 24
        prev_link = baseurl + '?count=' + str(prev_count) + '&before=' + before
        oc.add(DirectoryObject(key=Callback(videos,
                                            link=prev_link,
                                            baseurl=baseurl,
                                            count=int(count)),
                               title='....previous page'))
    else:
        prev_link = None

    # Find Video Links

    children = search_page['data']['children']
    if children:
        for child in children:
            try:
                childtype = child['data']['media']['oembed']['type']
            except:
                childtype = None
            if childtype == 'video':
                title = child['data'].get('title')
                if title:
                    title = title.strip('amp;')
                url = child['data'].get('url')
                thumb = child['data']['media']['oembed'].get('thumbnail_url')
                if not thumb:
                    thumb = R(ICON)
                summary = child['data']['media']['oembed'].get('description')
                if not summary:
                    summary = "No description provided."
                if good_url(url):
                    oc.add(VideoClipObject(
                        url=url,
                        title=title,
                        thumb=thumb,
                        summary=summary))
    # Add Next Menu

    if after:
        next_link = baseurl + '?count=' + str(count) + '&after=' + after
        oc.add(DirectoryObject(key=Callback(videos,
                                            link=next_link,
                                            baseurl=baseurl,
                                            count=int(count)),
                               title='next...'))
    return oc


def enter_manual(query):
    '''
    enter_manual allows a user to enter a subreddit
    manually.
    '''
    oc = ObjectContainer()
    link = 'http://www.reddit.com/r/' + query + '/.json'
    title = 'r/' + query
    title = title.replace('porn', '')
    oc.add(DirectoryObject(key=Callback(videos,
                                        link=link,
                                        baseurl=link),
                           title=title))
    return oc


def get_domains():
    '''
    get_domains lists all the videos on reddit for the
    domains in categories.domain_list.
    '''
    oc = ObjectContainer()
    for domain in sorted(domain_list):
        link = 'http://www.reddit.com/domain/' + domain + '/.json'
        title = 'domain/' + domain
        oc.add(DirectoryObject(key=Callback(videos,
                                            link=link,
                                            baseurl=link),
                               title=title))
    return oc
