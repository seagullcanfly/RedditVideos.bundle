####################################################################################################################
#
#                                  Reddit Videos Plex Channel
#
# This is a channel for Plex.  It allows users to browse videos that have been submitted to reddit.com.
# Users can store and delete favorite subreddits, multireddits, and browse supplied categories.  All menu options
# can be customized in the preferences.  If you have any questions or requests, find me on reddit at
# u/seagullcanfly or at github https://github.com/seagullcanfly/RedditVideos.bundle.
#
####################################################################################################################

NAME = "Reddit Videos"
USER_AGENT = 'seagullcanfly on Reddit RedditVideos Plex plugin'  # https://github.com/reddit/reddit/wiki/API


def good_url(url):
    """ This will filter out unwanted words in the url."""
    return ('playlist' not in url) and ('crackle.com' not in url) and url

####################################################################################################################


def Start():
    """
    Mandatory to include.
    """
    ObjectContainer.title1 = NAME

###############################################  MENU  #############################################################


@handler('/video/redditvideos', 'Reddit Videos')
def MainMenu():
    """ Creates the following menus: Videos, Custom Favorites, Enter Multireddit, Enter Manual
        All domains, Subreddit Discovery, Gaming Discovery   """
    oc = ObjectContainer()

    # Videos Menu
    if Prefs['show_videos']:
        oc.add(DirectoryObject
              (key=Callback(view_sort,
                            url='http://www.reddit.com/r/videos/.json'),
               title='Videos Subreddit'))

    # Custom Favorites Menu
    if Prefs['show_custom_favorites']:
        oc.add(DirectoryObject
              (key=Callback(custom_favorites),
               title='Custom Favorites',
               summary='This is where you can store your favorite subreddits', ))

    # Enter Multireddit
    if Prefs['show_enter_multireddit']:
        oc.add(DirectoryObject
              (key=Callback(enter_multireddit),
               title='Enter a multireddit',
               summary='By creating a multireddit on reddit, you can maintain your favorite subreddits online.', ))

    # Enter Manual Menu
    if Prefs['show_enter_manual']:
        oc.add(InputDirectoryObject
              (key=Callback(enter_manual),
               title='Enter a subreddit',
               summary='Manually entered subreddits are not saved. Enter the name of a subreddit.' +
               '\nDo not include "r/".  e.g., "r/videos" should be entered as "videos"',
               prompt="enter the name of a subreddit"))

    # Search Reddit
    if Prefs['show_search_reddit']:
        oc.add(InputDirectoryObject
              (key=Callback(domain_search),
               title='Search Reddit',
               summary='This will search all youtube videos uploaded to reddit.',
               prompt="enter your search term"))

    # All Domains Menu
    if Prefs['show_domains']:
        oc.add(DirectoryObject
              (key=Callback(get_domains),
               title='All Domains',
               summary='This is a neat trick with reddit.  You can view the top videos regardless of' +
               ' what subreddit they are in just by the domain they come from.'))

    # Subreddit Discovery Menu
    if Prefs['show_subreddit_discovery']:
        oc.add(DirectoryObject
              (key=Callback(subreddit_discovery,
                            url="http://www.reddit.com/user/seagullcanfly/m/plexsubreddits"),
               title="Subreddit Discovery",
               summary="This is an automatic list maintained by u/seagullcanfly."))

    # Gaming Subreddits
    if Prefs['show_gaming_subreddits']:
        oc.add(DirectoryObject
              (key=Callback(subreddit_discovery,
                            url="http://www.reddit.com/user/seagullcanfly/m/gamingvideos"),
               title="Gaming Subreddits",
               summary="A collection of gaming subreddits."))

    # Preferences
    oc.add(PrefsObject
          (title='Change channel settings'))

    return oc

###############################################  MULTIREDDITS  ######################################################


