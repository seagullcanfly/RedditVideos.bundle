### Reddit Videos Plex Channel ###

from utilities import good_url
from categories import reddit_categories, master_list, domain_list

NAME = "Reddit Videos"
ART = 'art-default.jpg'
ICON = 'icon-default.png'
USER_AGENT = 'seagullcanfly on Reddit RedditVideos Plex plugin' # https://github.com/reddit/reddit/wiki/API


def Start():
    """
Mandatory to include.
    """
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
    Enter a manual subreddit
    Custom Favorites
    All subreddits
    All domains
    Categories
    """
    oc = ObjectContainer(view_group='InfoList')
    # Enter Manual Menu
    oc.add(InputDirectoryObject(key=Callback(enter_manual),
                                title='enter a subreddit',
                                summary='Manually entered subreddits are not saved.' +
                                        'Enter the name of a subreddit.' +
                                        '\nDo not include "r/".  e.g., "r/videos"' +
                                        ' should be entered as "videos"',
                                prompt="enter the name of a subreddit",
                                thumb=R(ICON)))

    # Custom Favorites Menu
    oc.add(DirectoryObject(key=Callback(custom_favorites),
                           title='Custom Favorites',
                           summary='This is where you can store your favorite subreddits', ))

    # All Subreddits Menu
    oc.add(DirectoryObject(key=Callback(LiveMenu),
                           title="All subreddits",
                           summary="This is just a list of subreddits included by default.  There" +
                                   "are plenty of other subreddits to add to your favorites."))
    # All Domains Menu
    oc.add(DirectoryObject(key=Callback(get_domains),
                           title='All Domains',
                           summary='This is a neat trick with reddit.  You can view the top videos' +
                                   'regardless of what subreddit they are in just by the domain they come' +
                                   'from.'))
    # Start adding menus for each category
    for element in sorted(reddit_categories.keys()):
        title = element
        c_list = reddit_categories[element]['c_list']
        summary = reddit_categories[element]['summary']
        oc.add(DirectoryObject(key=Callback(LiveMenu, category=c_list),
                               title=title,
                               summary=summary))
    return oc


def LiveMenu(category=None):
    """
    The LiveMenu shows the name of the subreddit before the next directory
    which only shows the sorting options by hot, top, and new.
    """
    oc = ObjectContainer()
    if not category:
        subreddits = master_list
    else:
        subreddits = category
    for subreddit in sorted(subreddits):
        url = 'http://www.reddit.com/r/%s/.json' % subreddit
        title = 'r/%s' % subreddit

        oc.add(DirectoryObject(key=Callback(ViewSort,
                                            url=url,
                                            title=title,
                                            limit=100),
                               title=title))
    return oc


def ViewSort(url, title, limit=100):
    """
    Currently all videos can be sorted by hot, new, and top.  Top includes all time,
    month, week, day, and hour.
    """
    oc = ObjectContainer()
    url_list = url.split('.json')
    top_url = url_list[0] + 'top/.json'
    new_url = url_list[0] + 'new/.json'

    # Hot
    oc.add(DirectoryObject(key=Callback(videos,
                                        url=url,
                                        title=title + ":  Hot",
                                        limit=limit),
                           title="Hot"))
    # New
    oc.add(DirectoryObject(key=Callback(videos,
                                        url=new_url,
                                        title=title + ":  New",
                                        limit=100),
                           title="New"))
    # Top - with sortings
    sortings = {'all': 'Top - All Time', 'month': 'Top - Month',
                'week': 'Top - Week', 'day': 'Top - Day',
                'hour': 'Top - Hour'}
    sort_order = ['all', 'month', 'week', 'day', 'hour']

    for view in sort_order:
        oc.add(DirectoryObject(key=Callback(videos,
                                            url=top_url,
                                            title=sortings[view],
                                            limit=100,
                                            sort=view),
                               title=sortings[view]))
    return oc


def videos(url, title, count=0, limit=25, after='', sort=None):
    """
    This method returns all the video links for any specific page.  It can only
    return videos for direct links to videos.  There is no current or future plan
    to search text posts for links to videos.
    """
    oc = ObjectContainer(title2=title)
    result = {}
    url += '?count=%d&limit=%d&after=%s' % (count, limit, after)
    if sort:
        url += '&sort=top&t=%s' % sort
    Log(url)
    search_page = JSON.ObjectFromURL(url, sleep=2.0, cacheTime=600, headers={'User-Agent': USER_AGENT})

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


def custom_favorites():
    """
    This is just a menu for entering in favorites.
    """
    oc = ObjectContainer()
    oc.add(InputDirectoryObject(key=Callback(enter_favorite),
                                title='Add a Custom Favorite',
                                summary='Enter the name of a subreddit.' +
                                        '\nDo not include "r/".  e.g., "r/videos"' +
                                        ' should be entered as "videos"',
                                prompt="enter the name of a subreddit",
                                thumb=R(ICON)))
    oc.add(InputDirectoryObject(key=Callback(delete_favorite),
                                title='Delete a Custom Favorite',
                                summary='Enter the name of a subreddit.' +
                                        '\nDo not include "r/".  e.g., "r/videos"' +
                                        ' should be entered as "videos"',
                                prompt="enter the name of a subreddit",
                                thumb=R(ICON)))
    Log('the value of dict favorites is %s' % Dict['favorites'])
    try:
        custom_faves = Dict['favorites']
        Log('The stored dictionary was opened and the result was %s' % custom_faves)
    except:
        Log('Creating an empty list since there were no stored favorites.')
        custom_faves = []
        Dict['favorites'] = custom_faves
    for subreddit in custom_faves:
        url = 'http://www.reddit.com/r/%s/.json' % subreddit
        title = 'r/%s' % subreddit
        oc.add(DirectoryObject(key=Callback(ViewSort,
                                            url=url,
                                            title=title),
                               title=title))
    return oc


def enter_favorite(query):
    """
    This adds a user-generated subreddit in persistent storage.
    """
    try:
        custom_faves = Dict['favorites']
        Log('Favorites was opened and it is %s' % custom_faves)
    except:
        Log('Apparently there are no favorites in the dictionary %s' % Dict['favorites'])
        custom_faves = []
    custom_faves.append(query)
    Dict['favorites'] = custom_faves
    Dict.Save()


def delete_favorite(query):
    """
    This deletes a user-generated subreddit from persistent storage.
    """
    current_list = Dict['favorites']
    try:
        current_list.remove(query)
    except ValueError:
        Log('subreddit was not already stored as a favorite')
    Dict['favorites'] = current_list
    Dict.Save()


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


def enter_manual(query):
    """
    enter_manual allows a user to enter a subreddit
    manually.
    """
    oc = ObjectContainer()
    url = 'http://www.reddit.com/r/%s/.json' % query
    title = 'r/' + query
    oc.add(DirectoryObject(key=Callback(ViewSort,
                                        url=url,
                                        title=title),
                           title=title))
    return oc
