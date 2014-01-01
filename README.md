##Reddit Videos 
*This is the official Reddit Videos Plex plugin development git.*

###Current Features:
* Manually Enter any subreddit to look for videos.
* Maintain a list of customizable favorite subreddits.
* ~~Browse hard-coded subreddits.~~
* View the most popular videos from specific domains like youtube.com or ted.com irrespective of subreddit.
* Sort the subreddits by hot, new, or top (all time, month, week, day, and hour)
* Discover subreddits from user-maintained multi-reddit (replaces hard-coded subreddits)

###Upcoming Features:
* Support for images
* Automatic playlist creation (not sure if possible)
* View comments for individual videos
* User authentication

###Installation:
The official version can be installed directly from Plex.  Some of the changes noted here may not be available immediately until the changes have been merged with Plex's github account.

The development version can enabled by editing "__init__.py".  Instructions to edit it are in the file, but they also follow:

DEVELOPMENT SECTION

 1. Replace the @handler line below with 2nd handler
 2. Rename the entire bundle to RedditVideosDev.bundle to prevent Plex from automatically reverting to the official version.
 3. Replace the @handler line with the 1st handler and rename the folder to RedditVideos.bundle to restore the channel.
 4. Place the .bundle folder and all of its contents in your Plex Media Server Plug-Ins directory.

 1st handler
 @handler('/video/redditvideos', 'Reddit Videos')
 2nd handler
 @handler('/video/redditvideosdev', 'Dev Reddit Videos')