def subreddit_discovery(url):
    """ subreddit_discovery automatically pulls a maintained list of popular subreddits
        from a published multireddit."""
    oc = ObjectContainer()
    oc.add(DirectoryObject
          (key=Callback(videos,
                        url=url + ".json"),
           title="All Subreddits Combined.."))
    content = HTML.ElementFromURL(url)
    multi_subreddits = content.xpath('//ul[@class="subreddits"]//li/a/text()')
    clean_subreddits = []
    for sub in multi_subreddits:
        sub = sub.split('r/')[-1]
        clean_subreddits.append(sub.title())
    subreddits = clean_subreddits
    for subreddit in sorted(subreddits):
        url = 'http://www.reddit.com/r/%s/.json' % subreddit
        title = 'r/%s' % subreddit
        oc.add(DirectoryObject
              (key=Callback(view_sort,
                            url=url),
               title=title))
    return oc


def enter_multireddit():
    """ Has the following menus:
          Add a Multireddit
          Delete a Multireddit
          Custom Favorites Populated """
    oc = ObjectContainer()
    # if no multireddits exist, the directory should show instructions once.
    try:
        multireddits = Dict['multireddits']
    except KeyError:
        Dict['multireddits'] = []
        return ObjectContainer(header="Instructions",
                               message="Find or create a public multireddit on reddit. " +
                               "Remember the user name and multireddit name.")

    if multireddits:
        # List stored Multireddits
        for user, multi in multireddits:
            user = user.strip()
            multi = multi.strip()
            url = 'http://www.reddit.com/user/%s/m/%s' % (user, multi)
            title = "%s's %s" % (user, multi)
            oc.add(DirectoryObject
                  (key=Callback(subreddit_discovery,
                                url=url),
                   title=title,
                   summary="This is a stored multireddit."))

        # Add a Multireddit
    oc.add(InputDirectoryObject
          (key=Callback(enter_multi),
           title='Add a Multireddit',
           summary='Enter the user who created the subreddit, a comma (",") followed by the name' +
           ' of the multireddit.  For example, you could enter this without the quotation marks' +
           ' to enter my gamingvideos multireddit, "seagullcanfly, gamingvideos"',
           prompt="enter the user who created the multireddit, a comma, then the multireddit's name" +
           "e.g., seagullcanfly, gamingvideos"))

        # Delete a Multireddit
    oc.add(InputDirectoryObject
           (key=Callback(delete_multi),
            title='Delete a Multireddit',
            summary='Enter the user who created the subreddit, a comma (",") followed by the name' +
            ' of the multireddit.  For example, you could enter this without the quotation marks' +
            ' to enter my gamingvideos multireddit, "seagullcanfly, gamingvideos"',
            prompt="enter the user who created the multireddit, a comma, then the multireddit's name" +
            "e.g., seagullcanfly, gamingvideos"))
    return oc


def enter_multi(query):
    """ This adds a user-generated multireddit in persistent storage."""
    try:
        multireddits = Dict['multireddits']
    except KeyError:
        multireddits = []
    query = query.split(',')
    query = (query[0], query[1])
    if not multireddits:
        multireddits = []
    multireddits.append(query)
    Dict['multireddits'] = multireddits
    Dict.Save()


def delete_multi(query):
    """ This deletes a user-generated multireddit from persistent storage."""
    multireddits = Dict['multireddits']
    query = query.split(',')
    query = (query[0], query[1])
    try:
        multireddits.remove(query)
    except KeyError:
        Log('Problem with deleting multireddit from storage')
    Dict['multireddits'] = multireddits
    Dict.Save()

####################################################################################################################


@handler('/video/redditvideos', 'Reddit Videos')
def view_sort(url):
    """ Currently all videos can be sorted by hot, new, and top.  Top includes all time,
        month, week, day, and hour."""
    oc = ObjectContainer()
    url_list = url.split('.json')
    top_url = url_list[0] + 'top/.json'
    new_url = url_list[0] + 'new/.json'

    # Hot
    oc.add(DirectoryObject
          (key=Callback(videos,
                        url=url),
           title="Hot"))
    # New
    oc.add(DirectoryObject
          (key=Callback(videos,
                        url=new_url),
           title="New"))
    # Top - with sortings
    sortings = {'all': 'Top - All Time',
                'year': 'Top - Year',
                'month': 'Top - Month',
                'week': 'Top - Week',
                'day': 'Top - Day',
                'hour': 'Top - Hour'}
    sort_order = ['all', 'year', 'month', 'week', 'day', 'hour']
    for view in sort_order:
        oc.add(DirectoryObject
              (key=Callback(videos,
                            url=top_url,
                            sort=view),
               title=sortings[view]))
    return oc

