from bs4 import BeautifulSoup as bs
import subprocess

def get_table_url(title):
    '''
    Get the link of the artist-title table on MLDb.
    The search is performed by title and the exact match of it.
    input:
        title (string)
    output:
        url (string)
    '''
    baseURL = "http://mldb.org/search"
    mq = title
    si = 2  # search by title
    mm = 2  # exact match
    ob = 1  # relevant
    args = {'mq': mq, 'si': si, 'mm' : mm, 'ob' : ob}
    table_url = baseURL + '?' + '&'.join(['='.join(
                               [key, str(args[key])]) for key in args])
    return table_url

def get_lyric_url(artist, table_url):
    '''
    Get the link of the lyric based on an exact match to the title and artist.
    input:
        artist (string)
        table_url (string)
    output:
        lyric_url (string)  *When there is a match in artist, else None
    '''
    content = subprocess.run(["curl", "-L", "-H", "User-Agent: NotBot", table_url],
    capture_output=True).stdout
    soup = bs(content, 'html.parser')

    #Find the <a> element with an exact match in artist name
    a_artist = soup.find("a", text = artist)  
    '''
    HTML structure:
    <td class="fa">
	  	  <a href='artist-9523-taylor-swift.html'> Artist1 </a>
	  	  <a href='artist-9523-taylor-swift.html'> Artist2 </a>
	  </td>
	  <td class="ft">
	  	  <a href="song-244430-love-story.html"> Title </a>
	  </td>
    '''
    if a_artist:
        # With the <a> element that matches author, find the first <a> element
        # under next <td> that correspond to the song and extract the link
        lyric_url = "http://mldb.org/" + a_artist.find_next("td").find("a").get("href")
        return lyric_url
    else:
        # If a_artist is empty, then there is no exact match in the first page
        return None

def new_page(table_url):
    '''
    Browse through all the pages for an exact match
    input:
        table_url (string)
    output:
        lyric_url (string) *When there is a match in artist, else None
    '''
    content = subprocess.run(["curl", "-L", "-H", "User-Agent: NotBot", table_url],
    capture_output=True).stdout
    soup = bs(content, 'html.parser')

    # Check if there are multiple pages
    pages = soup.select('a[href*="from="]')
    if pages:
        # There are multiple pages
        for page in pages:
            # for each page, apply get_lyric_url
            table_url = "http://mldb.org/" + page["href"]
            lyric_url = get_lyric_url(artist, table_url)
            if lyric_url is not None:
                # if the exact match is found, return it and end the loop
                return lyric_url
    # If no match in all pages
    return None

def create_dict(lyric_url, table_url):
    '''
    Create a dictionary containing information about artist, album, and lyrics.
    input:
        lyric_url (string)
        table_url (string)  *If lyrics are returned directly
    output:
        diction (dictionary)
    '''
    content = subprocess.run(["curl", "-L", "-H", "User-Agent: NotBot", lyric_url], 
    capture_output=True).stdout
    soup = bs(content, 'html.parser')

    diction = {}
    if soup.find("th", text = "Artist(s)"):
        # When multiple songs are returned and the lyric_url is returned as desired
        diction["Artist(s)"] = [name.get_text() for name in soup.find(
            "th", text = "Artist(s)").find_parent().find_all("a")]
        diction["Album(s)"] = [album.get_text() for album in soup.find(
            "th", text = "Album(s)").find_parent().find_all("a")]
        diction["Lyrics"] = soup.find("p").get_text()
        return diction
    else:
        # If lyrics are returned directly from the initial search, 
        # then the table_url link directly to the lyric_url
        lyric_url = table_url
        return create_dict(lyric_url, None)

def lyrics_artist_album(title, artist):
    '''
    Create a dictionary containing information about artist, album, and lyrics.
    input:
        title (string)
        artist (string)
    output:
        diction (dictionary)
    '''
    # Basic String manipulation
    title = "+".join(title.split())
    artist = artist.title()
    
    table_url = get_table_url(title)
    lyric_url = get_lyric_url(artist, table_url)

    if lyric_url is None:
        # If no match is found, chech if there's more pages
        lyric_url = new_page(table_url)
        if lyric_url is None:
            # If no match across all page, end the function
            print("Didn't find any match - check for input error.")
            return None
    diction = create_dict(lyric_url, table_url)

    return diction

title = "Dance in the Dark"
artist = "Bruce Springsteen"
song_info = lyrics_artist_album(title, artist)
for i in song_info:
    print(i, ":\n", song_info[i], sep = "")

print("\n____________________________________________________________________________\n")
title = "Leaving Las Vegas"
artist = "Sheryl Crow"
song_info = lyrics_artist_album(title, artist)
for i in song_info:
    print(i, ":\n", song_info[i], sep = "")

print("\n____________________________________________________________________________\n")
# Case for multiple pages
title = "Dance with"
artist = "Blink 182"
song_info = lyrics_artist_album(title, artist)
for i in song_info:
    print(i, ":\n", song_info[i], sep = "")