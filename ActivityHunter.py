""" CONSTANTS """
BASE_URL = 'https://www.instagram.com/'
LOGIN_URL = BASE_URL + 'accounts/login/ajax/'
STORIES_UA = 'Instagram 52.0.0.8.83 (iPhone; CPU iPhone OS 11_1 like Mac OS X; en_US; en-US; scale=2.00; 750x1334) AppleWebKit/605.1.15'
CHROME_WIN_UA = 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 Safari/537.36'
IMG_FEED = BASE_URL +  'graphql/query/?query_hash=e7e2f4da4b02303f74f0841279e52d76&variables=%7B%22id%22%3A%2254113000%22%2C%22first%22%3A50%2C%22after%22%3A%22'
FOLLOWS_FIRST_URL = BASE_URL + 'graphql/query/?query_hash=c56ee0ae1f89cdbd1c89e2bc6b8f3d18&variables=%7B%22id%22%3A%22{0}%22%2C%22include_reel%22%3Atrue%2C%22first%22%3A50%7D'
FOLLOWS_URL = BASE_URL + 'graphql/query/?query_hash=c56ee0ae1f89cdbd1c89e2bc6b8f3d18&variables=%7B%22id%22%3A%22{0}%22%2C%22include_reel%22%3Afalse%2C%22first%22%3A50%2C%22after%22%3A%22{1}%22%7D'
TIMELINE_URL = BASE_URL + 'graphql/query/?query_hash=a5164aed103f24b03e7b7747a2d94e3c&variables='
TIMELINE_VARS = '{{"id":"{0}","first":50,"after":"{1}"}}'
LIKES_URL = BASE_URL + 'graphql/query/?query_hash=e0f59e4a1c8d78d0161873bc2ee7ec44&variables='
LIKES_VARS = '{{"shortcode":"{0}","include_reel":true,"first":50,"after":"{1}"}}'
COMMENTS_URL = BASE_URL + 'graphql/query/?query_hash=f0986789a5c5d17c2400faebf16efd0d&variables='
COMMENTS_VAR = '{{"shortcode":"{0}","first":50,"after":"{1}"}}'
FOLLOWS_URL = BASE_URL + 'graphql/query/?query_hash=c56ee0ae1f89cdbd1c89e2bc6b8f3d18&variables='
FOLLOWS_VARS = '{{"id":"{0}","include_reel":true,"fetch_mutual":false,"first":50,"after":"{1}"}}'

OUTPUT_STRING = "{:<20s}{:<10s}{:<20s}{:<13s}{:<28s}{:<20s}"
SLEEP_IN_SECONDS = 1
TRY_AGAIN_SLEEP_SECS = 3600

""" IMPORTS """
import requests, json, time, hashlib, datetime, argparse

