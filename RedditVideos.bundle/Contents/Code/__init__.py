### Reddit Videos Plex Channel ###

from utilities import good_url
from categories import reddit_categories, master_list, domain_list

NAME = "Reddit Videos"
ART = 'art-default.jpg'
ICON = 'icon-default.png'
USER_AGENT = 'seagullcanfly on Reddit RedditVideos Plex plugin' # https://github.com/reddit/reddit/wiki/API

def Start():
    Plugin.AddViewGroup('List', viewMode='List', mediaType='items')
    Plugin.AddViewGroup('InfoList', viewMode='InfoList', mediaType='items')
    ObjectContainer.art = R(ART)
    ObjectContainer.title1 = NAME
    DirectoryObject.thumb = R(ICON)
    NextPageObject.thumb = R(ICON)
    VideoClipObject.thumb = R(ICON)

@handler('/video/redditvideos', 'Reddit Videos', thumb=ICON, art=ART)
def MainMenu():
    """
    Creates the following menu:
    enter a manual subreddit
    all subreddits
    all domains
    a list of category subreddits
    """
    oc = ObjectContainer(view_group='InfoList')
    # Enter Manual Menu
    oc.add(InputDirectoryObject(key=Callback(enter_manual),
                                title='enter a subreddit',
                                summary='Enter the name of a subreddit.' +
                                '\nDo not include "r/".  e.g., "r/videos"' +
                                ' should be entered as "videos"',
                                prompt="enter the name of a subreddit",
                                thumb=R(ICON)))

    # Custom Favorites Menu
    oc.add(DirectoryObject(key=Callback(custom_favorites),
                                title='Custom Favorites',
                                summary='This is where you can store your favorite subreddits',))

    # All Subreddits Menu
    oc.add(DirectoryObject(key=Callback(LiveMenu),
                           title="all the subreddits",
                           summary="alphabetical order"))
    # All Domains Menu
    oc.add(DirectoryObject(key=Callback(get_domains),
                           title='all domains'))
    # Start adding menus for each category
    for element in sorted(reddit_categories.keys()):
        title = element
        c_list = reddit_categories[element]['c_list']
        summary = reddit_categories[element]['summary']
        oc.add(DirectoryObject(key=Callback(LiveMenu, category=c_list),
                               title=title,
                               summary=summary))
    return oc

def custom_favorites():

    """
This is just a menu for entering in favorites.
    @return:
    """
    oc = ObjectContainer()
    oc.add(InputDirectoryObject(key=Callback(enter_favorite),
                                title='enter a subreddit',
                                summary='Enter the name of a subreddit.' +
                                '\nDo not include "r/".  e.g., "r/videos"' +
                                ' should be entered as "videos"',
                                prompt="enter the name of a subreddit",
                                thumb=R(ICON)))
    Log ('the value of dict favorites is %s' % Dict['favorites'])
    try:
        custom_faves = Dict['favorites']
        Log ('The stored dictionary was opened and the result was %s' % custom_faves)
    except:
        Log ('Creating an empty list since there were no stored favorites.')
        custom_faves = []
        Dict['favorites'] = custom_faves
    for subreddit in custom_faves:
        url = 'http://www.reddit.com/r/%s/.json' % subreddit
        title = 'r/%s' % subreddit
        oc.add(DirectoryObject(key=Callback(videos,
                                            url=url,
                                            title=title),
                               title=title))
    return oc


def LiveMenu(category=None):
    oc = ObjectContainer()
    if not category:
        subreddits = master_list
    else:
        subreddits = category
    for subreddit in sorted(subreddits):
        url = 'http://www.reddit.com/r/%s/.json' % subreddit
        title = 'r/%s' % subreddit

        oc.add(DirectoryObject(key=Callback(videos,
                                            url=url,
                                            title=title,
                                            limit=100),
                               title=title))
    return oc


def videos(url, title, count=0, limit=25, after=''):
    oc = ObjectContainer(title2=title)
    result = {}
    search_page = JSON.ObjectFromURL('%s?count=%d&limit=%d&after=%s' % (url, count, limit, after), sleep=2.0, cacheTime=600, headers={'User-Agent': USER_AGENT})

    @parallelize
    def get_videos():
        # Find Video Links
        children = search_page['data']['children']

        if children:
            for num in range(len(children)):
                child = children[num]

                @task
                def get_video(num=num, result=result, child=child):
                    try:
                        childtype = child['data']['media']['oembed']['type']
                    except:
                        childtype = None

                    if childtype == 'video':
                        video_url = child['data'].get('url')

                        video_title = child['data'].get('title')
                        if video_title:
                            video_title = video_title.replace('&amp;', '&').replace('\n', '')

                        summary = child['data']['media']['oembed'].get('description')
                        if summary:
                            summary = summary.replace('&amp;', '&')
                        else:
                            summary = "No description provided."

                        if good_url(video_url):
                            try:
                                video = URLService.MetadataObjectForURL(video_url)
                                video.title = video_title
                                video.summary = summary

                                result[num] = video
                            except:
                                pass

    keys = result.keys()
    keys.sort()

    for key in keys:
        oc.add(result[key])

    # Find/Add Next Menu
    after = search_page['data'].get('after')
    count += limit

    if after:
        oc.add(NextPageObject(key=Callback(videos,
                                           url=url,
                                           title=title,
                                           count=count,
                                           limit=limit,
                                           after=after),
                              title='Next ...'))
    return oc


def enter_manual(query):
    """
    enter_manual allows a user to enter a subreddit
    manually.
    """
    oc = ObjectContainer()
    url = 'http://www.reddit.com/r/%s/.json' % query
    title = 'r/' + query
    oc.add(DirectoryObject(key=Callback(videos,
                                        url=url,
                                        title=title),
                           title=title))
    return oc

def enter_favorite(query):
    oc = ObjectContainer()
    try:
        custom_faves = Dict['favorites']
        Log ('Favorites was opened and it is %s' % custom_faves)
    except:
        Log ('Apparently there are no favorites in the dictionary %s' % Dict['favorites'])
        custom_faves = []
    custom_faves.append(query)
    Dict['favorites'] = custom_faves
    Dict.Save()
    return oc

def get_domains():
    """
    get_domains lists all the videos on reddit for the
    domains in categories.domain_list.
    """
    oc = ObjectContainer()
    for domain in sorted(domain_list):
        url = 'http://www.reddit.com/domain/%s/.json' % domain
        title = 'domain/' + domain
        oc.add(DirectoryObject(key=Callback(videos,
                                            url=url,
                                            title=title),
                               title=title))
    return oc