####################################################################################################################


class VideoData:

    def __init__(self, video_post_data):
        self.link = False
        self.text = False
        self.urls = []
        self.domain = video_post_data['data'].get('domain')
        self.title = video_post_data['data'].get('title')
        self.score = str(video_post_data['data'].get('score'))
        self.id = str(video_post_data['data'].get('id'))
        self.subreddit = video_post_data['data'].get('subreddit')
        self.thumbnail = video_post_data['data'].get('thumbnail')
        self.nsfw = video_post_data['data'].get('over_18')  # working on this
        if self.domain in ['youtube.com', 'vimeo.com']:
            try:
                self.summary = video_post_data['data']['media']['oembed'].get('description')
            except AttributeError:
                self.summary = self.title
            self.urls = [video_post_data['data'].get('url')]
        if video_post_data['data'].get('is_self'):
            self.summary = video_post_data['data']['selftext']
            text_post = self.summary
            youtube_prefix = 'http://www.'
            youtube_key = 'youtube.com/watch?v='
            youtube_length = len(youtube_key) + 11
            start_index = text_post.find(youtube_key)
            while start_index > 0:
                text_post = text_post[start_index::]
                end_index = youtube_length
                vid_url = youtube_prefix + text_post[:end_index]
                if vid_url not in self.urls and good_url(vid_url):
                    self.urls.append(vid_url)
                text_post = text_post[end_index::]
                start_index = text_post.find(youtube_key)


def videos(url, count=0, limit=32, after='', sort=None):
    """ This method returns all the video links for any specific page. """
    oc = ObjectContainer()
    url += '?count=%d&limit=%d&after=%s' % (count, limit, after)
    if sort:
        url += '&sort=top&t=%s' % sort
    search_page = JSON.ObjectFromURL(url, sleep=2.0, cacheTime=600, headers={'User-Agent': USER_AGENT})

    @parallelize
    def get_videos():
        for video_child in search_page['data']['children']:

            @task
            def get_video(video_post=video_child):
                reddit_video = VideoData(video_post)
                if Prefs['show_score']:
                    video_title = reddit_video.score + " | " + reddit_video.title
                for video_url in reddit_video.urls:
                    if good_url(video_url):
                        if Prefs['show_comment_menu']:
                            oc.add(DirectoryObject(key=Callback(commented_videos,
                                                                video_url=video_url,
                                                                video_id=reddit_video.id,
                                                                video_subreddit=reddit_video.subreddit,
                                                                video_title=video_title,
                                                                video_summary=reddit_video.summary),
                                                   title=video_title,
                                                   thumb=reddit_video.thumbnail))
                        else:
                            video_object = URLService.MetadataObjectForURL(video_url)
                            video_object.title = String.StripTags(video_title)
                            video_object.summary = String.StripTags(reddit_video.summary)
                            oc.add(video_object)

    # Find/Add Next Menu
    after = search_page['data'].get('after')
    count += limit

    if after:
        oc.add(NextPageObject
              (key=Callback(videos,
                            url=url,
                            count=count,
                            limit=limit,
                            after=after),
               title='Next ...'))
    return oc


