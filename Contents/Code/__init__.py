### Reddit Videos Plex Channel ###

from utilities import good_url
from categories import reddit_categories, master_list, domain_list

NAME = "Reddit Videos"
USER_AGENT = 'seagullcanfly on Reddit RedditVideos Plex plugin' # https://github.com/reddit/reddit/wiki/API


def Start():
    """
Mandatory to include.
    """
    ObjectContainer.title1 = NAME

# DEVELOPMENT SECTION
#
# 1.) Replace the @handler line below with 2nd handler
# 2.) Rename the entire bundle to RedditVideosDev.bundle to prevent
#     Plex from automatically reverting to the official version.
# 3.) Replace the @handler line with the 1st handler and rename the
#     folder to RedditVideos.bundle to restore the channel.
# 4.) Place the .bundle folder and all of its contents in your
#     Plex Media Server directory.
#
# 1st handler
# @handler('/video/redditvideos', 'Reddit Videos')
# 2nd handler
# @handler('/video/redditvideosdev', 'Dev Reddit Videos')

@handler('/video/redditvideosdev', 'Dev Reddit Videos')
def MainMenu():
    """
    Creates the following menu:
    Enter a manual subreddit
    Custom Favorites
    All subreddits
    All domains
    Categories
    """
    oc = ObjectContainer()
    # Enter Manual Menu
    oc.add(InputDirectoryObject(key=Callback(enter_manual),
                                title='Enter a subreddit',
                                summary='Manually entered subreddits are not saved.' +
                                        'Enter the name of a subreddit.' +
                                        '\nDo not include "r/".  e.g., "r/videos"' +
                                        ' should be entered as "videos"',
                                prompt="enter the name of a subreddit"))

    # Custom Favorites Menu
    oc.add(DirectoryObject(key=Callback(custom_favorites),
                           title='Custom Favorites',
                           summary='This is where you can store your favorite subreddits', ))

    # All Subreddits Menu
    # oc.add(DirectoryObject(key=Callback(LiveMenu),
    #                        title="All subreddits",
    #                        summary="This is just a list of subreddits included by default.  There" +
    #                                "are plenty of other subreddits to add to your favorites."))
    # All Domains Menu
    oc.add(DirectoryObject(key=Callback(get_domains),
                           title='All Domains',
                           summary='This is a neat trick with reddit.  You can view the top videos' +
                                   'regardless of what subreddit they are in just by the domain they come' +
                                   'from.'))
    # # Start adding menus for each category
    # for element in sorted(reddit_categories.keys()):
    #     title = element
    #     c_list = reddit_categories[element]['c_list']
    #     summary = reddit_categories[element]['summary']
    #     oc.add(DirectoryObject(key=Callback(LiveMenu, category=c_list),
    #                            title=title,
    #                            summary=summary))
    # MultiReddit Menu
    oc.add(DirectoryObject(key=Callback(MultiMenu),
                           title="Subreddit Discovery",
                           summary="This is an automatic list maintained by u/efidol and u/seagullcanfly."))

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


def MultiMenu():
    """
    The MultiMenu is an automatic way of maintaining popular subreddits
    and categories.
    """
    oc = ObjectContainer()
    multi_reddit_url = "http://www.reddit.com/user/efidol/m/cordfreetv"
    oc.add(DirectoryObject(key=Callback(videos,
                                        url=multi_reddit_url+".json",
                                        title="All Discovery Subreddits",
                                        limit=100),
                           title="All Discovery Subreddits"))
    content = HTML.ElementFromURL(multi_reddit_url)
    #page = HTML.ElementFromString(content)
    multi_subreddits = content.xpath('//ul[@class="subreddits"]//li/a/text()')
    clean_subreddits = []
    for sub in multi_subreddits:
        sub = sub.split('r/')[-1]
        clean_subreddits.append(sub.title())
    subreddits = clean_subreddits
    Log(subreddits)
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
                                prompt="enter the name of a subreddit"))
    oc.add(InputDirectoryObject(key=Callback(delete_favorite),
                                title='Delete a Custom Favorite',
                                summary='Enter the name of a subreddit.' +
                                        '\nDo not include "r/".  e.g., "r/videos"' +
                                        ' should be entered as "videos"',
                                prompt="enter the name of a subreddit"))
    try:
        custom_faves = Dict['favorites']
    except:
        custom_faves = []
        Dict['favorites'] = custom_faves
    if not custom_faves:
        custom_faves = ['enterfavoritesubreddits']
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
    except:
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
