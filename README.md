# InstaDloader

This script will parse, query, and download almost anything posted to Instagram:
- Posts
- Reels
- Stories
- Highlights
- Private all of the above (only works for stories right now)

The format is:
- Any post will be in its own folder with `username [shortcode]` and inside of the folder will be each item in the post, the query, and a simple post metadata info file.
- Any reel will be put in its own folder called `reels` with the query and metadata being placed into its own folder called `data` with the same file names for easy location. This is aimed toward downloaded memes in the form of reels, and not making them have their own folder.
- Any post with only one item that is a video will be treated as a reel and be subject to the organization above.
- Stories will be placed into a folder called `username's Stories` and will sync and update as you download. Any already downloaded will be ignored and it will only download new ones. Each individual story item has an info file to go along with it, and a global `items.json` to keep track of all items.
- Highlights will be placed into a folder called `username [highlight <highlight_code>]`. Inside of this folder will be every highlight with a single `info.json` with information such as the title, the username, last updated, highlight ID, and the total number of items. It is updated when you re-download. It also makes an `items.json` file that will be updated with all the individual items and their individual highlight IDs so you can re-download the highlight to grab new stuff and only download the new stuff, syncing the folder.

To download from private anything, you must use the `-p` or `--private` argument before the URL. To download stories and highlights of any type, private or not, you still need to use `-p` or `--private` as they need user login.

The cookies come from the Firefox browser as to come from Chrome, the program would need extra permissions to access cookies data while Chrome is open. Simply login to instagram in Firefox and the code should work for that.

Under regular downloading (no private) I suggest using a VPN, so you can change IP anytime Instagram rate limits you. As the normal downloading without cookies does not interact with your account directly, you'll be fine with downloading in semi-bulk, but be modest and careful.

Under private downloading (or stories/highlights), using a VPN never hurts, but the code is designed to implement a long random delay in between each download request to reduce possible rate limits and flags. Be careful and don't download too much at once.

For stories, when you download a story from a user, it will need to request the user page to find their ID. It will cache this ID in a `user_cache.json` in the same directory that the program file sits. Anytime you re-download from the same person, it will use this cached ID and prevent another request. It will request another if the username changes.

## TODO:
- [ ] Make private mode work for highlights, reels and posts.
- [ ] Add method to download profile picture along with current stats (posts, followers, following) as well as BIO.
- [ ] Add method to download an entire profile. If rate limited, pause and wait for interaction from user after VPN IP changes. This will not be available for private pages. Too much risk.
- [ ] Add configuration to decide a lot of specifics, such as where to download each type of post/reel/story/highlight as well as what information to keep alongside it.

## Why did I make this:

There are already quiet a few downloaders out there, but they usually have some restrictions:
- `yt-dlp` can only do videos, such as reels. Plus, you need to dig through the documentation to figure out how to get information such as metadata and such saved as well. Mine will do that for you.
- `gallery-dl` can do posts AND videos, but even if the account is public, it requires you to login, which is pretty annoying. 
- `snapinsta` is one of many online downloaders, but it provides poor filenames and organization when downloaded. Can be good for simple meme downloads, but beyond that, it can get a bit frustrating.
- `instaloader` does exist, and it's not necessarily bad, but this is also a project for me to learn about code and how systems work.

## Disclaimer:

This project is for educational purposes only.
Users are responsible for complying with Instagram's Terms of Service.
Do not use this to download content you do not have permission to access.