def commented_videos(video_url, video_id, video_subreddit, video_title, video_summary):
    """If turned on in the channel's preferences, another menu level will be created that
    shows the top-rated comments for a video."""
    oc = ObjectContainer()
    video_object = URLService.MetadataObjectForURL(video_url)
    video_object.title = String.StripTags(video_title)
    video_object.summary = String.StripTags(video_summary)
    oc.add(video_object)
    comment_url = 'http://www.reddit.com/r/' + video_subreddit + '/' + video_id + '.json'
    comment_page = JSON.ObjectFromURL(comment_url, sleep=2.0, cacheTime=600, headers={'User-Agent': USER_AGENT})
    comments = comment_page[1]['data']['children']
    for comment in comments:
        comment_text = comment['data'].get('body')
        if not comment_text:
            comment_text = "Not yet commented on."
        oc.add(PopupDirectoryObject(key=Callback(show_comment,
                                                 comment=comment_text),
                                    title=comment_text[0:20],
                                    summary=comment_text))
    return oc


def show_comment(comment):
    return ObjectContainer(header='Video Comment', message=comment)

###############################################  FAVORITES  ########################################################


def custom_favorites():
    """ Has the following menus:
          Add a Custom Favorite
          Delete a Custom Favorite
          Custom Favorites Populated"""
    oc = ObjectContainer()

    # Add a Custom Favorite
    oc.add(InputDirectoryObject
          (key=Callback(enter_favorite),
           title='Add a Custom Favorite',
           summary='Enter the name of a subreddit.\nDo not include "r/".  e.g., "r/videos"' +
           ' should be entered as "videos."',
           prompt="Enter the name of a subreddit"))

    # Delete a Custom Favorite
    oc.add(InputDirectoryObject
          (key=Callback(delete_favorite),
           title='Delete a Custom Favorite',
           summary='Enter the name of a subreddit.\nDo not include "r/".  e.g., "r/videos"' +
           ' should be entered as "videos."',
           prompt="Enter the name of a subreddit"))

    # Custom Favorites
    try:
        custom_faves = Dict['favorites']
    except KeyError:
        custom_faves = ['enterfavoritesubreddits']
        Dict['favorites'] = custom_faves
    for subreddit in custom_faves:
        url = 'http://www.reddit.com/r/%s/.json' % subreddit
        title = 'r/%s' % subreddit
        oc.add(DirectoryObject
              (key=Callback(view_sort,
                            url=url),
               title=title))
    return oc


def enter_favorite(query):
    """ This adds a user-generated subreddit in persistent storage."""
    try:
        custom_faves = Dict['favorites']
    except KeyError:
        custom_faves = []
    custom_faves.append(query)
    Dict['favorites'] = custom_faves
    Dict.Save()


def delete_favorite(query):
    """ This deletes a user-generated subreddit from persistent storage."""
    current_list = Dict['favorites']
    try:
        current_list.remove(query)
    except ValueError:
        Log('subreddit was not already stored as a favorite')
    Dict['favorites'] = current_list
    Dict.Save()

###############################################  DOMAINS  ##########################################################


def get_domains():
    """ get_domains lists all the videos on reddit for the domains in domain_list."""
    oc = ObjectContainer()
    domain_list = ['youtube.com', 'vimeo.com']
    for domain in sorted(domain_list):
        url = 'http://www.reddit.com/domain/%s/.json' % domain
        title = 'domain/' + domain
        oc.add(DirectoryObject
              (key=Callback(videos,
                            url=url),
               title=title))
    return oc

###############################################  SEARCH  ###########################################################


def domain_search(query):
    """ domain_search searches for any video uploaded to reddit on youtube that matches the query."""
    oc = ObjectContainer()
    search_url = "http://www.reddit.com/domain/youtube.com/search.json?q=%s&restrict_sr=on" % query
    title = 'Searching for "%s"....' % query
    oc.add(DirectoryObject
          (key=Callback(videos,
                        url=search_url),
           title=title))
    return oc

###############################################  MANUAL  ###########################################################


def enter_manual(query):
    """ enter_manual allows a user to enter a subreddit manually."""
    oc = ObjectContainer()
    url = 'http://www.reddit.com/r/%s/.json' % query
    title = 'r/' + query
    oc.add(DirectoryObject
          (key=Callback(view_sort,
                        url=url),
           title=title))
    return oc