class ActivityHunter:
    
    def __init__(self, **kwargs): 
        self.is_logged_in = False 
        attr = dict(target_user = '', from_users=[], comments = True,
                        likes = True, tag = True, to_time = None, 
                        from_time = 0, login_name=None, login_pw = None,
                        all_follows = False, popularity = 300)
        
        attr.update(kwargs)
        for key in attr:
            self.__dict__[key] = attr.get(key)
       
        if self.to_time:
            self.to_time = time.mktime(datetime.datetime.strptime(self.to_time, "%d/%m/%Y").timetuple())
        if self.from_time:
            self.from_time = time.mktime(datetime.datetime.strptime(self.from_time, "%d/%m/%Y").timetuple())
        
        if self.all_follows:
            self.from_users = self.get_follows(self.target_user)
            
        
        self.start_session()
               
    #Logs in to Instagram
    def start_session(self):
        self.session = requests.Session()
        self.session.headers = {'user-agent': CHROME_WIN_UA}
        self.session.cookies.set('ig_pr', '1')             
        self.session.headers.update({'Referer': BASE_URL, 'user-agent': STORIES_UA})
        
        if self.login_name and self.login_pw:
            self._login()  
            
    def _login(self):
        req = self.session.get(BASE_URL)
        self.session.headers.update({'X-CSRFToken': req.cookies['csrftoken']})
        
        login_data = {'username': self.login_name, 'password': self.login_pw}
        login = self.session.post(LOGIN_URL, data=login_data, allow_redirects=True)
        self.session.headers.update({'X-CSRFToken': login.cookies['csrftoken']})
        self.cookies = login.cookies
        response = json.loads(login.text)
        
        if not response.get('user'):
            print('No such username or verification problem')
        elif response.get('user') and response.get('authenticated') is False:
            print('Wrong password')
        else:
            print('Login successful!')
            self.is_logged_in = True 
        
    def to_json(self, data):
        #Universal sleep for all functions that fetches data from Instagram
        time.sleep(SLEEP_IN_SECONDS)      
        return json.loads(data)
    
    def _gen_query_graphql(self, url, url_vars, media_id, end_cursor = ""):
        endpoint_url = url + url_vars     
        while True:
            #update gis session cookie (required for no-login scraping)
            params = url_vars.format(media_id, end_cursor)   
            self.update_ig_gis_header(params)    
            
            edges, has_next_page, end_cursor = self._data_request(endpoint_url.format(media_id, end_cursor), media_id)

            for edge in edges:
                yield edge['node']                                                  
            if has_next_page:
             #If data on next page, continue                                                                 
                 continue
            else:
                break
                  
    def scrape(self):   
        print('Scraping activity...')
        print("-"*110)
        print(OUTPUT_STRING.format("TARGET NAME", "ACTION", "ON USER", "UPLOAD TIME", "MEDIA URL", "ACTION CONTENT"))
        print("-"*110)
        
        for user in self.from_users:
            self.query_timeline(user)            
        print('Done.')
        
    def query_timeline(self, username):
        sharedData = self.get_sharedData(username)
        user_id = sharedData['id']
        
        for media in self._gen_query_graphql(TIMELINE_URL, TIMELINE_VARS, user_id):
            upload_time = media['taken_at_timestamp']
            upload_dateformat = (self.format_timestamp(upload_time))
            like_count = media['edge_media_preview_like']['count']
            shortcode = media['shortcode']
            
            
            
            if self.popularity and like_count > self.popularity:
                continue
            
            if self.from_time:
                #Break if media is timestamp is lower than lowest interval span
                if self.from_time > upload_time:
                    break
            if self.to_time:
                #Continue to next if upload time is higher than to time
                if self.to_time < upload_time:
                    continue
            
            if self.tag:
                for tagged_user in media['edge_media_to_tagged_user']['edges']:
                    if tagged_user['node']['user']['username'] in self.target_user:
                        print(OUTPUT_STRING.format(self.target_user,"tag", username, upload_dateformat, "instagr.am/p/"+media['shortcode'],""))                     
                       
            #Check if likes enable in settings and likes exist in post
            if self.likes and like_count:
                    for likes in self._gen_query_graphql(LIKES_URL, LIKES_VARS, shortcode):
                        if likes['username'] in self.target_user:                          
                            print(OUTPUT_STRING.format(likes['username'],"like",username, upload_dateformat,"instagr.am/p/"+media['shortcode'],""))                          
                            break
            
            if self.comments:
                comment_preview_edges = media['edge_media_to_comment']['edges']
                has_next_page = media['edge_media_to_comment']['page_info']['has_next_page']
                
                #Check if comments exist in post
                if comment_preview_edges:
                    #If post has less comments than preview, scrape direct from media, otherwise scrape from post
                    for comments in self._gen_query_graphql(COMMENTS_URL, COMMENTS_VAR, shortcode) if has_next_page else [a['node'] for a in comment_preview_edges]:
                        if comments['owner']['username'] in self.target_user:
                            print(OUTPUT_STRING.format(self.target_user, "comment", username, upload_dateformat,"instagr.am/p/"+media['shortcode'], comments['text']))
                        
    
    def get_follows(self, username):
        sharedData = self.get_sharedData(username)
        user_id = sharedData['id']
        
        if not self.is_logged_in:
            print("You need to be logged in to get users followers")
            return
        
        print('Getting all follows...')
        follows = []
        for edge in self._gen_query_graphql(FOLLOWS_URL, FOLLOWS_VARS, user_id):   
             if not edge['is_private']:
                 follows.append(edge['username'])
                 
        print('Found {} open users'.format(len(follows)))
        return follows
             
    #Function that get response data from Instagram
    #Return JSON
    def _data_request(self, data_url, media_id):
        while(True):
            response = self.session.get(data_url)        
            response = self.to_json(response.text)
                     
            try:
                #TIMELINE
                if 'a5164aed103f24b03e7b7747a2d94e3c' in data_url:
                    end_cursor = response['data']['user']['edge_owner_to_timeline_media']['page_info']['end_cursor']
                    has_next_page = response['data']['user']['edge_owner_to_timeline_media']['page_info']['has_next_page'] 
                    edges = response['data']['user']['edge_owner_to_timeline_media']['edges']   
                    
                #LIKES
                elif 'e0f59e4a1c8d78d0161873bc2ee7ec44' in data_url:                   
                    end_cursor = response['data']['shortcode_media']['edge_liked_by']['page_info']['end_cursor']  
                    has_next_page = response['data']['shortcode_media']['edge_liked_by']['page_info']['has_next_page']   
                    edges = response['data']['shortcode_media']['edge_liked_by']['edges']
                    
                #COMMENTS
                elif 'f0986789a5c5d17c2400faebf16efd0d' in data_url:
                   end_cursor = response['data'] ['shortcode_media']['edge_media_to_comment']['page_info']['end_cursor'] 
                   has_next_page = response['data']['shortcode_media']['edge_media_to_comment']['page_info']['has_next_page']  
                   edges = response['data']['shortcode_media']['edge_media_to_comment']['edges']
                #FOLLOWS
                elif 'c56ee0ae1f89cdbd1c89e2bc6b8f3d18' in data_url:
                    end_cursor = response['data'] ['user']['edge_follow']['page_info']['end_cursor'] 
                    has_next_page = response['data'] ['user']['edge_follow']['page_info']['has_next_page']  
                    edges = response['data']['user']['edge_follow']['edges']
                                   
                return edges, has_next_page, end_cursor
                
            #If reached KeyError, probably reached request limit
            except KeyError as e:
                if  'rate limited' in response['message']:
                    print('reached maximum rate limit.. trying again in {} min'.format(TRY_AGAIN_SLEEP_SECS/60))
                    time.sleep(TRY_AGAIN_SLEEP_SECS)
                else:
                    print("Keyerror: "+
                          response + 
                          "\n exit program..")
                    raise SystemExit          
                
    #Update the gis-cookie
    #md5-hash = rhx_value:params
    #rhx_value is stored in sharedData
    def update_ig_gis_header(self, params):
        self.session.headers.update({
            'x-instagram-gis': 
                hashlib.md5((self.rhx_gis + ":" + params).encode('utf-8')).hexdigest()
            })      
                                 
    #Parse sharedData from source code
    #sharedData is needed for grabbing IDs etc
    def get_sharedData(self, username):     
        response = self.session.get(BASE_URL+username)      
        sharedData = self.to_json(response.text.split("window._sharedData = ")[1].split(";</script>")[0])        
        #Update current rhx_gis
        self.rhx_gis = sharedData['rhx_gis']     
        return sharedData['entry_data']['ProfilePage'][0]['graphql']['user']
    
    def format_timestamp(self,timestamp):
        return time.strftime("%D", time.localtime(int(timestamp)))
        
def main():
    parser = argparse.ArgumentParser(description='---Activity Hunter--- Track and collect a users activity on Instagram')
    parser.add_argument("--target-user", help='<Required> Track this users activity activity', required=True)
    parser.add_argument('--from-users',"--from_users", help='<Required> Track activity on these accounts, separated with space',nargs='+', required=True)

    parser.add_argument('--login-name',"--login_name", help='Login name (required if user acc is private)')
    parser.add_argument('--login-password',"--login_pw", help='Login password (required if user acc is private)')
    parser.add_argument('--likes', help='track likes by target', action="store_true")
    parser.add_argument('--tags', help='track tags in media of target', action="store_true")
    parser.add_argument('--comments', help='track comments by target', action="store_true")
    parser.add_argument('--popularity', help='Set limit to amount of likes on media (recommended)', type=int)
    parser.add_argument('--from-time','--from_time', help='check media after date uploaded, d/m/Y format')
    parser.add_argument('--to-time','--to_time', help='check media before date, d/m/Y format')
    
    args = parser.parse_args() 
    
    a = ActivityHunter(**vars(args))
    
    a.scrape()
   

if __name__ == '__main__':
    main()